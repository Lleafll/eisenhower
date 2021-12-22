from datetime import date, timedelta

from task import (
    Task,
    is_urgent,
    has_snoozed_date,
    is_completed,
    is_important,
    Importance,
    to_primitive_dicts, tasks_from_primitive_dicts)


def test_snooze_empty_task() -> None:
    task = Task()
    assert task.snooze is None


def test_due_empty_task() -> None:
    task = Task()
    assert task.snooze is None


def test_is_urgent_task() -> None:
    task = Task()
    assert not is_urgent(task)


def test_is_urgent_due_task() -> None:
    task = Task(due=date(5, 3, 2))
    assert is_urgent(task)


def test_is_urgent_undue_task() -> None:
    task = Task(due=None)
    assert not is_urgent(task)


def test_is_urgent_task_in_the_distant_future() -> None:
    task = Task(due=date(9999, 1, 1))
    assert not is_urgent(task)


def test_has_snoozed_date_when_not_snoozed() -> None:
    assert not has_snoozed_date(Task())


def test_has_snoozed_date_when_snoozed_is_in_the_past() -> None:
    assert not has_snoozed_date(Task(snooze=date.today() - timedelta(days=2)))


def test_has_snoozed_date_when_snoozed_is_in_the_future() -> None:
    assert has_snoozed_date(Task(snooze=date.today() + timedelta(days=2)))


def test_is_completed() -> None:
    assert not is_completed(Task())
    assert is_completed(Task(completed=date(1, 1, 1)))


def test_is_important() -> None:
    assert not is_important(Task())
    assert not is_important(Task(importance=Importance.Unimportant))
    assert is_important(Task(importance=Importance.Important))


def test_to_primitive_dicts() -> None:
    tasks = [Task("gjnio")]
    expected = [{
        "name": "gjnio",
        "importance": "Unimportant",
        "completed": None,
        "due": None,
        "snooze": None
    }]
    assert to_primitive_dicts(tasks) == expected


def test_tasks_from_primitive_dicts() -> None:
    dicts = [{
        "name": "bgfb",
        "importance": "Unimportant",
        "completed": None,
        "due": None,
        "snooze": None
    }]
    expected = [Task("bgfb")]
    assert tasks_from_primitive_dicts(dicts) == expected