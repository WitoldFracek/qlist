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

    assert 0 == EagerQList().fold(lambda acc, x: acc + x, 0)


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


def test_batch():
    expected = EagerQList([EagerQList([0, 1]), EagerQList([2, 3]), EagerQList([4])])
    res = EagerQList(range(5)).batch(2)
    for b1, b2 in zip(expected, res):
        assert b1 == b2

    expected = EagerQList(range(10))
    res = EagerQList(range(10)).batch(3).flatmap(lambda x: x)
    assert expected == res

    expected = EagerQList(range(10))
    res = EagerQList(range(10)).batch(4).flatten()
    assert expected == res

    expected = EagerQList(range(10))
    res = EagerQList(range(10)).batch(expected.len())[0]
    assert expected == res


def test_iter():
    expected = 0
    res = next(EagerQList(range(10)).iter())
    assert expected == res


def test_chain():
    expected = EagerQList([0, 1, 2, 3, 4, 5])
    res = EagerQList(range(0, 3)).chain(range(3, 6))
    assert expected == res

    expected = EagerQList([0, 1, 2])
    res = EagerQList(range(0, 3)).chain([])
    assert expected == res

    expected = EagerQList([0, 1, 2])
    res = EagerQList([]).chain(range(0, 3))
    assert expected == res

    expected = EagerQList()
    res = EagerQList().chain([])
    assert expected == res


def test_merge():
    expected = EagerQList([1, 2, 3, 4, 5, 6])
    res = EagerQList([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right)
    assert expected == res

    expected = EagerQList([1, 2, 3])
    res = EagerQList([1, 2, 3]).merge([], lambda left, right: False)
    assert expected == res

    expected = EagerQList([1, 2, 3])
    res = EagerQList().merge([1, 2, 3], lambda left, right: True)
    assert expected == res

    expected = EagerQList()
    res = EagerQList().merge([], lambda left, right: False)
    assert expected == res


def test_full_flatten():
    expected = EagerQList(['a', 'b', 'c'])
    res = EagerQList('abc').full_flatten()
    assert expected == res

    assert EagerQList([[1, 2, 3]]).flatten() == EagerQList([[1, 2, 3]]).full_flatten()

    expected = EagerQList([97, 97, 97, "b", "b", "b", "c", "c", "c", "d", "d", "d", " "])
    res = EagerQList([b"aaa", ["bbb"], [["ccc"], "ddd"], "", [[[" "]], []]]).full_flatten()
    assert res == expected

    expected = EagerQList(['abc', 'def', 'ghi'])
    res = EagerQList([['abc', 'def'], 'ghi']).full_flatten(break_str=False)
    assert res == expected

    expected = EagerQList([[], ['abc'], [True, False]])
    res = EagerQList([[], ['abc'], [True, False]]).full_flatten(preserve_type=list)
    assert res == expected

    expected = EagerQList()
    res = EagerQList([[], [[]], [[], []]]).full_flatten()
    assert res == expected

    expected = EagerQList(['a', 'b', 'c', ['def', 'ghi']])
    res = EagerQList(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list)
    assert res == expected

    expected = EagerQList(['abc', ['def', 'ghi']])
    res = EagerQList([('abc',), ['def', 'ghi']]).full_flatten(preserve_type=list, break_str=False)
    assert res == expected


def test_all():
    assert EagerQList([1, True, [1, 2, 3]]).all()
    assert EagerQList().all()
    assert EagerQList([True, True, True]).all()
    assert EagerQList([False, False, False]).all(mapper=lambda x: not x)
    assert EagerQList(['abc', 'def', 'gdi']).all(mapper=lambda s: len(s) > 1)
    assert not EagerQList([False, False, False]).all()
    assert not EagerQList(['', 'a', 'aa']).all()
    assert EagerQList(range(10)).filter(lambda x: x % 2 == 1).map(lambda x: x * 2).all(lambda x: x % 2 == 0)


def test_any():
    assert EagerQList([1, True, [1, 2, 3]]).any()
    assert not EagerQList().any()
    assert EagerQList([True, False, False]).any()
    assert EagerQList([True, True, False]).any(mapper=lambda x: not x)
    assert EagerQList(['abc', 'def', 'gdi']).any(mapper=lambda s: len(s) > 1)
    assert not EagerQList([False, False, False]).any()
    assert EagerQList(['', 'a', 'aa']).any()
    assert EagerQList(range(10)).filter(lambda x: x < 5).any(lambda x: x % 2 == 0)


def test_take_while():
    expected = EagerQList([0, 1, 2])
    res = EagerQList(range(10)).take_while(lambda n: n < 3)
    assert res == expected

    expected = EagerQList()
    res = EagerQList(range(10)).take_while(lambda n: isinstance(n, str))
    assert res == expected

    expected = EagerQList()
    res = EagerQList([]).take_while(lambda x: x > 2)
    assert res == expected

    expected = EagerQList(range(10))
    res = EagerQList(range(5)).take_while(lambda x: x < 100).chain([5, 6, 7, 8, 9])
    assert res == expected


def test_sum():
    assert EagerQList(range(4)).sum() == 6
    assert EagerQList([1]).sum() == 1
    assert EagerQList().sum() is None
    assert EagerQList(range(4)).fold(lambda acc, x: acc + x, 0) == EagerQList(range(4)).sum()


def test_batch_by():
    expected = EagerQList()
    res = EagerQList().batch_by(int)
    assert res == expected

    expected = EagerQList([[0], [1], [2]])
    res= EagerQList(range(3)).batch_by(lambda x: x)
    assert res == expected

    expected = EagerQList([['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']])
    res = EagerQList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0])
    assert res == expected

    expected = EagerQList([['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']])
    res = EagerQList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1])
    assert res == expected

    expected = EagerQList([[0, 1, 2, 3]])
    res = EagerQList(range(4)).batch_by(lambda x: True)
    assert res == expected


