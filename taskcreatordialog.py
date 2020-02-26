from PySide2 import QtWidgets
from task import Task, Importance, Immediate, DueDate
from typing import Optional


class TaskCreatorDialogQt(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget]) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Task")
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
        self._important_button.setChecked(True)
        due_buttons_box = QtWidgets.QGroupBox(self)
        self._no_due_button = QtWidgets.QRadioButton(
                "No due date", due_buttons_box)
        self._immediate_due_button = QtWidgets.QRadioButton(
                "Immediate", due_buttons_box)
        self._due_date_button = QtWidgets.QRadioButton(
                "Due date", due_buttons_box)
        due_buttons_layout = QtWidgets.QHBoxLayout(due_buttons_box)
        due_buttons_layout.addWidget(self._no_due_button)
        due_buttons_layout.addWidget(self._immediate_due_button)
        due_buttons_layout.addWidget(self._due_date_button)
        self._no_due_button.setChecked(True)
        self._due_date_widget = QtWidgets.QCalendarWidget(self)
        self._due_date_widget.hide()
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self)
        layout = QtWidgets.QFormLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.addRow("Name", self._name_widget)
        layout.addRow("Important", importance_buttons_box)
        layout.addRow("Due", due_buttons_box)
        layout.addRow("", self._due_date_widget)
        layout.addRow(buttons)
        self._due_date_button.toggled.connect(self._due_date_widget.setVisible)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def task(self) -> Task:
        name: str = self._name_widget.text()
        importance: Importance = Importance.Important \
            if self._importance_widget.isChecked() else Importance.Unimportant
        if self._no_due_button.isChecked():
            due: Optional[DueDate] = None
        elif self._immediate_due_button.isChecked():
            due = Immediate
        else:
            due = self._due_widget.selectedDate()
        return Task(name, importance, due)

    @staticmethod
    def askNewTask(parent: Optional[QtWidgets.QWidget]) -> Optional[Task]:
        dialog = TaskCreatorDialogQt(parent)
        success = dialog.exec_()
        if success == QtWidgets.QDialog.Accepted:
            return dialog.task()
        else:
            return None
