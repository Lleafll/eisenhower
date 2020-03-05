from PySide2 import QtWidgets
from typing import Iterable, Optional
from task import Task
from taskviewqt import TaskViewQt


class TasksViewQt(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._layout: Optional[QtWidgets.QVBoxLayout] = None

    def set_tasks(self, tasks: Iterable[Task]) -> None:
        self._layout = QtWidgets.QVBoxLayout(self)
        for task in tasks:
            self._layout.addWidget(TaskViewQt(task, self))
        self._layout.addStretch()
