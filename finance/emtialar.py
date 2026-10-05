import yfinance as yf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from kripto import KriptoDetayPenceresi  # Ortak detay penceresi

class EmtialarTab:
    def __init__(self, main_window):
        self.ui = main_window
        
        # Genişletilmiş Emtia Listesi
        self.emtia_listesi = [
            # Değerli Madenler
            {"symbol": "GC=F", "name": "Altın (Gold)", "kategori": "Değerli Madenler"},
            {"symbol": "SI=F", "name": "Gümüş (Silver)", "kategori": "Değerli Madenler"},
            {"symbol": "PL=F", "name": "Platin (Platinum)", "kategori": "Değerli Madenler"},
            {"symbol": "PA=F", "name": "Paladyum (Palladium)", "kategori": "Değerli Madenler"},
            {"symbol": "HG=F", "name": "Bakır (Copper)", "kategori": "Değerli Madenler"},
            
            # Enerji
            {"symbol": "CL=F", "name": "Ham Petrol WTI (Crude Oil)", "kategori": "Enerji"},
            {"symbol": "BZ=F", "name": "Brent Petrol (Brent Oil)", "kategori": "Enerji"},
            {"symbol": "NG=F", "name": "Doğal Gaz (Natural Gas)", "kategori": "Enerji"},
            {"symbol": "HO=F", "name": "Isıtma Yakıtı (Heating Oil)", "kategori": "Enerji"},
            {"symbol": "RB=F", "name": "Benzin (RBOB Gasoline)", "kategori": "Enerji"},
            
            # Tarım & Gıda
            {"symbol": "ZC=F", "name": "Mısır (Corn)", "kategori": "Tarım"},
            {"symbol": "ZS=F", "name": "Soya Fasulyesi (Soybeans)", "kategori": "Tarım"},
            {"symbol": "ZW=F", "name": "Buğday (Wheat)", "kategori": "Tarım"},
            {"symbol": "SB=F", "name": "Şeker (Sugar)", "kategori": "Tarım"},
            {"symbol": "KC=F", "name": "Kahve (Coffee)", "kategori": "Tarım"},
            {"symbol": "CT=F", "name": "Pamuk (Cotton)", "kategori": "Tarım"},
            {"symbol": "CC=F", "name": "Kakao (Cocoa)", "kategori": "Tarım"},
            {"symbol": "OJ=F", "name": "Portakal Suyu (Orange Juice)", "kategori": "Tarım"},
            
            # Sanayi Metalleri
            {"symbol": "ALI=F", "name": "Alüminyum (Aluminum)", "kategori": "Sanayi Metalleri"},
            {"symbol": "LE=F", "name": "Canlı Sığır (Live Cattle)", "kategori": "Sanayi Metalleri"},
            {"symbol": "HE=F", "name": "Yağsız Domuz Eti (Lean Hogs)", "kategori": "Sanayi Metalleri"}
        ]
        
        self.init_ui()

    def init_ui(self):
        # ComboBox ayarları
        self.ui.comboBox_13.clear()
        self.ui.comboBox_13.addItems(["Tüm Emtialar", "Değerli Madenler", "Tarım", "Enerji", "Sanayi Metalleri"])
        
        # Tablo başlıkları
        self.ui.tableWidget_8.setColumnCount(4)
        self.ui.tableWidget_8.setHorizontalHeaderLabels(["Emtia Adı", "Sembol", "Fiyat", "Değişim (%)"])
        self.ui.tableWidget_8.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_8.verticalHeader().setVisible(False)
        self.ui.tableWidget_8.setShowGrid(False)
        
        # Sinyaller / Bağlantılar
        self.ui.comboBox_13.currentIndexChanged.connect(self.filtrele_ve_yukle)
        self.ui.lineEdit_6.textChanged.connect(self.filtrele_ve_yukle)
        self.ui.tableWidget_8.itemDoubleClicked.connect(self.detay_grafik_ac)
        
        # İlk verileri yükle
        self.filtrele_ve_yukle()

    def filtrele_ve_yukle(self):
        secilen_kategori = self.ui.comboBox_13.currentText()
        arama_metni = self.ui.lineEdit_6.text().lower()
        
        self.ui.tableWidget_8.setRowCount(0)
        
        filtrelenmis = []
        for item in self.emtia_listesi:
            kategori_uyuyor = (secilen_kategori == "Tüm Emtialar" or item["kategori"] == secilen_kategori)
            arama_uyuyor = (arama_metni in item["name"].lower() or arama_metni in item["symbol"].lower())
            
            if kategori_uyuyor and arama_uyuyor:
                filtrelenmis.append(item)
                
        for row_idx, item in enumerate(filtrelenmis):
            self.ui.tableWidget_8.insertRow(row_idx)
            
            name_item = QTableWidgetItem(item["name"])
            symbol_item = QTableWidgetItem(item["symbol"])
            price_item = QTableWidgetItem("Yükleniyor...")
            change_item = QTableWidgetItem("...")
            
            # Hücreleri salt okunur yap
            for col_item in (name_item, symbol_item, price_item, change_item):
                col_item.setFlags(col_item.flags() ^ Qt.ItemIsEditable)
                
            self.ui.tableWidget_8.setItem(row_idx, 0, name_item)
            self.ui.tableWidget_8.setItem(row_idx, 1, symbol_item)
            self.ui.tableWidget_8.setItem(row_idx, 2, price_item)
            self.ui.tableWidget_8.setItem(row_idx, 3, change_item)
            
            # Try-Except Güvenlik Koruması ile Veri Çekme
            try:
                ticker = yf.Ticker(item["symbol"])
                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 1:
                    current_price = hist['Close'].iloc[-1]
                    price_item.setText(f"{current_price:.2f}")
                    
                    if len(hist) >= 2:
                        prev_price = hist['Close'].iloc[-2]
                        change = ((current_price - prev_price) / prev_price) * 100
                        change_item.setText(f"%{change:+.2f}")
                        if change > 0:
                            change_item.setForeground(Qt.green)
                        elif change < 0:
                            change_item.setForeground(Qt.red)
                else:
                    price_item.setText("Veri Yok")
            except Exception as e:
                price_item.setText("Hata")
                print(f"Emtia veri çekme hatası ({item['symbol']}): {e}")

    def detay_grafik_ac(self, table_item):
        """Tablodaki emtiaya çift tıklandığında ortak grafik detay penceresini açar."""
        row = table_item.row()
        symbol_item = self.ui.tableWidget_8.item(row, 1)
        price_item = self.ui.tableWidget_8.item(row, 2)
        change_item = self.ui.tableWidget_8.item(row, 3)

        if symbol_item:
            symbol = symbol_item.text()
            price = price_item.text() if price_item else "0"
            change = change_item.text() if change_item else "0"

            detay_pencere = KriptoDetayPenceresi(symbol, price, change, self.ui, parent=self.ui)
            detay_pencere.exec()