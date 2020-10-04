from dataclasses import dataclass, field
from pathlib import Path
from datetime import date
from typing import Optional, Iterable, Tuple, List
from enum import Enum, auto


class Importance(Enum):
    Important = auto()
    Unimportant = auto()


@dataclass(frozen=True)
class Task:
    name: str
    importance: Importance
    due: Optional[date] = None
    snooze: Optional[date] = None
    completed: Optional[date] = None
    resources: List[Path] = field(default_factory=list)


def has_due_date(task: Task) -> bool:
    return task.due is not None


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
                Tuple[List[Task], List[Task], List[Task], List[Task]]:
    completed_tasks: List[Task] = []
    snoozed_tasks: List[Task] = []
    due_tasks: List[Task] = []
    normal_tasks: List[Task] = []
    for task in tasks:
        if is_completed(task):
            completed_tasks.append(task)
        elif has_snoozed_date(task):
            snoozed_tasks.append(task)
        elif has_due_date(task):
            due_tasks.append(task)
        else:
            normal_tasks.append(task)
    return due_tasks, normal_tasks, snoozed_tasks, completed_tasks
