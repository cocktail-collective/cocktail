import os
from PySide6 import QtCore, QtWidgets, QtGui, QtSql, QtNetwork
from cocktail import resources

from cocktail.ui.settings.view import DirectoryPicker


class CocktailSplashScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._image_label = QtWidgets.QLabel()
        self._image_label.setPixmap(resources.pixmap("splash.png"))
        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setProperty("class", "splash-screen-progress-bar")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._image_label)
        layout.addWidget(self._progress_bar)

    def setProgress(self, current, total):
        self._progress_bar.setValue(current)
        self._progress_bar.setMaximum(total)

    def setText(self, text: str):
        self._progress_bar.setFormat(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    # splash = CocktailSplashScreen()
    # splash.show()
    wizard = SetupWizard()
    wizard.show()
    app.exec()
