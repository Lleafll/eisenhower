from PySide2 import QtWidgets, QtCore, QtGui
from task import Task, has_due_date, has_snoozed_date, is_completed
from typing import Optional, Iterable, Sequence
from datetime import date
from enum import Enum, auto


TASK_ROLE = QtCore.Qt.UserRole + 1


class Column(Enum):
    Name = auto()
    Due = auto()
    Snoozed = auto()
    Archived = auto()


class TreeViewWithContextMenu(QtWidgets.QTreeView):
    add_task_requested = QtCore.Signal(str)
    complete_task_requested = QtCore.Signal(Task)
    unarchive_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)

    def __init__(
            self,
            displayed_columns: Sequence[Column],
            parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._displayed_columns = displayed_columns
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def columns(self) -> Sequence[Column]:
        return self._displayed_columns

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


def _build_row(
        task: Task,
        columns: Sequence[Column]) -> Sequence[QtGui.QStandardItem]:
    items = []
    for column in columns:
        if column == Column.Name:
            item = QtGui.QStandardItem(task.name)
        elif column == Column.Due:
            item = _build_date_item(task.due)
        elif column == Column.Snoozed:
            item = _build_date_item(
                    task.snooze if has_snoozed_date(task) else None)
        elif column == Column.Archived:
            item = _build_date_item(task.completed)
            item.setEditable(False)
        else:
            raise RuntimeError("Unhandled column")
        item.setData(task, role=TASK_ROLE)
        items.append(item)
    return items


def _set_rows(
        model: QtGui.QStandardItemModel,
        columns: Sequence[Column],
        tasks: Iterable[Task]) -> None:
    for task in tasks:
        row = _build_row(task, columns)
        model.appendRow(row)


def _set_header(
        model: QtGui.QStandardItemModel,
        columns: Sequence[Column]) -> None:
    header_labels = list([column.name for column in columns])
    model.setHorizontalHeaderLabels(header_labels)


def build_tree_view_model(
        columns: Sequence[Column],
        tasks: Iterable[Task]) -> QtGui.QStandardItemModel:
    model = QtGui.QStandardItemModel()
    _set_header(model, columns)
    _set_rows(model, columns, tasks)
    return model
