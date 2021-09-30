from typing import Optional
from datetime import date
from PySide6 import QtWidgets
from task import Task, Importance, has_snoozed_date


_default_task = Task("", Importance.Important)


class TaskCreatorDialogQt(QtWidgets.QDialog):
    def __init__(
            self,
            task: Task = _default_task,
            parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Task")
        self._name_widget = QtWidgets.QLineEdit(self)
        importance_buttons_box = QtWidgets.QGroupBox(self)
        self._important_button = QtWidgets.QRadioButton(
            "Important", importance_buttons_box)
        unimportant_button = QtWidgets.QRadioButton(
            "Unimportant", importance_buttons_box)
        importance_buttons_layout = QtWidgets.QHBoxLayout(
            importance_buttons_box)
        importance_buttons_layout.addWidget(self._important_button)
        importance_buttons_layout.addWidget(unimportant_button)
        due_buttons_box = QtWidgets.QGroupBox(self)
        self._due_date_button = QtWidgets.QRadioButton(
            "Due date", due_buttons_box)
        self._no_due_button = QtWidgets.QRadioButton(
            "No due date", due_buttons_box)
        due_buttons_layout = QtWidgets.QHBoxLayout(due_buttons_box)
        due_buttons_layout.addWidget(self._due_date_button)
        due_buttons_layout.addWidget(self._no_due_button)
        self._due_date_widget = QtWidgets.QCalendarWidget(self)
        self._due_date_widget.hide()
        snooze_buttons_box = QtWidgets.QGroupBox(self)
        self._is_snoozed_button = QtWidgets.QRadioButton(
            "Set snooze", snooze_buttons_box)
        self._no_snooze_button = QtWidgets.QRadioButton(
            "No snooze", snooze_buttons_box)
        snooze_buttons_layout = QtWidgets.QHBoxLayout(snooze_buttons_box)
        snooze_buttons_layout.addWidget(self._is_snoozed_button)
        snooze_buttons_layout.addWidget(self._no_snooze_button)
        self._snoozed_date_widget = QtWidgets.QCalendarWidget(self)
        self._snoozed_date_widget.hide()
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self)
        layout = QtWidgets.QFormLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.addRow("Name", self._name_widget)
        layout.addRow("Importance", importance_buttons_box)
        layout.addRow("Due", due_buttons_box)
        layout.addRow("", self._due_date_widget)
        layout.addRow("Snooze", snooze_buttons_box)
        layout.addRow("", self._snoozed_date_widget)
        layout.addRow(buttons)
        self._due_date_button.toggled.connect(self._due_date_widget.setVisible)
        self._is_snoozed_button.toggled.connect(
            self._snoozed_date_widget.setVisible)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._name_widget.setText(task.name)
        if task.importance == Importance.Important:
            self._important_button.setChecked(True)
        else:
            self._unimportant_button.setChecked(True)
        if task.due is None:
            self._no_due_button.setChecked(True)
        else:
            self._due_date_button.setChecked(True)
            self._due_date_widget.setSelectedDate(task.due)
        if has_snoozed_date(task):
            self._is_snoozed_button.setChecked(True)
            self._snoozed_date_widget.setSelectedDate(task.snooze)
        else:
            self._no_snooze_button.setChecked(True)

    def task(self) -> Task:
        name: str = self._name_widget.text()
        importance: Importance = Importance.Important \
            if self._important_button.isChecked() else Importance.Unimportant
        if self._no_due_button.isChecked():
            due: Optional[date] = None
        else:
            due = self._due_date_widget.selectedDate()
        if self._no_snooze_button.isChecked():
            snooze: Optional[date] = None
        else:
            snooze = self._snoozed_date_widget.selectedDate()
        return Task(
            name=name,
            importance=importance,
            due=due,
            snooze=snooze)

    @staticmethod
    def ask_new_task(
            parent: Optional[QtWidgets.QWidget] = None,
            task: Task = _default_task) -> Optional[Task]:
        dialog = TaskCreatorDialogQt(task, parent)
        success = dialog.exec_()
        if success == QtWidgets.QDialog.Accepted:
            return dialog.task()
        return None
