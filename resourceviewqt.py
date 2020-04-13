from PySide2 import QtWidgets, QtGui, QtCore
from task import Task


class ResourceViewQt(QtWidgets.QListView):
    def __init__(self, task: Task, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._model = QtGui.QStandardItemModel()
        for resource in task.resources:
            path = QtCore.QUrl(resource.as_uri())
            item = QtGui.QStandardItem(path)
            self._model.appendRow(item)
        self.setModel(self._model)
        self.setAcceptDrops(True)

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
