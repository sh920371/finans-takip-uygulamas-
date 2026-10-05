import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from finance_ui import Ui_MainWindow
from kureselborsalar import KureselBorsalarManager
from izlemelist import IzlemeListesiManager
from kripto import KriptoManager
from emtialar import EmtialarTab
from dovizpariteleri import DovizPariteleriTab
from haberler import HaberlerTab
from notlar import NotlarYoneticisi
from sohbet import SohbetSekmesi


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("HubFin")
        self.menuBar.hide()
        self.tabWidget_3.setStyleSheet("""
            QTabBar::close-button {
                background: transparent;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QTabBar::close-button:hover {
                background-color: rgba(255, 107, 107, 0.3);
            }
            QTabBar::close-button:pressed {
                background-color: #FF6B6B;
            }
        """)
        
        # Gereksiz kısımları kodla temizleyelim 
    
        
        self.borsalar_manager = KureselBorsalarManager(self)
        self.tabWidget_3.clear()
        self.izleme_listesi_yoneticisi = IzlemeListesiManager(self.tabWidget_3)
        self.kripto_manager = KriptoManager(self)
        self.kripto_manager.verileri_cek()
        self.emtia_manager = EmtialarTab(self)
        self.doviz_manager = DovizPariteleriTab(self)
        taranacak_tablolar = [
            self.tableWidget_2,
            self.tableWidget_3,
            self.tableWidget_6,
            self.tableWidget_7,
            self.tableWidget_8,
            self.tableWidget_9
        ]
        self.haberler_manager = HaberlerTab(self, taranacak_tablolar)  
        self.not_yoneticisi = NotlarYoneticisi(self)
        self.sohbet_sekmesi = SohbetSekmesi()
        self.tabWidget.addTab(self.sohbet_sekmesi, " Karşılaştırma ")
        # Sohbet başlıklı boş sekmeyi arayüzden bulup kaldıralım:
        for i in range(self.tabWidget.count()):
            if "Sohbet" in self.tabWidget.tabText(i):
                self.tabWidget.removeTab(i)
                break
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_6))
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_20)) 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern Dark Tema


app.setStyleSheet("""
    /* ==========================================
       MODERN DARK FINANCE
       ========================================== */

    QMainWindow {
        background-color: #0D0D12;
    }

    QWidget {
        background-color: #0D0D12;
        color: #E7E3EE;
        font-family: "Segoe UI";
    }


    /* ==========================================
       BUTONLAR
       ========================================== */

    QPushButton {
        background-color: #18151F;
        color: #DCD6E8;

        border: 1px solid #2B2635;
        border-radius: 7px;

        padding: 8px 14px;
        font-weight: 500;
    }

    QPushButton:hover {
        background-color: #211C2B;
        border-color: #6F5A86;
        color: #FFFFFF;
    }

    QPushButton:pressed {
        background-color: #2A2335;
    }


    /* ==========================================
       AKTİF / VURGU BUTON
       ========================================== */

    QPushButton:checked {
        background-color: #403052;
        border: 1px solid #80639C;
        color: #FFFFFF;
    }


    /* ==========================================
       TAB
       ========================================== */

    QTabWidget::pane {
        background-color: #0D0D12;
        border: none;
    }

    QTabBar::tab {
        background-color: #121117;
        color: #8E8799;

        border: 1px solid #211D27;
        border-bottom: none;

        padding: 9px 18px;
        margin-right: 3px;

        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
    }

    QTabBar::tab:hover {
        background-color: #1A1720;
        color: #D8D0E2;
    }

    QTabBar::tab:selected {
        background-color: #211B2A;
        color: #C9A8E8;

        border: 1px solid #4C3B59;
        border-bottom: 2px solid #A875D1;
    }


    /* ==========================================
       LINE EDIT
       ========================================== */

    QLineEdit {
        background-color: #15131A;
        color: #EDE8F2;

        border: 1px solid #2A2631;
        border-radius: 7px;

        padding: 8px 11px;
    }

    QLineEdit:hover {
        border-color: #5B4869;
    }

    QLineEdit:focus {
        border-color: #9466B5;
        background-color: #18151F;
    }


    /* ==========================================
       COMBOBOX
       ========================================== */

    QComboBox {
        background-color: #15131A;
        color: #E5DFEA;

        border: 1px solid #2A2631;
        border-radius: 7px;

        padding: 8px 11px;
    }

    QComboBox:hover {
        border-color: #5B4869;
    }

    QComboBox:focus {
        border-color: #9466B5;
    }

    QComboBox QAbstractItemView {
        background-color: #17141C;
        color: #E5DFEA;

        border: 1px solid #3A3043;

        selection-background-color: #3A2947;
        selection-color: #FFFFFF;
    }


    /* ==========================================
       TABLO
       ========================================== */

    QTableWidget {
        background-color: #111015;
        alternate-background-color: #15131A;

        color: #E4DEE9;

        border: 1px solid #29242F;
        border-radius: 8px;

        gridline-color: #211E26;

        selection-background-color: #392C46;
        selection-color: #FFFFFF;

        outline: none;
    }

    QTableWidget::item {
        padding: 8px;
    }

    QTableWidget::item:hover {
        background-color: #1C1821;
    }

    QHeaderView::section {
        background-color: #18151D;

        color: #9E95A8;

        border: none;
        border-bottom: 1px solid #302A37;

        padding: 9px;

        font-weight: 600;
    }


    /* ==========================================
       TEXT BROWSER / AI
       ========================================== */

    QTextBrowser {
        background-color: #121016;

        color: #E5DFEA;

        border: 1px solid #2B2531;
        border-radius: 8px;

        padding: 11px;
    }


    /* ==========================================
       LABEL
       ========================================== */

    QLabel {
        color: #D9D2E0;
    }


    /* ==========================================
       SCROLLBAR
       ========================================== */

    QScrollBar:vertical {
        background: #0D0D12;
        width: 8px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: #39313F;
        border-radius: 4px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: #6D557D;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background: #0D0D12;
        height: 8px;
        border: none;
    }

    QScrollBar::handle:horizontal {
        background: #39313F;
        border-radius: 4px;
    }
""")
window = MainWindow()
window.show()
sys.exit(app.exec())