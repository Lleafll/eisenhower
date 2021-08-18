from typing import Optional
from datetime import date
from dataclasses import replace
from pickle import load, dump
from pathlib import Path
from task import Task, Importance, SubTask
from history import History, Tasks


class TaskManager:
    def __init__(self, tasks: Tasks) -> None:
        self._history = History(tasks)

    def tasks(self) -> Tasks:
        return self._history.present()

    def add(self, task: Task) -> None:
        tasks = self._history.advance_history()
        tasks.append(task)

    def add_sub_task(self, task: Task) -> None:
        self._history.advance_history()
        task.sub_tasks.append(SubTask("New Subtask"))

    def delete(self, task: Task) -> None:
        tasks = self._history.advance_history()
        _delete(tasks, task)

    def replace(self, old_task: Task, new_task: Task) -> None:
        tasks = self._history.advance_history()
        _delete(tasks, old_task)
        tasks.append(new_task)

    def set_complete(self, task: Task, is_complete: bool = True) -> None:
        tasks = self._history.advance_history()
        _complete(tasks, task, is_complete)

    def schedule(self, task: Task, due: Optional[date]) -> None:
        tasks = self._history.advance_history()
        new_task = replace(task, due=due)
        _replace(tasks, task, new_task)

    def schedule_sub_task(self, sub_task: SubTask, due: Optional[date]) -> None:
        tasks = self._history.advance_history()
        new_task = replace(sub_task, due=due)
        _replace_sub_task(tasks, sub_task, new_task)

    def snooze(self, task: Task, time: Optional[date]) -> None:
        tasks = self._history.advance_history()
        new_task = replace(task, snooze=time)
        _replace(tasks, task, new_task)

    def snooze_sub_task(self, task: SubTask, time: Optional[date]) -> None:
        tasks = self._history.advance_history()
        new_task = replace(task, snooze=time)
        _replace_sub_task(tasks, task, new_task)

    def rename(self, task: Task, new_name: str) -> None:
        tasks = self._history.advance_history()
        new_task = replace(task, name=new_name)
        _replace(tasks, task, new_task)

    def rename_sub_task(self, sub_task: SubTask, new_name: str) -> None:
        tasks = self._history.advance_history()
        new_task = replace(sub_task, name=new_name)
        _replace_sub_task(tasks, sub_task, new_task)

    def set_importance(self, task: Task, importance: Importance) -> None:
        tasks = self._history.advance_history()
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


def _replace_sub_task(
        tasks: Tasks,
        old_sub_task: SubTask,
        new_sub_task: SubTask) -> None:
    try:
        for task in tasks:
            sub_tasks = task.sub_tasks
            if old_sub_task in sub_tasks:
                index = sub_tasks.index(old_sub_task)
                sub_tasks[index] = new_sub_task
    except ValueError:
        pass


def load_task_manager(import_path: Path) -> TaskManager:
    try:
        with open(import_path, "rb") as file:
            tasks: Tasks = load(file)
    except FileNotFoundError:
        tasks = []
    for i, task in enumerate(tasks):
        if not hasattr(task, "sub_tasks"):
            tasks[i] = Task(
                task.name,
                task.importance,
                task.due,
                task.snooze,
                task.completed,
                task.resources)
    return TaskManager(tasks)


def save_task_manager(export_path: Path, task_manager: TaskManager) -> None:
    with open(export_path, "wb") as file:
        return dump(task_manager.tasks(), file)
