from datetime import date
from enum import Enum, auto
from typing import Optional, Iterable, Sequence
from PySide6 import QtWidgets, QtCore, QtGui
from task import (
    Task,
    is_urgent,
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
            QtWidgets.QAbstractItemView.SelectedClicked |
            QtWidgets.QAbstractItemView.DoubleClicked)
        self.setAlternatingRowColors(True)
        palette = self.palette()
        base_color = color.lighter(115)
        palette.setColor(QtGui.QPalette.Base, base_color)
        palette.setColor(QtGui.QPalette.AlternateBase, color)
        self.setPalette(palette)
        self.setStyleSheet(
            "QHeaderView::section {"
            "background-color: rgb(114, 118, 138);"
            "border: none;"
            "}")
        self.header().setSortIndicatorShown(True)
        self.header().setSectionsClickable(True)
        self.setSortingEnabled(True)
        self.setItemsExpandable(False)

    def columns(self) -> Sequence[Column]:
        return self._displayed_columns

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        actions: list[QtGui.QAction] = []

        def add_action(name: str, signal: QtCore.Signal) -> None:
            set_unimportant_task = QtGui.QAction(name)
            set_unimportant_task.triggered.connect(lambda: signal.emit(task))
            actions.append(set_unimportant_task)

        if (index := self.indexAt(point)).isValid():
            task: Task = index.data(TASK_ROLE)
            if task.importance == Importance.Important:
                add_action("Make Unimportant", self.set_unimportant_requested)
            else:
                add_action("Make Important", self.set_important_requested)
            if Column.Due in self._displayed_columns:
                if is_urgent(task):
                    add_action("Remove Due", self.remove_due_requested)
            if has_snoozed_date(
                    task) and Column.Snoozed in self._displayed_columns:
                add_action("Remove Snooze", self.remove_snooze_requested)
            if is_completed(task):
                if Column.Archived in self._displayed_columns:
                    add_action("Unarchive", self.unarchive_task_requested)
            else:
                add_action("Complete", self.complete_task_requested)
            add_action("Delete", self.delete_task_requested)
        context_menu = QtWidgets.QMenu(self)
        context_menu.exec(actions, self.viewport().mapToGlobal(point))


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
    item = _build_date_item(date_)
    if date_ is not None and date_ <= date.today():
        font = item.font()
        font.setBold(True)
        item.setFont(font)
    return item


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
    root_item = model.invisibleRootItem()
    for task in tasks:
        row = _build_row(task, columns)
        root_item.appendRow(row)


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
