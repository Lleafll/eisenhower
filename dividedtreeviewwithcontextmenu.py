from PySide2 import QtWidgets, QtCore, QtGui
from treeviewwithcontextmenu import (
        TreeViewWithContextMenu, TASK_ROLE, build_tree_view_model, Column)
from task import Task, sort_tasks_by_relevance
from typing import Sequence
from datetime import date


class CalendarDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)

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


class ItemWordWrap(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

    def sizeHint(
            self,
            option: QtWidgets.QStyleOption,
            index: QtCore.QModelIndex) -> int:
        size = super().sizeHint(option, index)
        size.setHeight(35)
        return size


class SeparatedTreeViewWithContextMenu(QtWidgets.QWidget):
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
    task_view_requested = QtCore.Signal(Task)

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
        self._upper_list = TreeViewWithContextMenu(
                (Column.Name, Column.Due, Column.Snoozed), color, self)
        self._lower_list = TreeViewWithContextMenu(
                (Column.Name, Column.Due, Column.Snoozed), color, self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(1)
        layout.addWidget(header_label)
        for task_list in (self._upper_list, self._lower_list):
            layout.addWidget(task_list)
            task_list.setWordWrap(True)
            task_list.add_task_requested.connect(self.add_task_requested)
            task_list.complete_task_requested.connect(
                    self.complete_task_requested)
            task_list.delete_task_requested.connect(self.delete_task_requested)
            task_list.remove_due_requested.connect(self.remove_due_requested)
            task_list.remove_snooze_requested.connect(
                    self.remove_snooze_requested)
            task_list.set_important_requested.connect(
                    self.set_important_requested)
            task_list.set_unimportant_requested.connect(
                    self.set_unimportant_requested)
            task_list.task_view_requested.connect(self.task_view_requested)
        self._upper_list.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)
        self._lower_list.sortByColumn(2, QtCore.Qt.SortOrder.AscendingOrder)

    def add_tasks(self, tasks: Sequence[Task]) -> None:
        due_tasks, normal_tasks, snoozed_tasks, completed_tasks = \
                sort_tasks_by_relevance(tasks)
        _build_model_and_connect(
                self._upper_list, due_tasks + normal_tasks, self)
        _build_model_and_connect(self._lower_list, snoozed_tasks, self)

    def _item_changed(
            self,
            task_list: TreeViewWithContextMenu,
            item: QtGui.QStandardItem) -> None:
        task = item.data(TASK_ROLE)
        column_index = item.column()
        column = task_list.columns()[column_index]
        if column == Column.Name:
            new_name = item.data(QtCore.Qt.DisplayRole)
            self.rename_task_requested.emit(task, new_name)
        elif column == Column.Due:
            due = item.data(QtCore.Qt.DisplayRole)
            self.schedule_task_requested.emit(task, due)
        elif column == Column.Snoozed:
            snoozed = item.data(QtCore.Qt.DisplayRole)
            self.snooze_task_requested.emit(task, snoozed)


def _build_model_and_connect(
        task_list: TreeViewWithContextMenu,
        tasks: Sequence[Task],
        view: SeparatedTreeViewWithContextMenu) -> None:
    model = build_tree_view_model(task_list.columns(), tasks)
    task_list.setModel(model)
    header = task_list.header()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
    for i in range(1, 3):
        header.setSectionResizeMode(
                i, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.resizeSection(i, 80)
    header.setStretchLastSection(False)
    model.itemChanged.connect(lambda item: view._item_changed(task_list, item))
    task_list.setItemDelegateForColumn(0, ItemWordWrap(task_list))
    for i in (1, 2):
        task_list.setItemDelegateForColumn(i, CalendarDelegate(task_list))
