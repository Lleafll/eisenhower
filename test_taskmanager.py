from unittest import TestCase
from PySide6 import QtCore
from datetime import date

from task import Task, SubTask
from taskmanager import TaskManager, sanitize_sub_task


class TestTaskManager(TestCase):
    def test_add_sub_task(self):
        task = Task()
        task_manager = TaskManager([task])
        task_manager.add_sub_task(task)
        self.assertEqual(
            task_manager.tasks(),
            [Task(sub_tasks=(SubTask("New SubTask"),))])

    def test_delete_sub_task(self):
        sub_task = SubTask()
        task_manager = TaskManager([Task(sub_tasks=(sub_task,))])
        task_manager.delete_sub_task(sub_task)
        self.assertEqual(
            task_manager.tasks(),
            [Task()])

    def test_sanitize_sub_task(self):
        sub_task = SubTask("Name", QtCore.QDate(2001, 12, 24))
        self.assertEqual(sanitize_sub_task(sub_task), SubTask("Name", date(2001, 12, 24)))
