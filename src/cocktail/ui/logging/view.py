__all__ = ["LogView"]

from PySide6 import QtCore, QtWidgets, QtGui


class LogView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setUniformItemSizes(True)
