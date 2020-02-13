from PySide2 import QtWidgets, QtGui, QtCore
from task import Task, sort_tasks_by_relevance
from taskmanager import (
    TaskManager,
    load_task_manager,
    save_task_manager,
    Priority)
from typing import Optional, Sequence, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from treeviewwithcontextmenu import TreeViewWithContextMenu, TASK_ROLE


@dataclass(frozen=True)
class TaskManagerWrapper:
    instance: TaskManager
    path: Path


class MainWindowQt(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.showMaximized()
        self.setAcceptDrops(True)
        self._task_manager: Optional[TaskManagerWrapper] = None
        self._do_list = TreeViewWithContextMenu(self)
        self._decide_list = TreeViewWithContextMenu(self)
        self._delegate_list = TreeViewWithContextMenu(self)
        layout = QtWidgets.QHBoxLayout(self)
        for task_list in (
                self._do_list, self._decide_list, self._delegate_list):
            layout.addWidget(task_list)
            task_list.delete_task_requested.connect(self._delete_task)
            task_list.remove_due_requested.connect(self._set_due)
            task_list.remove_snooze_requested.connect(self._set_snooze)
        self._do_list.add_task_requested.connect(
                lambda text: self._add_task(text, Priority.do))
        self._decide_list.add_task_requested.connect(
                lambda text: self._add_task(text, Priority.decide))
        self._delegate_list.add_task_requested.connect(
                lambda text: self._add_task(text, Priority.delegate))
        self._update()

    def load_from_file(self, path: Path) -> None:
        task_manager = load_task_manager(path)
        if isinstance(task_manager, TaskManager):
            self._task_manager = TaskManagerWrapper(task_manager, path)
            self._update()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mime_data = event.mimeData()
        # DEBUG
        print(4)
        if mime_data.hasUrls():
            print(5)
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        # DEBUG
        print(6)
        path = event.mimeData().urls()[0]
        task_manager_path = Path(path.toLocalFile())
        self.load_from_file(task_manager_path)

    def _update(self) -> None:
        if self._task_manager is None:
            self._do_list.hide()
            self._decide_list.hide()
            self._delegate_list.hide()
        else:
            for priority, task_list in (
                    (Priority.do, self._do_list),
                    (Priority.decide, self._decide_list),
                    (Priority.delegate, self._delegate_list)):
                task_list.show()
                tasks = self._task_manager.instance.tasks(priority)
                model = _build_tree_view_model(tasks)
                task_list.setModel(model)
                model.itemChanged.connect(self._item_changed)

    def _item_changed(self, item: QtGui.QStandardItem) -> None:
        if self._task_manager is None:
            return
        task = item.data(TASK_ROLE)
        column = item.column()
        if column == 0:
            new_name = item.data(QtCore.Qt.DisplayRole)
            self._task_manager.instance.rename(task, new_name)
            self._update_and_save()
        elif column == 1:
            due = item.data(QtCore.Qt.DisplayRole)
            self._set_due(task, due)
        elif column == 2:
            snoozed = item.data(QtCore.Qt.DisplayRole)
            self._set_snooze(task, snoozed)

    def _update_and_save(self) -> None:
        if self._task_manager is None:
            return
        save_task_manager(self._task_manager.path, self._task_manager.instance)
        self._update()

    def _add_task(self, task_name: str, priority: Priority) -> None:
        if self._task_manager is None:
            return
        task = Task(task_name)
        self._task_manager.instance.add(task, priority)
        self._update_and_save()

    def _delete_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.delete(task)
        self._update_and_save()

    def _set_due(self, task: Task, due: Optional[date] = None) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.schedule(task, due)
        self._update_and_save()

    def _set_snooze(self, task: Task, snooze: Optional[date] = None) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.snooze(task, snooze)
        self._update_and_save()


def _date_to_qdate(date: Optional[date]) -> QtCore.QDate:
    if date is None:
        return QtCore.QDate()
    return QtCore.QDate(date.year, date.month, date.day)


def _build_date_item(date: Optional[date]) -> QtGui.QStandardItem:
    qdate = _date_to_qdate(date)
    item = QtGui.QStandardItem()
    item.setData(qdate, QtCore.Qt.DisplayRole)
    return item


def _build_row(task: Task) -> Tuple[QtGui.QStandardItem, ...]:
    name_item = QtGui.QStandardItem(task.name)
    due_item = _build_date_item(task.due)
    snoozed_item = _build_date_item(task.snooze)
    items = (name_item, due_item, snoozed_item)
    for item in items:
        item.setData(task, role=TASK_ROLE)
    return items


def _build_tree_view_model(
        tasks: Sequence[Task]) -> QtGui.QStandardItemModel:
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(("Name", "Due", "Snoozed"))
    for task in sort_tasks_by_relevance(tasks):
        row = _build_row(task)
        model.appendRow(row)
    return model
