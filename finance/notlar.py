import base64
from datetime import datetime
import sqlite3
 
from PySide6.QtCore import Qt, QBuffer, QIODevice
from PySide6.QtGui import QImage, QTextDocument
from PySide6.QtWidgets import (
    QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QFileDialog, QMessageBox,
    QLineEdit, QWidget
)
 
 
# ============================================================
# ORTAK YARDIMCI FONKSİYONLAR
# ============================================================
 
def _resmi_base64_html_yap(dosya_yolu, max_genislik=420):
    """Seçilen resmi ölçekleyip base64 olarak kodlar ve <img> etiketi HTML'i döndürür.
    Böylece resim ayrı bir dosyada değil, notun kendi içeriğinde (veritabanında) saklanır."""
    image = QImage(dosya_yolu)
    if image.isNull():
        return None
 
    if image.width() > max_genislik:
        image = image.scaledToWidth(max_genislik, Qt.TransformationMode.SmoothTransformation)
 
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    base64_veri = base64.b64encode(bytes(buffer.data())).decode("utf-8")
    buffer.close()
 
    return f'<br><img src="data:image/png;base64,{base64_veri}"><br>'
 
 
def _duz_metin_cikar(icerik_html):
    doc = QTextDocument()
    doc.setHtml(icerik_html)
    return doc.toPlainText().strip().replace("\n", " ")
 
 
def _onizleme_metni_olustur(icerik_html, uzunluk=90):
    """Not listesinde gösterilecek kısa, sade metin önizlemesini HTML içeriğinden çıkarır."""
    duz_metin = _duz_metin_cikar(icerik_html)
 
    if not duz_metin:
        if "<img" in icerik_html:
            return "🖼️ (Resimli not)"
        return "(Boş not)"
 
    if len(duz_metin) > uzunluk:
        return duz_metin[:uzunluk].rstrip() + "…"
    return duz_metin
 
 
# ============================================================
# NOT DÜZENLEME PENCERESİ
# ============================================================
 
