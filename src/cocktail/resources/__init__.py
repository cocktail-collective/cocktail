"""
This api is a wrapper around the importlib.resources module for loading resources
"""
import os
import random
import importlib.resources
import importlib.metadata
from PySide6 import QtGui


def icon(name: str) -> QtGui.QIcon:
    """
    get an icon resource
    """
    return QtGui.QIcon(pixmap(name))


def image(name: str) -> QtGui.QImage:
    """
    get an image resource
    """
    return QtGui.QImage.fromData(blob(name))


def pixmap(name: str) -> QtGui.QPixmap:
    """
    get a pixmap resource
    """
    return QtGui.QPixmap.fromImage(image(name))


def text(name: str) -> str:
    """
    get a text resource
    """
    return importlib.resources.read_text("cocktail.resources", name)


def blob(name: str) -> bytes:
    """
    get the binary data from a resource file
    """
    return importlib.resources.read_binary("cocktail.resources", name)
