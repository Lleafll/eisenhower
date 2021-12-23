from dataclasses import dataclass
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


def _date_to_string(date_: Optional[date]) -> Optional[str]:
    return date_.isoformat() if date_ is not None else None


def _to_primitive_dict(task: Task) -> dict:
    return {
        "name": task.name,
        "importance": task.importance.name,
        "completed": _date_to_string(task.completed),
        "due": _date_to_string(task.due),
        "snooze": _date_to_string(task.snooze)}


def to_primitive_dicts(tasks: Sequence[Task]) -> list[dict]:
    return [_to_primitive_dict(i) for i in tasks]


def _date_from_string(string: Optional[str]) -> Optional[date]:
    return date.fromisoformat(string) if string is not None else None


def _task_from_primitive_dict(from_dict: dict) -> Task:
    return Task(
        from_dict["name"],
        Importance[from_dict["importance"]],
        _date_from_string(from_dict["completed"]),
        _date_from_string(from_dict["due"]),
        _date_from_string(from_dict["snooze"]))


def tasks_from_primitive_dicts(dicts: list[dict]) -> list[Task]:
    return [_task_from_primitive_dict(i) for i in dicts]
