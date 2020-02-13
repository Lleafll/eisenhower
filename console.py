from taskmanager import (
    TaskManager,
    Priority,
    load_task_manager,
    save_task_manager)
from task import Task, sort_tasks_by_relevance
from typing import Sequence, List
import os
from pathlib import Path
from argparse import ArgumentParser


def _print_task(index: int, task: Task) -> None:
    print(f"    {index}: {task.name}")


def _print_tasks(tasks: Sequence[Task], displayed_tasks: List[Task]) -> None:
    for task in sort_tasks_by_relevance(tasks):
        displayed_tasks.append(task)
        _print_task(len(displayed_tasks), task)


def _print_task_manager(task_manager: TaskManager) -> List[Task]:
    os.system("cls")
    displayed_tasks: List[Task] = []
    for priority in (Priority.do, Priority.decide, Priority.delegate):
        print(priority.name)
        tasks = task_manager.tasks(priority)
        _print_tasks(tasks, displayed_tasks)
    return displayed_tasks


def _ask_for_task(displayed_tasks: Sequence[Task]) -> Task:
    task_index = int(input("Task? ")) - 1
    return displayed_tasks[task_index]


def _parse_command(
        task_manager: TaskManager,
        displayed_tasks: Sequence[Task],
        command: str) -> None:
    if command == "add" or command == "a":
        name = input("Name? ")
        task = Task(name, None, None)
        priority_strings = ", ".join(
            f"{i}={priority.name}" for i, priority in enumerate(Priority, 1))
        priority_string = input(f"Priority ({priority_strings})? ")
        priority = Priority(int(priority_string))
        task_manager.add(task, priority)
    elif command == "delete" or command == "d":
        task = _ask_for_task(displayed_tasks)
        task_manager.delete(task)
    else:
        input("Could not recognize command")


def _parse_args() -> Path:
    parser = ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    return Path(args.path)


if __name__ == "__main__":
    import_path = _parse_args()
    task_manager = load_task_manager(import_path)
    while True:
        displayed_tasks = _print_task_manager(task_manager)
        command = input("\n>")
        _parse_command(task_manager, displayed_tasks, command)
        save_task_manager(import_path, task_manager)
