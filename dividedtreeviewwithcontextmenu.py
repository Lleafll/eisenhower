from treeviewwithcontextmenu import (
        TreeViewWithContextMenu, TASK_ROLE, build_tree_view_model)
from PySide2 import QtWidgets, QtCore, QtGui
from task import Task, sort_tasks_by_relevance
from typing import Sequence
from datetime import date


class CalendarDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

    def paint(
            self,
            painter: QtGui.QPainter,
            option: QtWidgets.QStyleOptionViewItem,
            index: QtCore.QModelIndex) -> None:
        text = index.model().data(index, QtCore.Qt.DisplayRole).toString(
                QtCore.Qt.SystemLocaleDate)
        option.displayAlignment = \
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        self.drawDisplay(painter, option, option.rect, text)
        self.drawFocus(painter, option, option.rect)

    def createEditor(
            self,
            parent: QtWidgets.QWidget,
            option: QtWidgets.QStyleOptionViewItem,
            index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        date_edit = QtWidgets.QDateEdit(parent)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd.MM.yyyy")
        return date_edit

    def setEditorData(
            self,
            editor: QtWidgets.QWidget,
            index: QtCore.QModelIndex) -> None:
        date = index.model().data(index, QtCore.Qt.DisplayRole)
        if date.isNull():
            date = QtCore.QDate.currentDate()
        editor.setDate(date)

    def setModelData(
            self,
            editor: QtWidgets.QWidget,
            model: QtCore.QAbstractItemModel,
            index: QtCore.QModelIndex) -> None:
        date = editor.date()
        model.setData(index, date)


class SeparatedTreeViewWithContextMenu(QtWidgets.QWidget):
    add_task_requested = QtCore.Signal(str)
    complete_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    rename_task_requested = QtCore.Signal(Task, str)
    schedule_task_requested = QtCore.Signal(Task, date)
    snooze_task_requested = QtCore.Signal(Task, date)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._upper_list = TreeViewWithContextMenu(self)
        self._lower_list = TreeViewWithContextMenu(self)
        layout = QtWidgets.QVBoxLayout(self)
        for task_list in (self._upper_list, self._lower_list):
            layout.addWidget(task_list)
            task_list.add_task_requested.connect(self.add_task_requested)
            task_list.complete_task_requested.connect(
                    self.complete_task_requested)
            task_list.delete_task_requested.connect(self.delete_task_requested)
            task_list.remove_due_requested.connect(self.remove_due_requested)
            task_list.remove_snooze_requested.connect(
                    self.remove_snooze_requested)

    def add_tasks(self, tasks: Sequence[Task]) -> None:
        due_tasks, normal_tasks, snoozed_tasks, completed_tasks = \
                sort_tasks_by_relevance(tasks)
        upper_model = build_tree_view_model(due_tasks + normal_tasks)
        self._upper_list.setModel(upper_model)
        lower_model = build_tree_view_model(snoozed_tasks)
        self._lower_list.setModel(lower_model)
        upper_model.itemChanged.connect(self._item_changed)
        lower_model.itemChanged.connect(self._item_changed)
        self._upper_list.setItemDelegateForColumn(1, CalendarDelegate(self))
        self._upper_list.setItemDelegateForColumn(2, CalendarDelegate(self))
        self._lower_list.setItemDelegateForColumn(1, CalendarDelegate(self))
        self._lower_list.setItemDelegateForColumn(2, CalendarDelegate(self))

    def _item_changed(self, item: QtGui.QStandardItem) -> None:
        task = item.data(TASK_ROLE)
        column = item.column()
        if column == 0:
            new_name = item.data(QtCore.Qt.DisplayRole)
            self.rename_task_requested.emit(task, new_name)
        elif column == 1:
            due = item.data(QtCore.Qt.DisplayRole)
            self.schedule_task_requested.emit(task, due)
        elif column == 2:
            snoozed = item.data(QtCore.Qt.DisplayRole)
            self.snooze_task_requested.emit(task, snoozed)
