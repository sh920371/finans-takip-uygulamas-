import json
import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton
import pyqtgraph as pg
import yfinance as yf
import numpy as np
from datetime import datetime
 
 
# =========================================================
#  TEKNİK ANALİZ YARDIMCI FONKSİYONLARI
# =========================================================
 
def sma_full(prices, window):
    """Basit hareketli ortalama - dizinin başındaki eksik kısımları NaN ile doldurur (grafikte x eksenine hizalı kalması için)."""
    n = len(prices)
    result = np.full(n, np.nan)
    if n < window:
        return result
    csum = np.cumsum(np.insert(prices, 0, 0.0))
    sma = (csum[window:] - csum[:-window]) / window
    result[window - 1:] = sma
    return result
 
 
def bollinger_full(prices, window=20, num_std=2):
    """Bollinger Bantları: orta bant (SMA), üst bant, alt bant."""
    n = len(prices)
    sma = sma_full(prices, window)
    std = np.full(n, np.nan)
    for i in range(window - 1, n):
        std[i] = np.std(prices[i - window + 1:i + 1])
    upper = sma + num_std * std
    lower = sma - num_std * std
    return sma, upper, lower
 
 
def rsi_full(prices, period=14):
    """Wilder yöntemiyle RSI (Göreceli Güç Endeksi). 0-100 arası, NaN dolgulu, x eksenine hizalı dizi döner."""
    n = len(prices)
    rsi = np.full(n, np.nan)
    if n < period + 1:
        return rsi
 
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
 
    avg_gain = gains[:period].mean()
    avg_loss = losses[:period].mean()
    rsi[period] = 100.0 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
 
    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        if avg_loss == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100 - (100 / (1 + rs))
 
    return rsi
 
def ema_full(prices, window):
    """Üstel Hareketli Ortalama (EMA)"""
    n = len(prices)
    result = np.full(n, np.nan)
    if n < window:
        return result
    alpha = 2.0 / (window + 1)
    sma_init = np.mean(prices[:window])
    result[window - 1] = sma_init
    prev_ema = sma_init
    for i in range(window, n):
        curr_ema = (prices[i] * alpha) + (prev_ema * (1 - alpha))
        result[i] = curr_ema
        prev_ema = curr_ema
    return result
 
 
def macd_full(prices, fast=12, slow=26, signal=9):
    """MACD, Sinyal ve Histogram hesaplar"""
    n = len(prices)
    macd_line = np.full(n, np.nan)
    signal_line = np.full(n, np.nan)
    histogram = np.full(n, np.nan)
 
    if n < slow:
        return macd_line, signal_line, histogram
 
    ema_fast = ema_full(prices, fast)
    ema_slow = ema_full(prices, slow)
 
    for i in range(n):
        if not np.isnan(ema_fast[i]) and not np.isnan(ema_slow[i]):
            macd_line[i] = ema_fast[i] - ema_slow[i]
 
    valid_macd_indices = [i for i, val in enumerate(macd_line) if not np.isnan(val)]
    if len(valid_macd_indices) >= signal:
        start_idx = valid_macd_indices[0]
        valid_macd_vals = macd_line[start_idx:]
        sig_vals = ema_full(valid_macd_vals, signal)
        for idx, val in enumerate(sig_vals):
            if not np.isnan(val):
                signal_line[start_idx + idx] = val
                histogram[start_idx + idx] = macd_line[start_idx + idx] - val
 
    return macd_line, signal_line, histogram
 
 
def vwap_full(highs, lows, closes, volumes):
    """VWAP (Hacim Ağırlıklı Ortalama Fiyat) hesaplar"""
    n = len(closes)
    vwap = np.full(n, np.nan)
    if n == 0 or np.sum(volumes) == 0:
        return vwap
    
    typical_price = (highs + lows + closes) / 3.0
    tp_vol = typical_price * volumes
    cum_tp_vol = np.cumsum(tp_vol)
    cum_vol = np.cumsum(volumes)
    
    for i in range(n):
        if cum_vol[i] > 0:
            vwap[i] = cum_tp_vol[i] / cum_vol[i]
    return vwap
 
 
