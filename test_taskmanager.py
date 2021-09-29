from unittest import TestCase
from PySide6 import QtCore
from datetime import date

from task import Task, SubTask, Importance
from taskmanager import TaskManager, sanitize_sub_task


class TestTaskManager(TestCase):
    def test_sanitize_sub_task(self):
        sub_task = SubTask("Name", QtCore.QDate(2001, 12, 24))
        self.assertEqual(
            sanitize_sub_task(sub_task, Importance.Important, None),
            Task("Name", importance=Importance.Important, due=date(2001, 12, 24)))
