from datetime import date

from PySide6 import QtCore

from pickleserializer import sanitize_sub_task
from task import SubTask, Importance, Task


def test_sanitize_sub_task() -> None:
    # noinspection PyTypeChecker
    sub_task = SubTask("Name", QtCore.QDate(2001, 12, 24))
    assert sanitize_sub_task(sub_task, Importance.Important, None) \
        == Task("Name", importance=Importance.Important, due=date(2001, 12, 24))
