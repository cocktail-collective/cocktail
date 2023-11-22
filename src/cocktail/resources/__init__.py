"""
This api is a wrapper around the importlib.resources module for loading resources
"""
from . import resources_rc

resources_rc.qInitResources()

from PySide6 import QtGui, QtCore

# list all resources here


def icon(name: str) -> QtGui.QIcon:
    """
    get an icon resource
    """
    return QtGui.QIcon(pixmap(name))


def image(name: str) -> QtGui.QImage:
    """
    get an image resource
    """
    return QtGui.QImage(":/cocktail/images/" + name)


def pixmap(name: str) -> QtGui.QPixmap:
    """
    get a pixmap resource
    """
    return QtGui.QPixmap.fromImage(image(name))


def text(name: str) -> str:
    """
    get a text resource
    """

    resource = QtCore.QResource(":/cocktail/" + name)

    if not resource.isValid():
        raise ValueError(f"Resource {name} not found")

    return resource.uncompressedData().data().decode("utf-8")
