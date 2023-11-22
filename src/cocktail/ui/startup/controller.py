import os
import io
import json
import zipfile
import platformdirs
from PySide6 import QtCore, QtNetwork
from cocktail.ui.startup.view import CocktailSplashScreen


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

    api_url = "https://api.github.com/repos/cocktail-collective/cocktail/releases"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = CocktailSplashScreen()
        self.cache_dir = platformdirs.user_cache_dir("cocktail", "cocktail")
        self.network_manager = QtNetwork.QNetworkAccessManager()

        self.get_releases_step = DownloadStep(self.network_manager)
        self.download_db_step = DownloadStep(self.network_manager)
        self.unzip_db_step = UnZipStep()

        # move the unzip step to a thread so it doesn't block the ui.
        self.unzip_thread = QtCore.QThread()
        self.unzip_db_step.moveToThread(self.unzip_thread)

        self.get_releases_step.progress.connect(self.view.setProgress)
        self.download_db_step.progress.connect(self.view.setProgress)
        self.unzip_db_step.progress.connect(self.view.setProgress)

        self.get_releases_step.complete.connect(self.onReleasesReady)
        self.download_db_step.complete.connect(self.onZipDownloaded)
        self.unzip_db_step.complete.connect(self.onCompleted)

    def start(self):
        """
        begin the startup process.
        """
        db_path = os.path.join(self.cache_dir, "cocktail.sqlite3")
        if os.path.exists(db_path):
            self.onCompleted()
            return

        self.view.show()
        self.view.setText("Getting database...")
        self.view.setProgress(0, 0)
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

        self.view.setText("Downloading database...")
        self.view.setProgress(0, 0)
        self.download_db_step.download(url)

    def onZipDownloaded(self, reply: QtNetwork.QNetworkReply):
        """
        after downloading the database, we need to extract it.
        """
        self.view.setText("Extracting database...")
        self.view.setProgress(0, 0)
        self.unzip_db_step.extract(reply, self.cache_dir)

    def onCompleted(self):
        """
        cleanup and signal completion.
        """
        self.unzip_thread.quit()
        self.view.close()
        self.complete.emit()


if __name__ == "__main__":
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication()

    def onCompleted():
        print("qitting")
        app.closeAllWindows()
        app.quit()

    controller = StartupController()
    controller.complete.connect(onCompleted)

    controller.start()

    app.exec()
