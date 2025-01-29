__all__ = ["DatabaseController"]

from PySide6 import QtCore, QtWidgets, QtSql
import logging
import cocktail.core.database
from cocktail.core.database import data_classes, api as db_api
from cocktail.core.providers.model_data import ModelDataProvider
from cocktail.ui.database.view import DatabaseView
from cocktail.ui.logger import LogController


class DatabaseController(QtCore.QObject):
    updateComplete = QtCore.Signal()
    updateProgress = QtCore.Signal(int)
    updateMessage = QtCore.Signal(str)
    dataUpdated = QtCore.Signal()

    def __init__(self, connection, view=None, parent=None):
        super().__init__(parent)
        self.view = view or DatabaseView()
        self.connection: QtSql.QSqlDatabase = connection
        self.model_data_provider = ModelDataProvider()
        self.model_data_provider.pageReady.connect(self.onPageReady)
        self.model_data_provider.beginRequest.connect(self.onUpdateBegin)
        self.model_data_provider.progress.connect(self.onUpdateProgress)
        self.model_data_provider.endRequest.connect(self.onUpdateEnd)
        self.view.updateClicked.connect(self.updateModelData)

        self.logger = logging.getLogger(cocktail.core.database.__name__)
        self.log_controller = LogController(self.logger, self.view.log_view)
        self.log_controller.logMessageReceived.connect(self.updateMessage)

    def updateModelData(self, period: data_classes.Period = None):
        if period is None:
            period = db_api.get_db_update_period(self.connection)

        self.logger.info(f"Updating model data for period: {period.value}")

        self.model_data_provider.requestModelData(period)

    def onPageReady(self):
        page = self.model_data_provider.queue.get()
        db_api.insert_page(self.connection, page)
        self.dataUpdated.emit()

    def onUpdateBegin(self):
        self.updateMessage.emit("Querying API")
        self.view.setProgressText("Querying API")
        self.view.setProgress(0, 0)

    def onUpdateProgress(self, value, total):
        self.view.setProgressText(f"Making Updates")
        self.updateMessage.emit("Making Updates")
        self.view.setProgress(value, total)

    def onUpdateEnd(self):
        self.view.setProgress(0, 100)
        self.view.setProgressText("Update Complete")
        self.updateMessage.emit("Update Complete")
        db_api.set_last_updated(self.connection)
        self.updateComplete.emit()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    app = QtWidgets.QApplication()

    db = db_api.get_connection()

    controller = DatabaseController(db)
    controller.updateModelData(period=data_classes.Period.AllTime)
    controller.view.show()

    app.exec()
