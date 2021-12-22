from history import History, HistoryError
from task import Task
import pytest


def test_present() -> None:
    history = History([Task("gvfd")])
    assert history.present() == [Task("gvfd")]


def test_has_past_without_past() -> None:
    history = History([Task("hngf")])
    assert not history.has_past()


def test_has_future_without_future() -> None:
    history = History([Task("hg")])
    assert not history.has_future()


def test_advance_history() -> None:
    history = History([Task("sphk")])
    # new present initially equals former present
    expected_new_present = [Task("sphk")]
    assert history.advance_history() == expected_new_present
    assert history.present() == expected_new_present


def test_go_back_in_time() -> None:
    history = History([Task("fko")])
    history.advance_history()[0] = Task("gvkop")
    assert history.present() == [Task("gvkop")]
    assert history.go_back_in_time() == [Task("fko")]
    assert history.present() == [Task("fko")]


def test_go_back_in_time_throws_when_no_past() -> None:
    history = History([Task("akop")])
    with pytest.raises(HistoryError):
        history.go_back_in_time()


def test_go_forward_in_time() -> None:
    history = History([Task("dsnmkol")])
    history.advance_history()[0] = Task("fhndiso")
    history.go_back_in_time()
    assert history.present() == [Task("dsnmkol")]
    assert history.go_forward_in_time() == [Task("fhndiso")]
    assert history.present() == [Task("fhndiso")]


def test_go_forward_in_time_throws_when_no_future() -> None:
    history = History([Task("gsdjmpk")])
    with pytest.raises(HistoryError):
        history.go_forward_in_time()
