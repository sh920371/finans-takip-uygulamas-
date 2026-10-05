import json
import os
 
import numpy as np
import pandas as pd
import pyqtgraph as pg
import requests
import yfinance as yf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
 
 
# ============================================================
# BINANCE PERİYOT EŞLEŞTİRMESİ
# ============================================================
# Karşılaştırma ekranındaki periyot anahtarına göre Binance
# kline aralığı ve kaç mum çekileceği.
BINANCE_INTERVAL_MAP = {
    "1g": ("15m", 96),
    "1h": ("1h", 120),
    "1ay": ("1d", 30),
    "3ay": ("1d", 90),
    "6ay": ("1d", 180),
    "1y": ("1d", 365),
    "ytd": ("1d", 400),
}
 
 
def _binance_sembolu_mu(sembol):
    """Bir sembolün Binance formatında (örn. BTCUSDT) olup olmadığını anlar.
    yfinance formatındaki kripto sembolleri (BTC-USD), döviz pariteleri (USDTRY=X)
    ve hisse sembolleri (THYAO.IS) burada yanlışlıkla kripto sayılmasın diye
    '-', '=' ve '.' içeren semboller hariç tutulur."""
    s = sembol.upper().strip()
    if not s or "-" in s or "=" in s or "." in s:
        return False
    for suffix in ("USDT", "BUSD", "FDUSD", "BIDR", "BTC", "ETH", "BNB", "TRY"):
        if s.endswith(suffix) and len(s) > len(suffix):
            return True
    return False
 
 
def _indeksi_naive_utc_yap(seri):
    """Bir Series'in tarih indeksini saat dilimsiz (naive) UTC'ye çevirir.
    Hisse/döviz (yfinance, saat dilimi bilgili gün-içi veri döndürebiliyor) ile
    kripto (Binance, saat dilimsiz) verilerini aynı grafikte karşılaştırabilmek
    için ikisinin de aynı 'tür' tarih indeksine sahip olması şart - aksi halde
    pandas ikisini hizalayamıyor ve özellikle kısa periyotlarda (1g, 1h) hiç
    ortak veri bulunamıyordu."""
    if seri is None or seri.empty:
        return seri
 
    if getattr(seri.index, "tz", None) is not None:
        seri = seri.copy()
        seri.index = seri.index.tz_convert("UTC").tz_localize(None)
 
    return seri
 
 
def _binance_seri_getir(sembol, interval, limit):
    """Binance'ten kapanış fiyatlarını tarih indeksli bir pandas Series olarak döndürür."""
    url = f"https://api.binance.com/api/v3/klines?symbol={sembol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            return None
        veri = response.json()
        if not veri or not isinstance(veri, list):
            return None
 
        # NOT: datetime.fromtimestamp() sistem saat dilimini kullanır ve bu da
        # hangi bilgisayarda çalıştığına göre değişen, tutarsız sonuçlar verir.
        # Binance zaman damgaları zaten UTC epoch milisaniye cinsinden geldiği
        # için doğrudan UTC olarak yorumlamak (pd.to_datetime(..., unit="ms"))
        # hem daha doğru hem de yfinance ile aynı 'saat dilimsiz UTC' formatını
        # verir.
        zaman_damgalari = [k[0] for k in veri]
        kapanislar = [float(k[4]) for k in veri]
        tarih_indeksi = pd.to_datetime(zaman_damgalari, unit="ms")
        return pd.Series(kapanislar, index=tarih_indeksi, name=sembol).dropna()
    except Exception as e:
        print(f"Binance veri çekme hatası ({sembol}): {e}")
        return None
 
 
def _yfinance_seri_getir(sembol, yf_period, yf_interval="1d"):
    """yfinance'ten kapanış fiyatlarını tarih indeksli bir pandas Series olarak döndürür."""
    try:
        temp_df = yf.download(sembol, period=yf_period, interval=yf_interval, progress=False)
    except Exception as e:
        print(f"yfinance veri çekme hatası ({sembol}): {e}")
        return None
 
    if temp_df is None or temp_df.empty:
        # Bazı semboller/borsalar için seçilen intraday aralık desteklenmeyebilir
        # (örn. çok eski/az işlem gören hisseler). Böyle durumda günlük veriye düş.
        if yf_interval != "1d":
            try:
                temp_df = yf.download(sembol, period=yf_period, interval="1d", progress=False)
            except Exception:
                return None
        if temp_df is None or temp_df.empty:
            return None
 
    close_col = temp_df["Close"]
    if isinstance(close_col, pd.DataFrame):
        close_col = close_col.iloc[:, 0]
    seri = close_col.dropna().rename(sembol)
    return _indeksi_naive_utc_yap(seri)
 
 
