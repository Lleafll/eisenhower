from datetime import date
from pathlib import Path
from pickle import dump, load
from typing import Optional, cast

from PySide6 import QtCore

from task import Task, SubTask, Importance


def sanitize_sub_task(
        sub_task: SubTask,
        importance: Importance,
        completed: Optional[date]) -> Task:
    due = sub_task.due
    if sub_task.due is not None and type(sub_task.due) != date:
        qdate_due = cast(QtCore.QDate, due)
        due: date = date(qdate_due.year(), qdate_due.month(), qdate_due.day())
    return Task(
        sub_task.name,
        importance,
        completed,
        due,
        sub_task.snooze)


def _sanitize_task(task: Task) -> list[Task]:
    if hasattr(task, "sub_tasks"):
        return [sanitize_sub_task(
            sub_task, task.importance, task.completed) for sub_task in task.sub_tasks]
    else:
        return [task]


class PickleSerializer:
    def __init__(self, path: Path):
        self._path = path

    def save(self, tasks: list[Task]) -> None:
        with open(self._path, "wb") as file:
            dump(tasks, file)

    def load(self) -> list[Task]:
        try:
            with open(self._path, "rb") as file:
                tasks = load(file)
        except FileNotFoundError:
            tasks = []
        sanitized_tasks = []
        for task in tasks:
            sanitized_tasks.extend(_sanitize_task(task))
        return sanitized_tasks
