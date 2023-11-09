import sys; sys.path.append('../src')
from src.qwlist.qwlist import QList, Lazy
from src.qwlist.eager import EagerQList
import pytest


def test_qlist_from_iterable_constructor():
    expected = QList([0, 1, 2])
    res = QList(range(3))
    for e, r in zip(expected, res):
        assert e == r


def test_conversion_to_list():
    expected = [1, 2, 3]
    res = QList([1, 2, 3]).list()
    assert expected == res


def test_conversion_to_eager_qlist():
    expected = EagerQList([1, 2, 3])
    res = QList([1, 2, 3]).eager()
    assert expected == res


def test_empty_constructor():
    expect = []
    res = QList().list()
    assert expect == res

