from task import Task
from typing import Sequence, Optional
from datetime import date
from dataclasses import replace
from pickle import load, dump
from pathlib import Path
from history import History, Tasks
from priority import Priority
from collections import defaultdict


class TaskManager:
    def __init__(self, tasks: Tasks = defaultdict(list)) -> None:
        self._history = History(tasks)

    def tasks(self, priority: Priority) -> Sequence[Task]:
        return self._history.present()[priority]

    def add(self, task: Task, priority: Priority) -> None:
        tasks = self._history.write_history()
        _add(tasks, task, priority)

    def delete(self, task: Task) -> None:
        tasks = self._history.write_history()
        _delete(tasks, task)

    def set_complete(self, task: Task, is_complete: bool = True) -> None:
        tasks = self._history.write_history()
        _complete(tasks, task, is_complete)

    def move(self, task: Task, priority: Priority) -> None:
        tasks = self._history.write_history()
        _delete(tasks, task)
        _add(tasks, task, priority)

    def schedule(self, task: Task, due: Optional[date]) -> None:
        tasks = self._history.write_history()
        new_task = replace(task, due=due)
        _replace(tasks, task, new_task)

    def snooze(self, task: Task, time: Optional[date]) -> None:
        tasks = self._history.write_history()
        new_task = replace(task, snooze=time)
        _replace(tasks, task, new_task)

    def rename(self, task: Task, new_name: str) -> None:
        tasks = self._history.write_history()
        new_task = replace(task, name=new_name)
        _replace(tasks, task, new_task)

    def is_undoable(self) -> bool:
        return self._history.has_past()

    def is_redoable(self) -> bool:
        return self._history.has_future()

    def undo(self) -> None:
        self._history.go_back_in_time()

    def redo(self) -> None:
        self._history.go_forward_in_time()


def _delete(tasks: Tasks, task: Task) -> None:
    for task_list in tasks.values():
        try:
            task_list.remove(task)
            break
        except ValueError:
            pass


def _complete(tasks: Tasks, old_task: Task, is_complete: bool) -> None:
    for task_list in tasks.values():
        for i, task in enumerate(task_list):
            if task == old_task:
                if is_complete:
                    task_list[i] = replace(task, completed=date.today())
                else:
                    task_list[i] = replace(task, completed=None)
                break


def _add(tasks: Tasks, task: Task, priority: Priority) -> None:
    tasks[priority].append(task)


def _replace(tasks: Tasks, old_task: Task, new_task: Task) -> None:
    for task_list in tasks.values():
        try:
            index = task_list.index(old_task)
            task_list[index] = new_task
            break
        except ValueError:
            pass


def load_task_manager(import_path: Path) -> TaskManager:
    try:
        with open(import_path, "rb") as file:
            task_manager = load(file)
    except FileNotFoundError:
        task_manager = TaskManager()
    for time_point in task_manager._history._tasks:
        for tasks in time_point.values():
            for i, task in enumerate(tasks):
                if not hasattr(task, "notes"):
                    tasks[i] = Task(
                            task.name, task.due, task.snooze, task.completed)
    return task_manager


def save_task_manager(export_path: Path, task_manager: TaskManager) -> None:
    with open(export_path, "wb") as file:
        return dump(task_manager, file)
