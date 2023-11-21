from PySide6 import QtCore, QtWidgets, QtGui


class LogModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.records)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.records[index.row()].getMessage()
        if role == QtCore.Qt.DecorationRole:
            return self.records[index.row()].getIcon()
        return None

    def addRecord(self, record):
        self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
        self.records.insert(0, record)
        self.endInsertRows()
