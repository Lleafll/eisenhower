from datetime import date

from task import Task, Importance
from taskmanager import TaskManager


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


def test_schedule_task() -> None:
    manager = TaskManager([Task("g5")])
    manager.schedule_task(Task("g5"), date(2, 5, 7))
    assert manager.tasks() == [Task("g5", due=date(2, 5, 7))]
    manager.schedule_task(Task("g5", due=date(2, 5, 7)), None)
    assert manager.tasks() == [Task("g5", due=None)]


def test_snooze() -> None:
    manager = TaskManager([Task("fgjnio")])
    manager.snooze(Task("fgjnio"), date(4, 8, 5))
    assert manager.tasks() == [Task("fgjnio", snooze=date(4, 8, 5))]
    manager.snooze(Task("fgjnio", snooze=date(4, 8, 5)), None)
    assert manager.tasks() == [Task("fgjnio", snooze=None)]


def test_rename() -> None:
    manager = TaskManager([Task("gfio")])
    manager.rename(Task("gfio"), "ggrgr")
    assert manager.tasks() == [Task("ggrgr")]


def test_remove_due() -> None:
    manager = TaskManager([Task("bfg", due=date(5, 8, 1))])
    manager.remove_due(Task("bfg", due=date(5, 8, 1)))
    assert manager.tasks() == [Task("bfg")]


def test_remove_snooze() -> None:
    manager = TaskManager([Task("j54", snooze=date(5, 8, 1))])
    manager.remove_snooze(Task("j54", snooze=date(5, 8, 1)))
    assert manager.tasks() == [Task("j54")]


def test_set_importance() -> None:
    manager = TaskManager([Task("fio")])
    manager.set_importance(Task("fio"), Importance.Important)
    assert manager.tasks() == [Task("fio", importance=Importance.Important)]


def test_is_undoable_after_add() -> None:
    manager = TaskManager([])
    assert not manager.is_undoable()
    manager.add(Task())
    assert manager.is_undoable()


def test_is_redoable_after_undo() -> None:
    manager = TaskManager([])
    manager.add(Task())
    assert not manager.is_redoable()
    manager.undo()
    assert manager.is_redoable()


def test_redo() -> None:
    manager = TaskManager([])
    manager.add(Task("sop"))
    manager.undo()
    assert not manager.tasks()
    manager.redo()
    assert manager.tasks() == [Task("sop")]
