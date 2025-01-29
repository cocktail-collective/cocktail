import qtawesome
from PySide6 import QtCore, QtWidgets, QtGui, QtSql
from PySide6.QtGui import QStandardItemModel

from cocktail.ui.search.view import SearchView
from cocktail.core.database import util as db_util


class SearchController(QtCore.QObject):
    def __init__(self, connection, model, view=None, parent=None):
        super().__init__(parent)
        self.model: QtSql.QSqlQueryModel = model
        self.category_model = QtGui.QStandardItemModel()
        self.type_model = QtGui.QStandardItemModel()
        self.sort_order_model = QtGui.QStandardItemModel()
        self.base_model_model = QtGui.QStandardItemModel()

        self.connection: QtSql.QSqlDatabase = connection

        self.view = view or SearchView()
        self.view.setCategoryModel(self.category_model)
        self.view.setTypeModel(self.type_model)
        self.view.setSortOrderModel(self.sort_order_model)
        self.view.setBaseModelModel(self.base_model_model)

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
        self.updateNSFWLevels()
        self.updateSortOrder()
        self.updateBaseModels()
        self.onSearchChanged()

    def updateSortOrder(self):
        value = self.view.sortOrder()
        self.sort_order_model.clear()
        self.sort_order_model.appendRow(QtGui.QStandardItem("Updated"))
        self.sort_order_model.appendRow(QtGui.QStandardItem("Name"))
        self.sort_order_model.appendRow(QtGui.QStandardItem("Id"))
        self.sort_order_model.appendRow(QtGui.QStandardItem("Highest Rating"))
        self.sort_order_model.appendRow(QtGui.QStandardItem("Most Downloads"))
        self.sort_order_model.appendRow(QtGui.QStandardItem("Most ThumbsUps"))
        if value:
            self.view.setSortOrder(value)

    def updateNSFWLevels(self):
        sql = """
        SELECT MIN(nsfw),MAX(nsfw) FROM model
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        if query.next():
            minimum = query.value(0) or 0
            maximum = query.value(1) or 100
            self.view.setNSFWRanges(minimum, maximum)

    def updateBaseModels(self):
        value = self.view.baseModel()

        self.base_model_model.clear()
        all_item = QtGui.QStandardItem("All")
        all_item.setIcon(qtawesome.icon("mdi6.tag"))
        self.base_model_model.appendRow(all_item)

        sql = """
        SELECT DISTINCT base_model FROM model_version ORDER BY base_model
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        while query.next():
            icon = qtawesome.icon("mdi6.brain")
            item = QtGui.QStandardItem(query.value(0))
            item.setIcon(icon)
            self.base_model_model.appendRow(item)

        if value:
            self.view.setBaseModel(value)

    def updateCategories(self):
        sql = """
        SELECT DISTINCT category FROM model ORDER BY category
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        value = self.view.category()

        self.category_model.clear()
        item = QtGui.QStandardItem("All")
        item.setIcon(qtawesome.icon("mdi6.tag"))
        self.category_model.appendRow(item)

        while query.next():
            icon = self.category_icons.get(query.value(0), qtawesome.icon("mdi6.tag"))
            item = QtGui.QStandardItem(query.value(0))
            item.setIcon(icon)
            self.category_model.appendRow(item)

        self.view.setCategory(value)

    def updateTypes(self):
        sql = """
        SELECT DISTINCT type FROM model ORDER BY type
        """
        query = QtSql.QSqlQuery(self.connection)
        query.exec(sql)

        value = self.view.type()

        self.type_model.clear()
        item = QtGui.QStandardItem("All")
        item.setIcon(qtawesome.icon("mdi6.tag"))
        self.type_model.appendRow(item)

        while query.next():
            icon = self.type_icons.get(query.value(0), qtawesome.icon("mdi6.tag"))
            item = QtGui.QStandardItem(query.value(0))
            item.setIcon(icon)
            self.type_model.appendRow(item)

        self.view.setType(value)

    def onSearchChanged(self):
        where = []
        join = ""

        text = self.view.search_text.text()
        model_type = self.view.type()
        model_category = self.view.category()
        base_model = self.view.baseModel()

        bind = {}

        if text:
            where.append("m.name LIKE :text")
            bind["text"] = f"%{text}%"

        if model_type != "All":
            where.append("m.type = :type")
            bind["type"] = model_type

        if model_category != "All":
            where.append("m.category = :category")
            bind["category"] = model_category

        if base_model != "All":
            where.append("mv.base_model = :base_model")
            bind["base_model"] = base_model
            join = "JOIN model_version  mv ON m.id=mv.model_id"

        if self.view.nsfw():
            where.append(f"nsfw <= {self.view.nsfw()}")

        sort_order = self.view.sortOrder()
        if sort_order == "Id":
            order_by = "id DESC"
        elif sort_order == "Name":
            order_by = "name ASC"
        elif sort_order == "Highest Rating":
            order_by = "rating_score DESC"
        elif sort_order == "Most Downloads":
            order_by = "download_cnt DESC"
        elif sort_order == "Most ThumbsUps":
            order_by = "thumbs_up_cnt DESC"
        else:
            order_by = "updated_at DESC"

        if where:
            where = " AND ".join(where)
            where = f"WHERE {where}"
        else:
            where = ""

        sql = f"""
        SELECT DISTINCT m.* 
        FROM model m
        {join}
        {where}
        ORDER BY {order_by}
        """

        query = QtSql.QSqlQuery(self.connection)
        query.prepare(sql)
        for k, v in bind.items():
            query.bindValue(f":{k}", v)

        query.exec()
        self.model.setQuery(query)
