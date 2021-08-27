from typing import Optional, Any, List
from datetime import date
from dataclasses import replace
from pickle import load, dump
from pathlib import Path
from task import Task, Importance, SubTask
from history import History, Tasks
from PySide2 import QtCore


class TaskManager:
    def __init__(self, tasks: Tasks) -> None:
        self._history = History(tasks)

    def tasks(self) -> Tasks:
        return self._history.present()

    def add(self, task: Task) -> None:
        tasks = self._history.advance_history()
        tasks.append(task)

    def add_sub_task(self, task: Task) -> None:
        tasks = self._history.advance_history()
        sub_tasks = list(task.sub_tasks)
        sub_tasks.append(SubTask("New SubTask"))
        new_task = replace(task, sub_tasks=tuple(sub_tasks))
        _replace(tasks, task, new_task)

    def delete(self, task: Task) -> None:
        tasks = self._history.advance_history()
        _delete(tasks, task)

    def delete_sub_task(self, task: SubTask) -> None:
        tasks = self._history.advance_history()
        _delete_sub_task(tasks, task)

    def replace(self, old_task: Task, new_task: Task) -> None:
        tasks = self._history.advance_history()
        _delete(tasks, old_task)
        tasks.append(new_task)

    def set_complete(self, task: Task, is_complete: bool = True) -> None:
        tasks = self._history.advance_history()
        _complete(tasks, task, is_complete)

    def schedule_sub_task(self, sub_task: SubTask, due: Optional[date]) -> None:
        tasks = self._history.advance_history()
        new_task = replace(sub_task, due=due)
        _replace_sub_task(tasks, sub_task, new_task)

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

    def remove_due_sub_task(self, sub_task: SubTask):
        tasks = self._history.advance_history()
        new_task = replace(sub_task, due=None)
        _replace_sub_task(tasks, sub_task, new_task)

    def remove_snooze(self, task: Task) -> None:
        tasks = self._history.advance_history()
        new_sub_tasks = list(replace(sub_task, snooze=None) for sub_task in task.sub_tasks)
        new_task = replace(task, sub_tasks=tuple(new_sub_tasks))
        _replace(tasks, task, new_task)

    def remove_snooze_sub_task(self, sub_task: SubTask) -> None:
        tasks = self._history.advance_history()
        new_task = replace(sub_task, snooze=None)
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


def _delete_sub_task(tasks: Tasks, sub_task: SubTask) -> None:
    for task in tasks:
        sub_tasks = task.sub_tasks
        if sub_task in sub_tasks:
            try:
                mutable_subtasks = list(sub_tasks)
                mutable_subtasks.remove(sub_task)
                new_task = replace(task, sub_tasks=tuple(mutable_subtasks))
                _replace(tasks, task, new_task)
            except ValueError:
                pass
            return


def _complete(tasks: Tasks, old_task: Task, is_complete: bool) -> None:
    for i, task in enumerate(tasks):
        if task == old_task:
            if is_complete:
                tasks[i] = replace(task, completed=date.today())
            else:
                tasks[i] = replace(task, completed=None)
            break


def _replace(tasks: Tasks, old_task: Task, new_task: Task) -> None:
    index = tasks.index(old_task)
    tasks[index] = new_task


def _replace_sub_task(
        tasks: Tasks,
        old_sub_task: SubTask,
        new_sub_task: SubTask) -> None:
    for task in tasks:
        sub_tasks = task.sub_tasks
        if old_sub_task in sub_tasks:
            index = sub_tasks.index(old_sub_task)
            mutable_sub_tasks = list(sub_tasks)
            mutable_sub_tasks[index] = new_sub_task
            new_task = replace(task, sub_tasks=tuple(mutable_sub_tasks))
            _replace(tasks, task, new_task)
            return


def _sanitize_task(task: Task) -> Task:
    return Task(
        task.name,
        task.importance,
        task.sub_tasks,
        task.completed)


def load_task_manager(import_path: Path) -> TaskManager:
    try:
        with open(import_path, "rb") as file:
            tasks: Tasks = load(file)
    except FileNotFoundError:
        tasks = []
    for i, task in enumerate(tasks):
        tasks[i] = _sanitize_task(task)
    return TaskManager(tasks)


def save_task_manager(export_path: Path, task_manager: TaskManager) -> None:
    with open(export_path, "wb") as file:
        return dump(task_manager.tasks(), file)
