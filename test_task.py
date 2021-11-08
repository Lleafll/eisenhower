from datetime import date
from unittest import TestCase

from task import Task, is_urgent


class TestTask(TestCase):
    def test_snooze_empty_task(self):
        task = Task()
        self.assertIsNone(task.snooze)

    def test_due_empty_task(self):
        task = Task()
        self.assertIsNone(task.due)

    def test_is_urgent_task(self):
        task = Task()
        self.assertFalse(is_urgent(task))

    def test_is_urgent_due_task(self):
        task = Task(due=date(5, 3, 2))
        self.assertTrue(is_urgent(task))

    def test_is_urgent_undue_task(self):
        task = Task(due=None)
        self.assertFalse(is_urgent(task))

    def test_is_urgent_task_in_the_distant_future(self):
        task = Task(due=date(9999, 1, 1))
        self.assertFalse(is_urgent(task))
