__all__ = ["ImageProvider", "ImageProviderProxyModel"]
from PySide6 import QtCore, QtGui, QtNetwork
from functools import partial

from cocktail.core.http import NetworkManager
from cocktail.core.cache import FixedLengthMapping


class ImageProviderProxyModel(QtCore.QIdentityProxyModel):
    """
    A Proxy model which provides images for an underlying model.

    This class must be subclassed and the getUrl method must be implemented.
    """

    ImageRoles = [QtCore.Qt.ItemDataRole.DecorationRole]

    def __init__(self, image_provider=None, parent=None):
        super().__init__(parent)
        self.image_provider: ImageProvider = image_provider or ImageProvider()

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        if role in self.ImageRoles:
            return self.getImage(index, role)

        return super().data(index, role)

    def getImage(self, index, role=QtCore.Qt.ItemDataRole.DecorationRole):
        url = self.getUrl(index, role)

        if self.image_provider.hasImage(url):
            return self.image_provider.getImage(url)

        callback = partial(self.onImageDownloaded, index=index, url=url)

        self.image_provider.queueImageDownload(url, callback)

        return None

    def getUrl(self, index: QtCore.QModelIndex, role):
        raise NotImplementedError

    def onImageDownloaded(self, image, url, index):
        self.dataChanged.emit(index, index, [QtCore.Qt.DecorationRole])


class ImageProvider(QtCore.QObject):
    """
    A proxy model which displays images from a column containing URLs.
    """

    def __init__(self, cache=None, parent=None):
        super().__init__(parent)
        self.network_manager = NetworkManager()
        self._cache = cache or FixedLengthMapping(max_entries=100)

    def hasImage(self, url):
        return url in self._cache

    def getImage(self, url):
        return self._cache[url]

    def queueImageDownload(self, url, callback):
        if url in self._cache:
            callback(self._cache[url])
            return

        self._cache[url] = None  # prevent duplicate requests

        reply = self.network_manager.get(url)
        callback = partial(self.onImageDownloaded, reply=reply, callback=callback)

        reply.finished.connect(callback)

        return None

    def onImageDownloaded(self, reply: QtNetwork.QNetworkReply, callback):
        if reply.error() != QtNetwork.QNetworkReply.NoError:
            self._cache[reply.url().toString()] = None
            callback(None)
            return

        image = QtGui.QImage.fromData(reply.readAll())

        self._cache[reply.url().toString()] = image

        callback(image)
