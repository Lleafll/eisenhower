from typing import Optional, Iterable, Sequence
from datetime import date
from enum import Enum, auto
from PySide2 import QtWidgets, QtCore, QtGui
from task import (
        Task,
        has_due_date,
        has_snoozed_date,
        is_completed,
        Importance)


TASK_ROLE = QtCore.Qt.UserRole + 1


class Column(Enum):
    Name = auto()
    Due = auto()
    Snoozed = auto()
    Archived = auto()


class TreeViewWithContextMenu(QtWidgets.QTreeView):
    add_task_requested = QtCore.Signal()
    complete_task_requested = QtCore.Signal(Task)
    unarchive_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)
    set_important_requested = QtCore.Signal(Task)
    set_unimportant_requested = QtCore.Signal(Task)
    task_view_requested = QtCore.Signal(Task)

    def __init__(
            self,
            displayed_columns: Sequence[Column],
            color: QtGui.QColor,
            parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._displayed_columns = displayed_columns
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)
        self.setRootIsDecorated(False)
        self.setEditTriggers(
                QtWidgets.QAbstractItemView.EditKeyPressed |
                QtWidgets.QAbstractItemView.AnyKeyPressed |
                QtWidgets.QAbstractItemView.SelectedClicked)
        self.setAlternatingRowColors(True)
        palette = self.palette()
        base_color = color.lighter(115)
        palette.setColor(QtGui.QPalette.Base, base_color)
        palette.setColor(QtGui.QPalette.AlternateBase, color)
        self.setPalette(palette)
        self.doubleClicked.connect(lambda index: self.task_view_requested.emit(
            self.model().data(index, TASK_ROLE)))
        self.setStyleSheet(
            "QHeaderView::section {"
            "background-color: rgb(114, 118, 138);"
            "border: none;"
            "}")
        self.header().setSortIndicatorShown(True)
        self.header().setSectionsClickable(True)
        self.setSortingEnabled(True)

    def columns(self) -> Sequence[Column]:
        return self._displayed_columns

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        index = self.indexAt(point)
        context_menu = QtWidgets.QMenu()
        if index.isValid():
            rename_action = QtWidgets.QAction("Change")
            rename_action.triggered.connect(lambda: self.edit(index))
            context_menu.addAction(rename_action)
            task: Task = index.data(TASK_ROLE)
            if task.importance == Importance.Important:
                set_unimportant_task = QtWidgets.QAction("Make Unimportant")
                set_unimportant_task.triggered.connect(
                        lambda: self.set_unimportant_requested.emit(task))
                context_menu.addAction(set_unimportant_task)
            else:
                set_important_task = QtWidgets.QAction("Make Important")
                set_important_task.triggered.connect(
                        lambda: self.set_important_requested.emit(task))
                context_menu.addAction(set_important_task)
            if Column.Due in self._displayed_columns:
                if has_due_date(task):
                    remove_due_action = QtWidgets.QAction("Remove Due")
                    remove_due_action.triggered.connect(
                        lambda: self.remove_due_requested.emit(task))
                    context_menu.addAction(remove_due_action)
            if has_snoozed_date(
                    task) and Column.Snoozed in self._displayed_columns:
                remove_snooze_action = QtWidgets.QAction("Remove Snooze")
                remove_snooze_action.triggered.connect(
                    lambda: self.remove_snooze_requested.emit(task))
                context_menu.addAction(remove_snooze_action)
            if is_completed(task):
                if Column.Archived in self._displayed_columns:
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
        if len(context_menu.actions()) > 0:
            context_menu.exec_(self.viewport().mapToGlobal(point))


def _date_to_qdate(task_date: Optional[date]) -> QtCore.QDate:
    if task_date is None:
        return QtCore.QDate()
    if isinstance(task_date, QtCore.QDate):
        return task_date
    return QtCore.QDate(task_date.year, task_date.month, task_date.day)


def _build_date_item(date_: Optional[date]) -> QtGui.QStandardItem:
    qdate = _date_to_qdate(date_)
    item = QtGui.QStandardItem()
    item.setData(qdate, QtCore.Qt.DisplayRole)
    return item


def _build_due_date_item(date_: Optional[date]) -> QtGui.QStandardItem:
    return _build_date_item(date_)  # type: ignore


def _build_row(
        task: Task,
        columns: Sequence[Column]) -> Sequence[QtGui.QStandardItem]:
    items = []
    for column in columns:
        if column == Column.Name:
            item = QtGui.QStandardItem(task.name)
        elif column == Column.Due:
            item = _build_due_date_item(task.due)
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
