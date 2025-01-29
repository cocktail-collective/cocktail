import os
import json
import logging
import shutil
import platform
import subprocess
from PySide6 import QtCore, QtSql, QtGui, QtNetwork, QtWidgets

from cocktail.core.database import data_classes
from cocktail.ui.download.view import DownloadDialog, ModelDownloadView

logger = logging.getLogger(__name__)


class ModelDownloadController(QtCore.QObject):
    def __init__(self, connection, view=None, parent=None):
        super().__init__(parent)
        self.settings = QtCore.QSettings("cocktail", "cocktail")
        self.db_connection: QtSql.QSqlDatabase = connection
        self.download_dialog = DownloadDialog()
        self.view = view or ModelDownloadView()
        self.network_manager = QtNetwork.QNetworkAccessManager()

    def download(self, model: data_classes.Model):
        if isinstance(model, data_classes.Model):
            self.downloadModel(model)
        elif isinstance(model, data_classes.ModelVersion):
            self.downloadModelVersion(model)
        elif isinstance(model, data_classes.ModelFile):
            self.downloadModelFile(model)
        else:
            raise TypeError(f"Invalid data type: {type(model)}")

    def downloadModel(self, model: data_classes.Model):
        model_version_sql = QtSql.QSqlQuery(self.db_connection)
        model_version_sql.prepare(
            """
            SELECT * FROM model_version
            WHERE model_id = :model_id
            ORDER BY id DESC
            LIMIT 1
            """
        )
        model_version_sql.bindValue(":model_id", model.id)
        if not model_version_sql.exec():
            raise RuntimeError(
                f"Failed to execute query: {model_version_sql.lastError().text()}, {model_version_sql.lastQuery()}"
            )
        model_version_sql.next()
        model_version = data_classes.ModelVersion.from_record(
            model_version_sql.record()
        )

        self.downloadModelVersion(model, model_version)

    def downloadModelVersion(
        self, model: data_classes.Model, model_version: data_classes.ModelVersion
    ):
        model_file_sql = QtSql.QSqlQuery(self.db_connection)
        model_file_sql.prepare(
            """
            SELECT * FROM model_file
            WHERE model_version_id = :model_version_id
            AND safe = 1
            ORDER BY is_primary DESC
            LIMIT 1
            """
        )
        model_file_sql.bindValue(":model_version_id", model_version.id)
        if not model_file_sql.exec():
            raise RuntimeError(
                f"Failed to execute query: {model_file_sql.lastError().text()}, {model_file_sql.lastQuery()}"
            )
        model_file_sql.next()
        model_file = data_classes.ModelFile.from_record(model_file_sql.record())

        self.downloadModelFile(model, model_version, model_file)

    def downloadModelFile(
        self,
        model: data_classes.Model,
        model_version: data_classes.ModelVersion,
        model_file: data_classes.ModelFile,
    ):
        rect = self.download_dialog.rect()
        rect.moveCenter(QtGui.QCursor.pos())
        self.download_dialog.setGeometry(rect)

        logger.debug(f"Downloading {model_file.name} from {model_file.url}")

        filename = model_file.name
        root = self.settings.value("paths/root", os.path.expanduser("~"))
        model_type_dir = self.settings.value(f"paths/{model.type}")

        if model_type_dir and os.path.isabs(model_type_dir):
            final_path = os.path.join(model_type_dir, filename)

        elif model_type_dir:
            final_path = os.path.join(root, model_type_dir, filename)

        else:
            logger.debug(
                f"No model type directory set for: {model.type}, prompting user for path"
            )
            final_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.download_dialog, "Save As", root, filename
            )

        if not final_path:
            return

        if os.path.exists(final_path):
            reply = QtWidgets.QMessageBox.question(
                self.download_dialog,
                "File Exists",
                "File already exists. Overwrite?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if reply == QtWidgets.QMessageBox.No:
                return
            else:
                os.remove(final_path)

        final_path = final_path.format(
            category=model.category,
        )

        dirname, basename = os.path.split(final_path)
        filename, _ = os.path.splitext(basename)

        image_path = os.path.join(dirname, f"{filename}.jpg")
        image = self.get_image(model_version)
        image_url = image.url if image else None

        if image_url:
            self._download(image_url, image_path)

        json_path = os.path.join(dirname, f"{filename}.json")

        metadata = {
            "name": model.name,
            "activation text": ",".join(model_version.trained_words),
            "description": model_version.description + "\n\n" + model.description,
            "model": model._asdict(),
            "version": model_version._asdict(),
            "image": image._asdict() if image else None,
        }

        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=4)

        api_key = ""
        if (k := os.environ.get('CIVITAI_API_KEY', None)) is not None:
            api_key = f"?token={k}"

        reply = self._download(model_file.url + api_key, final_path)

        widget = self.view.addDownload(model_file.name, reply)
        widget.requestOpenDirectory.connect(
            lambda p=final_path: self.onOpenDirectoryClick(os.path.dirname(p))
        )

    def get_image(self, model_version: data_classes.ModelVersion):
        query = QtSql.QSqlQuery(self.db_connection)
        query.prepare(
            """
            SELECT * FROM model_image
            WHERE model_version_id = :model_version_id
            ORDER BY id DESC
            """
        )
        query.bindValue(":model_version_id", model_version.id)

        if not query.exec():
            raise RuntimeError(
                f"Failed to execute query: {query.lastError().text()}, {query.lastQuery()}"
            )

        query.next()
        return data_classes.ModelImage.from_record(query.record())

    def _download(self, url, path):
        temp_path = path + ".part"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        reply = self.network_manager.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
        reply.readyRead.connect(lambda p=temp_path, r=reply: self.dumpBytes(p, r))
        reply.finished.connect(
            lambda p=temp_path, f=path: self.onDownloadFinished(p, f)
        )

        return reply

    def dumpBytes(self, path, reply: QtNetwork.QNetworkReply):
        with open(path, "ab") as f:
            f.write(bytearray(reply.readAll()))

    def onDownloadFinished(self, tmp_path, final_path):
        shutil.move(tmp_path, final_path)

    def onOpenDirectoryClick(self, path):
        if platform.platform().startswith("Windows"):
            subprocess.Popen(f'explorer /select,"{path}"')
        elif platform.platform().startswith("Linux"):
            subprocess.Popen(["xdg-open", path])
        elif platform.platform().startswith("Mac"):
            subprocess.Popen(["open", path])
