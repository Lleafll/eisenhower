from dataclasses import dataclass, asdict
from datetime import date, timedelta
from enum import Enum, auto
from typing import Optional, Iterable, Sequence


class Importance(Enum):
    Important = auto()
    Unimportant = auto()


# Deprecated
@dataclass(frozen=True)
class SubTask:
    name: str = "SubTask"
    due: Optional[date] = None
    snooze: Optional[date] = None


@dataclass(frozen=True)
class Task:
    name: str = "Task"
    importance: Importance = Importance.Unimportant
    completed: Optional[date] = None
    due: Optional[date] = None
    snooze: Optional[date] = None


def is_urgent(task: Task) -> bool:
    due = task.due
    if due is None:
        return False
    return (due - date.today()) < timedelta(days=14)


def has_snoozed_date(task: Task) -> bool:
    if task.snooze is None:
        return False
    return task.snooze > date.today()


def is_completed(task: Task) -> bool:
    return task.completed is not None


def is_important(task: Task) -> bool:
    return task.importance == Importance.Important


def sort_tasks_by_relevance(
        tasks: Iterable[Task]) -> \
        tuple[list[Task], list[Task], list[Task], list[Task]]:
    completed_tasks: list[Task] = []
    snoozed_tasks: list[Task] = []
    due_tasks: list[Task] = []
    normal_tasks: list[Task] = []
    for task in tasks:
        if is_completed(task):
            completed_tasks.append(task)
        elif has_snoozed_date(task):
            snoozed_tasks.append(task)
        elif is_urgent(task):
            due_tasks.append(task)
        else:
            normal_tasks.append(task)
    return due_tasks, normal_tasks, snoozed_tasks, completed_tasks


def _to_primitive_dict(task: Task) -> dict:
    primitive_dict = asdict(task)
    primitive_dict["importance"] = task.importance.name
    return primitive_dict


def to_primitive_dicts(tasks: Sequence[Task]) -> list[dict]:
    return [_to_primitive_dict(task) for task in tasks]
