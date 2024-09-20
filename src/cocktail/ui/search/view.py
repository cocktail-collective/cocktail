from PySide6 import QtCore, QtWidgets, QtGui


class SearchView(QtWidgets.QWidget):
    searchChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowFlags.FramelessWindowHint)
        self.search_text = QtWidgets.QLineEdit()
        self.search_text.setPlaceholderText("Search")
        self.base_model_selector = QtWidgets.QComboBox()
        self.nsfw_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.nsfw_slider.setProperty("class", "nsfw-slider")
        self.sort_order_selector = QtWidgets.QComboBox()

        self.category_selector = QtWidgets.QComboBox()
        self.type_selector = QtWidgets.QComboBox()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.search_text, 100)
        layout.addWidget(QtWidgets.QLabel("Category"), 1)
        layout.addWidget(self.category_selector, 1)
        layout.addWidget(QtWidgets.QLabel("Type"), 1)
        layout.addWidget(self.type_selector, 1)
        layout.addWidget(QtWidgets.QLabel("Model"), 1)
        layout.addWidget(self.base_model_selector, 1)
        layout.addWidget(QtWidgets.QLabel("NSFW Level"), 1)
        layout.addWidget(self.nsfw_slider, 10)
        layout.addWidget(QtWidgets.QLabel("Sort By"), 1)
        layout.addWidget(self.sort_order_selector, 1)

        self.search_text.textChanged.connect(lambda *_: self.searchChanged.emit())
        self.category_selector.currentTextChanged.connect(
            lambda *_: self.searchChanged.emit()
        )
        self.type_selector.currentTextChanged.connect(
            lambda *_: self.searchChanged.emit()
        )
        self.base_model_selector.currentIndexChanged.connect(
            lambda *_: self.searchChanged.emit()
        )
        self.nsfw_slider.sliderReleased.connect(lambda *_: self.searchChanged.emit())
        self.sort_order_selector.currentTextChanged.connect(lambda *_: self.searchChanged.emit())

    def nsfw(self):
        return self.nsfw_slider.value()

    def setNSFWRanges(self, minimum, maximum):
        self.nsfw_slider.setMinimum(minimum)
        self.nsfw_slider.setMaximum(maximum)
        if self.nsfw_slider == 0:
            self.nsfw_slider.setValue(minimum)

    def setNSFWLevel(self, level):
        self.nsfw_slider.setValue(level)

    def type(self):
        return self.type_selector.currentText()

    def setType(self, name: str):
        self.type_selector.setCurrentText(name)

    def setTypeModel(self, model):
        self.type_selector.setModel(model)

    def category(self):
        return self.category_selector.currentText()

    def setCategoryModel(self, model):
        self.category_selector.setModel(model)

    def setCategory(self, category):
        self.category_selector.setCurrentText(category)

    def setSortOrderModel(self, model):
        self.sort_order_selector.setModel(model)

    def setSortOrder(self, order: str):
        self.sort_order_selector.setCurrentText(order)

    def sortOrder(self):
        return self.sort_order_selector.currentText()

    def setBaseModelModel(self, model):
        self.base_model_selector.setModel(model)

    def setBaseModel(self, name: str):
        self.base_model_selector.setCurrentText(name)

    def baseModel(self):
        return self.base_model_selector.currentText()
