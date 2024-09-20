__all__ = ["ImageGalleryView", "ImageWidget"]

import typing
import PySide6.QtCore
import qtawesome
from PySide6 import QtCore, QtGui, QtWidgets


class ImageWidget(QtWidgets.QWidget):
    """
    A widget that displays an image.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._image: QtGui.QImage = None
        self._idle_icon = qtawesome.icon("mdi.image-off").pixmap(128, 128).toImage()
        self._placeholder = qtawesome.icon("fa.hourglass").pixmap(128, 128).toImage()

        self._animation = QtCore.QVariantAnimation()
        self._animation.setStartValue(0)
        self._animation.setEndValue(180)
        self._animation.setDuration(1000)
        self._animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        self._animation.setLoopCount(-1)
        self._animation.valueChanged.connect(lambda _: self.update())

        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
        )

        self._mask = None
        self._border_pen = 0

    @QtCore.Property(QtGui.QPen)
    def borderPen(self):
        return self._border_pen

    @borderPen.setter
    def borderPen(self, pen):
        self._border_pen = pen
        self.update()

    def setMask(self, mask: QtGui.QPainterPath):
        self._mask = mask
        self.update()

    def setImage(self, image: QtGui.QImage):
        if image is None:
            self._image = self._idle_icon
        else:
            self._image = image

        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        if self._mask:
            painter.setClipPath(self._mask)

        if not self._image:
            image = self._placeholder
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(self._animation.currentValue())
            painter.translate(-self.width() / 2, -self.height() / 2)

        else:
            image = self._image

        if image.width() > self.width() or image.height() > self.height():
            image = image.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )

        image_rect = QtCore.QRect(0, 0, image.width(), image.height())
        image_rect.moveCenter(self.rect().center())
        painter.drawImage(image_rect, image)

        painter.setClipping(False)

        if self._border_pen:
            painter.setPen(self._border_pen)
            if self._mask:
                painter.drawPath(self._mask)
            else:
                painter.drawRect(self.rect())


class NavigationView(QtWidgets.QWidget):
    indexChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setProperty("class", "gallery-nav-view")
        self._buttons: typing.List[QtWidgets.QPushButton] = []
        self.button_layout = QtWidgets.QHBoxLayout()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addStretch()
        layout.addLayout(self.button_layout)
        layout.addStretch()

        self.setItemCount(1)

    def setItemCount(self, count: int):
        for button in self._buttons:
            self.button_layout.removeWidget(button)
            button.deleteLater()

        self._buttons.clear()

        for index in range(count):
            button = QtWidgets.QPushButton()
            button.setProperty("class", "gallery-nav-button")
            button.setCheckable(True)
            button.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
            button.setAutoExclusive(True)
            self.button_layout.addWidget(button)
            self._buttons.append(button)

            def callback(b=button, i=index):
                self.indexChanged.emit(i)

            button.clicked.connect(callback)

        if self._buttons:
            self._buttons[0].setChecked(True)

    def setIndex(self, index: int):
        self._buttons[index].setChecked(True)


class ImageGalleryView(QtWidgets.QWidget):
    """
    A widget that displays a Carousel of images with forward/back buttons
    """

    indexChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._border_radius = 0
        self._row = 0
        self._model: QtCore.QAbstractItemModel = None

        self.image_widget = ImageWidget()
        self.navigation_group = NavigationView()

        column_layout = QtWidgets.QHBoxLayout()
        column_layout.addWidget(self.image_widget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(column_layout)
        layout.addWidget(self.navigation_group)

        self.navigation_group.indexChanged.connect(self.onNavigationIndexChanged)

    def onNavigationIndexChanged(self, index):
        self._row = index
        self.updateImage()

    def setModel(self, model):
        if self._model:
            self._model.dataChanged.disconnect(self.onModelDataChanged)
            self._model.modelReset.disconnect(self.onModelReset)

        model.dataChanged.connect(self.onModelDataChanged)
        model.modelReset.connect(self.onModelReset)

        self._model = model
        self._row = 0
        self.navigation_group.setItemCount(self._model.rowCount())

        self.updateImage()

    def updateImage(self):
        index = self._model.index(self._row, 0)

        if not index.isValid():
            self.image_widget.setImage(None)
            return

        self.indexChanged.emit(index)

        image = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
        self.image_widget.setImage(image)

    def onModelDataChanged(self, topLeft, bottomRight, roles):
        if topLeft.row() <= self._row <= bottomRight.row():
            self.updateImage()

    def onModelReset(self):
        self.navigation_group.setItemCount(self._model.rowCount())
        self._row = 0
        self.updateImage()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self.borderRadius:
            mask = QtGui.QPainterPath()
            mask.addRoundedRect(self.rect(), self.borderRadius, self.borderRadius)
            self.setMask(QtGui.QRegion(mask.toFillPolygon().toPolygon()))

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        color_role = self.palette().ColorRole.Dark
        color_group = self.palette().currentColorGroup()
        color = self.palette().color(color_group, color_role)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(self.rect())

    @QtCore.Property(int)
    def borderRadius(self):
        return self._border_radius

    @borderRadius.setter
    def borderRadius(self, radius):
        self._border_radius = radius
        self.update()
