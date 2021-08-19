from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Iterable, Tuple, List, Union


class Importance(Enum):
    Important = auto()
    Unimportant = auto()


@dataclass(frozen=True)
class SubTask:
    name: str = "SubTask"
    due: Optional[date] = None
    snooze: Optional[date] = None
    completed: Optional[date] = None


@dataclass(frozen=True)
class Task:
    name: str = "Task"
    importance: Importance = Importance.Unimportant
    resources: List[Path] = field(default_factory=list)
    sub_tasks: List[SubTask] = field(default_factory=list)
    version: int = 2

    @property
    def snooze(self) -> Optional[date]:
        try:
            return min([sub_task.snooze for sub_task in self.sub_tasks if sub_task.snooze is not None])
        except ValueError:
            return None

    @property
    def due(self) -> Optional[date]:
        try:
            return min([sub_task.due for sub_task in self.sub_tasks if sub_task.due is not None])
        except ValueError:
            return None

    @property
    def completed(self) -> Optional[date]:
        if any(sub_task.completed is None for sub_task in self.sub_tasks):
            return None
        else:
            try:
                return max([sub_task.completed for sub_task in self.sub_tasks if sub_task.completed is not None])
            except ValueError:
                return None


def has_due_date(task: Union[Task, SubTask]) -> bool:
    if isinstance(task, Task):
        return (task.due is not None) or (any(i is not None for i in task.sub_tasks))
    else:
        return task.due is not None

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
        elif has_due_date(task):
            due_tasks.append(task)
        else:
            normal_tasks.append(task)
    return due_tasks, normal_tasks, snoozed_tasks, completed_tasks
