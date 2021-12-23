from datetime import date
from pathlib import Path
from typing import Optional

from mainpresenter import MainPresenter
from task import Task


class MockView:
    def __init__(self) -> None:
        self.update_tasks_calls: list[list[Task]] = []
        self.window_title = ""
        self.hide_lists_calls = 0

    def update_tasks(self, tasks: list[Task]) -> None:
        self.update_tasks_calls.append(tasks)

    def setWindowTitle(self, title: str) -> None:
        self.window_title = title

    def hide_lists(self) -> None:
        self.hide_lists_calls += 1


class MockSerializerWrapper:
    def __init__(self, tasks: list[Task]) -> None:
        self.path: Optional[Path] = None
        self.tasks = tasks

        class MockSerializer:
            def __init__(_, path: Path) -> None:
                self.path = path

            def load(self) -> list[Task]:
                return tasks

            def save(_, new_tasks: list[Task]) -> None:
                self.tasks = new_tasks

        self.serializer = MockSerializer


def test_load_from_file() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("jabra")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path("load_path"))
    assert view.update_tasks_calls == [[Task("jabra")]]
    assert view.window_title == "load_path"
    assert serializer_wrapper.path == Path("load_path")


def test_request_update_without_loaded_file_hides_lists() -> None:
    view = MockView()
    presenter = MainPresenter(view)
    assert view.hide_lists_calls == 0
    presenter.request_update()
    assert view.hide_lists_calls == 1
    assert view.update_tasks_calls == []


def test_request_update_update_tasks_when_file_is_loaded() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("dill")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path("load_path"))
    view.update_tasks_calls = []
    presenter.request_update()
    assert view.update_tasks_calls == [[Task("dill")]]


def test_add_task_updates_tasks() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("curry")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path("load_path"))
    presenter.add_task(Task("asos"))
    assert view.update_tasks_calls[-1] == [Task("curry"), Task("asos")]


def test_add_task_saves_tasks() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("lamp")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path(""))
    presenter.add_task(Task("clock"))
    assert serializer_wrapper.tasks == [Task("lamp"), Task("clock")]


def test_complete_task() -> None:
    view = MockView()
    serializer_wrapper = MockSerializerWrapper([Task("bind")])
    presenter = MainPresenter(view, serializer_wrapper.serializer)
    presenter.load_from_file(Path(""))
    presenter.complete_task(Task("bind"))
    assert view.update_tasks_calls[-1] \
           == [Task("bind", completed=date.today())]
    assert serializer_wrapper.tasks == [Task("bind", completed=date.today())]
