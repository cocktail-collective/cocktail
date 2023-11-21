from PySide6 import QtCore

from cocktail.core.providers import ImageProviderProxyModel


class ModelGalleryProxyModel(ImageProviderProxyModel):
    """
    A proxy model which displays images from a column containing URLs.
    """

    NameRole = QtCore.Qt.ItemDataRole.UserRole + 1
    TypeRole = QtCore.Qt.ItemDataRole.UserRole + 2
    BaseModelRole = QtCore.Qt.ItemDataRole.UserRole + 3
    CreatorImageRole = QtCore.Qt.ItemDataRole.UserRole + 4

    ImageRoles = [QtCore.Qt.ItemDataRole.DecorationRole, CreatorImageRole]

    ImageRoles = {
        QtCore.Qt.ItemDataRole.DecorationRole: "image",
        CreatorImageRole: "creator_image",
    }

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            record = self.sourceModel().record(index.row())
            return record.value("name")

        elif role == ModelGalleryProxyModel.NameRole:
            record = self.sourceModel().record(index.row())
            return record.value("name")

        elif role == ModelGalleryProxyModel.TypeRole:
            record = self.sourceModel().record(index.row())
            return record.value("type")

        return super().data(index, role)

    def getUrl(
        self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole.DecorationRole
    ):
        name = self.ImageRoles[role]
        record = self.sourceModel().record(index.row())
        return record.value(name)
