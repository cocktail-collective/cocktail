__all__ = ["DatabaseView"]

from PySide6 import QtCore, QtWidgets
from cocktail.ui.logging import LogView


class DatabaseView(QtWidgets.QWidget):
    updateClicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_button = QtWidgets.QPushButton("Update")
        self.progress_bar = QtWidgets.QProgressBar()
        self.log_view = LogView()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.update_button, 1)
        layout.addWidget(self.progress_bar, 1)
        layout.addWidget(self.log_view, 100)

        self.update_button.clicked.connect(self.updateClicked)

    def setProgress(self, progress, total):
        self.progress_bar.setValue(progress)
        self.progress_bar.setMaximum(total)

    def setProgressText(self, text):
        self.progress_bar.setFormat(text)
