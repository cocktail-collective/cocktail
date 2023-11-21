__all__ = ["ModelGalleryView"]
import math
from PySide6 import QtCore, QtGui, QtWidgets, QtSql

from cocktail.ui.model_gallery.delegate import ModelGalleryItemDelegate


class ImageGalleryListView(QtWidgets.QListView):
    gridSizeChanged = QtCore.Signal(QtCore.QSize)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_delegate = ModelGalleryItemDelegate()

        self.setWrapping(True)
        self.setFlow(QtWidgets.QListView.Flow.LeftToRight)
        self.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.setGridSize(QtCore.QSize(450, 650))
        self.setItemDelegate(self._item_delegate)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.gridSizeChanged.connect(self._item_delegate.setItemSize)

        self._items_per_row = 5
        self._item_aspect_ratio = 1.5

    def setItemsPerRow(self, items_per_row):
        self._items_per_row = items_per_row
        self.setGridSize(self.calculateGridSize())
        self.doItemsLayout()

    def setGridSize(self, size: QtCore.QSize) -> None:
        super().setGridSize(size)
        self.gridSizeChanged.emit(size)

    def itemsPerRow(self):
        return self._items_per_row

    def calculateGridSize(self):
        width = math.floor(
            (
                self.viewport().width()
                - self.contentsMargins().left()
                - self.contentsMargins().right()
            )
            / self._items_per_row
        )
        width *= 0.99
        height = math.floor(width * self._item_aspect_ratio)
        return QtCore.QSize(width, height)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        size = self.calculateGridSize()
        self.setGridSize(size)
        self.verticalScrollBar().setSingleStep(size.height() // 5)

        return super().resizeEvent(e)


class ModelGalleryView(QtWidgets.QWidget):
    modelIndexChanged = QtCore.Signal(QtCore.QModelIndex)
    contextMenuRequested = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._list_view = ImageGalleryListView()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._list_view)

        self._list_view.clicked.connect(self.modelIndexChanged)
        self._list_view.customContextMenuRequested.connect(self.onContextMenuRequested)

    def onContextMenuRequested(self, pos):
        index = self._list_view.indexAt(pos)
        self.contextMenuRequested.emit(index)

    def setModel(self, model):
        self._list_view.setModel(model)
