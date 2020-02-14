from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence, Tuple, List
from itertools import filterfalse


@dataclass(frozen=True)
class Task:
    name: str
    due: Optional[date] = None
    snooze: Optional[date] = None


def has_due_date(task: Task) -> bool:
    return task.due is not None


def has_snoozed_date(task: Task) -> bool:
    if task.snooze is None:
        return False
    return task.snooze > date.today()


def sort_tasks_by_relevance(
        tasks: Sequence[Task]) -> Tuple[List[Task], List[Task], List[Task]]:
    due_tasks = sorted(
            filterfalse(has_snoozed_date, filter(has_due_date, tasks)),
            key=lambda task: task.due)
    normal_tasks = list(
            filterfalse(has_snoozed_date, filterfalse(has_due_date, tasks)))
    snoozed_tasks = sorted(
            filter(has_snoozed_date, tasks),
            key=lambda task: task.snooze)
    return due_tasks, normal_tasks, snoozed_tasks
