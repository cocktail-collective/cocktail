__all__ = ["LogController"]

import logging
import qtawesome
from PySide6 import QtCore, QtWidgets, QtGui
from cocktail.ui.logging.handler import LogHandler
from cocktail.ui.logging.view import LogView


class LogController(QtCore.QObject):
    def __init__(self, logger, view=None, parent=None):
        super().__init__(parent)
        self.model = QtGui.QStandardItemModel()
        self.view = view or LogView()
        self.view.setModel(self.model)
        self.handler = LogHandler()
        self.logger: logging.Logger = logger
        self.logger.addHandler(self.handler)
        self.icons = {
            logging.DEBUG: qtawesome.icon("fa5s.info-circle", color="gray"),
            logging.INFO: qtawesome.icon("fa5s.info-circle", color="lightblue"),
            logging.WARNING: qtawesome.icon("fa5s.exclamation-triangle"),
            logging.ERROR: qtawesome.icon("fa5s.exclamation-circle"),
            logging.CRITICAL: qtawesome.icon("fa5s.exclamation-circle"),
        }
        self.handler.signals.recordReady.connect(self.onRecordReady)

    def onRecordReady(self, record):
        item = QtGui.QStandardItem(record.getMessage())
        item.setIcon(self.icons[record.levelno])

        self.model.appendRow(item)