def seri_getir(sembol, secilen_periyot, yf_period, yf_interval="1d"):
    """Sembolün türüne göre doğru kaynaktan (Binance ya da yfinance) veri çeker."""
    if _binance_sembolu_mu(sembol):
        interval, limit = BINANCE_INTERVAL_MAP.get(secilen_periyot, ("1d", 200))
        seri = _binance_seri_getir(sembol, interval, limit)
        if seri is not None and not seri.empty:
            return seri
        return None
 
    return _yfinance_seri_getir(sembol, yf_period, yf_interval)
 
 
def _tarih_ekseni_etiketleri_olustur(tarihler, hedef_etiket_sayisi=7):
    """Grafiğin alt eksenindeki 0,1,2,3... gibi anlamsız indeks numaraları yerine
    gerçek tarih/saat etiketleri üretir. Veri yoğunluğuna göre otomatik olarak
    seyrekleştirir, böylece etiketler üst üste binmez."""
    n = len(tarihler)
    if n == 0:
        return []
 
    adim = max(1, n // hedef_etiket_sayisi)
    etiketler = []
 
    for i in range(0, n, adim):
        tarih = tarihler[i]
        if hasattr(tarih, "strftime"):
            gun_ici_veri_var = getattr(tarih, "hour", 0) != 0 or getattr(tarih, "minute", 0) != 0
            metin = tarih.strftime("%d %b %H:%M") if gun_ici_veri_var else tarih.strftime("%d %b")
        else:
            metin = str(tarih)
        etiketler.append((i, metin))
 
    # Son noktayı da her zaman göster ki grafiğin nereye kadar gittiği belli olsun
    if etiketler[-1][0] != n - 1:
        son_tarih = tarihler[-1]
        if hasattr(son_tarih, "strftime"):
            gun_ici_veri_var = getattr(son_tarih, "hour", 0) != 0 or getattr(son_tarih, "minute", 0) != 0
            metin = son_tarih.strftime("%d %b %H:%M") if gun_ici_veri_var else son_tarih.strftime("%d %b")
        else:
            metin = str(son_tarih)
        etiketler.append((n - 1, metin))
 
    return etiketler
 
 
def _korelasyon_yorumu_olustur(korelasyon):
    """Pearson korelasyon katsayısını sade dilde yorumlar."""
    if korelasyon is None or (isinstance(korelasyon, float) and np.isnan(korelasyon)):
        return "Hesaplanamadı", "#a1a1aa", "Korelasyon hesaplamak için yeterli ortak veri noktası yok."
 
    if korelasyon >= 0.7:
        return (
            f"Güçlü Pozitif (+{korelasyon:.2f})", "#ef4444",
            "İki varlık genellikle aynı yönde hareket ediyor. Bu ikisini birlikte tutmak "
            "çeşitlendirme (risk dağıtma) açısından fazla avantaj sağlamayabilir; ikisi de "
            "aynı anda düşebilir."
        )
    if korelasyon >= 0.3:
        return (
            f"Orta Düzey Pozitif (+{korelasyon:.2f})", "#facc15",
            "İki varlık kısmen aynı yönde hareket etme eğiliminde, ama aralarında belirgin "
            "farklılıklar da var."
        )
    if korelasyon > -0.3:
        return (
            f"Zayıf / Anlamsız ({korelasyon:+.2f})", "#a1a1aa",
            "İki varlığın hareketleri birbirinden büyük ölçüde bağımsız görünüyor."
        )
    if korelasyon > -0.7:
        return (
            f"Orta Düzey Negatif ({korelasyon:+.2f})", "#38bdf8",
            "İki varlık kısmen ters yönde hareket etme eğiliminde; biri düşerken diğeri "
            "yükselebiliyor."
        )
    return (
        f"Güçlü Negatif ({korelasyon:+.2f})", "#22c55e",
        "İki varlık büyük ölçüde ters yönde hareket ediyor. Bu tür bir ikili birlikte "
        "tutulduğunda genellikle riski dengeleyici bir etki yapar (biri kaybederken diğeri "
        "kazanma eğiliminde olabilir)."
    )
 
 
def _rsi_hesapla(seri, period=14):
    """Wilder yöntemine yakın, basit ve hızlı bir RSI (Göreceli Güç Endeksi)
    hesaplaması. 0-100 arası, ilk `period` kadar değer NaN olur (yeterli veri
    birikene kadar hesaplanamaz - grafikte connect='finite' ile bu boşluklar
    otomatik atlanır)."""
    delta = seri.diff()
    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)
 
    ort_kazanc = kazanc.rolling(period).mean()
    ort_kayip = kayip.rolling(period).mean()
 
    rs = ort_kazanc / ort_kayip.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))
 
 
