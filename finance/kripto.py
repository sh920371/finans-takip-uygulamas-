import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QPushButton


try:
    from izlemelist import IzlemeTabContent
except ImportError:
    IzlemeTabContent = None

class BinanceWorker(QThread):
    data_ready = Signal(list)

    def run(self):
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.data_ready.emit(response.json())
        except Exception as e:
            print(f"Binance veri çekme hatası: {e}")
            self.data_ready.emit([])

class KriptoDetayPenceresi(QDialog):
    """Kripto detaylarını ve küresel borsalardaki gibi yıldız butonunu barındıran pencere."""
    def __init__(self, symbol, price, change, main_window, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.price = price
        self.change = change
        self.win = main_window

        self.setWindowTitle(f"{symbol} - Detaylı Grafik ve Analiz")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #09090b; color: #f8fafc;")

        layout = QVBoxLayout(self)

        # Üst Bar & Yıldız Butonu
        top_bar = QHBoxLayout()
        self.yildiz_btn = QPushButton("☆ İzleme Listesine Ekle")
        self.yildiz_btn.setStyleSheet("""
            QPushButton {
                background-color: #18181b;
                color: gold;
                border: 1px solid #27272a;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27272a;
            }
        """)
        self.yildiz_btn.clicked.connect(self.yildiz_tiklandi)
        top_bar.addWidget(self.yildiz_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Grafik / İzleme Bileşeni (izlemelist.py içerisindeki yapı)
        if IzlemeTabContent:
            self.grafik_widget = IzlemeTabContent(
                symbol=symbol, 
                name=symbol, 
                current_price=price, 
                change_str=change
            )
            layout.addWidget(self.grafik_widget)

    def yildiz_tiklandi(self):
        """Detay penceresindeki yıldıza basıldığında ikinci tabdeki izleme listesine ekler/çıkarır."""
        if "☆" in self.yildiz_btn.text():
            self.yildiz_btn.setText("★ İzleme Listesinde")
            if hasattr(self.win, "izleme_listesi_yoneticisi") and self.win.izleme_listesi_yoneticisi:
                self.win.izleme_listesi_yoneticisi.add_or_focus_symbol(
                    symbol=self.symbol,
                    name=self.symbol,
                    current_price=self.price,
                    change_str=self.change,
                    asset_type="CRYPTO"
                )
        else:
            self.yildiz_btn.setText("☆ İzleme Listesine Ekle")
            if hasattr(self.win, "izleme_listesi_yoneticisi") and self.win.izleme_listesi_yoneticisi:
                self.win.izleme_listesi_yoneticisi.remove_symbol_by_symbol(self.symbol)


class KriptoManager:
    def __init__(self, main_window):
        self.win = main_window
        self.raw_data = []

        self.table = self.win.tableWidget_7
        self.parite_combo = self.win.comboBox_10
        self.kategori_combo = self.win.comboBox_11
        self.yon_combo = self.win.comboBox_12
        self.min_spin = self.win.doubleSpinBox_7
        self.max_spin = self.win.doubleSpinBox_8
        self.search_input = self.win.lineEdit_4

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sembol", "Fiyat", "24s Değişim", "Hacim (USDT)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.comboboxlari_doldur()

        # Sinyaller
        self.parite_combo.currentIndexChanged.connect(self.filtrele_ve_goster)
        self.kategori_combo.currentIndexChanged.connect(self.filtrele_ve_goster)
        self.yon_combo.currentIndexChanged.connect(self.filtrele_ve_goster)
        self.min_spin.valueChanged.connect(self.filtrele_ve_goster)
        self.max_spin.valueChanged.connect(self.filtrele_ve_goster)
        self.search_input.textChanged.connect(self.filtrele_ve_goster)
        
        self.table.itemClicked.connect(self.satir_tiklandi)
        self.kategori_sozlugu = {
            "LAYER 1": ["BTC", "ETH", "SOL", "AVAX", "ADA", "BNB", "NEAR", "APT", "SUI", "FTM"],
            "DEFI": ["UNI", "AAVE", "MKR", "CRV", "SUSHI", "INJ", "CAKE"],
            "AI": ["FET", "AGIX", "RNDR", "OCEAN", "AI"],
            "MEME": ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF"]
        }

    def comboboxlari_doldur(self):
        self.parite_combo.clear()
        self.parite_combo.addItems(["TÜMÜ", "USDT", "BTC", "ETH", "BNB"])

        self.kategori_combo.clear()
        self.kategori_combo.addItems(["Tümü", "Layer 1", "DeFi", "AI", "Meme"])

        if self.yon_combo.count() == 0:
            self.yon_combo.addItems(["Tümü", "Yükselenler", "Düşenler"])

    def verileri_cek(self):
        self.worker = BinanceWorker()
        self.worker.data_ready.connect(self.veri_geldi_callback)
        self.worker.start()

    def veri_geldi_callback(self, data):
        self.raw_data = data
        self.filtrele_ve_goster()

    def filtrele_ve_goster(self):
        if not self.raw_data:
            return

        parite = self.parite_combo.currentText().strip().upper()
        secilen_kategori = self.kategori_combo.currentText().strip().upper()
        yon = self.yon_combo.currentText().strip().upper()
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        search_text = self.search_input.text().strip().upper()

        filtrelenmis_liste = []

        for item in self.raw_data:
            symbol = item.get("symbol", "")

            try:
                volume = float(item.get("quoteVolume", 0))
                price = float(item.get("lastPrice", 0))
                change = float(item.get("priceChangePercent", 0))
            except ValueError:
                continue

            # --- OPTİMİZASYON: Hacmi 50.000 USDT'nin altında olan binlerce çöp coini baştan eliyoruz ---
            if volume < 50000:
                continue

            if search_text and search_text not in symbol:
                continue

            if parite and parite != "TÜMÜ" and not symbol.endswith(parite):
                continue

            # --- KATEGORİ FİLTRESİ ---
            if secilen_kategori and secilen_kategori != "TÜMÜ":
                kategori_listesi = self.kategori_sozlugu.get(secilen_kategori, [])
                bulundu = False
                for cat_coin in kategori_listesi:
                    if symbol == cat_coin + parite or symbol.startswith(cat_coin):
                        bulundu = True
                        break
                if kategori_listesi and not bulundu:
                    continue

            # --- YÖN FİLTRESİ ---
            yon_text = yon.replace("İ", "I").upper()
            if "YUKSELEN" in yon_text and change <= 0:
                continue
            if "DUSEN" in yon_text and change >= 0:
                continue

            if min_val != 0.0 or max_val != 0.0:
                if not (min_val <= change <= max_val):
                    continue

            filtrelenmis_liste.append({
                "symbol": symbol,
                "price": price,
                "change": change,
                "volume": volume
            })

        # Hacme göre sırala
        filtrelenmis_liste.sort(key=lambda x: x["volume"], reverse=True)
        
        # --- OPTİMİZASYON: Listeyi en yüksek hacimli ilk 400 coin ile sınırla ---
        filtrelenmis_liste = filtrelenmis_liste[:400]

        self.tabloya_bas(filtrelenmis_liste)

    def tabloya_bas(self, veri_listesi):
        self.table.setRowCount(len(veri_listesi))

        for row_idx, data in enumerate(veri_listesi):
            symbol = data["symbol"]
            price_str = f"{data['price']:.4f}" if data['price'] < 1 else f"{data['price']:.2f}"
            change_val = data["change"]
            change_str = f"+%{change_val:.2f}" if change_val >= 0 else f"%{change_val:.2f}"

            self.table.setItem(row_idx, 0, QTableWidgetItem(symbol))
            self.table.setItem(row_idx, 1, QTableWidgetItem(price_str))

            change_item = QTableWidgetItem(change_str)
            if change_val >= 0:
                change_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                change_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 2, change_item)

            vol_str = f"{data['volume']:,.0f}"
            self.table.setItem(row_idx, 3, QTableWidgetItem(vol_str))

    def satir_tiklandi(self, item):
        row = item.row()
        symbol_item = self.table.item(row, 0)
        price_item = self.table.item(row, 1)
        change_item = self.table.item(row, 2)

        if symbol_item:
            symbol = symbol_item.text()
            price = price_item.text() if price_item else "0"
            change = change_item.text() if change_item else "0"

            detay_pencere = KriptoDetayPenceresi(symbol, price, change, self.win, parent=self.win)
            detay_pencere.exec()