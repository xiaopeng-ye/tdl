# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(770, 180)
        MainWindow.setMinimumSize(QtCore.QSize(770, 180))
        MainWindow.setMaximumSize(QtCore.QSize(770, 180))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../../../../Pictures/Clase/PDL/0.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 771, 181))
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.frame.setFont(font)
        self.frame.setToolTip("")
        self.frame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame.setAutoFillBackground(False)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.QRuta = QtWidgets.QLabel(self.frame)
        self.QRuta.setGeometry(QtCore.QRect(20, 20, 151, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.QRuta.setFont(font)
        self.QRuta.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QRuta.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.QRuta.setFrameShadow(QtWidgets.QFrame.Plain)
        self.QRuta.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.QRuta.setObjectName("QRuta")
        self.BAceptar = QtWidgets.QPushButton(self.frame)
        self.BAceptar.setGeometry(QtCore.QRect(520, 130, 111, 31))
        self.BAceptar.setObjectName("BAceptar")
        self.BBuscar = QtWidgets.QPushButton(self.frame)
        self.BBuscar.setGeometry(QtCore.QRect(670, 70, 90, 31))
        self.BBuscar.setObjectName("BBuscar")
        self.BCancelar = QtWidgets.QPushButton(self.frame)
        self.BCancelar.setGeometry(QtCore.QRect(650, 130, 111, 31))
        self.BCancelar.setObjectName("BCancelar")
        self.textEdit = QtWidgets.QPlainTextEdit(self.frame)
        self.textEdit.setGeometry(QtCore.QRect(20, 70, 640, 31))
        self.textEdit.setMinimumSize(QtCore.QSize(640, 10))
        self.textEdit.setMaximumSize(QtCore.QSize(640, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Procesadores de Lenguajes"))
        self.QRuta.setText(_translate("MainWindow", "Ruta del código:"))
        self.BAceptar.setText(_translate("MainWindow", "Aceptar"))
        self.BBuscar.setText(_translate("MainWindow", "Buscar..."))
        self.BCancelar.setText(_translate("MainWindow", "Cancelar"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Escriba o busque una ruta"))

