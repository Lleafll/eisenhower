from task import Task
from typing import List
from copy import copy


Tasks = List[Task]


class HistoryError(RuntimeError):
    pass


class History:
    def __init__(self, present: Tasks) -> None:
        self._tasks: List[Tasks] = [present]
        self._current = 0

    def present(self) -> Tasks:
        return self._tasks[self._current]

    def has_past(self) -> bool:
        return self._current > 0

    def go_back_in_time(self) -> Tasks:
        if not self.has_past():
            raise HistoryError("No recorded past")
        self._current -= 1
        return self.present()

    def has_future(self) -> bool:
        return self._current < len(self._tasks) - 1

    def go_forward_in_time(self) -> Tasks:
        if not self.has_future():
            raise HistoryError("No recorded future")
        self._current += 1
        return self.present()

    def write_history(self) -> Tasks:
        # No deep copy necessary, all elements are immutable
        new_present = copy(self.present())
        self._current += 1
        del self._tasks[self._current:]
        self._tasks.append(new_present)
        return new_present
