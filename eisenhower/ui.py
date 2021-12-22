import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets
from mainwindowqt import MainWindowQt


def _parse_argv() -> Optional[Path]:
    parser = ArgumentParser()
    parser.add_argument("path", type=str, nargs="?")
    args = parser.parse_args()
    if args.path is None:
        return None
    return Path(args.path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindowQt()
    path = _parse_argv()
    if path is not None:
        main_window.load_from_file(path)
    main_window.show()
    app.exec()
