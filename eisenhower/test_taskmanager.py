from PySide6 import QtCore
from datetime import date

from task import Task, SubTask, Importance
from taskmanager import sanitize_sub_task, TaskManager


def test_sanitize_sub_task() -> None:
    # noinspection PyTypeChecker
    sub_task = SubTask("Name", QtCore.QDate(2001, 12, 24))
    assert sanitize_sub_task(sub_task, Importance.Important, None) \
        == Task("Name", importance=Importance.Important, due=date(2001, 12, 24))


def test_add() -> None:
    manager = TaskManager([Task("cvje")])
    manager.add(Task("fjdp"))
    assert manager.tasks() == [Task("cvje"), Task("fjdp")]


def test_delete() -> None:
    manager = TaskManager([Task("fmnk"), Task("jdoi")])
    manager.delete(Task("fmnk"))
    assert manager.tasks() == [Task("jdoi")]


def test_replace() -> None:
    manager = TaskManager([Task("fnk"), Task("fkop")])
    manager.replace(Task("fkop"), Task("f0ß"))
    assert manager.tasks() == [Task("fnk"), Task("f0ß")]


def test_set_complete() -> None:
    manager = TaskManager([Task("fj9")])
    manager.set_complete(Task("fj9"))
    assert manager.tasks() == [Task("fj9", completed=date.today())]
    manager.set_complete(Task("fj9", completed=date.today()), False)
    assert manager.tasks() == [Task("fj9", completed=None)]