def generate_technical_report(symbol, name, period, prices, highs, lows, volumes,
                              sma_short, sma_long, upper_band, lower_band, rsi, ema_short, macd, signal_line, vwap):
    """Bir finans uzmanının yazacağı formatta HTML teknik analiz raporu üretir."""
    last_macd = macd[-1] if len(macd) > 0 and not np.isnan(macd[-1]) else 0
    last_signal = signal_line[-1] if len(signal_line) > 0 and not np.isnan(signal_line[-1]) else 0
    macd_durum = "Boğa (Pozitif)" if last_macd > last_signal else "Ayı (Negatif)"
    
    last_vwap = vwap[-1] if len(vwap) > 0 and not np.isnan(vwap[-1]) else 0
    price_vs_vwap = "VWAP Üstünde (Güçlü)" if prices[-1] > last_vwap else "VWAP Altında (Zayıf)"
    last_price = prices[-1]
    min_p, max_p = float(np.min(prices)), float(np.max(prices))
 
    # ---- Trend ----
    last_sma_short = sma_short[-1] if not np.isnan(sma_short[-1]) else None
    last_sma_long = sma_long[-1] if not np.isnan(sma_long[-1]) else None
 
    if last_sma_short is not None and last_sma_long is not None:
        if last_sma_short > last_sma_long and last_price > last_sma_short:
            trend = "Yükseliş Trendi"
            trend_color = "#22c55e"
            trend_desc = "Kısa vadeli ortalama uzun vadeli ortalamanın üzerinde seyrediyor ve fiyat kısa vadeli ortalamayı destek olarak kullanıyor. Bu görünüm alıcıların kontrolde olduğuna işaret ediyor."
        elif last_sma_short < last_sma_long and last_price < last_sma_short:
            trend = "Düşüş Trendi"
            trend_color = "#ef4444"
            trend_desc = "Kısa vadeli ortalama uzun vadeli ortalamanın altında ve fiyat kısa vadeli ortalamanın altında kalıyor. Bu görünüm satıcıların baskın olduğuna işaret ediyor."
        else:
            trend = "Yatay / Kararsız Bölge"
            trend_color = "#facc15"
            trend_desc = "Kısa ve uzun vadeli ortalamalar iç içe geçmiş durumda; piyasa net bir yön belirlemiş değil, yön arayışı sürüyor."
    else:
        trend = "Yetersiz Veri"
        trend_color = "#a1a1aa"
        trend_desc = "Trend hesaplaması için yeterli veri noktası bulunmuyor."
 
    # ---- Momentum (RSI) ----
    last_rsi = rsi[-1] if len(rsi) > 0 and not np.isnan(rsi[-1]) else None
    if last_rsi is not None:
        if last_rsi >= 70:
            momentum = f"Aşırı Alım ({last_rsi:.1f})"
            momentum_color = "#ef4444"
            momentum_desc = "RSI aşırı alım bölgesinde; kısa vadede kâr satışlarıyla gelebilecek bir geri çekilme ihtimali normalden yüksek."
        elif last_rsi <= 30:
            momentum = f"Aşırı Satım ({last_rsi:.1f})"
            momentum_color = "#22c55e"
            momentum_desc = "RSI aşırı satım bölgesinde; teknik olarak tepki alımlarına açık bir zemin oluşmuş durumda."
        else:
            momentum = f"Nötr ({last_rsi:.1f})"
            momentum_color = "#a1a1aa"
            momentum_desc = "RSI nötr bantta; momentum ne aşırı alım ne aşırı satım tarafında baskın değil."
    else:
        momentum = "Hesaplanamadı"
        momentum_color = "#a1a1aa"
        momentum_desc = "RSI için yeterli veri yok."
 
    # ---- Volatilite (Bollinger Bant Genişliği) ----
    if not np.isnan(upper_band[-1]) and not np.isnan(lower_band[-1]) and last_sma_short:
        band_width_pct = ((upper_band[-1] - lower_band[-1]) / sma_short[-1]) * 100
        if band_width_pct > 8:
            volatility = f"Yüksek (Bant Genişliği: %{band_width_pct:.1f})"
            volatility_desc = "Bantlar geniş; fiyat hareketleri sert ve dalgalı seyrediyor, pozisyon büyüklüğünde temkinli olunmalı."
        elif band_width_pct < 3:
            volatility = f"Düşük / Sıkışma (Bant Genişliği: %{band_width_pct:.1f})"
            volatility_desc = "Bantlar daralmış durumda; bu tür sıkışmalar genellikle ileride sert bir yön hareketinin öncüsü olabilir."
        else:
            volatility = f"Normal (Bant Genişliği: %{band_width_pct:.1f})"
            volatility_desc = "Volatilite tarihsel ortalamalara yakın seyrediyor."
    else:
        volatility = "Hesaplanamadı"
        volatility_desc = "Bollinger Bantları için yeterli veri yok."
 
    # ---- Destek / Direnç ----
    lookback = min(len(prices), 20)
    support = float(np.min(lows[-lookback:])) if len(lows) >= lookback else min_p
    resistance = float(np.max(highs[-lookback:])) if len(highs) >= lookback else max_p
 
    # ---- Hacim ----
    volume_comment = ""
    if len(volumes) >= 5 and np.sum(volumes) > 0:
        recent_avg = np.mean(volumes[-5:])
        overall_avg = np.mean(volumes)
        if overall_avg > 0:
            if recent_avg > overall_avg * 1.3:
                volume_comment = "Son işlemlerde hacim, periyot ortalamasının belirgin şekilde üzerinde; mevcut harekete güçlü bir katılım eşlik ediyor."
            elif recent_avg < overall_avg * 0.7:
                volume_comment = "Son işlemlerde hacim, periyot ortalamasının altında; harekete katılım zayıf, bu da mevcut trendin gücünü sorgulatabilir."
            else:
                volume_comment = "Hacim, periyot ortalamasına yakın seyrediyor; belirgin bir anomali gözlenmiyor."
 
    # ---- Senaryo Bazlı Görünüm ----
    if trend == "Yükseliş Trendi" and last_rsi is not None and last_rsi < 70:
        outlook = (f"Trend and momentum şu an için birlikte yukarı yönlü çalışıyor. "
                   f"<b>{resistance:.4f}</b> direnç seviyesinin üzerinde kalıcılık, hareketin devam etme ihtimalini güçlendirebilir. "
                   f"Buna karşın <b>{support:.4f}</b> desteğinin kırılması, kısa vadeli görünümü zayıflatabilir.")
    elif trend == "Düşüş Trendi" and last_rsi is not None and last_rsi > 30:
        outlook = (f"Trend and momentum aşağı yönlü baskıyı destekliyor. "
                   f"<b>{support:.4f}</b> desteğinin altına sarkma, satış baskısının süreceğine işaret edebilir. "
                   f"<b>{resistance:.4f}</b> direncinin üzerine bir kapanış ise zayıflayan bir tepki denemesine kapı açabilir.")
    else:
        outlook = (f"Fiyat şu an <b>{support:.4f}</b> destek ile <b>{resistance:.4f}</b> direnç arasında sıkışmış durumda. "
                   f"Yön netleşmeden önce bu bandın kırılması izlenmesi gereken en önemli teknik sinyal olacaktır.")
 
    # ---- Geçmiş Performans (Sade Dil Yorumu için) ----
    total_return_pct = ((last_price - prices[0]) / prices[0]) * 100 if prices[0] != 0 else 0
    daily_changes = np.diff(prices)
    up_days = int(np.sum(daily_changes > 0))
    down_days = int(np.sum(daily_changes < 0))
    total_days = up_days + down_days
    up_ratio = (up_days / total_days * 100) if total_days > 0 else 0
 
    signal_count = sum([
        1 if trend == "Yükseliş Trendi" else (-1 if trend == "Düşüş Trendi" else 0),
        1 if (last_rsi is not None and 30 < last_rsi < 70 and trend == "Yükseliş Trendi") or (last_rsi is not None and last_rsi <= 30) else (-1 if (last_rsi is not None and last_rsi >= 70) else 0),
        1 if macd_durum.startswith("Boğa") else -1,
        1 if price_vs_vwap.startswith("VWAP Üstünde") else -1,
    ])
 
    if signal_count >= 2:
        genel_yon = "yukarı yönlü"
        genel_renk = "#22c55e"
        genel_ihtimal = "yükseliş eğiliminin sürme ihtimali, göstergelerin çoğunluğu aynı yönü işaret ettiği için şu an için düşüşe göre bir miktar daha kuvvetli görünüyor"
    elif signal_count <= -2:
        genel_yon = "aşağı yönlü"
        genel_renk = "#ef4444"
        genel_ihtimal = "düşüş eğiliminin sürme ihtimali, göstergelerin çoğunluğu aynı yönü işaret ettiği için şu an için yükselişe göre bir miktar daha kuvvetli görünüyor"
    else:
        genel_yon = "kararsız"
        genel_renk = "#facc15"
        genel_ihtimal = "göstergeler birbiriyle çelişiyor; bu da net bir yön çıkarmak yerine temkinli kalmayı gerektiriyor"
 
    genel_gorunum_html = f"""
    <b>8) Genel Görünüm (Sade Dilde)</b><br>
    <span style="color:#d4d4d8;">
    Son {period.upper()} periyotta {name}, toplamda
    <b style="color:{'#22c55e' if total_return_pct >= 0 else '#ef4444'}">%{total_return_pct:.1f}</b> değişim gösterdi
    ve incelenen günlerin <b>%{up_ratio:.0f}</b> kadarında fiyat bir önceki güne göre yükseldi.<br><br>
    Şu anki teknik tabloya (trend, RSI, MACD, VWAP) birlikte bakıldığında genel eğilim
    <b style="color:{genel_renk};">{genel_yon}</b> tarafa biraz daha ağır basıyor: {genel_ihtimal}.
    Ama bunu bir garanti olarak değil, "olasılık dengesi şu an bu yöne az da olsa eğik" şeklinde okumak gerekir —
    geçmiş fiyat hareketi gelecekteki yönü kesin olarak belirlemez, piyasa haberi veya beklenmedik bir gelişme bu tabloyu
    her an tersine çevirebilir.
    </span><br><br>
    """
 
    glossary_html = """
    <b>9) Terimler Ne Anlama Geliyor?</b><br>
    <span style="color:#a1a1aa; font-size:11px; line-height:1.5;">
    • <b>SMA / EMA (Hareketli Ortalama):</b> Son X günün ortalama fiyatı. Fiyat bu ortalamanın üzerindeyse genelde "güçlü", altındaysa "zayıf" kabul edilir.<br>
    • <b>RSI:</b> 0-100 arası değişen bir "hız göstergesi". 70 üzeri "çok hızlı yükseldi, biraz durabilir" (aşırı alım), 30 altı "çok hızlı düştü, tepki gelebilir" (aşırı satım) anlamına gelir.<br>
    • <b>MACD:</b> İki farklı hareketli ortalama arasındaki farkı izler; bu fark sinyal çizgisinin üzerindeyse alıcılar, altındaysa satıcılar baskın sayılır.<br>
    • <b>VWAP:</b> Hacimle ağırlıklandırılmış ortalama fiyat. Fiyat VWAP'ın üzerindeyse gün içi alıcılar, altındaysa satıcılar avantajlı sayılır.<br>
    • <b>Bollinger Bantları:</b> Fiyatın etrafındaki "normal dalgalanma" sınırları. Bantlar daralırsa sakinlik, genişlerse sert hareket anlamına gelir.<br>
    • <b>Destek / Direnç:</b> Fiyatın geçmişte zorlanıp geri döndüğü seviyeler. Destek "taban", direnç "tavan" gibi düşünülebilir.
    </span><br><br>
    """
 
    html = f"""
    <b>📊 {name} ({symbol}) — {period.upper()} Teknik Analiz Raporu</b><br>
    <span style="color:#71717a;">{len(prices)} veri noktası üzerinden hesaplanmıştır.</span><br><br>
 
    <b>1) Genel Trend</b><br>
    <span style="color:{trend_color}; font-weight:bold;">{trend}</span><br>
    <span style="color:#d4d4d8;">{trend_desc}</span><br><br>
 
    <b>2) Momentum (RSI 14)</b><br>
    <span style="color:{momentum_color}; font-weight:bold;">{momentum}</span><br>
    <span style="color:#d4d4d8;">{momentum_desc}</span><br><br>
 
    <b>3) Volatilite (Bollinger Bantları)</b><br>
    <span style="color:#38bdf8; font-weight:bold;">{volatility}</span><br>
    <span style="color:#d4d4d8;">{volatility_desc}</span><br><br>
    
    <b>4) MACD & VWAP Durumu</b><br>
    • MACD: <span style="color:#38bdf8;">{macd_durum}</span><br>
    • VWAP: <span style="color:#ec4899;">{price_vs_vwap}</span><br><br>
 
    <b>5) Destek / Direnç Seviyeleri</b><br>
    🟢 Destek: <b>{support:.4f}</b> &nbsp;&nbsp; 🔴 Direnç: <b>{resistance:.4f}</b><br>
    <span style="color:#d4d4d8;">Periyot Dip: {min_p:.4f} &nbsp;|&nbsp; Periyot Zirve: {max_p:.4f} &nbsp;|&nbsp; Son Fiyat: {last_price:.4f}</span><br><br>
 
    {"<b>6) Hacim Analizi</b><br><span style='color:#d4d4d8;'>" + volume_comment + "</span><br><br>" if volume_comment else ""}
 
    <b>7) Teknik Görünüm</b><br>
    <span style="color:#e4e4e7;">{outlook}</span><br><br>
 
    {genel_gorunum_html}
    {glossary_html}
 
    <span style="color:#52525b; font-size:10px;">
    ⚠️ Bu rapor yalnızca geçmiş fiyat/hacim verilerine dayalı otomatik bir teknik değerlendirmedir.
    Kesin bir gelecek tahmini içermez ve yatırım tavsiyesi niteliği taşımaz.
    </span>
    """
    return html
 
 
