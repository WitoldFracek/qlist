import sys; sys.path.append('../src')
from src.qwlist.qwlist import QList
from src.qwlist.eager import EagerQList
import pytest


def test_qlist_from_iterable_constructor():
    expected = EagerQList([0, 1, 2])
    res = EagerQList(range(3))
    for e, r in zip(expected, res):
        assert e == r


def test_len():
    assert 3 == EagerQList([0, 1, 2]).len()


def test_conversion_to_list():
    expected = [1, 2, 3]
    res = EagerQList([1, 2, 3]).list()
    assert isinstance(res, list)
    assert expected == res


def test_conversion_to_qlist():
    expected = QList([1, 2, 3])
    res = EagerQList([1, 2, 3]).qlist()
    assert isinstance(res, QList)
    assert expected == res


def test_empty_constructor():
    expect = []
    res = EagerQList().list()
    assert expect == res


def test_eager_qlist_from_generator():
    def gen():
        yield 1
        yield 2
        yield 3
    expected = EagerQList([1, 2, 3])
    res = EagerQList(gen())
    assert expected == res


def test_getitem_index():
    qlist = EagerQList([1, 2, 3])
    assert 1 == qlist[0]
    assert 3 == qlist[-1]
    pytest.raises(IndexError, lambda: qlist[3])
    pytest.raises(IndexError, lambda: qlist[-4])


def test_getitem_slice():
    qlist = EagerQList(range(10))
    assert isinstance(qlist[:], EagerQList)
    assert qlist == qlist[:]
    assert [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] == qlist[::-1].list()
    assert EagerQList([0, 1, 2]) == qlist[:3]
    assert EagerQList([0, 2, 4]) == qlist[:6:2]


def test_map():
    expected = EagerQList(['0', '1', '2'])
    res = EagerQList(range(3)).map(str)
    assert expected == res


def test_filter():
    expected = EagerQList([0, 2, 4])
    res = EagerQList(range(5)).filter(lambda x: x % 2 == 0)
    assert expected == res


def test_flatmap():
    expected = EagerQList([0, 0, 1, 1])
    res = EagerQList(range(2)).flatmap(lambda x: [x, x])
    assert expected == res, 'standard flatmap failed'

    expected = EagerQList()
    res = EagerQList(range(10)).flatmap(lambda x: [])
    assert expected == res, 'flatmap to empty list failed'


def test_foreach():
    counter = 0

    def counter_up(x):
        nonlocal counter
        counter += 1

    EagerQList().foreach(counter_up)
    assert 0 == counter

    EagerQList(range(10)).foreach(counter_up)
    assert 10 == counter

    elem_sum = 0

    def side_effect_sum(x):
        nonlocal elem_sum
        elem_sum += x

    EagerQList(range(4)).foreach(side_effect_sum)
    assert 6 == elem_sum


def test_fold():
    expected = 6
    res = EagerQList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
    assert expected == res

    expected = '123'
    res = EagerQList(['1', '2', '3']).fold(lambda acc, x: acc + x, '')
    assert expected == res

    expected = '321'
    res = EagerQList(['1', '2', '3']).fold(lambda acc, x: x + acc, '')
    assert expected == res

    res = EagerQList(range(10)).fold(lambda acc, x: 0, 0)
    assert 0 == res


def test_fold_right():
    expected = 6
    res = EagerQList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
    assert expected == res

    expected = '123'
    res = EagerQList(['1', '2', '3']).fold_right(lambda acc, x: x + acc, '')
    assert expected == res

    expected = '321'
    res = EagerQList(['1', '2', '3']).fold_right(lambda acc, x: acc + x, '')
    assert expected == res

    res = EagerQList(range(10)).fold_right(lambda acc, x: 0, 0)
    assert 0 == res


def test_zip():
    expected = EagerQList([(1, 0), (2, 1), (3, 2)])
    res = EagerQList([1, 2, 3]).zip([0, 1, 2])
    assert expected == res

    expected = EagerQList([(1, 0), (2, 1), (3, 2)])
    res = EagerQList([1, 2, 3]).zip(range(100))
    assert expected == res

    expected = EagerQList()
    res = EagerQList(range(10)).zip(QList())
    assert expected == res


def test_sorted():
    expected = EagerQList(range(5))
    res = EagerQList([0, 2, 1, 3, 4]).sorted()
    assert expected == res
    res = EagerQList([0, 2, 1, 3, 4]).sorted(reverse=True)
    assert expected[::-1] == res

    expected = EagerQList([(4, 'a'), (3, 'b'), (7, 'c')])
    res = EagerQList([(3, 'b'), (4, 'a'), (7, 'c')]).sorted(key=lambda x: x[1])
    assert expected == res


def test_method_chaining():
    res = (
        EagerQList(range(100))
        .filter(lambda x: x % 3 == 0)[:10]
        .map(str)[6:]
        .zip(range(4))
        .flatmap(lambda pair: ((pair[0], n) for n in range(pair[1])))
        .fold(lambda acc, x: acc + x[1], 0)
    )
    assert 4 == res


def test_methods_are_eager():
    qlist = EagerQList([1, 2, 3])
    assert isinstance(qlist.map(str), EagerQList)
    assert isinstance(qlist.filter(bool), EagerQList)
    assert isinstance(qlist.flatmap(lambda x: [x, x]), EagerQList)
    assert isinstance(qlist.zip(range(3)), EagerQList)
    assert isinstance(EagerQList([[1, 1]]).flatten(), EagerQList)


def test_flatten():
    expected = EagerQList([1, 2, 3, 1, 2, 3])
    res = EagerQList([[1, 2, 3], [1, 2, 3]]).flatten()
    assert expected == res

    expected = EagerQList()
    res = EagerQList([[], [], []]).flatten()
    assert expected == res

    expected = EagerQList([[1, 2], [1, 2], [1, 2]])
    res = EagerQList([[[1, 2], [1, 2], [1, 2]]]).flatten()
    assert expected == res

