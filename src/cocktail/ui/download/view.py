from typing import Optional
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
import PySide6.QtGui
import qtawesome


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path_edit = QtWidgets.QLineEdit()
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.clicked.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.path_edit)
        self.layout.addWidget(self.download_button)


class ModelDownloadItemWidget(QtWidgets.QWidget):
    cancled = QtCore.Signal()
    requestOpenDirectory = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.file_icon = QtWidgets.QPushButton()
        self.file_icon.setIcon(qtawesome.icon("fa5s.file"))
        self.file_icon.setFlat(True)
        self.file_icon.setIconSize(QtCore.QSize(32, 32))

        self.name = QtWidgets.QLabel("Name")
        self.progress_bar = QtWidgets.QProgressBar()
        self.cancel_button = QtWidgets.QPushButton()
        self.cancel_button.setIcon(qtawesome.icon("fa5s.times-circle"))
        self.cancel_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        self.cancel_button.setFlat(True)
        self.cancel_button.setIconSize(QtCore.QSize(32, 32))

        self.open_directory_button = QtWidgets.QPushButton()
        self.open_directory_button.setIcon(qtawesome.icon("fa5s.folder-open"))
        self.open_directory_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        self.open_directory_button.setFlat(True)
        self.open_directory_button.setIconSize(QtCore.QSize(32, 32))
        self.open_directory_button.hide()

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addWidget(self.name)
        info_layout.addWidget(self.progress_bar)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.file_icon)
        self.layout.addLayout(info_layout)
        self.layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.open_directory_button)

        self.open_directory_button.clicked.connect(self.requestOpenDirectory)
        self.cancel_button.clicked.connect(self.onCanceled)

    def onCanceled(self):
        self.setDisabled(True)
        self.cancled.emit()

    def setProgress(self, current, total):
        try:
            progress = current / total * 100
        except ZeroDivisionError:
            progress = 0

        self.progress_bar.setValue(progress)
        if progress == 100:
            self.cancel_button.setDisabled(True)
            self.cancel_button.setText("Done")
            self.cancel_button.hide()
            self.open_directory_button.show()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        return super().resizeEvent(event)


class ModelDownloadView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items_layout = QtWidgets.QVBoxLayout()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.items_layout)
        main_layout.addStretch(100)

    def addDownload(self, name, network_reply: QtNetwork.QNetworkReply):
        widget = ModelDownloadItemWidget()
        widget.name.setText(name)
        widget.cancled.connect(network_reply.abort)
        network_reply.downloadProgress.connect(widget.setProgress)
        self.items_layout.addWidget(widget)
        return widget


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = ModelDownloadView()
    manager = QtNetwork.QNetworkAccessManager()
    url = "https://civitai.com/api/download/models/124626"
    reply = manager.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
    view.addDownload("Test", reply)
    view.show()
    sys.exit(app.exec_())
