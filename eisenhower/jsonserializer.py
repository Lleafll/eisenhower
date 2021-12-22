import json
from pathlib import Path
from typing import Sequence

from task import Task, to_primitive_dicts, tasks_from_primitive_dicts


class JsonSerializer:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, tasks: Sequence[Task]) -> None:
        with open(self._path, "w") as file:
            json.dump(to_primitive_dicts(tasks), file)

    def load(self) -> list[Task]:
        with open(self._path, "r") as file:
            return tasks_from_primitive_dicts(json.load(file))