class IzlemeTabContent(QWidget):
    def __init__(self, symbol, name, current_price, change_str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
 
        self.symbol = symbol
        self.name = name
        self.current_price = current_price
        self.change_str = change_str
        self.current_period = "1y"
 
        # --- SOL: TRADINGVIEW TARZI SÜPER GRAFİK & PERİYOT BUTONLARI ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
 
        period_layout = QHBoxLayout()
        period_layout.setSpacing(4)
 
        self.btn_1d = self.create_period_btn("1G", "1d")
        self.btn_1wk = self.create_period_btn("1H", "1wk")
        self.btn_1mo = self.create_period_btn("1A", "1mo")
        self.btn_1y = self.create_period_btn("1Y", "1y")
        self.btn_max = self.create_period_btn("TÜMÜ", "max")
 
        self.btn_1y.setStyleSheet(self.get_period_btn_style(active=True))
 
        period_layout.addWidget(self.btn_1d)
        period_layout.addWidget(self.btn_1wk)
        period_layout.addWidget(self.btn_1mo)
        period_layout.addWidget(self.btn_1y)
        period_layout.addWidget(self.btn_max)
        period_layout.addStretch()
 
        self.plot_layout = pg.GraphicsLayoutWidget()
        self.plot_layout.setBackground('#050505')
 
        # Satır 0: Fiyat + SMA + Bollinger | Satır 1: Hacim | Satır 2: RSI | Satır 3: MACD
        self.plot1 = self.plot_layout.addPlot(row=0, col=0)
        self.plot1.showGrid(x=True, y=True, alpha=0.2)
        self.plot1.setMouseEnabled(x=True, y=True)
 
        self.plot_layout.nextRow()
        self.plot2 = self.plot_layout.addPlot(row=1, col=0)
        self.plot2.showGrid(x=True, y=True, alpha=0.2)
        self.plot2.setXLink(self.plot1)
        self.plot2.setMaximumHeight(90)
 
        self.plot_layout.nextRow()
        self.plot3 = self.plot_layout.addPlot(row=2, col=0)
        self.plot3.showGrid(x=True, y=True, alpha=0.2)
        self.plot3.setXLink(self.plot1)
        self.plot3.setYRange(0, 100)
        self.plot3.setMaximumHeight(90)
 
        self.plot_layout.nextRow()
        self.plot4 = self.plot_layout.addPlot(row=3, col=0)
        self.plot4.showGrid(x=True, y=True, alpha=0.2)
        self.plot4.setXLink(self.plot1)
        self.plot4.setMaximumHeight(70)
 
        self.macd_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#3f3f46', style=pg.QtCore.Qt.DashLine))
        self.plot4.addItem(self.macd_vLine)
        self.plot4.addLine(y=0, pen=pg.mkPen('#71717a', width=1, style=pg.QtCore.Qt.DotLine))
 
        self.plot_layout.ci.layout.setRowSpacing(0, 5)
        self.plot_layout.ci.layout.setRowStretchFactor(0, 4)
        self.plot_layout.ci.layout.setRowStretchFactor(1, 1)
        self.plot_layout.ci.layout.setRowStretchFactor(2, 1)
        self.plot_layout.ci.layout.setRowStretchFactor(3, 1)
 
        left_layout.addLayout(period_layout)
        left_layout.addWidget(self.plot_layout, stretch=1)
 
        self.x_data = []
        self.y_data = []
        self.dates_list = []
        self.rsi_data = np.array([])
        self.sma_short_data = np.array([])
        self.sma_long_data = np.array([])
        self.ema_short_data = np.array([])
        self.ema_long_data = np.array([])
        self.macd_data = np.array([])
        self.signal_data = np.array([])
        self.vwap_data = np.array([])
 
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#71717a', style=pg.QtCore.Qt.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#71717a', style=pg.QtCore.Qt.DashLine))
        self.plot1.addItem(self.vLine, ignoreBounds=True)
        self.plot1.addItem(self.hLine, ignoreBounds=True)
 
        self.rsi_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#3f3f46', style=pg.QtCore.Qt.DashLine))
        self.plot3.addItem(self.rsi_vLine, ignoreBounds=True)
        self.plot3.addLine(y=70, pen=pg.mkPen('#ef4444', width=1, style=pg.QtCore.Qt.DotLine))
        self.plot3.addLine(y=30, pen=pg.mkPen('#22c55e', width=1, style=pg.QtCore.Qt.DotLine))
 
        self.proxy = pg.SignalProxy(self.plot1.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
 
        # --- SAĞ: PROFESYONEL DETAY & ANLIK İMLEÇ BİLGİSİ ---
        right_panel = QWidget()
        right_panel.setFixedWidth(340)
        right_panel.setStyleSheet("background-color: #09090b; border-left: 1px solid #27272a;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)
 
        lbl_name = QLabel(f"<b>{name}</b> ({symbol})")
        lbl_name.setStyleSheet("color: #f8fafc; font-size: 15px;")
 
        change_color = "#22c55e" if "+" in str(change_str) else "#ef4444"
        lbl_price = QLabel(f"Fiyat: {current_price}")
        lbl_price.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: bold;")
        lbl_change = QLabel(f"Değişim: {change_str}")
        lbl_change.setStyleSheet(f"color: {change_color}; font-size: 13px; font-weight: bold;")
 
        self.lbl_cursor_info = QLabel("<b>İmleç Bilgisi:</b><br>Grafik üzerinde gezinin...")
        self.lbl_cursor_info.setStyleSheet("color: #e4e4e7; font-size: 11px; background-color: #18181b; padding: 8px; border-radius: 6px; border: 1px solid #27272a;")
 
        lbl_comment_title = QLabel("<b>Derinlemesine Teknik & Yapay Zeka Raporu</b>")
        lbl_comment_title.setStyleSheet("color: #a1a1aa; font-size: 12px; margin-top: 5px;")
 
        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #121214;
                color: #e4e4e7;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        self.text_browser.setHtml("<font color='#a1a1aa'>Veriler analiz ediliyor...</font>")
 
        right_layout.addWidget(lbl_name)
        right_layout.addWidget(lbl_price)
        right_layout.addWidget(lbl_change)
        right_layout.addWidget(self.lbl_cursor_info)
        right_layout.addWidget(lbl_comment_title)
        right_layout.addWidget(self.text_browser, stretch=1)
 
        layout.addWidget(left_container, stretch=4)
        layout.addWidget(right_panel, stretch=1)
 
        self.load_and_plot(symbol, self.current_period)
 
    def create_period_btn(self, text, period_key):
        btn = QPushButton(text)
        btn.setCursor(pg.QtCore.Qt.PointingHandCursor)
        btn.setStyleSheet(self.get_period_btn_style(active=False))
        btn.clicked.connect(lambda: self.change_period(period_key, btn))
        return btn
 
    def get_period_btn_style(self, active=False):
        if active:
            return """
                QPushButton {
                    background-color: #38bdf8;
                    color: #050505;
                    font-weight: bold;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                    border: none;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #18181b;
                    color: #a1a1aa;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                    border: 1px solid #27272a;
                }
                QPushButton:hover {
                    background-color: #27272a;
                    color: #f4f4f5;
                }
            """
 
    def change_period(self, period, clicked_btn):
        self.current_period = period
        for btn in [self.btn_1d, self.btn_1wk, self.btn_1mo, self.btn_1y, self.btn_max]:
            btn.setStyleSheet(self.get_period_btn_style(active=False))
        clicked_btn.setStyleSheet(self.get_period_btn_style(active=True))
        self.load_and_plot(self.symbol, self.current_period)
 
    def mouse_moved(self, evt):
        pos = evt[0]
        if self.plot1.sceneBoundingRect().contains(pos):
            mousePoint = self.plot1.vb.mapSceneToView(pos)
            index = int(round(mousePoint.x()))
 
            if 0 <= index < len(self.x_data):
                px = self.x_data[index]
                py = self.y_data[index]
                dt_obj = self.dates_list[index]
 
                if isinstance(dt_obj, datetime):
                    date_str = dt_obj.strftime('%Y-%m-%d %H:%M') if dt_obj.hour != 0 or dt_obj.minute != 0 else dt_obj.strftime('%Y-%m-%d')
                else:
                    date_str = str(dt_obj)
 
                self.vLine.setPos(px)
                self.hLine.setPos(py)
                self.rsi_vLine.setPos(px)
                self.macd_vLine.setPos(px)
 
                rsi_txt = ""
                if len(self.rsi_data) == len(self.x_data) and not np.isnan(self.rsi_data[index]):
                    rsi_txt = f"📉 RSI: <b>{self.rsi_data[index]:.1f}</b><br>"
 
                sma_txt = ""
                if len(self.sma_short_data) == len(self.x_data) and not np.isnan(self.sma_short_data[index]):
                    sma_txt = f"📏 SMA Kısa: <b>{self.sma_short_data[index]:.2f}</b><br>"
 
                sma_long_txt = ""
                if len(self.sma_long_data) == len(self.x_data) and not np.isnan(self.sma_long_data[index]):
                    sma_long_txt = f"📐 SMA Uzun: <b>{self.sma_long_data[index]:.2f}</b><br>"
 
                ema_txt = ""
                if len(self.ema_short_data) == len(self.x_data) and not np.isnan(self.ema_short_data[index]):
                    ema_txt += f"🟢 EMA Kısa: <b>{self.ema_short_data[index]:.2f}</b><br>"
                if len(self.ema_long_data) == len(self.x_data) and not np.isnan(self.ema_long_data[index]):
                    ema_txt += f"🟡 EMA Uzun: <b>{self.ema_long_data[index]:.2f}</b><br>"
 
                macd_txt = ""
                if len(self.macd_data) == len(self.x_data) and not np.isnan(self.macd_data[index]):
                    macd_txt += f"🔵 MACD: <b>{self.macd_data[index]:.4f}</b><br>"
                if len(self.signal_data) == len(self.x_data) and not np.isnan(self.signal_data[index]):
                    macd_txt += f"🟠 Sinyal: <b>{self.signal_data[index]:.4f}</b><br>"
 
                vwap_txt = ""
                if len(self.vwap_data) == len(self.x_data) and not np.isnan(self.vwap_data[index]):
                    vwap_txt = f"🩷 VWAP: <b>{self.vwap_data[index]:.2f}</b><br>"
 
                self.lbl_cursor_info.setText(
                    f"<b>İmleç Detayı:</b><br>"
                    f"📅 Tarih: <b>{date_str}</b><br>"
                    f"💰 Fiyat: <font color='#38bdf8'><b>{py:.2f}</b></font><br>"
                    f"{sma_txt}{sma_long_txt}{ema_txt}{vwap_txt}{macd_txt}{rsi_txt}"
                )
 
    def load_and_plot(self, symbol, period):
        try:
            self.plot1.clear()
            self.plot2.clear()
            self.plot3.clear()
            self.plot4.clear()
            
            self.plot1.addItem(self.vLine)
            self.plot1.addItem(self.hLine)
            self.plot3.addItem(self.rsi_vLine)
            self.plot3.addLine(y=70, pen=pg.mkPen('#ef4444', width=1, style=pg.QtCore.Qt.DotLine))
            self.plot3.addLine(y=30, pen=pg.mkPen('#22c55e', width=1, style=pg.QtCore.Qt.DotLine))
            
            self.plot4.addItem(self.macd_vLine)
            self.plot4.addLine(y=0, pen=pg.mkPen('#71717a', width=1, style=pg.QtCore.Qt.DotLine))
 
            prices = []
            volumes = []
            dates = []
            highs = []
            lows = []
            opens = []
 
            is_crypto = any(ext in symbol.upper() for ext in ["USDT", "BIDR", "BTC", "ETH", "BNB", "FDUSD", "JPY", "RUB"])
 
            if is_crypto:
                interval_map = {
                    "1d": ("5m", 288),
                    "1wk": ("30m", 336),
                    "1mo": ("2h", 360),
                    "1y": ("1d", 365),
                    "max": ("1d", 1000)
                }
                binance_interval, limit = interval_map.get(period, ("1d", 365))
 
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={binance_interval}&limit={limit}"
                response = requests.get(url, timeout=5)
 
                if response.status_code == 200:
                    raw_klines = response.json()
                    if raw_klines:
                        timestamps = [k[0] / 1000.0 for k in raw_klines]
                        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
                        opens = np.array([float(k[1]) for k in raw_klines])
                        highs = np.array([float(k[2]) for k in raw_klines])
                        lows = np.array([float(k[3]) for k in raw_klines])
                        prices = np.array([float(k[4]) for k in raw_klines])
                        volumes = np.array([float(k[5]) for k in raw_klines])
 
            else:
                yf_interval = "1d"
                if period == "1d":
                    yf_interval = "5m"
                elif period == "1wk":
                    yf_interval = "30m"
                elif period == "1mo":
                    yf_interval = "1h"
 
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=yf_interval, auto_adjust=False)
 
                if hist is not None and not hist.empty:
                    prices = hist["Close"].values
                    volumes = hist["Volume"].values if "Volume" in hist.columns else np.zeros(len(prices))
                    dates = hist.index.to_pydatetime()
                    opens = hist["Open"].values if "Open" in hist.columns else prices
                    highs = hist["High"].values if "High" in hist.columns else prices
                    lows = hist["Low"].values if "Low" in hist.columns else prices
 
            # --- GRAFİĞE AKTARMA ORTAK ALAN ---
            if len(prices) > 0:
                self.y_data = prices
                self.x_data = list(range(len(prices)))
                self.dates_list = dates
 
                # --- Göstergeler ---
                short_window = max(5, min(20, len(prices) // 8))
                long_window = max(short_window + 5, min(50, len(prices) // 3))
 
                sma_short = sma_full(prices, short_window)
                sma_long = sma_full(prices, long_window)
                bb_mid, bb_upper, bb_lower = bollinger_full(prices, window=min(20, max(5, len(prices) // 5)))
                rsi = rsi_full(prices, period=14)
 
                ema_short = ema_full(prices, 9)
                ema_long = ema_full(prices, 21)
                macd, signal_line, macd_hist = macd_full(prices)
                
                ref_highs = highs if len(highs) == len(prices) else prices
                ref_lows = lows if len(lows) == len(prices) else prices
                vwap = vwap_full(ref_highs, ref_lows, prices, volumes)
 
                self.sma_short_data = sma_short
                self.sma_long_data = sma_long
                self.rsi_data = rsi
                self.ema_short_data = ema_short
                self.ema_long_data = ema_long
                self.macd_data = macd
                self.signal_data = signal_line
                self.vwap_data = vwap
 
                # Fiyat + göstergeler
                self.plot1.plot(self.x_data, prices, pen=pg.mkPen(color='#38bdf8', width=1.8), name="Kapanış")
                self.plot1.plot(self.x_data, sma_short, pen=pg.mkPen(color='#facc15', width=1, style=pg.QtCore.Qt.DashLine), connect="finite", name=f"SMA {short_window}")
                self.plot1.plot(self.x_data, sma_long, pen=pg.mkPen(color='#c084fc', width=1, style=pg.QtCore.Qt.DashLine), connect="finite", name=f"SMA {long_window}")
 
                bb_upper_curve = self.plot1.plot(self.x_data, bb_upper, pen=pg.mkPen(color='#3f3f46', width=1), connect="finite")
                bb_lower_curve = self.plot1.plot(self.x_data, bb_lower, pen=pg.mkPen(color='#3f3f46', width=1), connect="finite")
                fill = pg.FillBetweenItem(bb_upper_curve, bb_lower_curve, brush=pg.mkBrush(56, 189, 248, 18))
                self.plot1.addItem(fill)
 
                # Hacim barları
                if len(volumes) > 0:
                    ref_opens = opens if len(opens) == len(prices) else prices
                    brushes = [
                        pg.mkBrush('#22c55e') if prices[i] >= ref_opens[i] else pg.mkBrush('#ef4444')
                        for i in range(len(prices))
                    ]
                    bargraph = pg.BarGraphItem(x=self.x_data, height=volumes, width=0.8, brushes=brushes)
                    self.plot2.addItem(bargraph)
 
                # RSI çizgisi
                self.plot3.plot(self.x_data, rsi, pen=pg.mkPen(color='#facc15', width=1.5), connect="finite")
                
                # Ana grafiğe (plot1) EMA ve VWAP ekleme
                self.plot1.plot(self.x_data, ema_short, pen=pg.mkPen(color='#34d399', width=1.2), connect="finite")
                self.plot1.plot(self.x_data, ema_long, pen=pg.mkPen(color='#fbbf24', width=1.2), connect="finite")
                self.plot1.plot(self.x_data, vwap, pen=pg.mkPen(color='#ec4899', width=1.2, style=pg.QtCore.Qt.DashLine), connect="finite")
 
                # MACD grafiğini (plot4) doldurma
                self.plot4.plot(self.x_data, macd, pen=pg.mkPen(color='#38bdf8', width=1.2), connect="finite")
                self.plot4.plot(self.x_data, signal_line, pen=pg.mkPen(color='#f97316', width=1.2), connect="finite")
                hist_brushes = [pg.mkBrush('#22c55e') if (val >= 0) else pg.mkBrush('#ef4444') for val in macd_hist]
                self.plot4.addItem(pg.BarGraphItem(x=self.x_data, height=macd_hist, width=0.7, brushes=hist_brushes))
 
                yorum_html = generate_technical_report(
                    symbol, self.name, period, prices, ref_highs, ref_lows, volumes,
                    sma_short, sma_long, bb_upper, bb_lower, rsi, ema_short, macd, signal_line, vwap
                )
                self.text_browser.setHtml(yorum_html)
            else:
                self.text_browser.setHtml(f"<font color='#ef4444'>Bu periyot için '{symbol}' varlığına ait yeterli veri bulunamadı.</font>")
 
        except Exception as e:
            print(f"Grafik yüklenirken hata oluştu ({symbol}): {e}")
            self.text_browser.setHtml(f"<font color='#ef4444'>Hata: {str(e)}</font>")
 
 
class IzlemeListesiManager:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
 
        self.state_file = "watch_state.json"
        self.restore_state()
 
    def add_or_focus_symbol(self, symbol, name, current_price, change_str, asset_type):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == symbol:
                self.tab_widget.setCurrentIndex(i)
                return
 
        new_tab = IzlemeTabContent(symbol, name, current_price, change_str)
        self.tab_widget.addTab(new_tab, symbol)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.save_state()
 
    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        if widget:
            widget.deleteLater()
        self.save_state()
 
    def remove_symbol_by_symbol(self, symbol):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == symbol:
                self.close_tab(i)
                break
 
    def save_state(self):
        tabs_data = []
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, "symbol"):
                tabs_data.append({
                    "symbol": widget.symbol,
                    "name": widget.name,
                    "current_price": widget.current_price,
                    "change_str": widget.change_str
                })
 
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(tabs_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Durum kaydedilemedi: {e}")
 
    def restore_state(self):
        if not os.path.exists(self.state_file):
            return
 
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                tabs_data = json.load(f)
 
            for item in tabs_data:
                symbol = item.get("symbol")
                name = item.get("name")
                price = item.get("current_price")
                change = item.get("change_str")
                if symbol and name:
                    self.add_or_focus_symbol(symbol, name, price, change, "")
        except Exception as e:
            print(f"Durum geri yüklenemedi: {e}")