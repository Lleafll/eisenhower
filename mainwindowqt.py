from PySide2 import QtWidgets, QtGui
from task import (
        Task,
        is_completed,
        has_due_date,
        is_important,
        DueDate,
        Immediate,
        Importance)
from taskmanager import (
        TaskManager, load_task_manager, save_task_manager)
from typing import Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from dividedtreeviewwithcontextmenu import SeparatedTreeViewWithContextMenu
from treeviewwithcontextmenu import (
        TreeViewWithContextMenu, build_tree_view_model, Column)
from itertools import filterfalse
from taskcreatordialog import TaskCreatorDialogQt


@dataclass(frozen=True)
class TaskManagerWrapper:
    instance: TaskManager
    path: Path


def _style_button(button: QtWidgets.QPushButton) -> None:
    button.setStyleSheet(
            "QPushButton:pressed {background-color: rgb(164, 168, 188)}" \
                    "QPushButton {background-color: rgb(114, 118, 138); border: 1px solid black; padding: 4px}" \
            "QPushButton:disabled { background-color: rgb(50, 54, 76) }")


class MainWindowQt(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("Eisenhower")
        self.setAcceptDrops(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(50, 54, 76))
        self.setPalette(palette)
        self._task_manager: Optional[TaskManagerWrapper] = None
        layout = QtWidgets.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self._undo_button = QtWidgets.QPushButton("Undo")
        self._redo_button = QtWidgets.QPushButton("Redo")
        self._add_task_button = QtWidgets.QPushButton("Add Task")
        self._show_archive_button = QtWidgets.QPushButton("Show Archive")
        _style_button(self._undo_button)
        _style_button(self._redo_button)
        _style_button(self._add_task_button)
        _style_button(self._show_archive_button)
        button_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(self._add_task_button)
        button_layout.addWidget(self._undo_button)
        button_layout.addWidget(self._redo_button)
        button_layout.addWidget(self._show_archive_button)
        button_layout.addStretch()
        self._do_list = SeparatedTreeViewWithContextMenu(
                "Do", QtGui.QColor(240, 98, 146), self)
        self._decide_list = SeparatedTreeViewWithContextMenu(
                "Decide", QtGui.QColor(255, 149, 157), self)
        self._delegate_list = SeparatedTreeViewWithContextMenu(
                "Delegate", QtGui.QColor(255, 215, 140), self)
        self._drop_list = SeparatedTreeViewWithContextMenu(
                "Drop", QtGui.QColor(128, 222, 234), self)
        task_layout = QtWidgets.QHBoxLayout()
        task_layout.setMargin(0)
        task_layout.setSpacing(5)
        layout.addLayout(task_layout)
        for task_list in (
                self._do_list,
                self._decide_list,
                self._delegate_list,
                self._drop_list):
            task_layout.addWidget(task_list)
            task_list.complete_task_requested.connect(self._complete_task)
            task_list.delete_task_requested.connect(self._delete_task)
            task_list.rename_task_requested.connect(self._rename_task)
            task_list.schedule_task_requested.connect(self._set_due)
            task_list.snooze_task_requested.connect(self._set_snooze)
            task_list.remove_due_requested.connect(self._set_due)
            task_list.remove_snooze_requested.connect(self._set_snooze)
            task_list.add_task_requested.connect(self._add_task)
            task_list.set_immediate_requested.connect(
                    lambda task: self._set_due(task, Immediate))
            task_list.set_important_requested.connect(
                    lambda task: self._set_importance(
                        task, Importance.Important))
            task_list.set_unimportant_requested.connect(
                    lambda task: self._set_importance(
                        task, Importance.Unimportant))
            task_list.task_view_requested.connect(self._open_task)
        self._undo_button.clicked.connect(self._undo)
        self._redo_button.clicked.connect(self._redo)
        self._add_task_button.clicked.connect(self._add_task)
        self._show_archive_button.clicked.connect(self._show_archive)
        self._archive_view = TreeViewWithContextMenu(
                (Column.Name, Column.Archived),
                QtGui.QColor(255, 255, 255),
                self)
        self._archive_view.setWindowFlag(QtGui.Qt.Window)
        self._archive_view.setWindowTitle("Task Archive")
        self._archive_view.hide()
        self._archive_view.delete_task_requested.connect(self._delete_task)
        self._archive_view.unarchive_task_requested.connect(
                self._unarchive_task)
        self._update()

    def load_from_file(self, path: Path) -> None:
        task_manager = load_task_manager(path)
        if isinstance(task_manager, TaskManager):
            self._task_manager = TaskManagerWrapper(task_manager, path)
            self.setWindowTitle(path.name)
            self._update()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        path = event.mimeData().urls()[0]
        task_manager_path = Path(path.toLocalFile())
        self.load_from_file(task_manager_path)

    def _update(self) -> None:
        if self._task_manager is None:
            self._do_list.hide()
            self._decide_list.hide()
            self._delegate_list.hide()
            self._drop_list.hide()
            self._undo_button.hide()
            self._redo_button.hide()
            self._show_archive_button.hide()
        else:
            tasks = self._task_manager.instance.tasks()
            non_archived_tasks = list(filterfalse(is_completed, tasks))
            archived_tasks = filter(is_completed, tasks)
            for filter_func, task_list in (
                    (_is_do_task, self._do_list),
                    (_is_decide_task, self._decide_list),
                    (_is_delegate_task, self._delegate_list),
                    (_is_drop_task, self._drop_list)):
                task_list.show()
                task_list_tasks = list(filter(filter_func, non_archived_tasks))
                if len(task_list_tasks) > 0:
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
        save_task_manager(self._task_manager.path, self._task_manager.instance)
        self._update()

    def _add_task(self) -> None:
        if self._task_manager is None:
            return
        task = TaskCreatorDialogQt.askNewTask(self)
        if task is None:
            return
        self._task_manager.instance.add(task)
        self._update_and_save()

    def _open_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        new_task = TaskCreatorDialogQt.askNewTask(self, task)
        if new_task is None:
            return
        self._task_manager.instance.replace(task, new_task)
        self._update_and_save()

    def _complete_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.set_complete(task)
        self._update_and_save()

    def _delete_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.delete(task)
        self._update_and_save()

    def _rename_task(self, task: Task, name: str) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.rename(task, name)
        self._update_and_save()

    def _set_due(self, task: Task, due: Optional[DueDate] = None) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.schedule(task, due)
        self._update_and_save()

    def _set_snooze(self, task: Task, snooze: Optional[date] = None) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.snooze(task, snooze)
        self._update_and_save()

    def _set_importance(self, task: Task, importance: Importance) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.set_importance(task, importance)
        self._update_and_save()

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

    def _unarchive_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.set_complete(task, False)
        self._update_and_save()


def _is_do_task(task: Task) -> bool:
    return is_important(task) and has_due_date(task)


def _is_decide_task(task: Task) -> bool:
    return is_important(task) and (not has_due_date(task))


def _is_delegate_task(task: Task) -> bool:
    return (not is_important(task)) and has_due_date(task)


def _is_drop_task(task: Task) -> bool:
    return (not is_important(task)) and (not has_due_date(task))
