__all__ = ["SettingsController"]

from typing import Any
from PySide6 import QtCore, QtWidgets, QtGui, QtSql
from cocktail.ui.settings.view import SettingsView


PRESETS = {
    "Automatic-1111": {
        "paths/Checkpoint": "models/Stable-diffusion",
        "paths/Controlnet": "extensions/sd-webui-controlnet/models",
        "paths/Hypernetwork": "models/hypernetworks",
        "paths/LORA": "models/Lora",
        "paths/LoCon": "models/Lora",
        "paths/TextualInversion": "embeddings",
        "paths/VAE": "models/VAE",
    },
    "ComfyUI": {
        "paths/Checkpoint": "models/checkpoints",
        "paths/Controlnet": "models/controlnet",
        "paths/Hypernetwork": "models/hypernetworks",
        "paths/LORA": "models/loras",
        "paths/LoCon": "models/loras",
        "paths/TextualInversion": "models/embeddings",
        "paths/VAE": "models/vae",
        "paths/Upscaler": "models/upscale_models",
    },
}


def walk_namespaces(namespace: str) -> list[str]:
    """
    Walks a namespace and returns a list of all the namespaces and keys.
    """
    namespaces = []
    while "/" in namespace:
        namespace, key = namespace.rsplit("/", 1)
        namespaces.append((namespace, f"{namespace}/{key}", key))

    namespaces.append((None, namespace, namespace))
    namespaces.reverse()
    return namespaces


class ValueItem(QtGui.QStandardItem):
    def __init__(self, key, value):
        super().__init__(value)
        self.key = key
        self.value = value


class SettingsController(QtCore.QObject):
    def __init__(self, connection, view=None, parent=None):
        super().__init__(parent=parent)
        self.connection: QtSql.QSqlDatabase = connection
        self.settings = QtCore.QSettings("cocktail", "cocktail")

        self.view = view or SettingsView()

        self.presets_model = QtGui.QStandardItemModel()

        self.view.setPresetsModel(self.presets_model)
        self.view.appyPreset.connect(self.onAcceptClicked)

        self.view.settingChanged.connect(self.onSettingChanged)

        self.populate()

    def populate(self):
        self.view.addSetting(
            "General",
            "Models Root",
            "paths/root",
            self.settings.value("models-root"),
            hint="directory",
            tooltip="The root directory of your stable diffusion tool",
        )
        for model_type in self.iterModelTypes():
            self.view.addSetting(
                "Paths",
                model_type,
                f"paths/{model_type}",
                self.settings.value(f"paths/{model_type}"),
                hint="directory",
                tooltip=f"The directory where {model_type} data is stored.<br>"
                "this can be a relative path to the models root<br><br>"
                f"'models/{model_type}'<br><br>"
                "or an absolute path <br><br>"
                f"'/home/user/models/{model_type}'",
            )

        self.populatePresets()

    def populatePresets(self):
        self.presets_model.clear()
        for preset_name, preset in PRESETS.items():
            item = QtGui.QStandardItem(preset_name)
            self.presets_model.appendRow(item)

    def onSettingChanged(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()

    def onAcceptClicked(self, preset_name):
        preset = PRESETS[preset_name]
        for k, v in preset.items():
            self.view.updateValue(k, v)

    def iterModelTypes(self):
        query = QtSql.QSqlQuery("SELECT DISTINCT type FROM model", self.connection)
        query.exec()

        if query.lastError().isValid():
            raise Exception(query.lastError().text())

        while query.next():
            yield query.value(0)


if __name__ == "__main__":
    from cocktail.core.database import get_connection

    app = QtWidgets.QApplication()
    connection = get_connection()
    print(connection)
    print(connection.tables())
    controller = SettingsController(connection)
    controller.view.show()

    app.exec()
