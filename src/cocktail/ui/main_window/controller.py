__all__ = ["MainWindowController"]
from PySide6 import QtCore, QtWidgets
from cocktail.ui.main_window.view import MainWindow
from cocktail.ui.model_gallery import ModelGalleryController
from cocktail.ui.model_info import ModelInfoController
from cocktail.core.providers import ImageProvider
from cocktail.ui.download import ModelDownloadController
from cocktail.ui.database import DatabaseController
from cocktail.ui.search import SearchController
from cocktail.ui.settings import SettingsController

from cocktail.core.database import get_connection


class MainWindowController(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.connection = get_connection()
        self.image_provider = ImageProvider()

        self.view = MainWindow()
        self.download_controller = ModelDownloadController(
            self.connection, self.view.central_widget.model_download_view
        )
        self.model_gallery_controller = ModelGalleryController(
            self.connection, self.view.central_widget.model_gallery_view
        )

        self.model_info_controller = ModelInfoController(
            self.connection,
            self.image_provider,
            self.view.central_widget.model_info_view,
        )
        self.model_info_controller.version_info_controller.requestDownload.connect(
            self.download_controller.downloadModelFile
        )

        self.model_gallery_controller.modelDataChanged.connect(
            self.model_info_controller.setModelData
        )
        self.model_gallery_controller.requestDownloadModel.connect(
            self.download_controller.downloadModel
        )


        self.database_controller = DatabaseController(
            self.connection, self.view.central_widget.database_view
        )
        self.search_controller = SearchController(
            self.connection,
            self.model_gallery_controller.base_model,
            self.view.central_widget.search_view,
        )
        self.database_controller.dataUpdated.connect(self.search_controller.update)
        self.database_controller.dataUpdated.connect(self.search_controller.onSearchChanged)
        self.database_controller.updateMessage.connect(self.view.statusBar().showMessage)

        self.settings_controller = SettingsController(
            self.connection, self.view.central_widget.settings_view
        )

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    app = QtWidgets.QApplication()
    controller = MainWindowController()
    controller.view.show()
    app.exec()