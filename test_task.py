from datetime import date
from unittest import TestCase

from task import Task, SubTask


class TestTask(TestCase):
    def test_snooze_empty_task(self):
        task = Task()
        self.assertIsNone(task.snooze)

    def test_snooze_one_sub_task(self):
        task = Task(sub_tasks=[SubTask()])
        self.assertIsNone(task.snooze)

    def test_snooze_one_snoozed_sub_task(self):
        task = Task(sub_tasks=[SubTask(snooze=date(1, 2, 3))])
        self.assertEqual(task.snooze, date(1, 2, 3))

    def test_snooze_several_snoozed_sub_task(self):
        task = Task(sub_tasks=[
            SubTask(snooze=date(9, 10, 11)),
            SubTask(snooze=date(3, 4, 5)),
            SubTask(snooze=date(6, 7, 8))])
        self.assertEqual(task.snooze, date(3, 4, 5))
