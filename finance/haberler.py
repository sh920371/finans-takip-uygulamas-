from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView


class HaberlerTab:

    def __init__(self, main_window, taranacak_tablolar):

        self.ui = main_window
        self.taranacak_tablolar = taranacak_tablolar

        # Daha önce bildirilen alarmları tutar
        self.bildirilenler = set()

        # Alarm kayıtları
        self.tum_alarmlar = []

        self.init_ui()

        # =========================================================
        # ALARM TARAMA
        # =========================================================
        #
        # Artık QThread kullanmıyoruz.
        #
        # Çünkü QTableWidget yalnızca GUI thread'inde okunmalı.
        #
        # Her 60 saniyede bir alarm_tara() çalışacak.
        #
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.alarm_tara)
        self.alarm_timer.start(60000)

        # Uygulama açıldıktan 1 saniye sonra ilk kontrol
        # Böylece ana pencerenin açılışı sırasında ekstra yük bindirmiyoruz.
        QTimer.singleShot(
            1000,
            self.alarm_tara
        )

    # =============================================================
    # ARAYÜZ
    # =============================================================

    def init_ui(self):

        self.ui.comboBox_17.clear()

        self.ui.comboBox_17.addItems([
            "Tümü",
            "⚠️ Ani Düşüş",
            "🚀 Ani Yükseliş"
        ])

        self.ui.tableWidget_10.setColumnCount(3)

        self.ui.tableWidget_10.setHorizontalHeaderLabels([
            "Kategori",
            "Alarm Bildirimi",
            "Zaman"
        ])

        self.ui.tableWidget_10.verticalHeader().setVisible(False)

        header = self.ui.tableWidget_10.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.ui.comboBox_17.currentIndexChanged.connect(
            self.filtrele
        )

        self.ui.lineEdit_8.textChanged.connect(
            self.filtrele
        )

        self.ui.tableWidget_10.setRowCount(0)

        self.ui.tableWidget_10.setShowGrid(False)

        self.ui.tableWidget_10.verticalHeader().setDefaultSectionSize(
            45
        )

        font = self.ui.tableWidget_10.font()
        font.setPointSize(11)

        self.ui.tableWidget_10.setFont(font)

        self.ui.tableWidget_10.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #15131A;
                color: #C9A8E8;
                font-weight: bold;
                font-size: 10pt;
                border: none;
                padding: 5px;
            }
        """)

    # =============================================================
    # TABLOLARI OKU
    # =============================================================

    def guvenli_tablo_okuyucu(self):

        """
        Ana GUI thread'inde çalışır.

        Tablolardaki sembol ve değişim değerlerini
        normal Python verisine çevirir.
        """

        toplanan_veriler = []

        for tablo in self.taranacak_tablolar:

            try:

                satir_sayisi = tablo.rowCount()
                sutun_sayisi = tablo.columnCount()

                if sutun_sayisi < 2:
                    continue

                # İlk sütun = sembol
                sutun_sembol = 0

                # Son sütun = değişim
                sutun_degisim = sutun_sayisi - 1

                for row in range(satir_sayisi):

                    sembol_item = tablo.item(
                        row,
                        sutun_sembol
                    )

                    degisim_item = tablo.item(
                        row,
                        sutun_degisim
                    )

                    if not sembol_item or not degisim_item:
                        continue

                    try:

                        sembol = (
                            sembol_item
                            .text()
                            .strip()
                        )

                        degisim_str = (
                            degisim_item
                            .text()
                            .replace("%", "")
                            .replace(",", ".")
                            .strip()
                        )

                        # +%5.2 gibi ifadeler varsa
                        degisim_str = degisim_str.replace(
                            "+",
                            ""
                        )

                        degisim = float(
                            degisim_str
                        )

                        toplanan_veriler.append(
                            (
                                sembol,
                                degisim
                            )
                        )

                    except (ValueError, TypeError):
                        continue

            except Exception as e:

                print(
                    f"Alarm tablosu okuma hatası: {e}"
                )

        return toplanan_veriler

    # =============================================================
    # ALARM TARAMA
    # =============================================================

    def alarm_tara(self):

        """
        Tablolardaki güncel değişimleri kontrol eder.

        Artık QThread yok.
        QTableWidget tamamen GUI thread'inde okunuyor.
        """

        try:

            toplanan_veriler = (
                self.guvenli_tablo_okuyucu()
            )

            for sembol, degisim in toplanan_veriler:

                # %5 hareket yoksa alarm üretme
                if abs(degisim) < 5.0:
                    continue

                if degisim < 0:

                    kategori = "⚠️ Ani Düşüş"
                    hareket = "düşüş"

                else:

                    kategori = "🚀 Ani Yükseliş"
                    hareket = "yükseliş"

                mesaj = (
                    f"{sembol} ani "
                    f"{hareket} "
                    f"%{abs(degisim):.1f}"
                )

                # Aynı sembolün aynı yöndeki alarmını
                # sürekli tekrar üretme.
                #
                # Örneğin:
                #
                # BTC %5.2
                # BTC %5.8
                # BTC %6.1
                #
                # bunların hepsi aynı "yükseliş alarmı"dır.
                #
                yon = (
                    "DUSUS"
                    if degisim < 0
                    else "YUKSELIS"
                )

                benzersiz_anahtar = (
                    f"{sembol}_{yon}"
                )

                if benzersiz_anahtar in self.bildirilenler:
                    continue

                self.bildirilenler.add(
                    benzersiz_anahtar
                )

                self.guvenli_alarm_ekle([
                    kategori,
                    mesaj,
                    "Şimdi"
                ])

        except Exception as e:

            print(
                f"Alarm tarama hatası: {e}"
            )

    # =============================================================
    # ALARM EKLE
    # =============================================================

    def guvenli_alarm_ekle(self, veri_listesi):

        try:

            kategori = veri_listesi[0]
            mesaj = veri_listesi[1]
            zaman = veri_listesi[2]

            alarm = {
                "kategori": kategori,
                "mesaj": mesaj,
                "zaman": zaman
            }

            self.tum_alarmlar.insert(
                0,
                alarm
            )

            self.tabloyu_guncelle()

        except Exception as e:

            print(
                f"Alarm ekleme hatası: {e}"
            )

    # =============================================================
    # FİLTRE
    # =============================================================

    def filtrele(self):

        self.tabloyu_guncelle()

    # =============================================================
    # ALARM TABLOSUNU GÜNCELLE
    # =============================================================

    def tabloyu_guncelle(self):

        self.ui.tableWidget_10.setUpdatesEnabled(
            False
        )

        try:

            secilen_kategori = (
                self.ui.comboBox_17
                .currentText()
            )

            arama_metni = (
                self.ui.lineEdit_8
                .text()
                .lower()
                .strip()
            )

            self.ui.tableWidget_10.setRowCount(0)

            for alarm in self.tum_alarmlar:

                kategori_uyuyor = (
                    secilen_kategori == "Tümü"
                    or
                    alarm["kategori"] == secilen_kategori
                )

                arama_uyuyor = (
                    arama_metni in
                    alarm["mesaj"].lower()
                )

                if not (
                    kategori_uyuyor
                    and
                    arama_uyuyor
                ):
                    continue

                row_idx = (
                    self.ui.tableWidget_10
                    .rowCount()
                )

                self.ui.tableWidget_10.insertRow(
                    row_idx
                )

                cat_item = QTableWidgetItem(
                    alarm["kategori"]
                )

                msg_item = QTableWidgetItem(
                    alarm["mesaj"]
                )

                date_item = QTableWidgetItem(
                    alarm["zaman"]
                )

                # =================================================
                # RENK
                # =================================================

                if "Düşüş" in alarm["kategori"]:

                    cat_item.setForeground(
                        QColor("#FF6B6B")
                    )

                    msg_item.setForeground(
                        QColor("#FF6B6B")
                    )

                else:

                    cat_item.setForeground(
                        QColor("#51CF66")
                    )

                    msg_item.setForeground(
                        QColor("#51CF66")
                    )

                # =================================================
                # DÜZENLENEMESİN
                # =================================================

                for col_item in (
                    cat_item,
                    msg_item,
                    date_item
                ):

                    col_item.setFlags(
                        col_item.flags()
                        & ~Qt.ItemIsEditable
                    )

                # =================================================
                # TABLOYA EKLE
                # =================================================

                self.ui.tableWidget_10.setItem(
                    row_idx,
                    0,
                    cat_item
                )

                self.ui.tableWidget_10.setItem(
                    row_idx,
                    1,
                    msg_item
                )

                self.ui.tableWidget_10.setItem(
                    row_idx,
                    2,
                    date_item
                )

        finally:

            self.ui.tableWidget_10.setUpdatesEnabled(
                True
            )

    # =============================================================
    # DURDUR
    # =============================================================

    def durdur(self):

        """
        Ana pencere kapanırken çağırabilirsin.

        Eski QThread olmadığı için artık
        wait() gerekmiyor.
        """

        if hasattr(self, "alarm_timer"):

            self.alarm_timer.stop()
            self.alarm_timer.deleteLater()

            self.alarm_timer = None