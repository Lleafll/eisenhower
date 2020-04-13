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
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(QtCore.Qt.ElideMiddle)

    def resources(self) -> List[Path]:
        resources: List[Path] = []
        for row_index in range(self._model.rowCount(QtCore.QModelIndex())):
            index = self._model.index(row_index, 0, QtCore.QModelIndex())
            data = index.data(QtCore.Qt.DisplayRole)
            path = Path(data)
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
                item.setData(url.toDisplayString(), QtCore.Qt.DisplayRole)
                self._model.appendRow(item)

    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        index = self.indexAt(point)
        context_menu = QtWidgets.QMenu()
        if index.isValid():
            open_action = QtWidgets.QAction("Open")
            open_action.triggered.connect(lambda: startfile(
                index.data(QtCore.Qt.DisplayRole)))
            context_menu.addAction(open_action)
            rename_action = QtWidgets.QAction("Rename")
            rename_action.triggered.connect(lambda: self.edit(index))
            context_menu.addAction(rename_action)
            delete_action = QtWidgets.QAction("Delete")
            delete_action.triggered.connect(lambda: self._model.removeRow(
                index.row()))
            context_menu.addAction(delete_action)
        if len(context_menu.actions()) > 0:
            context_menu.exec_(self.viewport().mapToGlobal(point))
