from pathlib import Path
from typing import Optional, Type, TypeVar
from dataclasses import dataclass

from task import Task
from jsonserializer import JsonSerializer
from taskmanager import TaskManager


_Serializer = TypeVar("_Serializer")


class MainPresenter:
    def __init__(
            self,
            view: "MainWindowQt",
            serializer: _Serializer = JsonSerializer) -> None:
        self._view = view
        self._serializer_type = serializer
        self._serializer: Optional[_Serializer] = None
        self._task_manager: Optional[TaskManager] = None

    def load_from_file(self, path: Path) -> None:
        self._serializer = self._serializer_type(path)
        self._task_manager = TaskManager(self._serializer.load())
        self._view.setWindowTitle(path.name)
        self.request_update()

    def request_update(self) -> None:
        if self._task_manager is None:
            self._view.hide_lists()
        else:
            self._view.update_tasks(self._task_manager.tasks())

    def _save_and_update_view(self) -> None:
        assert self._task_manager is not None
        assert self._serializer is not None
        self._serializer.save(self._task_manager.tasks())
        self._view.update_tasks(self._task_manager.tasks())

    def add_task(self, task: Task) -> None:
        assert self._task_manager is not None
        self._task_manager.add(task)
        self._save_and_update_view()

    def complete_task(self, task: Task) -> None:
        assert self._task_manager is not None
        self._task_manager.set_complete(task)
        self._save_and_update_view()

    def delete_task(self, task: Task) -> None:
        assert self._task_manager is not None
        self._task_manager.delete(task)
        self._save_and_update_view()

    def rename_task(self, task: Task, name: str) -> None:
        assert self._task_manager is not None
        self._task_manager.rename(task, name)
        self._save_and_update_view()
