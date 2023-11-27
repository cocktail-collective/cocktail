import os
import io
import json
import zipfile
import logging
from PySide6 import QtCore, QtNetwork
from cocktail.ui.startup.view import CocktailSplashScreen, SetupWizard
from cocktail.core.database import api as db_api


logger = logging.getLogger(__name__)


def get_db_url(data):
    # TODO: handle pagination
    for item in data:
        if item["prerelease"]:
            continue
        for asset in item["assets"]:
            if asset["name"] == "database.zip":
                return asset["browser_download_url"]


class DownloadStep(QtCore.QObject):
    """
    download a file from a url.
    """

    progress = QtCore.Signal(int, int)
    complete = QtCore.Signal(QtNetwork.QNetworkReply)

    def __init__(self, network_manager: QtNetwork.QNetworkAccessManager, parent=None):
        super().__init__(parent)
        self.network_manager = network_manager

    def download(self, url):
        request = QtNetwork.QNetworkRequest()
        request.setUrl(url)
        reply = self.network_manager.get(request)
        reply.downloadProgress.connect(self.onProgress)
        reply.finished.connect(self.onFinished)

    def onProgress(self, bytesReceived: int, bytesTotal: int):
        self.progress.emit(bytesReceived, bytesTotal)

    def onFinished(self):
        self.complete.emit(self.sender())


class UnZipStep(QtCore.QObject):
    """
    unzip a file into a directory.
    """

    progress = QtCore.Signal(int, int)
    complete = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.CHUNK_SIZE = 1024 * 1024

    def extract(self, reply: QtNetwork.QNetworkReply, destination: str):
        buffer = io.BytesIO(reply.readAll().data())

        with zipfile.ZipFile(buffer) as zip_file:
            total_size = sum(info.file_size for info in zip_file.infolist())
            current_size = 0
            for info in zip_file.infolist():
                with zip_file.open(info) as file, open(
                    os.path.join(destination, info.filename), "wb"
                ) as output_file:
                    while True:
                        chunk = file.read(self.CHUNK_SIZE)
                        if not chunk:
                            break

                        output_file.write(chunk)
                        current_size += len(chunk)
                        self.progress.emit(current_size, total_size)

        self.complete.emit()


class StartupController(QtCore.QObject):
    """
    This controller is responsible for the startup process of the application.

    - Check if the database exists.
    - If not, download it and extract it.
    - signal completion.
    """

    complete = QtCore.Signal()
    canceled = QtCore.Signal()

    api_url = "https://api.github.com/repos/cocktail-collective/cocktail/releases"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.splash = CocktailSplashScreen()
        self.wizard = SetupWizard()
        self.database_path = db_api.get_database_path()
        self.network_manager = QtNetwork.QNetworkAccessManager()

        self.get_releases_step = DownloadStep(self.network_manager)
        self.download_db_step = DownloadStep(self.network_manager)
        self.unzip_db_step = UnZipStep()

        # move the unzip step to a thread so it doesn't block the ui.
        self.unzip_thread = QtCore.QThread()
        self.unzip_db_step.moveToThread(self.unzip_thread)

        self.get_releases_step.progress.connect(self.splash.setProgress)
        self.download_db_step.progress.connect(self.splash.setProgress)
        self.unzip_db_step.progress.connect(self.splash.setProgress)

        self.get_releases_step.complete.connect(self.onReleasesReady)
        self.download_db_step.complete.connect(self.onZipDownloaded)
        self.unzip_db_step.complete.connect(self.onZipExtracted)
        self.wizard.rejected.connect(self.onCanceled)
        self.wizard.accepted.connect(self.onCompleted)

    def start(self):
        """
        begin the startup process.
        """
        logger.info("checking for database...")
        if os.path.exists(self.database_path):
            logger.info("checking database schema...")
            connection = db_api.get_connection(self.database_path)
            if db_api.get_schema_version(connection) >= db_api.CURRENT_SCHEMA_VERSION:
                logger.info("database schema is up to date.")
                self.onCompleted()
                return
            else:
                logger.info("database schema is out of date, downloading database.")
                connection.close()
                os.remove(self.database_path)
        else:
            logger.info("database not found, downloading database.")

        self.splash.show()
        self.splash.setText("Getting database...")
        self.splash.setProgress(0, 0)
        self.get_releases_step.download(self.api_url)

    def onReleasesReady(self, reply: QtNetwork.QNetworkReply):
        """
        after querying the releases api, we need to find the latest release with a database asset.
        """
        raw_data = reply.readAll().data().decode("utf-8")
        data = json.loads(raw_data)

        url = get_db_url(data)

        if url is None:
            return

        self.splash.setText("Downloading database...")
        self.splash.setProgress(0, 0)
        self.download_db_step.download(url)

    def onZipDownloaded(self, reply: QtNetwork.QNetworkReply):
        """
        after downloading the database, we need to extract it.
        """
        self.splash.setText("Extracting database...")
        self.splash.setProgress(0, 0)
        self.unzip_db_step.extract(reply, os.path.dirname(self.database_path))

    def onZipExtracted(self):
        """
        after extracting the database, we need to show the setup wizard.
        """
        self.splash.close()
        self.wizard.show()

    def onCompleted(self):
        """
        cleanup and signal completion.
        """
        self.unzip_thread.quit()
        self.splash.close()
        self.complete.emit()

    def onCanceled(self):
        """
        cleanup and signal completion.
        """
        self.unzip_thread.quit()
        self.splash.close()
        self.canceled.emit()


if __name__ == "__main__":
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication()

    def onCompleted():
        print("qitting")
        app.closeAllWindows()
        app.quit()

    def onCanceled():
        print("canceled")
        app.closeAllWindows()
        app.quit()

    controller = StartupController()
    controller.complete.connect(onCompleted)
    controller.canceled.connect(onCanceled)

    controller.start()

    app.exec()