class NotDuzenlePenceresi(QDialog):
    def __init__(self, not_html, tarih_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Not Detayı ve Düzenleme")
        self.resize(650, 560)
        self.setMinimumSize(480, 380)
 
        # Kullanıcı "Notu Sil" butonuna bastıysa True olur, çağıran kod buna bakar
        self.silinsin_mi = False
 
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #b388ff;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
            }
            QTextEdit:focus {
                border: 2px solid #d1b3ff;
            }
            QLabel {
                color: #a1a1aa;
                font-size: 12px;
            }
            QPushButton {
                background-color: #b388ff;
                color: #1e1e2f;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #c9a8f0;
            }
            QPushButton#resimBtn {
                background-color: #2a2635;
                color: #d1b3ff;
                border: 1px solid #b388ff;
            }
            QPushButton#resimBtn:hover {
                background-color: #3a3245;
            }
            QPushButton#silBtn {
                background-color: #2a1a1a;
                color: #ff8a8a;
                border: 1px solid #b34747;
            }
            QPushButton#silBtn:hover {
                background-color: #3a2222;
            }
        """)
 
        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
 
        baslik = QLabel("<b style='color:#e4d9ff; font-size:15px;'>📝 Not Detayı</b>")
        layout.addWidget(baslik)
 
        self.textEdit_detay = QTextEdit()
        self.textEdit_detay.setAcceptRichText(True)
        self.textEdit_detay.setHtml(not_html)
        layout.addWidget(self.textEdit_detay, stretch=1)
 
        self.label_tarih = QLabel(f"Oluşturulma Tarihi: {tarih_str}")
        layout.addWidget(self.label_tarih)
 
        btn_layout = QHBoxLayout()
 
        self.btn_sil = QPushButton(" Notu Sil")
        self.btn_sil.setObjectName("silBtn")
        self.btn_sil.clicked.connect(self._notu_sil)
        btn_layout.addWidget(self.btn_sil)
 
        self.btn_resim = QPushButton(" Resim Ekle")
        self.btn_resim.setObjectName("resimBtn")
        self.btn_resim.clicked.connect(self._resim_ekle)
        btn_layout.addWidget(self.btn_resim)
 
        btn_layout.addStretch()
 
        self.btn_kaydet = QPushButton("Değişiklikleri Kaydet")
        self.btn_kaydet.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_kaydet)
 
        layout.addLayout(btn_layout)
        self.setLayout(layout)
 
    def _resim_ekle(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not dosya_yolu:
            return
 
        html_img = _resmi_base64_html_yap(dosya_yolu)
        if html_img is None:
            QMessageBox.warning(self, "Hata", "Resim yüklenemedi, dosya bozuk olabilir.")
            return
 
        self.textEdit_detay.insertHtml(html_img)
 
    def _notu_sil(self):
        cevap = QMessageBox.question(
            self,
            "Notu Sil",
            "Bu notu kalıcı olarak silmek istediğinize emin misiniz?\nBu işlem geri alınamaz.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if cevap == QMessageBox.StandardButton.Yes:
            self.silinsin_mi = True
            self.accept()
 
    def yeni_metni_al(self):
        """Notun tam HTML içeriğini (resimler dahil) döndürür."""
        return self.textEdit_detay.toHtml()
 
 
# ============================================================
# NOTLAR YÖNETİCİSİ
# ============================================================
 
class NotlarYoneticisi:
    def __init__(self, main_window, username=None):
        self.main_window = main_window
 
        # Her kullanıcının notları kendi veritabanı dosyasında saklanır,
        # böylece çıkış yapıp tekrar giriş yaptığında notlar kaybolmaz.
        self.db_path = f"notlar_{username}.db" if username else "notlar.db"
 
        # Tüm notların bellekteki kopyası - arama/filtreleme burada yapılır,
        # her tuşa basışta veritabanına gidilmez.
        self._tum_notlar = []
 
        self.veritabani_baglantisi_kur()
        self.stili_uygula()
        self._resim_butonunu_ekle()
        self._arama_kutusunu_ekle()
        self.baglantilari_kur()
        self.notlari_yukle()
 
    def veritabani_baglantisi_kur(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                icerik TEXT,
                tarih TEXT
            )
        """)
        self.conn.commit()
 
    def stili_uygula(self):
        # Liste satırları artık daha kompakt: daha küçük yazı ve daha ince dolgu,
        # böylece aynı ekranda çok daha fazla not gösterilebiliyor.
        tablo_stili = """
            QTableWidget {
                background-color: #121212;
                color: #ffffff;
                gridline-color: transparent;
                border: 2px solid #b388ff;
                border-radius: 12px;
                padding: 4px;
            }
            QTableWidget::item {
                background-color: #121212;
                color: #e4e4e7;
                padding: 8px 12px;
                margin: 3px;
                border-radius: 6px;
                border: 1px solid #121212;
                font-size: 16px;
            }
            QTableWidget::item:selected {
                background-color: #b388ff;
                color: #1e1e2f;
                border: 1px solid #b388ff;
            }
        """
        self.main_window.tableWidget.setStyleSheet(tablo_stili)
        self.main_window.tableWidget.setColumnCount(1)
        self.main_window.tableWidget.horizontalHeader().setVisible(False)
        self.main_window.tableWidget.verticalHeader().setVisible(False)
        self.main_window.tableWidget.horizontalHeader().setStretchLastSection(True)
 
    def _resim_butonunu_ekle(self):
        """Ana ekrandaki 'Not Ekle' butonunun yanına bir 'Resim Ekle' butonu ekler.
        Arayüz dosyasını (finance_ui.py) değiştirmeden, mevcut layout'a çalışma
        zamanında ekleme yapıyoruz."""
        buton = self.main_window.pushButton_2
        layout = buton.parentWidget().layout() if buton.parentWidget() else None
 
        if layout is None:
            self.btn_resim_ekle = None
            return
 
        idx = layout.indexOf(buton)
        layout.removeWidget(buton)
 
        satir_layout = QHBoxLayout()
        self.btn_resim_ekle = QPushButton(" Resim Ekle")
        self.btn_resim_ekle.setStyleSheet("""
            QPushButton {
                background-color: #2a2635;
                color: #d1b3ff;
                border: 1px solid #b388ff;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3245;
            }
        """)
        self.btn_resim_ekle.clicked.connect(self._ana_ekrana_resim_ekle)
 
        satir_layout.addWidget(self.btn_resim_ekle)
        satir_layout.addWidget(buton)
 
        kapsayici = QWidget()
        kapsayici.setLayout(satir_layout)
        layout.insertWidget(idx, kapsayici)
 
    def _ana_ekrana_resim_ekle(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self.main_window, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not dosya_yolu:
            return
 
        html_img = _resmi_base64_html_yap(dosya_yolu)
        if html_img is None:
            QMessageBox.warning(self.main_window, "Hata", "Resim yüklenemedi, dosya bozuk olabilir.")
            return
 
        self.main_window.textEdit.insertHtml(html_img)
 
    def _arama_kutusunu_ekle(self):
        """Not listesinin (tableWidget) hemen üstüne bir arama kutusu ekler."""
        tablo = self.main_window.tableWidget
        layout = tablo.parentWidget().layout() if tablo.parentWidget() else None
 
        if layout is None:
            self.arama_kutusu = None
            return
 
        idx = layout.indexOf(tablo)
 
        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.setPlaceholderText(" Notlarda ara...")
        self.arama_kutusu.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #b388ff;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #d1b3ff;
            }
        """)
        self.arama_kutusu.textChanged.connect(self._filtrele)
 
        layout.insertWidget(idx, self.arama_kutusu)
 
    def baglantilari_kur(self):
        self.main_window.tableWidget.itemClicked.connect(self.not_penceresini_ac)
        self.main_window.pushButton_2.clicked.connect(self.yeni_not_ekle)
 
    def notlari_yukle(self):
        """Veritabanından tüm notları okuyup belleğe alır ve listeyi (mevcut arama
        metnine göre filtrelenmiş halde) yeniden çizer."""
        self.cursor.execute("SELECT id, icerik, tarih FROM notlar ORDER BY id DESC")
        kayitlar = self.cursor.fetchall()
 
        self._tum_notlar = [
            {
                "id": kayit_id,
                "icerik": icerik_html,
                "tarih": tarih,
                "duz_metin": _duz_metin_cikar(icerik_html).lower(),
                "onizleme": _onizleme_metni_olustur(icerik_html),
            }
            for kayit_id, icerik_html, tarih in kayitlar
        ]
 
        self._filtrele(self.arama_kutusu.text() if self.arama_kutusu else "")
 
    def _filtrele(self, arama_metni):
        arama_metni = (arama_metni or "").strip().lower()
 
        if arama_metni:
            gosterilecekler = [n for n in self._tum_notlar if arama_metni in n["duz_metin"]]
        else:
            gosterilecekler = self._tum_notlar
 
        table = self.main_window.tableWidget
        table.setRowCount(0)
 
        for not_verisi in gosterilecekler:
            current_row = table.rowCount()
            table.insertRow(current_row)
 
            item = QTableWidgetItem(not_verisi["onizleme"])
            # Tam HTML içeriği (resimler dahil) veride saklanıyor, düzenleme
            # penceresi açılırken buradan okunuyor.
            item.setData(Qt.ItemDataRole.UserRole, (not_verisi["id"], not_verisi["tarih"], not_verisi["icerik"]))
            table.setItem(current_row, 0, item)
 
            # Kompakt liste - satırlar artık çok daha az yer kaplıyor
            table.setRowHeight(current_row, 34)
 
    def yeni_not_ekle(self):
        icerik_html = self.main_window.textEdit.toHtml()
        duz_metin = self.main_window.textEdit.toPlainText().strip()
 
        # Hem yazı hem resim boşsa kaydetme
        if not duz_metin and "<img" not in icerik_html:
            return
 
        tarih_str = datetime.now().strftime("%d.%m.%Y - %H:%M")
 
        self.cursor.execute("INSERT INTO notlar (icerik, tarih) VALUES (?, ?)", (icerik_html, tarih_str))
        self.conn.commit()
 
        self.notlari_yukle()
        self.main_window.textEdit.clear()
 
    def not_penceresini_ac(self, item):
        if not item:
            return
 
        kayit_id, tarih_str, icerik_html = item.data(Qt.ItemDataRole.UserRole)
 
        pencere = NotDuzenlePenceresi(icerik_html, tarih_str, self.main_window)
 
        if pencere.exec() == QDialog.DialogCode.Accepted:
            if pencere.silinsin_mi:
                self.cursor.execute("DELETE FROM notlar WHERE id = ?", (kayit_id,))
                self.conn.commit()
            else:
                yeni_icerik = pencere.yeni_metni_al()
                self.cursor.execute("UPDATE notlar SET icerik = ? WHERE id = ?", (yeni_icerik, kayit_id))
                self.conn.commit()
 
            self.notlari_yukle()
 