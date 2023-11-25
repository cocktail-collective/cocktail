__all__ = ["ImageGalleryProxyModel"]
from PySide6 import QtCore

from cocktail.core.providers import ImageProviderProxyModel


class ImageGalleryProxyModel(ImageProviderProxyModel):
    def getUrl(self, index: QtCore.QModelIndex, role):
        record = self.sourceModel().record(index.row())
        return record.value("url")

    def getBlurHash(self, index, role):
        record = self.sourceModel().record(index.row())
        value = record.value("blur_hash")
        return value
