from task import Task, Importance, DueDate
from typing import Optional
from datetime import date
from dataclasses import replace
from pickle import load, dump
from pathlib import Path
from history import History, Tasks


class TaskManager:
    def __init__(self, tasks: Tasks = []) -> None:
        self._history = History(tasks)

    def tasks(self) -> Tasks:
        return self._history.present()

    def add(self, task: Task) -> None:
        tasks = self._history.write_history()
        tasks.append(task)

    def delete(self, task: Task) -> None:
        tasks = self._history.write_history()
        _delete(tasks, task)

    def set_complete(self, task: Task, is_complete: bool = True) -> None:
        tasks = self._history.write_history()
        _complete(tasks, task, is_complete)

    def schedule(self, task: Task, due: Optional[DueDate]) -> None:
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

    def set_importance(self, task: Task, importance: Importance) -> None:
        tasks = self._history.write_history()
        new_task = replace(task, importance=importance)
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
    try:
        tasks.remove(task)
    except ValueError:
        pass


def _complete(tasks: Tasks, old_task: Task, is_complete: bool) -> None:
    for i, task in enumerate(tasks):
        if task == old_task:
            if is_complete:
                tasks[i] = replace(task, completed=date.today())
            else:
                tasks[i] = replace(task, completed=None)
            break


def _replace(tasks: Tasks, old_task: Task, new_task: Task) -> None:
    try:
        index = tasks.index(old_task)
        tasks[index] = new_task
    except ValueError:
        pass


def load_task_manager(import_path: Path) -> TaskManager:
    try:
        with open(import_path, "rb") as file:
            tasks: Tasks = load(file)
    except FileNotFoundError:
        tasks = []
    return TaskManager(tasks)


def save_task_manager(export_path: Path, task_manager: TaskManager) -> None:
    with open(export_path, "wb") as file:
        return dump(task_manager.tasks(), file)
