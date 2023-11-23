import os
import functools
from typing import Any
from PySide6 import QtCore, QtWidgets, QtGui, QtSql, QtNetwork
from cocktail import resources
import qtawesome as qta
from cocktail.ui.settings.controller import PRESETS, detect_tool


SELECT_DIRECTORY_DESCRIPTION = """
Please select the location where your diffusion tool is installed.
<br><br>
e.g. the location where you put Automatic1111 or ComfyUI...
"""


class PageBase(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fields = []

    def registerField(self, name, widget, property="text"):
        super().registerField(name, widget, property)
        self._fields.append(name)

    def fields(self):
        return {k: self.field(k) for k in self._fields}


class SelectToolDirectoryStep(PageBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Where is your diffusion tool installed?")
        self.description_box = QtWidgets.QTextEdit()
        self.description_box.setReadOnly(True)
        self.description_box.setHtml(SELECT_DIRECTORY_DESCRIPTION)

        self.directory_edit = QtWidgets.QLineEdit()
        self.browser_button = QtWidgets.QPushButton()
        self.browser_button.setIcon(qta.icon("mdi.folder-open"))

        edit_layout = QtWidgets.QHBoxLayout()
        edit_layout.addWidget(self.directory_edit)
        edit_layout.addWidget(self.browser_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.description_box)
        layout.addLayout(edit_layout)

        self.registerField("paths/root", self.directory_edit)

        self.browser_button.clicked.connect(self.onBrowseClicked)

    def onBrowseClicked(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Diffusion Tool Directory"
        )
        if directory:
            self.directory_edit.setText(directory)

    def validatePage(self) -> bool:
        return super().validatePage() and os.path.isdir(self.directory_edit.text())


class PathsTool(PageBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Select Diffusion Tool")
        self._label = QtWidgets.QLabel()

        self.paths_layout = QtWidgets.QFormLayout()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self._label)
        main_layout.addLayout(self.paths_layout)

        self._path_keys = []

    def initializePage(self) -> None:
        directory = self.field("paths/root")
        tool = detect_tool(directory)
        preset = PRESETS.get(tool)

        if tool:
            self._label.setText(f"Detected {tool}")
        else:
            self._label.setText("Uknown tool, please select paths manually")

        if preset:
            for key, value in preset.items():
                name = key.partition("/")[2]
                self.addPath(key, name, value)
        else:
            preset = list(PRESETS.keys())[0]

            for k, _ in PRESETS[preset].items():
                name = k.partition("/")[2]
                self.addPath(k, name, "")

    def addPath(self, key, name, value):
        self._path_keys.append(key)
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        edit = QtWidgets.QLineEdit(value)
        browse_button = QtWidgets.QPushButton()
        browse_button.setIcon(qta.icon("mdi.folder-open"))

        layout.addWidget(label)
        layout.addWidget(edit)
        layout.addWidget(browse_button)
        self.paths_layout.addRow(layout)

        callback = functools.partial(self.browse, edit)

        self.registerField(key, edit)
        browse_button.clicked.connect(callback)

    def browse(self, editor):
        root = self.field("paths/root")
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Diffusion Tool Directory", dir=root
        )
        if directory:
            if directory.startswith(root):
                directory = os.path.relpath(directory, self.field("paths/root"))
            editor.setText(directory)

    def validatePage(self) -> bool:
        all_filled = [self.field(k) for k in self._path_keys]
        if not all(all_filled):
            success = (
                QtWidgets.QMessageBox.question(
                    self,
                    "Missing Paths",
                    "Some paths are missing, do you want to continue?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                )
                == QtWidgets.QMessageBox.Yes
            )

        else:
            success = True

        if success:
            settings = QtCore.QSettings("cocktail", "cocktail")
            settings.setValue("paths/root", self.field("paths/root"))
            for k in self._path_keys:
                settings.setValue(k, self.field(k))

        return success


class SetupWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diffusion Tool Setup")
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)

        self.addPage(SelectToolDirectoryStep(self))
        self.addPage(PathsTool(self))


class CocktailSplashScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._image_label = QtWidgets.QLabel()
        self._image_label.setPixmap(resources.pixmap("splash.png"))
        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setProperty("class", "splash-screen-progress-bar")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._image_label)
        layout.addWidget(self._progress_bar)

    def setProgress(self, current, total):
        self._progress_bar.setValue(current)
        self._progress_bar.setMaximum(total)

    def setText(self, text: str):
        self._progress_bar.setFormat(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    # splash = CocktailSplashScreen()
    # splash.show()
    wizard = SetupWizard()
    wizard.show()
    app.exec()
