from typing import Sequence, cast
from datetime import date
from PySide6 import QtWidgets, QtCore, QtGui
from tasksview import (
    TasksView, TASK_ROLE, build_tree_view_model, Column)
from task import Task, sort_tasks_by_relevance


class CalendarDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(
            self,
            parent: QtWidgets.QWidget,
            _: QtWidgets.QStyleOptionViewItem,
            _2: QtCore.QModelIndex) -> QtWidgets.QWidget:
        date_edit = QtWidgets.QDateEdit(parent)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd.MM.yyyy")
        return date_edit

    def setEditorData(
            self,
            editor: QtWidgets.QWidget,
            index: QtCore.QModelIndex) -> None:
        editor = cast(QtWidgets.QDateEdit, editor)
        date_ = index.model().data(index, QtCore.Qt.DisplayRole)
        if date_.isNull():
            date_ = QtCore.QDate.currentDate()
        editor.setDate(date_)

    def setModelData(
            self,
            editor: QtWidgets.QWidget,
            model: QtCore.QAbstractItemModel,
            index: QtCore.QModelIndex) -> None:
        editor = cast(QtWidgets.QDateEdit, editor)
        model.setData(index, editor.date())


class ItemWordWrap(QtWidgets.QStyledItemDelegate):
    def sizeHint(
            self,
            option: QtWidgets.QStyleOption,
            index: QtCore.QModelIndex) -> QtCore.QSize:
        size = super().sizeHint(option, index)
        size.setHeight(35)
        return size


class DividedTasksView(QtWidgets.QWidget):
    add_task_requested = QtCore.Signal()
    complete_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    rename_task_requested = QtCore.Signal(Task, str)
    schedule_task_requested = QtCore.Signal(Task, date)
    snooze_task_requested = QtCore.Signal(Task, date)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)
    set_important_requested = QtCore.Signal(Task)
    set_unimportant_requested = QtCore.Signal(Task)

    def __init__(
            self,
            header_text: str,
            color: QtGui.QColor,
            parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        header_label = QtWidgets.QLabel(header_text, self)
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_label_font = header_label.font()
        header_label_font.setPointSize(14)
        header_label.setFont(header_label_font)
        header_label_palette = header_label.palette()
        header_label_palette.setColor(
            header_label.foregroundRole(), QtGui.QColor(114, 118, 138))
        header_label.setPalette(header_label_palette)
        self._upper_list = TasksView(
            (Column.Name, Column.Due, Column.Snoozed), color, self)
        self._lower_list = TasksView(
            (Column.Name, Column.Due, Column.Snoozed), color, self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(header_label)
        for task_list in (self._upper_list, self._lower_list):
            layout.addWidget(task_list)
            task_list.setWordWrap(True)
            task_list.add_task_requested.connect(self.add_task_requested)
            task_list.complete_task_requested.connect(
                self.complete_task_requested)
            task_list.delete_task_requested.connect(self.delete_task_requested)
            task_list.set_important_requested.connect(
                self.set_important_requested)
            task_list.set_unimportant_requested.connect(
                self.set_unimportant_requested)
            task_list.remove_snooze_requested.connect(self.remove_snooze_requested)
            task_list.remove_due_requested.connect(
                self.remove_due_requested)
        self._upper_list.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)
        self._lower_list.sortByColumn(2, QtCore.Qt.SortOrder.AscendingOrder)

    def add_tasks(self, tasks: Sequence[Task]) -> None:
        due_tasks, normal_tasks, snoozed_tasks, _ = \
            sort_tasks_by_relevance(tasks)
        _build_model_and_connect(
            self._upper_list, due_tasks + normal_tasks, self)
        _build_model_and_connect(self._lower_list, snoozed_tasks, self)

    def show_snoozed_tasks(self, should_show: bool = True) -> None:
        self._lower_list.setVisible(should_show)

    def item_changed(
            self,
            task_list: TasksView,
            item: QtGui.QStandardItem) -> None:
        task = item.data(TASK_ROLE)
        column = task_list.columns()[item.column()]
        self._task_item_changed(item, task, column)

    def _task_item_changed(
            self,
            item: QtGui.QStandardItem,
            task: Task,
            column: Column) -> None:
        if column == Column.Name:
            new_name = item.data(QtCore.Qt.DisplayRole)
            self.rename_task_requested.emit(task, new_name)
        elif column == Column.Due:
            due = item.data(QtCore.Qt.DisplayRole)
            self.schedule_task_requested.emit(task, _qdate_to_date(due))
        elif column == Column.Snoozed:
            snoozed = item.data(QtCore.Qt.DisplayRole)
            self.snooze_task_requested.emit(task, _qdate_to_date(snoozed))


def _build_model_and_connect(
        task_list: TasksView,
        tasks: Sequence[Task],
        view: DividedTasksView) -> None:
    model = build_tree_view_model(task_list.columns(), tasks)
    task_list.setModel(model)
    task_list.expandAll()
    header = task_list.header()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
    for i in range(1, 3):
        header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.resizeSection(i, 80)
    header.setStretchLastSection(False)
    model.itemChanged.connect(lambda item: view.item_changed(task_list, item))
    task_list.setItemDelegateForColumn(0, ItemWordWrap(task_list))
    for i in (1, 2):
        task_list.setItemDelegateForColumn(i, CalendarDelegate(task_list))


def _qdate_to_date(qdate: QtCore.QDate) -> date:
    return date(qdate.year(), qdate.month(), qdate.day())
