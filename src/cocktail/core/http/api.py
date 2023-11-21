__all__ = ["cached_session", "uncached_session", "NetworkManager"]
from PySide6 import QtNetwork, QtCore

import platformdirs
import contextlib
import requests
from cachecontrol import CacheControl
from cachecontrol.caches import SeparateBodyFileCache
from cocktail.core import decorators

__CACHE = None

# TODO: investigate using a QNetworkAccessManager instead of requests as it allows for caching.


@contextlib.contextmanager
def cached_session():
    """
    A context manager that provides a cached requests session for use in a with statement.
    """
    global __CACHE
    if __CACHE is None:
        __CACHE = SeparateBodyFileCache(platformdirs.user_cache_dir("cocktail", "http"))

    session = requests.Session()
    cached_session = CacheControl(session, cache=__CACHE)
    try:
        yield cached_session
    finally:
        cached_session.close()


@contextlib.contextmanager
def uncached_session():
    """
    A context manager that provides an uncached requests session for use in a with statement.
    """
    session = requests.Session()
    try:
        yield session
    finally:
        session.close()


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
            # request.setAttribute(
            #     QtNetwork.QNetworkRequest.Attribute.CacheLoadControlAttribute,
            #     QtNetwork.QNetworkRequest.CacheLoadControl.AlwaysNetwork
            # )
            #
            reply = self._manager.get(request)
        else:
            reply = self._manager.get(QtNetwork.QNetworkRequest(url))

        return reply
