from PySide6 import QtWidgets, QtCore, QtGui
from cocktail.ui.model_gallery.model import ModelGalleryProxyModel
from cocktail.ui.model_info.view import CreatorInfoView
import cocktail.resources


class InfoLabel(QtWidgets.QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setProperty("class", "model-info-label")


class ItemRenderWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._image = QtGui.QImage()
        self.selected = False

        self.model_name_label = InfoLabel("name")
        self.model_type_label = InfoLabel("type")

        info_layout = QtWidgets.QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(self.model_type_label)
        info_layout.insertStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addStretch(1)
        layout.addLayout(info_layout)
        layout.addWidget(self.model_name_label)

    def resize(self, size):
        super().resize(size)
        margin = size.width() * 0.025
        self.layout().setContentsMargins(margin * 2, margin * 2, margin * 2, margin * 2)

    def setModelName(self, name):
        self.model_name_label.setText(name)

    def setModelType(self, type):
        self.model_type_label.setText(type)

    def setImage(self, image):
        self._image = image

    def getImageAspectRatio(self, image):
        return image.width() / image.height()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.palette().color(QtGui.QPalette.ColorRole.Dark))

        margin = self.rect().width() * 0.025

        draw_rect = self.rect().adjusted(margin, margin, -margin, -margin)

        clip_path = QtGui.QPainterPath()
        clip_path.addRoundedRect(draw_rect, margin, margin)

        painter.setClipPath(clip_path)

        if self._image and not self._image.isNull():
            height = self.height()
            width = height * self.getImageAspectRatio(self._image)

            if width < self.width():
                width = self.width()
                height = width / self.getImageAspectRatio(self._image)

            target_size = QtCore.QSize(width, height)

            scaled_image = self._image.scaled(
                target_size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            image_rect = scaled_image.rect()
            image_rect.moveCenter(draw_rect.center())
            image_rect.moveTop(draw_rect.top())

            painter.drawImage(image_rect, scaled_image)

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 128))

        if self.selected:
            cg = self.palette().ColorGroup.Active
            cr = self.palette().ColorRole.Accent
        else:
            cg = self.palette().ColorGroup.Normal
            cr = self.palette().ColorRole.Shadow

        color = self.palette().color(cg, cr)
        pen = QtGui.QPen(color, 4)
        painter.setBrush(QtGui.Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawRoundedRect(draw_rect, margin, margin)

        painter.end()
        super().paintEvent(e)


class ModelGalleryItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_size = QtCore.QSize(450, 650)
        self._widget = ItemRenderWidget()
        self._error_image = cocktail.resources.icon("error.png").pixmap(512, 512)

    def setItemSize(self, size):
        self._item_size = size
        self._widget.resize(size)

    def sizeHint(self, *_):
        return self._item_size

    def paint(self, painter, option, index):
        self._widget.setModelName(index.data(ModelGalleryProxyModel.NameRole))
        self._widget.setModelType(index.data(ModelGalleryProxyModel.TypeRole))
        self._widget.setImage(index.data(QtCore.Qt.ItemDataRole.DecorationRole))
        self._widget.selected = bool(option.state & QtWidgets.QStyle.State_Selected)
        self._widget.setGeometry(option.rect)

        painter.save()
        try:
            pixmap = QtGui.QPixmap(self._widget.size())
            self._widget.render(pixmap)
            painter.drawPixmap(option.rect, pixmap)
        finally:
            painter.restore()
