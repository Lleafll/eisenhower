from treeviewwithcontextmenu import TreeViewWithContextMenu, TASK_ROLE
from PySide2 import QtWidgets, QtCore, QtGui
from task import Task, has_snoozed_date, sort_tasks_by_relevance
from typing import Sequence, Optional, Tuple
from datetime import date


class SeparatedTreeViewWithContextMenu(QtWidgets.QWidget):
    add_task_requested = QtCore.Signal(str)
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
            task_list.delete_task_requested.connect(self.delete_task_requested)
            task_list.remove_due_requested.connect(self.remove_due_requested)
            task_list.remove_snooze_requested.connect(
                    self.remove_snooze_requested)

    def add_tasks(self, tasks: Sequence[Task]) -> None:
        due_tasks, normal_tasks, snoozed_tasks = sort_tasks_by_relevance(tasks)
        upper_model = _build_tree_view_model(due_tasks + normal_tasks)
        self._upper_list.setModel(upper_model)
        lower_model = _build_tree_view_model(snoozed_tasks)
        self._lower_list.setModel(lower_model)
        upper_model.itemChanged.connect(self._item_changed)
        lower_model.itemChanged.connect(self._item_changed)

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


def _date_to_qdate(task_date: Optional[date]) -> QtCore.QDate:
    if task_date is None:
        return QtCore.QDate()
    if isinstance(task_date, QtCore.QDate):
        return task_date
    return QtCore.QDate(task_date.year, task_date.month, task_date.day)


def _build_date_item(date: Optional[date]) -> QtGui.QStandardItem:
    qdate = _date_to_qdate(date)
    item = QtGui.QStandardItem()
    item.setData(qdate, QtCore.Qt.DisplayRole)
    return item


def _build_row(task: Task) -> Tuple[QtGui.QStandardItem, ...]:
    name_item = QtGui.QStandardItem(task.name)
    due_item = _build_date_item(task.due)
    snoozed_item = _build_date_item(
            task.snooze if has_snoozed_date(task) else None)
    items = (name_item, due_item, snoozed_item)
    for item in items:
        item.setData(task, role=TASK_ROLE)
    return items


def _build_tree_view_model(
        tasks: Sequence[Task]) -> QtGui.QStandardItemModel:
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(("Name", "Due", "Snoozed"))
    for task in tasks:
        row = _build_row(task)
        model.appendRow(row)
    return model
