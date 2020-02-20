from PySide2 import QtWidgets, QtCore, QtGui
from task import Task, has_due_date, has_snoozed_date, is_completed
from typing import Optional, Tuple, Iterable
from datetime import date


TASK_ROLE = QtCore.Qt.UserRole + 1


class TreeViewWithContextMenu(QtWidgets.QTreeView):
    add_task_requested = QtCore.Signal(str)
    complete_task_requested = QtCore.Signal(Task)
    unarchive_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        index = self.indexAt(point)
        context_menu = QtWidgets.QMenu()
        if index.isValid():
            task = index.data(TASK_ROLE)
            if has_due_date(task):
                remove_due_action = QtWidgets.QAction("Remove Due")
                remove_due_action.triggered.connect(
                        lambda: self.remove_due_requested.emit(task))
                context_menu.addAction(remove_due_action)
            if has_snoozed_date(task):
                remove_snooze_action = QtWidgets.QAction("Remove Snooze")
                remove_snooze_action.triggered.connect(
                        lambda: self.remove_snooze_requested.emit(task))
                context_menu.addAction(remove_snooze_action)
            if is_completed(task):
                unarchive_action = QtWidgets.QAction("Unarchive")
                unarchive_action.triggered.connect(
                        lambda: self.unarchive_task_requested.emit(task))
                context_menu.addAction(unarchive_action)
            else:
                complete_action = QtWidgets.QAction("Complete")
                complete_action.triggered.connect(
                        lambda: self.complete_task_requested.emit(task))
                context_menu.addAction(complete_action)
            delete_action = QtWidgets.QAction("Delete")
            delete_action.triggered.connect(
                    lambda: self.delete_task_requested.emit(task))
            context_menu.addAction(delete_action)
        else:
            add_task_action = QtWidgets.QAction("Add Task")
            add_task_action.triggered.connect(
                    lambda: self.add_task_requested.emit("New Task"))
            context_menu.addAction(add_task_action)
        context_menu.exec_(self.viewport().mapToGlobal(point))


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
    archived_item = _build_date_item(task.completed)
    archived_item.setEditable(False)
    items = (name_item, due_item, snoozed_item, archived_item)
    for item in items:
        item.setData(task, role=TASK_ROLE)
    return items


def build_tree_view_model(
        tasks: Iterable[Task]) -> QtGui.QStandardItemModel:
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(("Name", "Due", "Snoozed", "Archived"))
    for task in tasks:
        row = _build_row(task)
        model.appendRow(row)
    return model
