from datetime import date, timedelta
from unittest import TestCase

from task import Task, SubTask, has_due_date, has_snoozed_date


class TestTask(TestCase):
    def test_snooze_empty_task(self):
        task = Task()
        self.assertIsNone(task.snooze)

    def test_snooze_one_sub_task(self):
        task = Task(sub_tasks=(SubTask(),))
        self.assertIsNone(task.snooze)

    def test_snooze_one_snoozed_sub_task(self):
        task = Task(sub_tasks=(SubTask(snooze=date.today() + timedelta(days=2)), ))
        self.assertEqual(task.snooze, date.today() + timedelta(days=2))

    def test_snooze_several_snoozed_sub_task(self):
        task = Task(sub_tasks=(
            SubTask(snooze=date(9, 10, 11)),
            SubTask(snooze=date(3, 4, 5)),
            SubTask(snooze=date(6, 7, 8)),
            SubTask(snooze=None)))
        self.assertEqual(task.snooze, None)

    def test_due_empty_task(self):
        task = Task()
        self.assertIsNone(task.due)

    def test_due_several_due_tasks(self):
        task = Task(sub_tasks=(
            SubTask(due=date(9, 10, 11)),
            SubTask(due=date(3, 4, 5)),
            SubTask(due=date(6, 7, 8))))
        self.assertEqual(task.due, date(3, 4, 5))

    def test_due_one_undue_task(self):
        task = Task(sub_tasks=(
            SubTask(due=date(9, 10, 11)),
            SubTask(due=date(3, 4, 5)),
            SubTask(due=date(6, 7, 8)),
            SubTask(due=None)))
        self.assertEqual(task.due, date(3, 4, 5))

    def test_has_due_date_sub_task(self):
        sub_task = SubTask()
        self.assertFalse(has_due_date(sub_task))

    def test_has_due_date_task(self):
        task = Task()
        self.assertFalse(has_due_date(task))

    def test_has_due_date_task_with_due_sub_task(self):
        task = Task(sub_tasks=(SubTask(due=date(5, 3, 2)),))
        self.assertTrue(has_due_date(task))

    def test_has_due_date_task_with_undue_sub_task(self):
        task = Task(sub_tasks=(SubTask(),))
        self.assertFalse(has_due_date(task))

    def test_uses_due_date_of_unsnoozed_subtask(self):
        task = Task(sub_tasks=(
            SubTask(due=date(1, 2, 3), snooze=date.today() + timedelta(days=2)),
            SubTask(due=date(4, 5, 6))))
        self.assertEqual(task.due, date(4, 5, 6))

    def test_uses_due_date_of_snoozed_subtasks_when_no_unsnoozed_subtask(self):
        task = Task(sub_tasks=(
            SubTask(due=date(1, 2, 3), snooze=date.today() + timedelta(days=2)),
            SubTask(due=date(4, 5, 6), snooze=date.today() + timedelta(days=3))))
        self.assertEqual(task.due, date(1, 2, 3))

    def test_snooze_is_None_when_task_has_unsnoozed_subtask_without_due_date(self):
        task = Task(sub_tasks=(
            SubTask(due=date(1, 2, 3), snooze=date.today() + timedelta(days=2)),
            SubTask(due=None, snooze=None)))
        self.assertIsNone(task.snooze)

    def test_is_not_snoozed_when_task_has_unsnoozed_subtask_without_due_date(self):
        task = Task(sub_tasks=(
            SubTask(due=date(1, 2, 3), snooze=date.today() + timedelta(days=2)),
            SubTask(due=None, snooze=None)))
        self.assertFalse(has_snoozed_date(task))

    def test_is_not_snoozed_when_task_has_snoozed_subtask_in_the_past_without_due_date(self):
        task = Task(sub_tasks=(
            SubTask(due=date(1, 2, 3), snooze=date.today() + timedelta(days=2)),
            SubTask(due=None, snooze=date(4, 5, 6))))
        self.assertFalse(has_snoozed_date(task))
