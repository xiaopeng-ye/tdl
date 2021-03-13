from PyQt5 import QtWidgets
from gui.window import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