class SohbetSekmesi(QWidget):
 
    def __init__(self, username=None):
        super().__init__()
        # Kullanıcıya özel izleme listesi dosyasını bulmak için gerekli
        self.username = username
 
        # Grafik imleci (crosshair) için ara veriler
        self._x_vals = []
        self._tarihler = []
        self._s1 = ""
        self._s2 = ""
        self._getiri1_arr = []
        self._getiri2_arr = []
 
        self.init_ui()
        self.varliklari_yukle()
 
    def showEvent(self, event):
        super().showEvent(event)
        # Sekme her açıldığında/görünür olduğunda izleme listesini otomatik tazele
        self.varliklari_yukle()
 
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
 
        # 1. Üst Kısım: Varlık ve Periyot Seçim Paneli
        secim_layout = QHBoxLayout()
 
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
 
        # Periyot Seçim Kutusu
        self.combo_period = QComboBox()
        self.combo_period.addItems(["1g", "1h", "1ay", "3ay", "6ay", "1y", "ytd"])
        self.combo_period.setCurrentText("1ay")  # Varsayılan 1 ay
 
        self.btn_karsilastir = QPushButton("Varlıkları Karşılaştır ve Teknik Analiz Yap")
        self.btn_karsilastir.setStyleSheet("""
            QPushButton {
                background-color: #b388ff;
                color: #1e1e2f;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #9575cd;
            }
        """)
        self.btn_karsilastir.clicked.connect(self.detayli_analiz_ve_ciz)
 
        secim_layout.addWidget(QLabel("1. Varlık:"))
        secim_layout.addWidget(self.combo1)
        secim_layout.addWidget(QLabel("2. Varlık:"))
        secim_layout.addWidget(self.combo2)
        secim_layout.addWidget(QLabel("Periyot:"))
        secim_layout.addWidget(self.combo_period)
        secim_layout.addWidget(self.btn_karsilastir)
        main_layout.addLayout(secim_layout)
 
        # 2. Orta Kısım: pyqtgraph İnteraktif Grafik Alanı
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#0d0d12")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)
        self.plot_widget.addLegend(offset=(10, 10))
 
        styles = {"color": "#b388ff", "font-size": "11px"}
        self.plot_widget.setLabel("left", "Getiri / Değişim (%)", **styles)
        self.plot_widget.setLabel("bottom", "İşlem Zaman Çizelgesi", **styles)
 
        # Sıfır çizgisi - pozitif/negatif bölgeyi ayırt etmek için
        self.plot_widget.addLine(y=0, pen=pg.mkPen("#3f3f46", width=1, style=Qt.PenStyle.DashLine))
 
        # Her yeni çizimde görünümü elimizdeki veriye göre otomatik ölçeklendir
        # (periyot değiştiğinde grafiğin eski, uyumsuz bir aralıkta sıkışık kalmaması için)
        self.plot_widget.getPlotItem().enableAutoRange(axis="xy", enable=True)
 
        # Grafik imleci (crosshair)
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen("#71717a", style=Qt.PenStyle.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen("#71717a", style=Qt.PenStyle.DashLine))
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self._mouse_moved)
 
        main_layout.addWidget(self.plot_widget, stretch=3)
 
        # RSI (momentum) paneli - ana grafiğin altında, x eksenine bağlı (linked)
        # ikinci bir panel. Her iki varlığın momentumunu ayrı ayrı gösterir.
        self.rsi_plot_widget = pg.PlotWidget()
        self.rsi_plot_widget.setBackground("#0d0d12")
        self.rsi_plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.rsi_plot_widget.setMaximumHeight(130)
        self.rsi_plot_widget.setYRange(0, 100)
        self.rsi_plot_widget.setLabel("left", "RSI", **styles)
        self.rsi_plot_widget.addLegend(offset=(10, 5))
        self.rsi_plot_widget.setXLink(self.plot_widget)
        self.rsi_plot_widget.addLine(y=70, pen=pg.mkPen("#ef4444", width=1, style=Qt.PenStyle.DotLine))
        self.rsi_plot_widget.addLine(y=30, pen=pg.mkPen("#22c55e", width=1, style=Qt.PenStyle.DotLine))
 
        main_layout.addWidget(self.rsi_plot_widget, stretch=1)
 
        # İmleç bilgi etiketi - fare grafik üzerinde gezinirken anlık değerleri gösterir
        self.imlec_label = QLabel("📍 Değerleri görmek için grafik üzerinde gezinin...")
        self.imlec_label.setStyleSheet("""
            QLabel {
                color: #e4e4e7;
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.imlec_label)
 
        # 3. Alt Kısım: Detaylı Teknik Karşılaştırma ve Yorum Kutusu
        self.yorum_kutusu = QTextEdit()
        self.yorum_kutusu.setReadOnly(True)
        self.yorum_kutusu.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI';
                font-size: 13px;
                border: 2px solid #b388ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.yorum_kutusu.setHtml(
            "<p style='color: #b388ff; font-weight: bold;'>🤖 İzleme listesindeki varlıklarınız yüklendi.</p>"
            "<p style='color: #e0e0e0;'>Karşılaştırmak istediğiniz varlıkları ve periyodu seçip <b>'Varlıkları Karşılaştır ve Teknik Analiz Yap'</b> butonuna basın...</p>"
        )
        main_layout.addWidget(self.yorum_kutusu, stretch=2)
 
        self.setLayout(main_layout)
 
    # ------------------------------------------------------------
    # GRAFİK İMLECİ
    # ------------------------------------------------------------
 
    def _mouse_moved(self, evt):
        pos = evt[0]
        if len(self._x_vals) == 0:
            return
        if not self.plot_widget.sceneBoundingRect().contains(pos):
            return
 
        vb = self.plot_widget.getPlotItem().vb
        mouse_point = vb.mapSceneToView(pos)
        index = int(round(mouse_point.x()))
 
        if 0 <= index < len(self._x_vals):
            self.vLine.setPos(mouse_point.x())
            self.hLine.setPos(mouse_point.y())
 
            tarih = self._tarihler[index]
            tarih_str = tarih.strftime("%Y-%m-%d") if hasattr(tarih, "strftime") else str(tarih)
 
            v1 = self._getiri1_arr[index]
            v2 = self._getiri2_arr[index]
 
            renk1 = "#b388ff"
            renk2 = "#00e676"
 
            self.imlec_label.setText(
                f"📅 <b>{tarih_str}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<span style='color:{renk1};'>{self._s1}: %{v1:+.2f}</span> &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<span style='color:{renk2};'>{self._s2}: %{v2:+.2f}</span>"
            )
            self.imlec_label.setTextFormat(Qt.TextFormat.RichText)
 
    # ------------------------------------------------------------
    # İZLEME LİSTESİNDEN SEMBOL YÜKLEME
    # ------------------------------------------------------------
 
    def _watch_state_dosya_yolu(self):
        """Kullanıcıya özel izleme listesi dosyasını döndürür.
        Yeni sistemde her kullanıcının kendi watch_state_<kullanici>.json dosyası var.
        Böyle bir dosya henüz yoksa (örn. hesap yeni açıldıysa) eski ortak
        watch_state.json'a geri düşer, böylece hiçbir kullanıcı boş ekranla kalmaz."""
        if self.username:
            kisiye_ozel = f"watch_state_{self.username}.json"
            if os.path.exists(kisiye_ozel):
                return kisiye_ozel
        return "watch_state.json"
 
    def varliklari_yukle(self):
        # Kullanıcının şu an seçtiği sembolleri hafızada tut
        secili1 = self.combo1.currentText().strip()
        secili2 = self.combo2.currentText().strip()
 
        ham_semboller = []
 
        dosya_yolu = self._watch_state_dosya_yolu()
 
        try:
            if os.path.exists(dosya_yolu):
                with open(dosya_yolu, "r", encoding="utf-8") as f:
                    data = json.load(f)
 
                    def derin_ara(item):
                        if isinstance(item, str):
                            item_str = item.strip()
                            if item_str and not item_str.startswith("{") and len(item_str) < 20:
                                ham_semboller.append(item_str)
                        elif isinstance(item, dict):
                            bulundu = False
                            for key in ["symbol", "ticker", "name"]:
                                if key in item and isinstance(item[key], str):
                                    val_str = item[key].strip()
                                    if len(val_str) < 15:
                                        ham_semboller.append(val_str)
                                        bulundu = True
                                        break
                            if not bulundu:
                                for val in item.values():
                                    derin_ara(val)
                        elif isinstance(item, list):
                            for sub_item in item:
                                derin_ara(sub_item)
 
                    derin_ara(data)
        except Exception as e:
            print(f"{dosya_yolu} okunurken hata: {e}")
 
        if not ham_semboller:
            ham_semboller = [
                "THYAO.IS", "GARAN.IS", "EREGL.IS", "AKBNK.IS",
                "ASELS.IS", "SASA.IS", "TUPRS.IS", "USDTRY=X", "BTCUSDT", "ETHUSDT"
            ]
 
        temiz_semboller = []
        for s in ham_semboller:
            s_clean = s.strip()
            if s_clean and not s_clean.startswith("{") and " " not in s_clean and len(s_clean) < 15:
                if s_clean not in temiz_semboller:
                    temiz_semboller.append(s_clean)
 
        if not temiz_semboller:
            temiz_semboller = ["THYAO.IS", "GARAN.IS", "ASELS.IS"]
 
        self.combo1.clear()
        self.combo2.clear()
        self.combo1.addItems(temiz_semboller)
        self.combo2.addItems(temiz_semboller)
 
        # Eski seçimler yeni listede varsa koru, yoksa akıllı indeks ataması yap
        if secili1 in temiz_semboller:
            self.combo1.setCurrentText(secili1)
 
        if secili2 in temiz_semboller and secili2 != self.combo1.currentText():
            self.combo2.setCurrentText(secili2)
        elif len(temiz_semboller) > 1:
            if self.combo2.currentText() == self.combo1.currentText():
                self.combo2.setCurrentIndex(1)
 
    # ------------------------------------------------------------
    # KARŞILAŞTIRMA VE ANALİZ
    # ------------------------------------------------------------
 
    def detayli_analiz_ve_ciz(self):
        s1 = self.combo1.currentText().strip()
        s2 = self.combo2.currentText().strip()
        secilen_periyot = self.combo_period.currentText()
 
        # yfinance için periyot eşleştirmesi (Binance için BINANCE_INTERVAL_MAP kullanılıyor)
        period_map = {
            "1g": "1d",
            "1h": "5d",
            "1ay": "1mo",
            "3ay": "3mo",
            "6ay": "6mo",
            "1y": "1y",
            "ytd": "ytd"
        }
        yf_period = period_map.get(secilen_periyot, "1mo")
 
        # yfinance mum aralığı (interval) - belirtilmezse yfinance her periyotta
        # günlük tek bar döndürür, "1g" ve "1h" seçiminde gün-içi (saatlik/dakikalık)
        # veri gösterebilmek için bunu ayrıca ayarlamak gerekiyor.
        yf_interval_map = {
            "1g": "5m",
            "1h": "60m",
            "1ay": "1d",
            "3ay": "1d",
            "6ay": "1d",
            "1y": "1d",
            "ytd": "1d",
        }
        yf_interval = yf_interval_map.get(secilen_periyot, "1d")
 
        if not s1 or not s2 or s1.startswith("{") or s2.startswith("{"):
            self.yorum_kutusu.setHtml("<p style='color: #ff5252;'>⚠️ Lütfen geçerli ve temiz borsa sembolleri seçtiğinizden emin olun.</p>")
            return
 
        if s1 == s2:
            self.yorum_kutusu.setHtml("<p style='color: #ff5252;'>⚠️ Lütfen karşılaştırmak için iki farklı varlık seçin.</p>")
            return
 
        self.yorum_kutusu.setHtml(f"<p style='color: #b388ff;'>⏳ '{s1}' ve '{s2}' için <b>{secilen_periyot.upper()}</b> periyodunda veriler alınıyor ve hesaplanıyor...</p>")
 
        try:
            series_list = []
            for sym in [s1, s2]:
                seri = seri_getir(sym, secilen_periyot, yf_period, yf_interval)
                if seri is not None and not seri.empty:
                    series_list.append(seri)
 
            if len(series_list) != 2:
                self.yorum_kutusu.setHtml(f"<p style='color: #ff5252;'>❌ '{s1}' veya '{s2}' için seçilen periyotta yeterli veri alınamadı.</p>")
                return
 
            df = pd.concat(series_list, axis=1).ffill().dropna()
 
            if df.empty or len(df) < 2:
                self.yorum_kutusu.setHtml("<p style='color: #ff5252;'>❌ Seçilen periyotta ortak işlem verisi bulunamadı.</p>")
                return
 
            df_norm = (df / df.iloc[0] - 1) * 100
 
            self.plot_widget.clear()
            self.plot_widget.addLegend(offset=(10, 10))
            self.plot_widget.addLine(y=0, pen=pg.mkPen("#3f3f46", width=1, style=Qt.PenStyle.DashLine))
            self.plot_widget.addItem(self.vLine, ignoreBounds=True)
            self.plot_widget.addItem(self.hLine, ignoreBounds=True)
 
            x_vals = np.arange(len(df_norm))
            y1 = df_norm[s1].values
            y2 = df_norm[s2].values
 
            renk1 = "#b388ff"
            renk2 = "#00e676"
 
            pen1 = pg.mkPen(color=renk1, width=2.5)
            curve1 = self.plot_widget.plot(x_vals, y1, pen=pen1, name=f"{s1} (%)")
 
            pen2 = pg.mkPen(color=renk2, width=2.5)
            curve2 = self.plot_widget.plot(x_vals, y2, pen=pen2, name=f"{s2} (%)")
 
            # Göreceli Güç çizgisi: s1/s2 fiyat oranının başlangıca göre yüzde değişimi.
            # Yukarı gidiyorsa s1, s2'ye göre güçleniyor; aşağı gidiyorsa zayıflıyor demektir.
            # Tek bakışta "hangisi hangisine göre daha iyi gidiyor" sorusuna cevap verir.
            goreceli_oran = df[s1] / df[s2]
            goreceli_guc = (goreceli_oran / goreceli_oran.iloc[0] - 1) * 100
            pen_goreceli = pg.mkPen(color="#facc15", width=1.5, style=Qt.PenStyle.DashLine)
            self.plot_widget.plot(
                x_vals, goreceli_guc.values, pen=pen_goreceli,
                name=f"{s1}/{s2} Göreceli Güç", connect="finite"
            )
 
            # Sıfır çizgisine göre dolgu - kazanç/kayıp bölgesini görsel olarak vurgular
            sifir_curve = self.plot_widget.plot(x_vals, np.zeros(len(x_vals)), pen=None)
            self.plot_widget.addItem(pg.FillBetweenItem(curve1, sifir_curve, brush=pg.mkBrush(179, 136, 255, 30)))
            self.plot_widget.addItem(pg.FillBetweenItem(curve2, sifir_curve, brush=pg.mkBrush(0, 230, 118, 22)))
 
            # X eksenine anlamsız 0,1,2... indeksleri yerine gerçek tarih/saat etiketleri koy
            tarih_etiketleri = _tarih_ekseni_etiketleri_olustur(list(df_norm.index))
            self.plot_widget.getAxis("bottom").setTicks([tarih_etiketleri])
 
            # ÖNEMLİ DÜZELTME: clear() sonrası pyqtgraph görünüm aralığını sıfırlamaz,
            # önceki periyodun (örn. "1y") geniş aralığını hafızada tutar. Yeni veri
            # daha az nokta içeriyorsa (örn. "1h" seçince), o eski geniş aralığın
            # ufak bir köşesine sıkışıp tek bir nokta gibi görünüyordu. Her çizimden
            # sonra görünümü elimizdeki gerçek veriye göre otomatik ölçeklendiriyoruz.
            self.plot_widget.getPlotItem().enableAutoRange(axis="xy", enable=True)
            self.plot_widget.getPlotItem().getViewBox().autoRange()
 
            # ---- RSI (momentum) paneli ----
            self.rsi_plot_widget.clear()
            self.rsi_plot_widget.addLegend(offset=(10, 5))
            self.rsi_plot_widget.addLine(y=70, pen=pg.mkPen("#ef4444", width=1, style=Qt.PenStyle.DotLine))
            self.rsi_plot_widget.addLine(y=30, pen=pg.mkPen("#22c55e", width=1, style=Qt.PenStyle.DotLine))
 
            rsi1 = _rsi_hesapla(df[s1])
            rsi2 = _rsi_hesapla(df[s2])
 
            self.rsi_plot_widget.plot(
                x_vals, rsi1.values, pen=pg.mkPen(color=renk1, width=1.5), name=s1, connect="finite"
            )
            self.rsi_plot_widget.plot(
                x_vals, rsi2.values, pen=pg.mkPen(color=renk2, width=1.5), name=s2, connect="finite"
            )
            self.rsi_plot_widget.setYRange(0, 100)
 
            # İmleç için ara verileri sakla
            self._x_vals = x_vals
            self._tarihler = list(df_norm.index)
            self._s1 = s1
            self._s2 = s2
            self._getiri1_arr = y1
            self._getiri2_arr = y2
 
            getiri1 = float(df_norm[s1].iloc[-1])
            getiri2 = float(df_norm[s2].iloc[-1])
            volatilite1 = float(df_norm[s1].std())
            volatilite2 = float(df_norm[s2].std())
            max1 = float(df_norm[s1].max())
            min1 = float(df_norm[s1].min())
            max2 = float(df_norm[s2].max())
            min2 = float(df_norm[s2].min())
 
            skor1 = getiri1 / (volatilite1 if volatilite1 > 0 else 1)
            skor2 = getiri2 / (volatilite2 if volatilite2 > 0 else 1)
 
            kazanan = s1 if skor1 > skor2 else s2
 
            # Korelasyon: iki varlığın günlük getirilerinin birlikte hareket edip
            # etmediğini ölçer. +1'e yakın = aynı yönde, -1'e yakın = ters yönde,
            # 0'a yakın = birbirinden bağımsız hareket ediyorlar demektir.
            try:
                gunluk_getiri1 = df[s1].pct_change().dropna()
                gunluk_getiri2 = df[s2].pct_change().dropna()
                korelasyon = gunluk_getiri1.corr(gunluk_getiri2)
                if isinstance(korelasyon, float) and np.isnan(korelasyon):
                    korelasyon = None
            except Exception:
                korelasyon = None
 
            korelasyon_etiket, korelasyon_renk, korelasyon_aciklama = _korelasyon_yorumu_olustur(korelasyon)
 
            # Göreceli güç ve RSI özetleri (grafikteki yeni panellerin sözel karşılığı)
            son_goreceli_guc = float(goreceli_guc.iloc[-1]) if not goreceli_guc.empty else 0.0
            goreceli_lider = s1 if son_goreceli_guc >= 0 else s2
 
            son_rsi1 = float(rsi1.dropna().iloc[-1]) if not rsi1.dropna().empty else None
            son_rsi2 = float(rsi2.dropna().iloc[-1]) if not rsi2.dropna().empty else None
 
            if son_rsi1 is not None and son_rsi2 is not None:
                rsi_ozet = f"{s1} RSI: <b>{son_rsi1:.1f}</b> &nbsp;|&nbsp; {s2} RSI: <b>{son_rsi2:.1f}</b>"
                daha_guclu_momentum = s1 if son_rsi1 > son_rsi2 else s2
                rsi_yorum = f"Şu anki momentum ({rsi_ozet}) açısından <b>{daha_guclu_momentum}</b> diğerine göre daha güçlü bir ivmeye sahip."
            else:
                rsi_yorum = "RSI hesaplamak için yeterli veri noktası yok."
 
            rapo_html = f"""
            <div style='color: #e0e0e0; font-family: Segoe UI, sans-serif; font-size: 13px;'>
                <p style='color: #b388ff; font-size: 15px; font-weight: bold; margin-bottom: 5px;'>📊 KAPSAMLI TEKNİK PİYASA VE RİSK ANALİZ RAPORU ({secilen_periyot.upper()})</p>
                <hr style='border: 0.5px solid #3d354c; margin-bottom: 10px;'>
 
                <p><b>📈 1. Seçilen Periyot Performans ve Getiri:</b><br>
                &nbsp;&nbsp;• <b>{s1}</b> Toplam Değişim: <span style='color: {"#00e676" if getiri1 >= 0 else "#ff5252"};'>%{getiri1:+.2f}</span><br>
                &nbsp;&nbsp;• <b>{s2}</b> Toplam Değişim: <span style='color: {"#00e676" if getiri2 >= 0 else "#ff5252"};'>%{getiri2:+.2f}</span></p>
 
                <p><b>📉 2. Fiyat Aralıkları (Zirve ve Dip Noktaları):</b><br>
                &nbsp;&nbsp;• {s1} -> En Yüksek: %{max1:+.2f} | En Düşük: %{min1:+.2f}<br>
                &nbsp;&nbsp;• {s2} -> En Yüksek: %{max2:+.2f} | En Düşük: %{min2:+.2f}</p>
 
                <p><b>⚖️ 3. Volatilite (Risk / Dalgalanma) Skoru:</b><br>
                &nbsp;&nbsp;• {s1} Oynaklık: <code>{volatilite1:.2f}</code><br>
                &nbsp;&nbsp;• {s2} Oynaklık: <code>{volatilite2:.2f}</code></p>
 
                <p><b>🔗 4. Korelasyon Analizi:</b><br>
                &nbsp;&nbsp;• Katsayı: <span style='color: {korelasyon_renk}; font-weight: bold;'>{korelasyon_etiket}</span><br>
                &nbsp;&nbsp;• {korelasyon_aciklama}</p>
 
                <p><b>⚡ 5. Göreceli Güç ve Momentum (RSI)</b><br>
                &nbsp;&nbsp;• Göreceli Güç: <b>{s1}/{s2}</b> oranı periyot başından bu yana <span style='color: {"#00e676" if son_goreceli_guc >= 0 else "#ff5252"};'>%{son_goreceli_guc:+.2f}</span> değişti — yani <b>{goreceli_lider}</b> bu periyotta diğerine göre üstün performans gösterdi.<br>
                &nbsp;&nbsp;• {rsi_yorum}</p>
 
                <p><b>🏆 6. Teknik Analiz ve Akıllı Değerlendirme:</b><br>
                İncelenen {secilen_periyot} aralığında <b>{s1}</b> toplam <span style='color: {"#00e676" if getiri1 >= 0 else "#ff5252"};'>%{getiri1:+.2f}</span> getiri sağlarken, <b>{s2}</b> varlığı <span style='color: {"#00e676" if getiri2 >= 0 else "#ff5252"};'>%{getiri2:+.2f}</span> değişim gösterdi.<br>
                • <b>Risk Profili:</b> {'<b>' + s1 + '</b>, ' + s2 + "'ye kıyasla daha düşük dalgalanma sergileyerek daha istikrarlı bir seyir izledi." if volatilite1 < volatilite2 else '<b>' + s2 + '</b>, ' + s1 + "'e kıyasla daha düşük dalgalanma sergileyerek daha istikrarlı bir seyir izledi."}<br>
                • <b>Verimlilik Özeti:</b> Risk birimi başına elde edilen getiri göz önüne alındığında, <b>{kazanan}</b> bu dönemde daha rasyonel ve verimli bir risk/kazanç dengesi kurdu.</p>
 
                <p style='color:#6b6475; font-size:10.5px; margin-top:8px;'>
                ⚠️ Bu rapor yalnızca geçmiş fiyat verilerine dayalı otomatik bir teknik değerlendirmedir,
                yatırım tavsiyesi değildir.
                </p>
            </div>
            """
 
            self.yorum_kutusu.setHtml(rapo_html)
 
        except Exception as e:
            self.yorum_kutusu.setHtml(f"<p style='color: #ff5252;'>⚠️ Teknik analiz hesaplanırken hata oluştu: {e}</p>")