from PySide2 import QtWidgets, QtGui
from task import Task
from taskmanager import (
        TaskManager, load_task_manager, save_task_manager, Priority)
from typing import Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from dividedtreeviewwithcontextmenu import SeparatedTreeViewWithContextMenu


@dataclass(frozen=True)
class TaskManagerWrapper:
    instance: TaskManager
    path: Path


class MainWindowQt(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("Eisenhower")
        self.setAcceptDrops(True)
        self._task_manager: Optional[TaskManagerWrapper] = None
        layout = QtWidgets.QVBoxLayout(self)
        self._undo_button = QtWidgets.QPushButton("Undo")
        self._redo_button = QtWidgets.QPushButton("Redo")
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(self._undo_button)
        button_layout.addWidget(self._redo_button)
        button_layout.addStretch()
        self._do_list = SeparatedTreeViewWithContextMenu(self)
        self._decide_list = SeparatedTreeViewWithContextMenu(self)
        self._delegate_list = SeparatedTreeViewWithContextMenu(self)
        task_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(task_layout)
        for task_list in (
                self._do_list, self._decide_list, self._delegate_list):
            task_layout.addWidget(task_list)
            task_list.complete_task_requested.connect(self._complete_task)
            task_list.delete_task_requested.connect(self._delete_task)
            task_list.rename_task_requested.connect(self._rename_task)
            task_list.schedule_task_requested.connect(self._set_due)
            task_list.snooze_task_requested.connect(self._set_snooze)
            task_list.remove_due_requested.connect(self._set_due)
            task_list.remove_snooze_requested.connect(self._set_snooze)
        self._undo_button.clicked.connect(self._undo)
        self._redo_button.clicked.connect(self._redo)
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
            self._undo_button.hide()
            self._redo_button.hide()
        else:
            for priority, task_list in (
                    (Priority.do, self._do_list),
                    (Priority.decide, self._decide_list),
                    (Priority.delegate, self._delegate_list)):
                task_list.show()
                tasks = self._task_manager.instance.tasks(priority)
                task_list.add_tasks(tasks)
            self._undo_button.show()
            self._redo_button.show()
            self._undo_button.setEnabled(
                    self._task_manager.instance.is_undoable())
            self._redo_button.setEnabled(
                    self._task_manager.instance.is_redoable())

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

    def _complete_task(self, task: Task) -> None:
        if self._task_manager is None:
            return
        self._task_manager.instance.complete(task)
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
