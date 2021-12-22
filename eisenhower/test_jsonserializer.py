from io import StringIO
from pathlib import Path
from typing import IO, Type

from jsonserializer import JsonSerializer
from task import Task


def build_mock_open(content: str = "") -> (StringIO, Type):
    file_ = StringIO(content)

    class MockOpen:
        def __init__(self, _: Path, method: str) -> None:
            assert method in ("w", "r")
            self.file = file_

        def __enter__(self) -> IO[str]:
            return self.file

        def __exit__(self, _, _2, _3) -> None:
            pass

    return file_, MockOpen


def test_save() -> None:
    file, mock_open = build_mock_open()
    serializer = JsonSerializer(Path("path"), mock_open)
    serializer.save([Task("kog")])
    expected = """[
    {
        "name": "kog",
        "importance": "Unimportant",
        "completed": null,
        "due": null,
        "snooze": null
    }
]"""
    assert file.getvalue() == expected


def test_load() -> None:
    content = """[
    {
        "name": "ztru",
        "importance": "Unimportant",
        "completed": null,
        "due": null,
        "snooze": null
    }
]"""
    file, mock_open = build_mock_open(content)
    serializer = JsonSerializer(Path("path"), mock_open)
    tasks = serializer.load()
    assert tasks == [Task("ztru")]


class FileNotFoundMockOpen:
    def __init__(self, _: Path, _2: str) -> None:
        raise FileNotFoundError

    def __enter__(self) -> IO[str]:
        return StringIO()

    def __exit__(self, _, _2, _3) -> None:
        pass


def test_load_when_file_not_exists() -> None:
    serializer = JsonSerializer(Path("path"), FileNotFoundMockOpen)
    assert serializer.load() == []
