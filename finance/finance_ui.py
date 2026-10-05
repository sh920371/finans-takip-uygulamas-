# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'finance.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(863, 600)
        self.actionCSV_Olarak_D_a_Aktar = QAction(MainWindow)
        self.actionCSV_Olarak_D_a_Aktar.setObjectName(u"actionCSV_Olarak_D_a_Aktar")
        self.actionPDF_Raporu_Al = QAction(MainWindow)
        self.actionPDF_Raporu_Al.setObjectName(u"actionPDF_Raporu_Al")
        self.action_k = QAction(MainWindow)
        self.action_k.setObjectName(u"action_k")
        self.actionTema = QAction(MainWindow)
        self.actionTema.setObjectName(u"actionTema")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget_2 = QTabWidget(self.tab)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab_9 = QWidget()
        self.tab_9.setObjectName(u"tab_9")
        self.verticalLayout_6 = QVBoxLayout(self.tab_9)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame = QFrame(self.tab_9)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox_2 = QComboBox(self.frame)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.horizontalLayout.addWidget(self.comboBox_2)

        self.comboBox_3 = QComboBox(self.frame)
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.horizontalLayout.addWidget(self.comboBox_3)

        self.comboBox = QComboBox(self.frame)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.doubleSpinBox = QDoubleSpinBox(self.frame)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setKeyboardTracking(True)
        self.doubleSpinBox.setProperty(u"showGroupSeparator", False)
        self.doubleSpinBox.setMinimum(-99.989999999999995)

        self.horizontalLayout.addWidget(self.doubleSpinBox)

        self.doubleSpinBox_2 = QDoubleSpinBox(self.frame)
        self.doubleSpinBox_2.setObjectName(u"doubleSpinBox_2")
        self.doubleSpinBox_2.setMinimum(-99.989999999999995)

        self.horizontalLayout.addWidget(self.doubleSpinBox_2)


        self.verticalLayout_6.addWidget(self.frame)

        self.frame_2 = QFrame(self.tab_9)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit = QLineEdit(self.frame_2)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setDragEnabled(False)
        self.lineEdit.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.lineEdit)


        self.verticalLayout_6.addWidget(self.frame_2)

        self.tableWidget_2 = QTableWidget(self.tab_9)
        self.tableWidget_2.setObjectName(u"tableWidget_2")

        self.verticalLayout_6.addWidget(self.tableWidget_2)

        self.tabWidget_2.addTab(self.tab_9, "")
        self.tab_10 = QWidget()
        self.tab_10.setObjectName(u"tab_10")
        self.verticalLayout_4 = QVBoxLayout(self.tab_10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tableWidget_3 = QTableWidget(self.tab_10)
        self.tableWidget_3.setObjectName(u"tableWidget_3")

        self.verticalLayout_4.addWidget(self.tableWidget_3)

        self.tabWidget_2.addTab(self.tab_10, "")
        self.tab_11 = QWidget()
        self.tab_11.setObjectName(u"tab_11")
        self.verticalLayout_8 = QVBoxLayout(self.tab_11)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.frame_5 = QFrame(self.tab_11)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.comboBox_7 = QComboBox(self.frame_5)
        self.comboBox_7.addItem("")
        self.comboBox_7.setObjectName(u"comboBox_7")

        self.horizontalLayout_5.addWidget(self.comboBox_7)

        self.comboBox_8 = QComboBox(self.frame_5)
        self.comboBox_8.addItem("")
        self.comboBox_8.setObjectName(u"comboBox_8")

        self.horizontalLayout_5.addWidget(self.comboBox_8)

        self.comboBox_9 = QComboBox(self.frame_5)
        self.comboBox_9.addItem("")
        self.comboBox_9.addItem("")
        self.comboBox_9.addItem("")
        self.comboBox_9.setObjectName(u"comboBox_9")

        self.horizontalLayout_5.addWidget(self.comboBox_9)

        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.doubleSpinBox_5 = QDoubleSpinBox(self.frame_5)
        self.doubleSpinBox_5.setObjectName(u"doubleSpinBox_5")
        self.doubleSpinBox_5.setKeyboardTracking(True)
        self.doubleSpinBox_5.setProperty(u"showGroupSeparator", False)
        self.doubleSpinBox_5.setMinimum(-99.989999999999995)

        self.horizontalLayout_5.addWidget(self.doubleSpinBox_5)

        self.doubleSpinBox_6 = QDoubleSpinBox(self.frame_5)
        self.doubleSpinBox_6.setObjectName(u"doubleSpinBox_6")
        self.doubleSpinBox_6.setMinimum(-99.989999999999995)

        self.horizontalLayout_5.addWidget(self.doubleSpinBox_6)


        self.verticalLayout_8.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.tab_11)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.frame_6)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lineEdit_3 = QLineEdit(self.frame_6)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setDragEnabled(False)
        self.lineEdit_3.setClearButtonEnabled(True)

        self.horizontalLayout_6.addWidget(self.lineEdit_3)


        self.verticalLayout_8.addWidget(self.frame_6)

        self.tableWidget_6 = QTableWidget(self.tab_11)
        self.tableWidget_6.setObjectName(u"tableWidget_6")

        self.verticalLayout_8.addWidget(self.tableWidget_6)

        self.tabWidget_2.addTab(self.tab_11, "")

        self.verticalLayout_2.addWidget(self.tabWidget_2)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_3 = QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget_3 = QTabWidget(self.tab_2)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tabWidget_3.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.tabWidget_3.setTabsClosable(True)
        self.tabWidget_3.setMovable(True)
        self.tab_12 = QWidget()
        self.tab_12.setObjectName(u"tab_12")
        self.tabWidget_3.addTab(self.tab_12, "")
        self.tab_13 = QWidget()
        self.tab_13.setObjectName(u"tab_13")
        self.tabWidget_3.addTab(self.tab_13, "")
        self.tab_14 = QWidget()
        self.tab_14.setObjectName(u"tab_14")
        self.tabWidget_3.addTab(self.tab_14, "")
        self.tab_15 = QWidget()
        self.tab_15.setObjectName(u"tab_15")
        self.tabWidget_3.addTab(self.tab_15, "")

        self.verticalLayout_3.addWidget(self.tabWidget_3)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_10 = QVBoxLayout(self.tab_4)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.frame_8 = QFrame(self.tab_4)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.comboBox_10 = QComboBox(self.frame_8)
        self.comboBox_10.addItem("")
        self.comboBox_10.setObjectName(u"comboBox_10")

        self.horizontalLayout_7.addWidget(self.comboBox_10)

        self.comboBox_11 = QComboBox(self.frame_8)
        self.comboBox_11.addItem("")
        self.comboBox_11.setObjectName(u"comboBox_11")

        self.horizontalLayout_7.addWidget(self.comboBox_11)

        self.comboBox_12 = QComboBox(self.frame_8)
        self.comboBox_12.addItem("")
        self.comboBox_12.addItem("")
        self.comboBox_12.addItem("")
        self.comboBox_12.setObjectName(u"comboBox_12")

        self.horizontalLayout_7.addWidget(self.comboBox_12)

        self.label_7 = QLabel(self.frame_8)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_7.addWidget(self.label_7)

        self.doubleSpinBox_7 = QDoubleSpinBox(self.frame_8)
        self.doubleSpinBox_7.setObjectName(u"doubleSpinBox_7")
        self.doubleSpinBox_7.setKeyboardTracking(True)
        self.doubleSpinBox_7.setProperty(u"showGroupSeparator", False)
        self.doubleSpinBox_7.setMinimum(-99.989999999999995)

        self.horizontalLayout_7.addWidget(self.doubleSpinBox_7)

        self.doubleSpinBox_8 = QDoubleSpinBox(self.frame_8)
        self.doubleSpinBox_8.setObjectName(u"doubleSpinBox_8")
        self.doubleSpinBox_8.setMinimum(-99.989999999999995)

        self.horizontalLayout_7.addWidget(self.doubleSpinBox_8)


        self.verticalLayout_10.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.tab_4)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_8 = QLabel(self.frame_9)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_8.addWidget(self.label_8)

        self.lineEdit_4 = QLineEdit(self.frame_9)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setDragEnabled(False)
        self.lineEdit_4.setClearButtonEnabled(True)

        self.horizontalLayout_8.addWidget(self.lineEdit_4)


        self.verticalLayout_10.addWidget(self.frame_9)

        self.tableWidget_7 = QTableWidget(self.tab_4)
        self.tableWidget_7.setObjectName(u"tableWidget_7")

        self.verticalLayout_10.addWidget(self.tableWidget_7)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.verticalLayout_11 = QVBoxLayout(self.tab_5)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.frame_10 = QFrame(self.tab_5)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.comboBox_13 = QComboBox(self.frame_10)
        self.comboBox_13.addItem("")
        self.comboBox_13.setObjectName(u"comboBox_13")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_13.sizePolicy().hasHeightForWidth())
        self.comboBox_13.setSizePolicy(sizePolicy)
        self.comboBox_13.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.comboBox_13.setMinimumContentsLength(0)

        self.horizontalLayout_10.addWidget(self.comboBox_13)

        self.label_10 = QLabel(self.frame_10)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_10.addWidget(self.label_10)

        self.lineEdit_6 = QLineEdit(self.frame_10)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.horizontalLayout_10.addWidget(self.lineEdit_6)


        self.verticalLayout_11.addWidget(self.frame_10)

        self.tableWidget_8 = QTableWidget(self.tab_5)
        self.tableWidget_8.setObjectName(u"tableWidget_8")

        self.verticalLayout_11.addWidget(self.tableWidget_8)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_8 = QWidget()
        self.tab_8.setObjectName(u"tab_8")
        self.verticalLayout_12 = QVBoxLayout(self.tab_8)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.frame_11 = QFrame(self.tab_8)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.comboBox_14 = QComboBox(self.frame_11)
        self.comboBox_14.addItem("")
        self.comboBox_14.setObjectName(u"comboBox_14")

        self.horizontalLayout_11.addWidget(self.comboBox_14)

        self.comboBox_15 = QComboBox(self.frame_11)
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.comboBox_15.setObjectName(u"comboBox_15")

        self.horizontalLayout_11.addWidget(self.comboBox_15)

        self.comboBox_16 = QComboBox(self.frame_11)
        self.comboBox_16.addItem("")
        self.comboBox_16.addItem("")
        self.comboBox_16.addItem("")
        self.comboBox_16.setObjectName(u"comboBox_16")

        self.horizontalLayout_11.addWidget(self.comboBox_16)

        self.label_11 = QLabel(self.frame_11)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_11.addWidget(self.label_11)

        self.doubleSpinBox_9 = QDoubleSpinBox(self.frame_11)
        self.doubleSpinBox_9.setObjectName(u"doubleSpinBox_9")
        self.doubleSpinBox_9.setKeyboardTracking(True)
        self.doubleSpinBox_9.setProperty(u"showGroupSeparator", False)
        self.doubleSpinBox_9.setMinimum(-99.989999999999995)

        self.horizontalLayout_11.addWidget(self.doubleSpinBox_9)

        self.doubleSpinBox_10 = QDoubleSpinBox(self.frame_11)
        self.doubleSpinBox_10.setObjectName(u"doubleSpinBox_10")
        self.doubleSpinBox_10.setMinimum(-99.989999999999995)

        self.horizontalLayout_11.addWidget(self.doubleSpinBox_10)


        self.verticalLayout_12.addWidget(self.frame_11)

        self.frame_12 = QFrame(self.tab_8)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_12 = QLabel(self.frame_12)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_12.addWidget(self.label_12)

        self.lineEdit_7 = QLineEdit(self.frame_12)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        self.lineEdit_7.setDragEnabled(False)
        self.lineEdit_7.setClearButtonEnabled(True)

        self.horizontalLayout_12.addWidget(self.lineEdit_7)


        self.verticalLayout_12.addWidget(self.frame_12)

        self.tableWidget_9 = QTableWidget(self.tab_8)
        self.tableWidget_9.setObjectName(u"tableWidget_9")

        self.verticalLayout_12.addWidget(self.tableWidget_9)

        self.tabWidget.addTab(self.tab_8, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_14 = QVBoxLayout(self.tab_3)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.frame_13 = QFrame(self.tab_3)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.comboBox_17 = QComboBox(self.frame_13)
        self.comboBox_17.addItem("")
        self.comboBox_17.addItem("")
        self.comboBox_17.addItem("")
        self.comboBox_17.addItem("")
        self.comboBox_17.addItem("")
        self.comboBox_17.addItem("")
        self.comboBox_17.setObjectName(u"comboBox_17")
        sizePolicy.setHeightForWidth(self.comboBox_17.sizePolicy().hasHeightForWidth())
        self.comboBox_17.setSizePolicy(sizePolicy)
        self.comboBox_17.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.comboBox_17.setMinimumContentsLength(0)

        self.horizontalLayout_13.addWidget(self.comboBox_17)

        self.label_13 = QLabel(self.frame_13)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_13.addWidget(self.label_13)

        self.lineEdit_8 = QLineEdit(self.frame_13)
        self.lineEdit_8.setObjectName(u"lineEdit_8")

        self.horizontalLayout_13.addWidget(self.lineEdit_8)


        self.verticalLayout_14.addWidget(self.frame_13)

        self.tableWidget_10 = QTableWidget(self.tab_3)
        self.tableWidget_10.setObjectName(u"tableWidget_10")

        self.verticalLayout_14.addWidget(self.tableWidget_10)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.verticalLayout_15 = QVBoxLayout(self.tab_6)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.textEdit_2 = QTextEdit(self.tab_6)
        self.textEdit_2.setObjectName(u"textEdit_2")

        self.verticalLayout_15.addWidget(self.textEdit_2)

        self.pushButton = QPushButton(self.tab_6)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_15.addWidget(self.pushButton)

        self.tableWidget_11 = QTableWidget(self.tab_6)
        self.tableWidget_11.setObjectName(u"tableWidget_11")

        self.verticalLayout_15.addWidget(self.tableWidget_11)

        self.tabWidget.addTab(self.tab_6, "")
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.tabWidget.addTab(self.tab_7, "")
        self.tab_16 = QWidget()
        self.tab_16.setObjectName(u"tab_16")
        self.verticalLayout_9 = QVBoxLayout(self.tab_16)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.frame_7 = QFrame(self.tab_16)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_7)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.textEdit = QTextEdit(self.frame_7)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout_13.addWidget(self.textEdit)

        self.pushButton_2 = QPushButton(self.frame_7)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_13.addWidget(self.pushButton_2)

        self.tableWidget = QTableWidget(self.frame_7)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout_13.addWidget(self.tableWidget)


        self.verticalLayout_9.addWidget(self.frame_7)

        self.tabWidget.addTab(self.tab_16, "")
        self.tab_20 = QWidget()
        self.tab_20.setObjectName(u"tab_20")
        self.verticalLayout_16 = QVBoxLayout(self.tab_20)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.scrollArea = QScrollArea(self.tab_20)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 811, 471))
        self.verticalLayout_17 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox.setObjectName(u"groupBox")

        self.verticalLayout_17.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_2.setObjectName(u"groupBox_2")

        self.verticalLayout_17.addWidget(self.groupBox_2)

        self.groupBox_4 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_4.setObjectName(u"groupBox_4")

        self.verticalLayout_17.addWidget(self.groupBox_4)

        self.groupBox_5 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_5.setObjectName(u"groupBox_5")

        self.verticalLayout_17.addWidget(self.groupBox_5)

        self.groupBox_3 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_3.setObjectName(u"groupBox_3")

        self.verticalLayout_17.addWidget(self.groupBox_3)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_16.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab_20, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 863, 26))
        self.menuD_a_Aktar = QMenu(self.menuBar)
        self.menuD_a_Aktar.setObjectName(u"menuD_a_Aktar")
        self.menuG_r_n_m = QMenu(self.menuBar)
        self.menuG_r_n_m.setObjectName(u"menuG_r_n_m")
        self.menuDil = QMenu(self.menuBar)
        self.menuDil.setObjectName(u"menuDil")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuD_a_Aktar.menuAction())
        self.menuBar.addAction(self.menuG_r_n_m.menuAction())
        self.menuBar.addAction(self.menuDil.menuAction())
        self.menuD_a_Aktar.addAction(self.actionCSV_Olarak_D_a_Aktar)
        self.menuD_a_Aktar.addAction(self.actionPDF_Raporu_Al)
        self.menuD_a_Aktar.addAction(self.action_k)
        self.menuG_r_n_m.addAction(self.actionTema)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(2)
        self.tabWidget_3.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionCSV_Olarak_D_a_Aktar.setText(QCoreApplication.translate("MainWindow", u"CSV Olarak D\u0131\u015fa Aktar", None))
        self.actionPDF_Raporu_Al.setText(QCoreApplication.translate("MainWindow", u"PDF Raporu Al", None))
        self.action_k.setText(QCoreApplication.translate("MainWindow", u"\u00c7\u0131k\u0131\u015f", None))
        self.actionTema.setText(QCoreApplication.translate("MainWindow", u"Tema", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", u"Endeks Se\u00e7iniz", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", u"B\u0130ST", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", u"NASTAQ", None))
        self.comboBox_2.setItemText(3, QCoreApplication.translate("MainWindow", u"DAX", None))
        self.comboBox_2.setItemText(4, QCoreApplication.translate("MainWindow", u"New Item", None))

        self.comboBox_3.setItemText(0, QCoreApplication.translate("MainWindow", u"Sekt\u00f6r Se\u00e7iniz", None))

        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm\u00fc", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Y\u00fckselen", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"D\u00fc\u015fen", None))

        self.label.setText(QCoreApplication.translate("MainWindow", u"De\u011fi\u015fim Aral\u0131\u011f\u0131:", None))
        self.doubleSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"Min ", None))
        self.doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.doubleSpinBox_2.setPrefix(QCoreApplication.translate("MainWindow", u"Max ", None))
        self.doubleSpinBox_2.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.lineEdit.setText("")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_9), QCoreApplication.translate("MainWindow", u"Hisseler", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_10), QCoreApplication.translate("MainWindow", u"Endeksler", None))
        self.comboBox_7.setItemText(0, QCoreApplication.translate("MainWindow", u"Tahvil \u015fe\u00e7iniz", None))

        self.comboBox_8.setItemText(0, QCoreApplication.translate("MainWindow", u"\u00dclke se\u00e7iniz", None))

        self.comboBox_9.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm\u00fc", None))
        self.comboBox_9.setItemText(1, QCoreApplication.translate("MainWindow", u"Y\u00fckselen", None))
        self.comboBox_9.setItemText(2, QCoreApplication.translate("MainWindow", u"D\u00fc\u015fen", None))

        self.label_5.setText(QCoreApplication.translate("MainWindow", u"De\u011fi\u015fim Aral\u0131\u011f\u0131:", None))
        self.doubleSpinBox_5.setPrefix(QCoreApplication.translate("MainWindow", u"Min ", None))
        self.doubleSpinBox_5.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.doubleSpinBox_6.setPrefix(QCoreApplication.translate("MainWindow", u"Max ", None))
        self.doubleSpinBox_6.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.lineEdit_3.setText("")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_11), QCoreApplication.translate("MainWindow", u"Tahviller", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"K\u00fcresel Borsalar", None))
        #self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_12), QCoreApplication.translate("MainWindow", u"B\u0130ST", None))
        #self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_13), QCoreApplication.translate("MainWindow", u"NASDAQ", None))
        #self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_14), QCoreApplication.translate("MainWindow", u"DAX", None))
        #self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_15), QCoreApplication.translate("MainWindow", u"Gold", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\u0130zleme Listesi", None))
        self.comboBox_10.setItemText(0, QCoreApplication.translate("MainWindow", u"Coin Paritesi Se\u00e7iniz", None))

        self.comboBox_11.setItemText(0, QCoreApplication.translate("MainWindow", u"Kategori Se\u00e7iniz", None))

        self.comboBox_12.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm\u00fc", None))
        self.comboBox_12.setItemText(1, QCoreApplication.translate("MainWindow", u"Y\u00fckselen", None))
        self.comboBox_12.setItemText(2, QCoreApplication.translate("MainWindow", u"D\u00fc\u015fen", None))

        self.label_7.setText(QCoreApplication.translate("MainWindow", u"De\u011fi\u015fim Aral\u0131\u011f\u0131:", None))
        self.doubleSpinBox_7.setPrefix(QCoreApplication.translate("MainWindow", u"Min ", None))
        self.doubleSpinBox_7.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.doubleSpinBox_8.setPrefix(QCoreApplication.translate("MainWindow", u"Max ", None))
        self.doubleSpinBox_8.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.lineEdit_4.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Kripto", None))
        self.comboBox_13.setItemText(0, QCoreApplication.translate("MainWindow", u"De\u011ferli Madenler", None))

        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", u"Emtialar", None))
        self.comboBox_14.setItemText(0, QCoreApplication.translate("MainWindow", u"Baz Birimi Se\u00e7iniz", None))

        self.comboBox_15.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm D\u00fcnya", None))
        self.comboBox_15.setItemText(1, QCoreApplication.translate("MainWindow", u"Maj\u00f6rler", None))
        self.comboBox_15.setItemText(2, QCoreApplication.translate("MainWindow", u"Geli\u015fmekte Olan Piyasalar ", None))
        self.comboBox_15.setItemText(3, QCoreApplication.translate("MainWindow", u"Orta Do\u011fu/Asya Kurlar\u0131", None))

        self.comboBox_16.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm\u00fc", None))
        self.comboBox_16.setItemText(1, QCoreApplication.translate("MainWindow", u"Y\u00fckselen", None))
        self.comboBox_16.setItemText(2, QCoreApplication.translate("MainWindow", u"D\u00fc\u015fen", None))

        self.label_11.setText(QCoreApplication.translate("MainWindow", u"De\u011fi\u015fim Aral\u0131\u011f\u0131:", None))
        self.doubleSpinBox_9.setPrefix(QCoreApplication.translate("MainWindow", u"Min ", None))
        self.doubleSpinBox_9.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.doubleSpinBox_10.setPrefix(QCoreApplication.translate("MainWindow", u"Max ", None))
        self.doubleSpinBox_10.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.lineEdit_7.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), QCoreApplication.translate("MainWindow", u"D\u00f6viz Pariteleri", None))
        self.comboBox_17.setItemText(0, QCoreApplication.translate("MainWindow", u"T\u00fcm\u00fc", None))
        self.comboBox_17.setItemText(1, QCoreApplication.translate("MainWindow", u"K\u00fcresel Borsalar ", None))
        self.comboBox_17.setItemText(2, QCoreApplication.translate("MainWindow", u"Kripto", None))
        self.comboBox_17.setItemText(3, QCoreApplication.translate("MainWindow", u"Emtialar", None))
        self.comboBox_17.setItemText(4, QCoreApplication.translate("MainWindow", u"D\u00f6viz Pariteleri", None))
        self.comboBox_17.setItemText(5, "")

        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Ara", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Haberler", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Yorum Ekle", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("MainWindow", u"Yorumlar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QCoreApplication.translate("MainWindow", u"Sohbet", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Not Ekle", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_16), QCoreApplication.translate("MainWindow", u"Notlar\u0131m", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"G\u00f6r\u00fcn\u00fcm ve Tema", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Dil ve B\u00f6lge", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Bildirim ve Alarm", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Veri ve Ba\u011flant\u0131", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Hesap/Profil/Oturum ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_20), QCoreApplication.translate("MainWindow", u"Ayarlar", None))
        self.menuD_a_Aktar.setTitle(QCoreApplication.translate("MainWindow", u"D\u0131\u015fa Aktar", None))
        self.menuG_r_n_m.setTitle(QCoreApplication.translate("MainWindow", u"G\u00f6r\u00fcn\u00fcm", None))
        self.menuDil.setTitle(QCoreApplication.translate("MainWindow", u"Dil", None))
    # retranslateUi

