from PySide2 import QtWidgets, QtGui, QtCore
from task import Task
from pathlib import Path
from typing import List
from os import startfile


class ResourceViewQt(QtWidgets.QListView):
    def __init__(self, task: Task, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._model = QtGui.QStandardItemModel()
        for resource in task.resources:
            path = resource.as_posix()
            item = QtGui.QStandardItem()
            item.setData(path, QtCore.Qt.DisplayRole)
            self._model.appendRow(item)
        self.setModel(self._model)
        self.setAcceptDrops(True)
        self.setEditTriggers(self.NoEditTriggers)
        self.doubleClicked.connect(lambda index: startfile(
            index.data(QtCore.Qt.DisplayRole)))

    def resources(self) -> List[Path]:
        resources: List[Path] = []
        for row_index in range(self._model.rowCount(QtCore.QModelIndex())):
            index = self._model.index(row_index, 0, QtCore.QModelIndex())
            data = index.data(QtCore.Qt.DisplayRole)
            print(data)
            path = Path(data.toString())
            resources.append(path)
        return resources

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                item = QtGui.QStandardItem()
                item.setData(url, QtCore.Qt.DisplayRole)
                self._model.appendRow(item)
