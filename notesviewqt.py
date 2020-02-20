from PySide2 import QtWidgets, QtCore
from task import Task
from typing import List


class NoteView(QtWidgets.QLineEdit):
    def __init__(self, note: str, parent: QtWidgets.QWidget) -> None:
        super().__init__(note, parent)


class NotesViewQt(QtWidgets.QWidget):
    def __init__(self, task: Task, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._notes = task.notes
        QtWidgets.QVBoxLayout(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)
        self._update()

    def notes(self) -> List[str]:
        return self._notes

    def _update(self) -> None:
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for i, note in enumerate(self._notes):
            note_item = NoteView(note, self)
            note_item.editingFinished.connect(
                    lambda: self._change_note(i, note_item.text()))
            note_item.show()
            layout.addWidget(note_item)
        layout.addStretch()

    def _change_note(self, index: int, text: str) -> None:
        self._notes[index] = text
        self._update()

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        context_menu = QtWidgets.QMenu()
        add_note_action = QtWidgets.QAction("Add Note")
        add_note_action.triggered.connect(self._add_note)
        context_menu.addAction(add_note_action)
        context_menu.exec_(self.mapToGlobal(point))

    def _add_note(self) -> None:
        self._notes.append("New Note")
        self._update()
