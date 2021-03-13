from PyQt5.QtWidgets import QFileDialog, QMessageBox

from parse import JSParser
from gui.window_ui import *

route = ''


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Botones
        self.BBuscar.clicked.connect(self.openFileNameDialog)
        self.BCancelar.clicked.connect(self.close)
        self.BAceptar.clicked.connect(self.save)

        # Guardar
        # self.BOk.clicked.connect(self.saveFileDialog)

        # parser
        self.parser = JSParser()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(self, "Seleccione el código fuente", "",
                                              "All Files (*);;JavaScript Files (*.js)", options=options)
        if file:
            self.textEdit.setPlainText(file)
            global route
            route = file
        else:
            self.textEdit.setPlainText('')

    def save(self):
        ruta = self.textEdit.toPlainText()
        if ruta == '':
            QMessageBox.about(self, "Alert", 'La ruta es vacía')
        else:
            try:
                self.parser.parse(ruta)
                QMessageBox.about(self, "Info", 'Correcto')
            except FileNotFoundError as fe:
                QMessageBox.about(self, "Alert", f'No existe el fichero {fe.filename}')
            except Exception as e:
                QMessageBox.about(self, "Alert", f'Error encontrado\n{e}')

    # def openFileNamesDialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
    #                                             "All Files (*);;Python Files (*.py)", options=options)
    #     if files:
    #         print(files)

    # def saveFileDialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
    #                                               "All Files (*);;Text Files (*.txt)", options=options)
    #     if fileName:
    #         print(fileName)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
