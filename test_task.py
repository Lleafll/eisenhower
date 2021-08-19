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
            SubTask(snooze=date(6, 7, 8)),
            SubTask(snooze=None)])
        self.assertEqual(task.snooze, date(3, 4, 5))

    def test_completed_empty_task(self):
        task = Task()
        self.assertIsNone(task.completed)

    def test_completed_one_uncompleted_tasks(self):
        task = Task(sub_tasks=[
            SubTask(completed=date(9, 10, 11)),
            SubTask(completed=date(3, 4, 5)),
            SubTask(completed=date(6, 7, 8)),
            SubTask(completed=None)])
        self.assertIsNone(task.completed)

    def test_completed_several_completed_tasks(self):
        task = Task(sub_tasks=[
            SubTask(completed=date(9, 10, 11)),
            SubTask(completed=date(3, 4, 5)),
            SubTask(completed=date(6, 7, 8))])
        self.assertEqual(task.completed, date(9, 10, 11))

    def test_due_empty_task(self):
        task = Task()
        self.assertIsNone(task.due)

    def test_due_several_due_tasks(self):
        task = Task(sub_tasks=[
            SubTask(due=date(9, 10, 11)),
            SubTask(due=date(3, 4, 5)),
            SubTask(due=date(6, 7, 8))])
        self.assertEqual(task.due, date(3, 4, 5))

    def test_due_one_undue_task(self):
        task = Task(sub_tasks=[
            SubTask(due=date(9, 10, 11)),
            SubTask(due=date(3, 4, 5)),
            SubTask(due=date(6, 7, 8)),
            SubTask(due=None)])
        self.assertEqual(task.due, date(3, 4, 5))
