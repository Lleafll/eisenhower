from unittest import TestCase

from task import Task, SubTask
from taskmanager import TaskManager


class TestTaskManager(TestCase):
    def test_add_sub_task(self):
        task = Task()
        task_manager = TaskManager([task])
        task_manager.add_sub_task(task)
        self.assertEqual(
            task_manager.tasks(),
            [Task(sub_tasks=(SubTask("New SubTask"),))])
