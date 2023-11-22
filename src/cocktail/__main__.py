import logging
import argparse

from PySide6 import QtWidgets, QtCore
from cocktail import resources
from cocktail.ui.main_window import MainWindowController
from cocktail.ui.startup import StartupController

MAIN_CONTROLLER = None


def apply_stylesheet():
    app = QtWidgets.QApplication.instance()
    style_sheet = resources.text("stylesheet.qss")
    app.setStyleSheet(style_sheet)


def list_resources(root=None):
    root = root or QtCore.QResource(":/cocktail")
    for child in root.children():
        child = QtCore.QResource(f"{root.absoluteFilePath()}/{child}")
        if child.isDir():
            list_resources(child)
        else:
            print(child.absoluteFilePath())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--no-update", action="store_true")
    parser.add_argument("--list-resources", action="store_true")

    args = parser.parse_args()

    app = QtWidgets.QApplication()
    icon = resources.icon("cocktail.png")
    app.setWindowIcon(icon)
    app.setApplicationName("Cocktail")
    apply_stylesheet()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)

    if args.list_resources:
        list_resources()

    def start():
        """
        Creating a database connection will create an empty database if one does not exist.
        This will fool the startup controller into thinking that the database is already
        downloaded and extracted. so we only instantiate the main window controller after
        the startup controller has completed.
        """
        global MAIN_CONTROLLER
        MAIN_CONTROLLER = MainWindowController()
        MAIN_CONTROLLER.view.showMaximized()
        if not args.no_update:
            MAIN_CONTROLLER.database_controller.updateModelData()

    startup_controller = StartupController()
    startup_controller.complete.connect(start)
    startup_controller.start()

    app.exec()


if __name__ == "__main__":
    main()
