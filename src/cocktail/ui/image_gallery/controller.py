__all__ = ["ImageGalleryController"]

from PySide6 import QtCore, QtSql
from cocktail.ui.image_gallery.view import ImageGalleryView
from cocktail.ui.image_gallery.model import ImageGalleryProxyModel
from cocktail.core.database import data_classes


class ImageGalleryController(QtCore.QObject):
    imageChanged = QtCore.Signal(data_classes.ModelImage)

    def __init__(self, connection, image_provider, view=None, parent=None):
        super().__init__(parent=parent)
        self.connection = connection
        self.model = QtSql.QSqlQueryModel()
        self.proxy_model = ImageGalleryProxyModel(image_provider)
        self.proxy_model.setSourceModel(self.model)
        self.view = view or ImageGalleryView()
        self.view.setModel(self.proxy_model)

        self.view.indexChanged.connect(self.onIndexChanged)

    def onIndexChanged(self, index: QtCore.QModelIndex):
        index = self.proxy_model.mapToSource(index)
        record = self.model.record(index.row())
        image = data_classes.ModelImage.from_record(record)
        self.imageChanged.emit(image)

    def setVersionId(self, version_id: int):
        query = QtSql.QSqlQuery(self.connection)
        query.prepare(
            """
            SELECT * FROM model_image WHERE model_version_id = :model_version_id
            ORDER BY id DESC
            """
        )

        query.bindValue(":model_version_id", version_id)

        if not query.exec():
            raise RuntimeError(
                f"Failed to execute query: {query.lastError().text()}, {query.lastQuery()}"
            )

        self.model.setQuery(query)
