import qtawesome
from PySide6 import QtCore, QtWidgets, QtGui, QtSql

from cocktail.ui.search.view import SearchView
from cocktail.core.database import util as db_util


class SearchController(QtCore.QObject):
    def __init__(self, connection, model, view=None, parent=None):
        super().__init__(parent)
        self.model: QtSql.QSqlQueryModel = model
        self.category_model = QtGui.QStandardItemModel()
        self.type_model = QtGui.QStandardItemModel()
        self.connection: QtSql.QSqlDatabase = connection

        self.view = view or SearchView()
        self.view.setCategoryModel(self.category_model)
        self.view.setTypeModel(self.type_model)

        self.view.searchChanged.connect(self.onSearchChanged)

        self.category_icons = {
            k: qtawesome.icon(v) for k, v in db_util.CATEGORY_ICONS.items()
        }

        self.type_icons = {
            k: qtawesome.icon(v) for k, v in db_util.MODEL_TYPE_ICONS.items()
        }

        self.update()

    def update(self):
        self.updateCategories()
        self.updateTypes()
        self.onSearchChanged()

    def updateCategories(self):
        sql = """
        SELECT DISTINCT category FROM model
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        self.category_model.clear()
        item = QtGui.QStandardItem("All")
        item.setIcon(qtawesome.icon("mdi6.tag"))
        self.category_model.appendRow(item)

        while query.next():
            icon = self.category_icons.get(query.value(0), qtawesome.icon("mdi6.tag"))
            item = QtGui.QStandardItem(query.value(0))
            item.setIcon(icon)
            self.category_model.appendRow(item)

    def updateTypes(self):
        sql = """
        SELECT DISTINCT type FROM model
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        self.type_model.clear()
        item = QtGui.QStandardItem("All")
        item.setIcon(qtawesome.icon("mdi6.tag"))
        self.type_model.appendRow(item)

        while query.next():
            icon = self.type_icons.get(query.value(0), qtawesome.icon("mdi6.tag"))
            item = QtGui.QStandardItem(query.value(0))
            item.setIcon(icon)
            self.type_model.appendRow(item)

    def onSearchChanged(self):
        where = []

        text = self.view.search_text.text()
        model_type = self.view.type()
        model_category = self.view.category()

        if text:
            where.append("name LIKE :text")

        if model_type != "All":
            where.append("type = :type")

        if model_category != "All":
            where.append("category = :category")

        if not self.view.nsfw():
            where.append("nsfw = 0")

        if where:
            where = " AND ".join(where)
            where = f"WHERE {where}"
        else:
            where = ""

        sql = f"""
        SELECT * FROM model
        {where}
        ORDER BY updated_at DESC
        """
        query = QtSql.QSqlQuery(self.connection)
        query.prepare(sql)

        if text:
            query.bindValue(":text", f"%{text}%")

        if model_type != "All":
            query.bindValue(":type", model_type)

        if model_category != "All":
            query.bindValue(":category", model_category)

        query.exec()
        self.model.setQuery(query)
