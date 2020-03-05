from PySide2 import QtWidgets
from task import Task, DueDate, ImmediateType
from datetime import date
from typing import Optional


def _date_to_str(value: Optional[date]) -> str:
    if value is None:
        return ""
    else:
        return str(value)


def _due_date_to_str(value: Optional[DueDate]) -> str:
    if isinstance(value, ImmediateType):
        return "Immediate"
    else:
        return _date_to_str(value)


class TaskViewQt(QtWidgets.QWidget):
    def __init__(self, task: Task, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        text_field = QtWidgets.QLabel(task.name, self)
        due_field = QtWidgets.QLabel(_due_date_to_str(task.due), self)
        snooze_field = QtWidgets.QLabel(_date_to_str(task.snooze), self)
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.addWidget(text_field)
        inner_layout = QtWidgets.QHBoxLayout()
        inner_layout.addWidget(due_field)
        inner_layout.addWidget(snooze_field)
        outer_layout.addLayout(inner_layout)
