__all__ = ["ModelInfoView", "CreatorInfoView", "ModelInfoHeader"]
from PySide6 import QtCore, QtWidgets, QtGui
from cocktail.ui.image_gallery import ImageWidget, ImageGalleryView
from cocktail.core.database import data_classes
from cocktail import util
import qtawesome


class FileInfo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_label = QtWidgets.QLabel()
        self.datatype_label = QtWidgets.QLabel()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("Size:"))
        layout.addWidget(self.size_label)
        layout.addWidget(QtWidgets.QLabel("Type:"))

        layout.addWidget(self.datatype_label)

    def setFileSize(self, size: float):
        self.size_label.setText(util.format_bytes(size * 1024))

    def setDatatype(self, datatype: str):
        self.datatype_label.setText(datatype)


class CreatorInfoView(QtWidgets.QWidget):
    """
    This widget displays the author's name and image
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "creator-info")
        self.creator_image = ImageWidget()
        self.creator_image.setProperty("class", "creator-image")
        self.creator_image.setFixedSize(64, 64)
        self.creator_image.borderPen = QtGui.QPen(QtGui.QColor(255, 255, 255, 64), 2)
        self.creator_name = QtWidgets.QLabel("Name")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.creator_image)
        layout.addWidget(self.creator_name)

    def setImage(self, image: QtGui.QImage):
        mask = QtGui.QPainterPath()
        mask.addEllipse(2, 2, 60, 60)
        self.creator_image.setMask(mask)
        self.creator_image.setImage(image)

    def setName(self, name: str):
        self.creator_name.setText(name)


class ModelInfoHeader(QtWidgets.QWidget):
    """
    This widget displays the model name and author information
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.model_name_label = QtWidgets.QLabel()
        self.model_name_label.setWordWrap(True)
        self.model_name_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.model_name_label.setProperty("class", "model-name")
        self.creator_info = CreatorInfoView()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.model_name_label, 1, QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.creator_info, 0, QtCore.Qt.AlignmentFlag.AlignRight)


class VersionInfoView(QtWidgets.QWidget):
    downloadClicked = QtCore.Signal()
    versionIndexChanged = QtCore.Signal(QtCore.QModelIndex)
    fileIndexChanged = QtCore.Signal(QtCore.QModelIndex)
    imageIndexChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.version_combo = QtWidgets.QComboBox()
        self.version_combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.image_gallery = ImageGalleryView()
        self.file_combo = QtWidgets.QComboBox()
        self.file_info = FileInfo()
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.setIcon(qtawesome.icon("fa5s.download"))

        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow("Version", self.version_combo)
        layout.addWidget(self.image_gallery)
        layout.addRow("File", self.file_combo)
        layout.addWidget(self.file_info)
        layout.addWidget(self.download_button)

        self.version_combo.currentIndexChanged.connect(self.onVersionIndexChanged)
        self.file_combo.currentIndexChanged.connect(self.onFileIndexChanged)
        self.image_gallery.indexChanged.connect(self.imageIndexChanged)
        self.download_button.clicked.connect(self.downloadClicked)

    def onVersionIndexChanged(self, index: int):
        index = self.version_combo.model().index(index, 0)
        self.versionIndexChanged.emit(index)

    def onFileIndexChanged(self, index: int):
        index = self.file_combo.model().index(index, 0)
        self.fileIndexChanged.emit(index)

    def setVersionModel(self, model):
        self.version_combo.setModel(model)

    def setImageModel(self, model):
        self.image_gallery.setModel(model)

    def setFileModel(self, model):
        self.file_combo.setModel(model)


class ModelInfoView(QtWidgets.QWidget):
    """
    This widget displays the model name and author information
    """

    requestFocus = QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.header_view = ModelInfoHeader()
        self.version_info = VersionInfoView()
        self.description = QtWidgets.QTextBrowser()
        self.description.setReadOnly(True)
        self.description.setProperty("class", "model-description")
        self.description.setOpenExternalLinks(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header_view, 1)
        layout.addWidget(self.version_info, 100)
        layout.addWidget(self.description, 100)

    def setModelData(self, model: data_classes.Model):
        self.description.setText(model.description)
        self.header_view.model_name_label.setText(model.name)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    creator_image = QtGui.QImage(
        "/home/rob/Downloads/1de4c2db-54a0-4fed-994f-45604bbdf0bc.jpeg"
    )
    image_1 = QtGui.QImage("/home/rob/Downloads/preview_image.jpeg")
    image_2 = QtGui.QImage("/home/rob/Downloads/00064-3994041509.jpeg")

    view = ModelInfoView()
    view.show()
    view.header_view.model_name_label.setText("Model Name")
    view.header_view.creator_info.setName("Author Name")
    view.header_view.creator_info.setImage(creator_image)
    version_model = QtGui.QStandardItemModel()
    version_model.appendRow(QtGui.QStandardItem("Version 1"))
    version_model.appendRow(QtGui.QStandardItem("Version 2"))

    model = QtGui.QStandardItemModel()
    item1 = QtGui.QStandardItem()
    item2 = QtGui.QStandardItem()
    item1.setData(image_1, QtCore.Qt.DecorationRole)
    item2.setData(image_2, QtCore.Qt.DecorationRole)

    model.appendRow(item1)
    model.appendRow(item2)

    view.setImageModel(model)
    view.file_info.setStatus("safe")

    sys.exit(app.exec_())
