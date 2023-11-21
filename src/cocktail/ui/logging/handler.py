import weakref
from PySide6 import QtCore, QtWidgets
from logging import Handler
from queue import Queue


class HandlerSignals(QtCore.QObject):
    recordReady = QtCore.Signal(object)


class LogHandler(Handler):
    def __init__(self):
        super().__init__()
        self.signals = HandlerSignals()

    def emit(self, record):
        self.signals.recordReady.emit(record)
