import logging
import argparse

from PySide6 import QtWidgets, QtCore
from cocktail import resources
from cocktail.ui.main_window import MainWindowController


def apply_stylesheet():
    app = QtWidgets.QApplication.instance()
    style_sheet = resources.text("stylesheet.qss")
    app.setStyleSheet(style_sheet)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--no-update", action="store_true")
    parser.add_argument("--reload-stylesheet", action="store_true")

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

    controller = MainWindowController()
    controller.view.showMaximized()

    if not args.no_update:
        controller.database_controller.updateModelData()

    if args.reload_stylesheet:
        ss_timer = QtCore.QTimer()
        ss_timer.setInterval(1000)
        ss_timer.timeout.connect(apply_stylesheet)
        ss_timer.start()

    app.exec()


if __name__ == "__main__":
    main()
