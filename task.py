from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto
from typing import Optional, Iterable, Tuple, List, Union


class Importance(Enum):
    Important = auto()
    Unimportant = auto()


@dataclass(frozen=True)
class SubTask:
    name: str = "SubTask"
    due: Optional[date] = None
    snooze: Optional[date] = None


@dataclass(frozen=True)
class Task:
    name: str = "Task"
    importance: Importance = Importance.Unimportant
    sub_tasks: Tuple[SubTask, ...] = field(default_factory=tuple)
    completed: Optional[date] = None

    @property
    def snooze(self) -> Optional[date]:
        try:
            if any(not has_snoozed_date(sub_task) for sub_task in self.sub_tasks):
                return None
            else:
                return min([sub_task.snooze for sub_task in self.sub_tasks if has_snoozed_date(sub_task)])
        except ValueError:
            return None

    @property
    def due(self) -> Optional[date]:
        try:
            if not all(has_snoozed_date(sub_task) for sub_task in self.sub_tasks):
                return min(
                    [sub_task.due for sub_task in self.sub_tasks
                     if sub_task.due is not None and not has_snoozed_date(sub_task)])
            else:
                return min([sub_task.due for sub_task in self.sub_tasks if sub_task.due is not None])
        except ValueError:
            return None


def is_urgent(task: Union[Task, SubTask]) -> bool:
    due = task.due
    if due is None:
        return False
    return (due - date.today()) < timedelta(days=14)


def has_snoozed_date(task: Union[Task, SubTask]) -> bool:
    if task.snooze is None:
        return False
    return task.snooze > date.today()


def is_completed(task: Union[Task, SubTask]) -> bool:
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
        elif is_urgent(task):
            due_tasks.append(task)
        else:
            normal_tasks.append(task)
    return due_tasks, normal_tasks, snoozed_tasks, completed_tasks
