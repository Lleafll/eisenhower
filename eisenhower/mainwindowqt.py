from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from datetime import date
from itertools import filterfalse
from PySide6 import QtWidgets, QtGui, QtCore

from mainpresenter import MainPresenter
from jsonserializer import JsonSerializer
from task import (
    Task,
    is_completed,
    is_urgent,
    is_important,
    Importance)
from taskmanager import TaskManager
from dividedtasksview import DividedTasksView
from tasksview import (
    TasksView, build_tree_view_model, Column)
from taskcreatordialogqt import TaskCreatorDialogQt


@dataclass(frozen=True)
class TaskManagerWrapper:
    instance: TaskManager
    path: Path


def _style_button(button: QtWidgets.QPushButton) -> None:
    button.setStyleSheet(
        "QPushButton:pressed {background-color: rgb(164, 168, 188)}"
        "QPushButton {background-color: rgb(114, 118, 138);"
        "border: 1px solid black; padding: 4px}"
        "QPushButton:disabled { background-color: rgb(50, 54, 76) }")


class MainWindowQt(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._serializer: Optional[JsonSerializer] = None
        self._presenter = MainPresenter(self)
        self._task_manager: Optional[TaskManagerWrapper] = None
        self.showMaximized()
        self.setWindowTitle("Eisenhower")
        self.setAcceptDrops(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(50, 54, 76))
        self.setPalette(palette)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._undo_button = QtWidgets.QPushButton("Undo")
        self._redo_button = QtWidgets.QPushButton("Redo")
        self._add_task_button = QtWidgets.QPushButton("Add Task")
        self._show_archive_button = QtWidgets.QPushButton("Show Archive")
        self._priority_button = QtWidgets.QPushButton("Priority Mode")
        self._priority_button.setCheckable(True)
        _style_button(self._undo_button)
        _style_button(self._redo_button)
        _style_button(self._add_task_button)
        _style_button(self._show_archive_button)
        _style_button(self._priority_button)
        button_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(self._add_task_button)
        button_layout.addWidget(self._undo_button)
        button_layout.addWidget(self._redo_button)
        button_layout.addWidget(self._show_archive_button)
        button_layout.addWidget(self._priority_button)
        button_layout.addStretch()
        self._do_list = DividedTasksView(
            "Do", QtGui.QColor(240, 98, 146), self)
        self._decide_list = DividedTasksView(
            "Decide", QtGui.QColor(255, 149, 157), self)
        self._delegate_list = DividedTasksView(
            "Delegate", QtGui.QColor(255, 215, 140), self)
        self._drop_list = DividedTasksView(
            "Drop", QtGui.QColor(128, 222, 234), self)
        task_layout = QtWidgets.QHBoxLayout()
        task_layout.setContentsMargins(0, 0, 0, 0)
        task_layout.setSpacing(5)
        layout.addLayout(task_layout)
        for task_list in (
                self._do_list,
                self._decide_list,
                self._delegate_list,
                self._drop_list):
            task_layout.addWidget(task_list)
            task_list.complete_task_requested.connect(
                self._presenter.complete_task)
            task_list.delete_task_requested.connect(
                self._presenter.delete_task)
            task_list.rename_task_requested.connect(
                self._presenter.rename_task)
            task_list.schedule_task_requested.connect(
                self._presenter.set_task_due)
            task_list.snooze_task_requested.connect(
                self._presenter.set_task_snooze)
            task_list.add_task_requested.connect(self._add_task)
            task_list.remove_due_requested.connect(
                lambda task: self._presenter.set_task_due(task, None))
            task_list.remove_snooze_requested.connect(
                lambda task: self._presenter.set_task_snooze(task, None))
            task_list.set_important_requested.connect(
                lambda task: self._presenter.set_importance(
                    task, Importance.Important))
            task_list.set_unimportant_requested.connect(
                lambda task: self._presenter.set_importance(
                    task, Importance.Unimportant))
        self._undo_button.clicked.connect(self._undo)
        self._redo_button.clicked.connect(self._redo)
        self._add_task_button.clicked.connect(self._add_task)
        self._show_archive_button.clicked.connect(self._show_archive)
        self._priority_button.toggled.connect(self._toggle_priority)
        self._archive_view = TasksView(
            (Column.Name, Column.Archived),
            QtGui.QColor(255, 255, 255),
            self)
        self._archive_view.setWindowFlag(QtGui.Qt.Window)
        self._archive_view.setWindowTitle("Task Archive")
        self._archive_view.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        self._archive_view.hide()
        self._archive_view.delete_task_requested.connect(
            self._presenter.delete_task)
        self._archive_view.unarchive_task_requested.connect(
            lambda task: self._presenter.complete_task(task, False))
        self._presenter.request_update()

    def load_from_file(self, path: Path) -> None:
        self._presenter.load_from_file(path)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        path = event.mimeData().urls()[0]
        task_manager_path = Path(path.toLocalFile())
        self.load_from_file(task_manager_path)

    def hide_lists(self) -> None:
        self._do_list.hide()
        self._decide_list.hide()
        self._delegate_list.hide()
        self._drop_list.hide()
        self._undo_button.hide()
        self._redo_button.hide()
        self._show_archive_button.hide()

    def update_tasks(self, tasks: list[Task]) -> None:
        non_archived_tasks = list(filterfalse(is_completed, tasks))
        archived_tasks = filter(is_completed, tasks)
        for filter_func, task_list in (
                (_is_do_task, self._do_list),
                (_is_decide_task, self._decide_list),
                (_is_delegate_task, self._delegate_list),
                (_is_drop_task, self._drop_list)):
            task_list.show()
            task_list_tasks = list(filter(filter_func, non_archived_tasks))
            task_list.add_tasks(task_list_tasks)
        archive_model = build_tree_view_model(
            self._archive_view.columns(), archived_tasks)
        self._archive_view.setModel(archive_model)
        self._undo_button.show()
        self._redo_button.show()
        self._show_archive_button.show()
        self._undo_button.setEnabled(
            self._task_manager.instance.is_undoable())
        self._redo_button.setEnabled(
            self._task_manager.instance.is_redoable())

    def _update_and_save(self) -> None:
        if self._task_manager is None:
            return
        assert self._serializer is not None
        self._serializer.save(self._task_manager.instance.tasks())
        self.update()

    def _add_task(self) -> None:
        task = TaskCreatorDialogQt.ask_new_task(self)
        if task is not None:
            self._presenter.add_task(task)

    def _undo(self) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.undo()
        self._update_and_save()

    def _redo(self) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.redo()
        self._update_and_save()

    def _show_archive(self) -> None:
        self._archive_view.show()

    def _toggle_priority(self, is_toggled: bool) -> None:
        if self._task_manager is None:
            return
        self._do_list.show_snoozed_tasks(not is_toggled)
        for task_list in (
                self._decide_list, self._delegate_list, self._drop_list):
            task_list.setHidden(is_toggled)


def _is_do_task(task: Task) -> bool:
    return is_important(task) and is_urgent(task)


def _is_decide_task(task: Task) -> bool:
    return is_important(task) and (not is_urgent(task))


def _is_delegate_task(task: Task) -> bool:
    return (not is_important(task)) and is_urgent(task)


def _is_drop_task(task: Task) -> bool:
    return (not is_important(task)) and (not is_urgent(task))