def test_min():
    assert EagerQList(range(10)).min() == 0
    assert EagerQList().min() is None
    assert EagerQList(['a', 'aaa', 'aa']).min(key=len) == 'a'


def test_max():
    assert EagerQList(range(10)).max() == 9
    assert EagerQList().max() is None
    assert EagerQList(['a', 'aaa', 'aa']).max(key=len) == 'aaa'


def test_scan():
    expected = EagerQList([1, 3, 6])
    res = EagerQList([1, 2, 3]).scan(lambda acc, x: acc + x, 0)
    assert res == expected

    expected = EagerQList(['1', '12', '123'])
    res = EagerQList(['1', '2', '3']).scan(lambda acc, x: acc + x, '')
    assert res == expected

    expected = EagerQList(['1', '21', '321'])
    res = EagerQList(['1', '2', '3']).scan(lambda acc, x: x + acc, '')
    assert res == expected

    expected = EagerQList([0, 0, 0, 0, 0])
    res = EagerQList(range(5)).scan(lambda acc, x: 0, 0)
    assert res == expected

    expected = EagerQList()
    res = EagerQList().scan(lambda acc, x: x, 0)
    assert res == expected


def test_window():
    expected = EagerQList()
    res = EagerQList().window(2)
    assert res == expected

    expected = EagerQList()
    res = EagerQList(range(10)).window(100)
    assert res == expected

    expected = EagerQList([[0, 1], [1, 2], [2, 3]])
    res = EagerQList(range(4)).window(2)
    assert res == expected

    expected = EagerQList([[0, 1, 2]])
    res = EagerQList(range(3)).window(3)
    assert res == expected

    try:
        EagerQList(range(10)).window(-4)
    except Exception:
        assert True
    else:
        assert False

    expected = EagerQList([[[0, 1, 2], [1, 2, 3]]])
    res = EagerQList(range(4)).window(3).window(2)
    assert res == expected

    expected = EagerQList([[i] for i in range(4)])
    res = EagerQList(range(4)).window(1)
    assert res == expected

    expected = EagerQList()
    res = EagerQList(range(5)).window(6)
    assert res == expected


def test_get():
    assert EagerQList().get(-1) is None
    assert EagerQList().get(0) is None
    assert EagerQList().get(10) is None
    assert EagerQList(range(1, 11)).get(0) == 1
    assert EagerQList(range(1, 11)).get(9) == 10
    assert EagerQList(range(1, 11)).get(10) is None

    assert EagerQList().get(-1, default=100) == 100
    assert EagerQList().get(0, default=100) == 100
    assert EagerQList().get(10, default=100) == 100
    assert EagerQList(range(1, 11)).get(0, default=100) == 1
    assert EagerQList(range(1, 11)).get(9, default=100) == 10
    assert EagerQList(range(1, 11)).get(10, default=100) == 100