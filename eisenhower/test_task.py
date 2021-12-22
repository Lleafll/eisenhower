from datetime import date

from task import Task, is_urgent


def test_snooze_empty_task():
    task = Task()
    assert task.snooze is None


def test_due_empty_task():
    task = Task()
    assert task.snooze is None


def test_is_urgent_task():
    task = Task()
    assert not is_urgent(task)


def test_is_urgent_due_task():
    task = Task(due=date(5, 3, 2))
    assert is_urgent(task)


def test_is_urgent_undue_task():
    task = Task(due=None)
    assert not is_urgent(task)


def test_is_urgent_task_in_the_distant_future():
    task = Task(due=date(9999, 1, 1))
    assert not is_urgent(task)
