__all__ = ["NetworkManager"]
from PySide6 import QtNetwork, QtCore

import platformdirs
from cocktail.core import decorators


class NetworkManager:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    @decorators.run_once
    def __init__(self):
        self._manager = QtNetwork.QNetworkAccessManager()
        self._cache = QtNetwork.QNetworkDiskCache()
        self._cache.setCacheDirectory(platformdirs.user_cache_dir("cocktail", "http"))
        self._manager.setCache(self._cache)

    def get(self, url, cache_enabled=True):
        url = QtCore.QUrl(url)

        if not cache_enabled:
            request = QtNetwork.QNetworkRequest(url)

            reply = self._manager.get(request)
        else:
            reply = self._manager.get(QtNetwork.QNetworkRequest(url))

        return reply
