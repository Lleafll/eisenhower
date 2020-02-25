from pickle import load
from taskmanager import save_task_manager, TaskManager
from priority import Priority
from task import Task, Immediate, Importance
from history import Tasks
from pathlib import Path
from typing import Any, Generator


def _convert_tasks(
        old_tasks: Any,
        immediate: bool,
        importance: Importance) -> Generator[Task, None, None]:
    for old_task in old_tasks:
        if immediate:
            due_date = Immediate if old_task.due is None else old_task.due
        else:
            due_date = old_task.due
        yield Task(
                old_task.name,
                importance,
                due_date,
                old_task.snooze,
                old_task.completed)


if __name__ == "__main__":
    with open("todo.todo", "rb") as file:
        old_task_manager = load(file)
    tasks: Tasks = []
    do_tasks = old_task_manager._history.present()[Priority.do]
    tasks.extend(_convert_tasks(do_tasks, True, Importance.Important))
    decide_tasks = old_task_manager._history.present()[Priority.decide]
    tasks.extend(_convert_tasks(decide_tasks, False, Importance.Important))
    delegate_tasks = old_task_manager._history.present()[Priority.delegate]
    tasks.extend(_convert_tasks(delegate_tasks, True, Importance.Unimportant))
    drop_tasks = old_task_manager._history.present()[Priority.eliminate]
    tasks.extend(_convert_tasks(drop_tasks, False, Importance.Unimportant))
    save_task_manager(Path("todoconverted.todo"), TaskManager(tasks))
