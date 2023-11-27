__all__ = ["ModelInfoController"]

from PySide6 import QtCore, QtGui, QtWidgets, QtSql
from cocktail.ui.model_info.view import CreatorInfoView, VersionInfoView, ModelInfoView
from cocktail.core.providers import ImageProvider
from cocktail.core.database import data_classes
from cocktail.ui.image_gallery import ImageGalleryController


class CreatorInfoController(QtCore.QObject):
    def __init__(self, image_provider, view=None, parent=None):
        super().__init__(parent=parent)
        self.image_provider: ImageProvider = image_provider
        self.view = view or CreatorInfoView()

    def setImageUrl(self, url: str):
        self.image_provider.queueImageDownload(url, self.setImage)

    def setImage(self, image: QtGui.QImage):
        self.view.setImage(image)

    def setName(self, name: str):
        self.view.setName(name)


class VersionInfoController(QtCore.QObject):
    versionIdChanged = QtCore.Signal(int)
    requestDownload = QtCore.Signal(
        data_classes.Model, data_classes.ModelVersion, data_classes.ModelFile
    )

    def __init__(self, connection, view=None, parent=None):
        super().__init__(parent=parent)
        self.connection = connection

        self._model: data_classes.Model = None
        self._model_version: data_classes.ModelVersion = None
        self._model_file: data_classes.ModelFile = None

        self.version_model = QtSql.QSqlQueryModel()
        self.file_model = QtSql.QSqlQueryModel()

        self.view = view or VersionInfoView()
        self.view.setVersionModel(self.version_model)
        self.view.setFileModel(self.file_model)

        self.view.versionIndexChanged.connect(self.onVersionIndexChanged)
        self.view.fileIndexChanged.connect(self.onFileIndexChanged)
        self.view.downloadClicked.connect(self.onDownloadClicked)

    def setModel(self, model: data_classes.Model):
        self._model = model

        query = QtSql.QSqlQuery(self.connection)

        fields = [f for f in data_classes.ModelVersion._fields if f not in ["name"]]

        fields.insert(0, "name")

        fields_str = ", ".join(fields)

        query.prepare(
            f"""
            SELECT {fields_str} FROM model_version WHERE model_id = :model_id
            ORDER BY id DESC
            """
        )

        query.bindValue(":model_id", model.id)

        if not query.exec():
            raise RuntimeError(
                f"Failed to execute query: {query.lastError().text()}, {query.lastQuery()}"
            )

        self.version_model.setQuery(query)

    def setModelVersion(self, model_version: data_classes.ModelVersion):
        self._model_version = model_version

        query = QtSql.QSqlQuery(self.connection)
        query.prepare(
            """
            SELECT * FROM model_file WHERE model_version_id = :id
            AND safe = 1
            ORDER BY is_primary DESC
            """
        )
        query.bindValue(":id", model_version.id)

        if not query.exec():
            raise RuntimeError(
                f"Failed to execute query: {query.lastError().text()}, {query.lastQuery()}"
            )

        self.file_model.setQuery(query)

    def onVersionIndexChanged(self, index: QtCore.QModelIndex):
        record = self.version_model.record(index.row())
        model_version = data_classes.ModelVersion.from_record(record)

        self.setModelVersion(model_version)
        self.versionIdChanged.emit(model_version.id)

    def onFileIndexChanged(self, index: QtCore.QModelIndex):
        record = self.file_model.record(index.row())
        self._model_file = model_file = data_classes.ModelFile.from_record(record)

        self.view.file_info.setFileSize(model_file.size)
        self.view.file_info.setDatatype(model_file.datatype)

    def onImageIndexChanged(self, index: QtCore.QModelIndex):
        record = self.image_model.record(index.row())
        image = data_classes.ModelImage.from_record(record)

        self.view.image_info.setResolution(image.resolution)
        self.view.image_info.setFormat(image.format)

    def onDownloadClicked(self):
        self.requestDownload.emit(self._model, self._model_version, self._model_file)


class ModelInfoController(QtCore.QObject):
    """
    This class is responsible for populating the ModelInfoView when a model is picked.
    """

    def __init__(
        self,
        connection: QtSql.QSqlDatabase,
        image_provider,
        view=None,
        parent=None,
    ):
        super().__init__(parent)
        self.connection = connection
        self.view = view or ModelInfoView()
        self.image_provider = image_provider

        self.creator_controller = CreatorInfoController(
            view=self.view.header_view.creator_info, image_provider=self.image_provider
        )

        self.version_info_controller = VersionInfoController(
            self.connection, view=self.view.version_info
        )

        self.image_gallery_controller = ImageGalleryController(
            self.connection,
            self.image_provider,
            view=self.view.version_info.image_gallery,
        )
        self.image_gallery_controller.imageChanged.connect(
            self.view.version_info.setImageData
        )

        self.version_info_controller.versionIdChanged.connect(
            self.image_gallery_controller.setVersionId
        )

    def setModelData(self, model: data_classes.Model):
        self.view.requestFocus.emit(self.view)
        self.view.setModelData(model)
        self.view.setEnabled(True)

        self.creator_controller.setImageUrl(model.creator_image)
        self.creator_controller.setName(model.creator_name)
        self.version_info_controller.setModel(model)


if __name__ == "__main__":
    import sys
    from cocktail.core.database import get_connection
    from cocktail.core.providers import ImageProvider

    app = QtWidgets.QApplication(sys.argv)
    db = get_connection("/home/rob/dev/browser/cocktail.sqlite3")
    print(db.tables())

    query = QtSql.QSqlQuery(db)
    query.prepare(
        """
        SELECT *
        FROM model
        WHERE id = 34553
        """
    )

    if not query.exec():
        raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")

    query.next()
    model = data_classes.Model.from_record(query.record())
    image_provider = ImageProvider()
    controller = ModelInfoController(db, image_provider)
    controller.view.show()
    controller.setModelData(model)

    sys.exit(app.exec())
