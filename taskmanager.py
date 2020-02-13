from task import Task
from typing import List, DefaultDict, Sequence, Optional
from enum import Enum
from collections import defaultdict
from datetime import date
from dataclasses import replace
from pickle import load, dump
from pathlib import Path


class Priority(Enum):
    do = 1
    decide = 2
    delegate = 3
    eliminate = 4


class TaskManager:
    def __init__(self) -> None:
        self._tasks: DefaultDict[Priority, List[Task]] = defaultdict(list)

    def tasks(self, priority: Priority) -> Sequence[Task]:
        return self._tasks[priority]

    def add(self, task: Task, priority: Priority) -> None:
        self._tasks[priority].append(task)

    def delete(self, task: Task) -> None:
        for task_list in self._tasks.values():
            try:
                task_list.remove(task)
                break
            except ValueError:
                pass

    def move(self, task: Task, priority: Priority) -> None:
        self.delete(task)
        self.add(task, priority)

    def schedule(self, task: Task, due: Optional[date]) -> None:
        new_task = replace(task, due=due)
        self._replace(task, new_task)

    def snooze(self, task: Task, time: Optional[date]) -> None:
        new_task = replace(task, snooze=time)
        self._replace(task, new_task)

    def rename(self, task: Task, new_name: str) -> None:
        new_task = replace(task, name=new_name)
        self._replace(task, new_task)

    def _replace(self, old_task: Task, new_task: Task) -> None:
        for task_list in self._tasks.values():
            try:
                index = task_list.index(old_task)
                task_list[index] = new_task
                break
            except ValueError:
                pass


def load_task_manager(import_path: Path) -> TaskManager:
    try:
        with open(import_path, "rb") as file:
            return load(file)
    except FileNotFoundError:
        return TaskManager()


def save_task_manager(export_path: Path, task_manager: TaskManager) -> None:
    with open(export_path, "wb") as file:
        return dump(task_manager, file)
