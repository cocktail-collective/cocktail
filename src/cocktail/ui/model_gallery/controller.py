__all__ = ["ModelGalleryController"]

from PySide6 import QtCore, QtGui, QtWidgets, QtSql

from cocktail.ui.model_gallery.view import ModelGalleryView
from cocktail.ui.model_gallery.model import ModelGalleryProxyModel
from cocktail.core.database import data_classes


class ModelGalleryController(QtCore.QObject):
    modelDataChanged = QtCore.Signal(data_classes.Model)
    requestDownloadModel = QtCore.Signal(data_classes.Model)

    def __init__(self, connection, view=None, parent=None):
        super().__init__(parent)
        self.db_connection: QtSql.QSqlDatabase = connection
        self.base_model = QtSql.QSqlQueryModel()
        self.proxy_model = ModelGalleryProxyModel()
        self.proxy_model.setSourceModel(self.base_model)

        self.view = view or ModelGalleryView()
        self.view.setModel(self.proxy_model)

        self.view.modelIndexChanged.connect(self.onModelIndexChanged)
        self.view.contextMenuRequested.connect(self.onContextMenuRequested)
        self.update()

    def update(self):
        self.setQuery("SELECT * FROM model")

    def onContextMenuRequested(self, index):
        record = self.base_model.record(index.row())
        model_data = data_classes.Model.from_record(record)

        menu = QtWidgets.QMenu(self.view)
        menu.addAction("Download")

        action = menu.exec_(QtGui.QCursor.pos())
        if action:
            if action.text() == "Download":
                self.requestDownloadModel.emit(model_data)

    def onModelIndexChanged(self, proxy_index):
        index = self.proxy_model.mapToSource(proxy_index)
        record = self.base_model.record(index.row())
        model_data = data_classes.Model.from_record(record)
        self.modelDataChanged.emit(model_data)

    def setQuery(self, text):
        query = QtSql.QSqlQuery(self.db_connection)
        query.prepare(text)
        query.exec()
        self.base_model.setQuery(query)


if __name__ == "__main__":
    from cocktail.core import database

    app = QtWidgets.QApplication([])
    connection = database.get_connection()
    print(connection.tables())
    controller = ModelGalleryController(connection)
    controller.view.show()

    app.exec()
