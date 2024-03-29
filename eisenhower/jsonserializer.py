import json
from pathlib import Path
from typing import Sequence

from task import Task, to_primitive_dicts, tasks_from_primitive_dicts


class JsonSerializer:
    def __init__(self, path: Path, open_=open) -> None:
        self._path = path
        self._open = open_

    def save(self, tasks: Sequence[Task]) -> None:
        with self._open(self._path, "w") as file:
            json.dump(to_primitive_dicts(tasks), file, indent=4)

    def load(self) -> list[Task]:
        try:
            with self._open(self._path, "r") as file:
                return tasks_from_primitive_dicts(json.load(file))
        except FileNotFoundError:
            return []
