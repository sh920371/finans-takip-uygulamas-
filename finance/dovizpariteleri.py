import yfinance as yf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from kripto import KriptoDetayPenceresi  # Ortak grafik/detay penceresi

class DovizPariteleriTab:
    def __init__(self, main_window):
        self.ui = main_window
        
        # Kapsamlı Döviz Pariteleri Listesi
        self.doviz_listesi = [
            # Dünya Majörler (Major Currencies)
            {"symbol": "EURUSD=X", "name": "EUR/USD", "kategori": "Dünya Majörler", "base": "EUR"},
            {"symbol": "GBPUSD=X", "name": "GBP/USD", "kategori": "Dünya Majörler", "base": "GBP"},
            {"symbol": "USDJPY=X", "name": "USD/JPY", "kategori": "Dünya Majörler", "base": "USD"},
            {"symbol": "AUDUSD=X", "name": "AUD/USD", "kategori": "Dünya Majörler", "base": "AUD"},
            {"symbol": "USDCAD=X", "name": "USD/CAD", "kategori": "Dünya Majörler", "base": "USD"},
            {"symbol": "USDCHF=X", "name": "USD/CHF", "kategori": "Dünya Majörler", "base": "USD"},
            {"symbol": "NZDUSD=X", "name": "NZD/USD", "kategori": "Dünya Majörler", "base": "NZD"},
            
            # Gelişmekte Olan Piyasalar (Emerging Markets)
            {"symbol": "USDTRY=X", "name": "USD/TRY", "kategori": "Gelişmekte Olan Piyasalar", "base": "USD"},
            {"symbol": "EURTRY=X", "name": "EUR/TRY", "kategori": "Gelişmekte Olan Piyasalar", "base": "EUR"},
            {"symbol": "USDMXN=X", "name": "USD/MXN", "kategori": "Gelişmekte Olan Piyasalar", "base": "USD"},
            {"symbol": "USDZAR=X", "name": "USD/ZAR", "kategori": "Gelişmekte Olan Piyasalar", "base": "USD"},
            {"symbol": "USDBRL=X", "name": "USD/BRL", "kategori": "Gelişmekte Olan Piyasalar", "base": "USD"},
            {"symbol": "USDINR=X", "name": "USD/INR", "kategori": "Gelişmekte Olan Piyasalar", "base": "USD"},
            
            # Orta Doğu (Middle East)
            {"symbol": "USDUAD=X", "name": "USD/AED", "kategori": "Orta Doğu", "base": "USD"},
            {"symbol": "USDSAR=X", "name": "USD/SAR", "kategori": "Orta Doğu", "base": "USD"},
            {"symbol": "USDQAR=X", "name": "USD/QAR", "kategori": "Orta Doğu", "base": "USD"},
            {"symbol": "USDILS=X", "name": "USD/ILS", "kategori": "Orta Doğu", "base": "USD"},
            
            # Asya Kurları (Asian Currencies)
            {"symbol": "USDCNH=X", "name": "USD/CNH", "kategori": "Asya Kurları", "base": "USD"},
            {"symbol": "USDKRW=X", "name": "USD/KRW", "kategori": "Asya Kurları", "base": "USD"},
            {"symbol": "USDSGD=X", "name": "USD/SGD", "kategori": "Asya Kurları", "base": "USD"},
            {"symbol": "USDHKD=X", "name": "USD/HKD", "kategori": "Asya Kurları", "base": "USD"},
            {"symbol": "USDTHB=X", "name": "USD/THB", "kategori": "Asya Kurları", "base": "USD"}
        ]
        
        self.init_ui()

    def init_ui(self):
        # 1. comboBox_14: Baz Birimi Seçiniz
        self.ui.comboBox_14.clear()
        self.ui.comboBox_14.addItems(["Tüm Bazlar", "USD", "EUR", "GBP", "AUD", "NZD"])
        
        # 2. comboBox_15: Tüm Dünya Majörler, Gelişmekte Olan, Orta Doğu, Asya
        self.ui.comboBox_15.clear()
        self.ui.comboBox_15.addItems([
            "Tüm Kategoriler", 
            "Dünya Majörler", 
            "Gelişmekte Olan Piyasalar", 
            "Orta Doğu", 
            "Asya Kurları"
        ])
        
        # 3. comboBox_16: Düşen, Yükselen, Tümü
        self.ui.comboBox_16.clear()
        self.ui.comboBox_16.addItems(["Tümü", "Yükselenler", "Düşenler"])
        
        # SpinBox (Min / Max Değişim Aralığı) Varsayılan Sınırları
        self.ui.doubleSpinBox_9.setRange(-100.0, 100.0)
        self.ui.doubleSpinBox_9.setValue(-100.0)
        self.ui.doubleSpinBox_10.setRange(-100.0, 100.0)
        self.ui.doubleSpinBox_10.setValue(100.0)
        
        # Tablo Yapılandırması
        self.ui.tableWidget_9.setColumnCount(4) # Tablo numarasını kendi arayüzüne göre güncelleyebilirsin (Örn: tableWidget_9)
        self.ui.tableWidget_9.setHorizontalHeaderLabels(["Parite", "Sembol", "Fiyat", "Değişim (%)"])
        self.ui.tableWidget_9.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_9.verticalHeader().setVisible(False)
        self.ui.tableWidget_9.setShowGrid(False)
        
        # Sinyaller / Bağlantılar
        self.ui.comboBox_14.currentIndexChanged.connect(self.doviz_filtrele_ve_yukle)
        self.ui.comboBox_15.currentIndexChanged.connect(self.doviz_filtrele_ve_yukle)
        self.ui.comboBox_16.currentIndexChanged.connect(self.doviz_filtrele_ve_yukle)
        self.ui.doubleSpinBox_9.valueChanged.connect(self.doviz_filtrele_ve_yukle)
        self.ui.doubleSpinBox_10.valueChanged.connect(self.doviz_filtrele_ve_yukle)
        self.ui.tableWidget_9.itemDoubleClicked.connect(self.detay_grafik_ac)
        
        # İlk Yükleme
        self.doviz_filtrele_ve_yukle()

    def doviz_filtrele_ve_yukle(self):
        secilen_baz = self.ui.comboBox_14.currentText()
        secilen_kategori = self.ui.comboBox_15.currentText()
        secilen_durum = self.ui.comboBox_16.currentText()
        min_degisim = self.ui.doubleSpinBox_9.value()
        max_degisim = self.ui.doubleSpinBox_10.value()
        
        self.ui.tableWidget_9.setRowCount(0)
        
        # Önce verileri güvenli şekilde çekip önbelleğe alalım veya filtreleyelim
        for row_idx, item in enumerate(self.doviz_listesi):
            # Filtre 1: Baz Birim
            if secilen_baz != "Tüm Bazlar" and item["base"] != secilen_baz:
                continue
            # Filtre 2: Kategori
            if secilen_kategori != "Tüm Kategoriler" and item["kategori"] != secilen_kategori:
                continue
                
            self.ui.tableWidget_9.insertRow(row_idx)
            
            name_item = QTableWidgetItem(item["name"])
            symbol_item = QTableWidgetItem(item["symbol"])
            price_item = QTableWidgetItem("Yükleniyor...")
            change_item = QTableWidgetItem("...")
            
            for col_item in (name_item, symbol_item, price_item, change_item):
                col_item.setFlags(col_item.flags() ^ Qt.ItemIsEditable)
                
            self.ui.tableWidget_9.setItem(row_idx, 0, name_item)
            self.ui.tableWidget_9.setItem(row_idx, 1, symbol_item)
            self.ui.tableWidget_9.setItem(row_idx, 2, price_item)
            self.ui.tableWidget_9.setItem(row_idx, 3, change_item)
            
            # Try-Except Güvenlik Koruması ile Veri Çekme
            try:
                ticker = yf.Ticker(item["symbol"])
                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 1:
                    current_price = hist['Close'].iloc[-1]
                    price_item.setText(f"{current_price:.4f}")
                    
                    if len(hist) >= 2:
                        prev_price = hist['Close'].iloc[-2]
                        change = ((current_price - prev_price) / prev_price) * 100
                        change_item.setText(f"%{change:+.2f}")
                        
                        # Durum ve Aralık Filtreleri Kontrolü
                        if secilen_durum == "Yükselenler" and change <= 0:
                            self.ui.tableWidget_9.setRowHidden(row_idx, True)
                        elif secilen_durum == "Düşenler" and change >= 0:
                            self.ui.tableWidget_9.setRowHidden(row_idx, True)
                        elif not (min_degisim <= change <= max_degisim):
                            self.ui.tableWidget_9.setRowHidden(row_idx, True)
                            
                        if change > 0:
                            change_item.setForeground(Qt.green)
                        elif change < 0:
                            change_item.setForeground(Qt.red)
                else:
                    price_item.setText("Veri Yok")
            except Exception as e:
                price_item.setText("Hata")
                print(f"Döviz veri çekme hatası ({item['symbol']}): {e}")

    def detay_grafik_ac(self, table_item):
        """Pariteye çift tıklandığında ortak grafik detay penceresini açar."""
        row = table_item.row()
        symbol_item = self.ui.tableWidget_9.item(row, 1)
        price_item = self.ui.tableWidget_9.item(row, 2)
        change_item = self.ui.tableWidget_9.item(row, 3)

        if symbol_item:
            symbol = symbol_item.text()
            price = price_item.text() if price_item else "0"
            change = change_item.text() if change_item else "0"

            detay_pencere = KriptoDetayPenceresi(symbol, price, change, self.ui, parent=self.ui)
            detay_pencere.exec()