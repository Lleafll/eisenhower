from pathlib import Path
from typing import Optional, Type, TypeVar
from dataclasses import dataclass

from jsonserializer import JsonSerializer
from taskmanager import TaskManager


@dataclass(frozen=True)
class _TaskManagerWrapper:
    instance: TaskManager
    path: Path


_Serializer = TypeVar("_Serializer")


class MainPresenter:
    def __init__(
            self,
            view: "MainWindowQt",
            serializer: _Serializer = JsonSerializer) -> None:
        self._view = view
        self._serializer_type = serializer
        self._serializer: Optional[_Serializer] = None
        self._task_manager: Optional[_TaskManagerWrapper] = None

    def load_from_file(self, path: Path) -> None:
        self._serializer = self._serializer_type(path)
        task_manager = TaskManager(self._serializer.load())
        self._task_manager = _TaskManagerWrapper(task_manager, path)
        self._view.setWindowTitle(path.name)
        self._view.update_tasks(task_manager.tasks())
