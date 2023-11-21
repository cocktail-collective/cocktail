from PySide6 import QtCore, QtWidgets, QtGui


class SearchView(QtWidgets.QWidget):
    searchChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowFlags.FramelessWindowHint)
        self.search_text = QtWidgets.QLineEdit()
        self.search_text.setPlaceholderText("Search")

        self.nsfw_checkbox = QtWidgets.QCheckBox("NSFW")

        self.category_selector = QtWidgets.QComboBox()
        self.type_selector = QtWidgets.QComboBox()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.search_text, 100)
        layout.addWidget(self.category_selector, 1)
        layout.addWidget(self.type_selector, 1)
        layout.addWidget(self.nsfw_checkbox, 1)

        self.search_text.textChanged.connect(lambda *_: self.searchChanged.emit())
        self.category_selector.currentTextChanged.connect(
            lambda *_: self.searchChanged.emit()
        )
        self.type_selector.currentTextChanged.connect(
            lambda *_: self.searchChanged.emit()
        )
        self.nsfw_checkbox.stateChanged.connect(lambda *_: self.searchChanged.emit())

    def nsfw(self):
        return self.nsfw_checkbox.isChecked()

    def type(self):
        return self.type_selector.currentText()

    def setTypeModel(self, model):
        self.type_selector.setModel(model)

    def category(self):
        return self.category_selector.currentText()

    def setCategoryModel(self, model):
        self.category_selector.setModel(model)
