from PySide2 import QtWidgets, QtCore
from task import Task, has_due_date, has_snoozed_date


TASK_ROLE = QtCore.Qt.UserRole + 1


class TreeViewWithContextMenu(QtWidgets.QTreeView):
    add_task_requested = QtCore.Signal(str)
    complete_task_requested = QtCore.Signal(Task)
    delete_task_requested = QtCore.Signal(Task)
    remove_due_requested = QtCore.Signal(Task)
    remove_snooze_requested = QtCore.Signal(Task)

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        index = self.indexAt(point)
        context_menu = QtWidgets.QMenu()
        if index.isValid():
            task = index.data(TASK_ROLE)
            if has_due_date(task):
                remove_due_action = QtWidgets.QAction("Remove Due")
                remove_due_action.triggered.connect(
                        lambda: self.remove_due_requested.emit(task))
                context_menu.addAction(remove_due_action)
            if has_snoozed_date(task):
                remove_snooze_action = QtWidgets.QAction("Remove Snooze")
                remove_snooze_action.triggered.connect(
                        lambda: self.remove_snooze_requested.emit(task))
                context_menu.addAction(remove_snooze_action)
            complete_action = QtWidgets.QAction("Complete")
            complete_action.triggered.connect(
                    lambda: self.complete_task_requested.emit(task))
            context_menu.addAction(complete_action)
            delete_action = QtWidgets.QAction("Delete")
            delete_action.triggered.connect(
                    lambda: self.delete_task_requested.emit(task))
            context_menu.addAction(delete_action)
        else:
            add_task_action = QtWidgets.QAction("Add Task")
            add_task_action.triggered.connect(
                    lambda: self.add_task_requested.emit("New Task"))
            context_menu.addAction(add_task_action)
        context_menu.exec_(self.viewport().mapToGlobal(point))
