from pathlib import Path
from typing import Optional

from mainpresenter import MainPresenter
from task import Task


class MockView:
    def __init__(self) -> None:
        self.update_tasks_calls: list[list[Task]] = []
        self.window_title = ""

    def update_tasks(self, tasks: list[Task]) -> None:
        self.update_tasks_calls.append(tasks)

    def setWindowTitle(self, title: str) -> None:
        self.window_title = title


class MockSerializerWrapper:
    def __init__(self, tasks: list[Task]) -> None:
        self.path: Optional[Path] = None

        def set_path(path: Path) -> None:
            self.path = path

        class MockSerializer:
            def __init__(self, path: Path) -> None:
                set_path(path)

            def load(self) -> list[Task]:
                return tasks

        self.serializer = MockSerializer


def test_load_from_file() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("jabra")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path("load_path"))
    assert view.update_tasks_calls == [[Task("jabra")]]
    assert view.window_title == "load_path"
    assert serializer_wrapper.path == Path("load_path")
