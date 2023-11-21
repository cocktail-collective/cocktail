__all__ = ["SettingsView"]
import textwrap
from PySide6 import QtCore, QtWidgets


class DirectoryPicker(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.value = None
        self._layout = QtWidgets.QHBoxLayout(self)
        self._path_label = QtWidgets.QLineEdit()
        self._browse_button = QtWidgets.QPushButton("Browse")
        self._layout.addWidget(self._path_label)
        self._layout.addWidget(self._browse_button)
        self._browse_button.clicked.connect(self.browse)

    def browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.setValue(path)

    def setValue(self, path):
        self.value = path
        self._path_label.setText(path)
        self.valueChanged.emit(path)

    def value(self):
        return self.value


class StringEditor(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.value = None
        self._layout = QtWidgets.QHBoxLayout(self)
        self._path_label = QtWidgets.QLineEdit()
        self._layout.addWidget(self._path_label)
        self._path_label.textChanged.connect(self.valueChanged)

    def setValue(self, value):
        self.value = value
        self._path_label.setText(value)

    def value(self):
        return self.value


class SettingsView(QtWidgets.QWidget):
    appyPreset = QtCore.Signal(str)
    settingChanged = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.presets_dropdown = QtWidgets.QComboBox()
        self.apply_preset_button = QtWidgets.QPushButton("Apply")

        self._settings_layout = QtWidgets.QVBoxLayout()
        self._groups = {}
        self._editors = {}

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.apply_preset_button)
        top_layout.addWidget(self.presets_dropdown)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_layout, 1)
        layout.addLayout(self._settings_layout, 10)
        layout.addStretch(100)

        self.apply_preset_button.clicked.connect(self.onApplyClicked)

    def addSetting(self, group_name, label, key, value, hint=None, tooltip=None):
        if group_name not in self._groups:
            group = self._groups[group_name] = QtWidgets.QGroupBox(group_name)
            group_layout = QtWidgets.QFormLayout(group)
            self._settings_layout.addWidget(group)
        else:
            group = self._groups[group_name]
            group_layout = group.layout()
        if hint == "directory":
            widget = DirectoryPicker()
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda path: self.settingChanged.emit(key, path)
            )
        else:
            widget = StringEditor()
            widget.setValue(value)

        if tooltip:
            widget.setToolTip(tooltip)

        widget.valueChanged.connect(lambda text: self.settingChanged.emit(key, text))

        self._editors[key] = widget
        group_layout.addRow(label, widget)

    def updateValue(self, key, value):
        self._editors[key].setValue(value)

    def setPresetsModel(self, model):
        self.presets_dropdown.setModel(model)

    def onApplyClicked(self):
        if (
            QtWidgets.QMessageBox.question(
                self, "Apply Preset", "Are you sure you want to apply this preset?"
            )
            == QtWidgets.QMessageBox.Yes
        ):
            self.appyPreset.emit(self.presets_dropdown.currentText())
