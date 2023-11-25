__all__ = ["ModelDataProvider"]
import logging

import json
from PySide6 import QtCore, QtGui, QtNetwork
from cocktail.core.database import data_classes

import queue as queue_api


logger = logging.getLogger(__name__)

API_URL = "https://civitai.com/api/v1"


class ModelDataProvider(QtCore.QObject):
    """
    A proxy model which displays images from a column containing URLs.
    """

    pageReady = QtCore.Signal()
    beginRequest = QtCore.Signal()
    progress = QtCore.Signal(int, int)
    endRequest = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QtNetwork.QNetworkAccessManager()
        self.queue = queue_api.Queue()
        self._busy = False
        self._retries = {}

    def requestModelData(self, period):
        if self._busy:
            return

        self._busy = True

        logger.debug(f"requesting model data for period: {period.value}")
        self._retries.clear()

        url = f"{API_URL}/models?period={period.value}&limit=20"
        self._requestPage(url)
        self.beginRequest.emit()

    def _requestPage(self, url):
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        request.setRawHeader(b"Accept", b"application/json")
        request.setRawHeader(b"Accept-Encoding", b"identity")

        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.onRequestFinished(reply))

    def onRequestFailed(self, reply: QtNetwork.QNetworkReply):
        retries = self._retries.get(reply.url().toString(), 0)
        url = reply.url().toString()

        if retries < 5:
            logger.debug(f"request failed, retrying: {url}")
            self._retries[url] = retries + 1
            self._requestPage(url)
        else:
            logger.debug(f"request failed, retries exceeded: {url}")
            self._busy = False
            self.endRequest.emit()

    def onRequestFinished(self, reply: QtNetwork.QNetworkReply):
        if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:
            self.onRequestFailed(reply)
            return

        data = reply.readAll()
        data = json.loads(bytearray(data))
        items = data["items"]

        self.queue.put(data_classes.deserialise_items(items))
        self.pageReady.emit()

        metadata = data["metadata"]
        current_page = metadata.get("currentPage")
        total_pages = metadata.get("totalPages")

        logger.debug(f"model request: {current_page}/{total_pages}")

        self.progress.emit(current_page, total_pages)

        next_page = metadata.get("nextPage")

        if next_page:
            self._requestPage(next_page)
        else:
            self._busy = False
            self.endRequest.emit()
