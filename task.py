from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Sequence, Tuple, List


@dataclass(frozen=True)
class Task:
    name: str
    due: Optional[date] = None
    snooze: Optional[date] = None
    completed: Optional[date] = None
    notes: List[str] = field(default_factory=list)


def has_due_date(task: Task) -> bool:
    return task.due is not None


def has_snoozed_date(task: Task) -> bool:
    if task.snooze is None:
        return False
    return task.snooze > date.today()


def is_completed(task: Task) -> bool:
    return task.completed is not None


def sort_tasks_by_relevance(
        tasks: Sequence[Task]) -> \
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
