import PySide6.QtGui
import qtawesome
from PySide6 import QtWidgets, QtGui, QtCore
from cocktail.ui.model_gallery import ModelGalleryView
from cocktail.ui.model_info import ModelInfoView
from cocktail.ui.download import ModelDownloadView
from cocktail.ui.database import DatabaseView
from cocktail.ui.search import SearchView
from cocktail.ui.settings import SettingsView


class TopBar(QtWidgets.QWidget):
    downloadClicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.download_icon = QtWidgets.QPushButton("Download")
        self.download_icon.setIcon(qtawesome.icon("fa5s.download"))

        layout = QtWidgets.QHBoxLayout(self)
        layout.insertStretch(0)
        layout.addWidget(self.download_icon)

        self.download_icon.clicked.connect(self.downloadClicked.emit)


class CenterWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.search_view = SearchView()
        self.model_gallery_view = ModelGalleryView()
        self.model_info_view = ModelInfoView()
        self.model_download_view = ModelDownloadView()
        self.database_view = DatabaseView()
        self.settings_view = SettingsView()

        self.tabs = QtWidgets.QTabWidget()
        info_icon = qtawesome.icon("fa5s.info-circle")
        self.tabs.addTab(self.model_info_view, info_icon, "Info")

        download_icon = qtawesome.icon("fa5s.download")
        self.tabs.addTab(self.model_download_view, download_icon, "Downloads")

        db_icon = qtawesome.icon("fa5s.database")
        self.tabs.addTab(self.database_view, db_icon, "Database")

        settings_icon = qtawesome.icon("fa5s.cog")
        self.tabs.addTab(self.settings_view, settings_icon, "Settings")

        browser_layout = QtWidgets.QVBoxLayout()
        browser_layout.addWidget(self.search_view)
        browser_layout.addWidget(self.model_gallery_view)

        tabs_scroll_area = QtWidgets.QScrollArea()
        tabs_scroll_area.setWidgetResizable(True)
        tabs_scroll_area.setWidget(self.tabs)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(browser_layout, 5)
        layout.addWidget(tabs_scroll_area, 2)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(layout)

        self.model_info_view.requestFocus.connect(self.switchToTab)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self.search_view.show()
        self.search_view.keyPressEvent(event)
        return super().keyPressEvent(event)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.search_view.hide()
        return super().focusInEvent(event)

    def onDownloadClicked(self):
        button_rect = self.top_bar.download_icon.geometry()
        view_rect = self.model_download_view.geometry()

        self.model_download_view.move(
            button_rect.left() + button_rect.width() - view_rect.width(),
            button_rect.bottom() + 10,
        )

        self.model_download_view.show()

    def switchToTab(self, widget):
        self.tabs.setCurrentWidget(widget)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.central_widget = CenterWidget()
        self.setCentralWidget(self.central_widget)
