import sys;
from gc import collect

sys.path.append('../src')
from src.qwlist.qwlist import QList, Lazy
from src.qwlist.eager import EagerQList
import pytest


def test_qlist_from_iterable_constructor():
    expected = QList([0, 1, 2])
    res = QList(range(3))
    for e, r in zip(expected, res):
        assert e == r


def test_len():
    assert 3 == QList([0, 1, 2]).len()


def test_conversion_to_list():
    expected = [1, 2, 3]
    res = QList([1, 2, 3]).list()
    assert isinstance(res, list)
    assert expected == res


def test_conversion_to_eager_qlist():
    expected = EagerQList([1, 2, 3])
    res = QList([1, 2, 3]).eager()
    assert isinstance(res, EagerQList)
    assert expected == res


def test_empty_constructor():
    expect = []
    res = QList().list()
    assert expect == res


def test_qlist_from_generator():
    def gen():
        yield 1
        yield 2
        yield 3
    expected = QList([1, 2, 3])
    res = QList(gen())
    assert expected == res


def test_getitem_index():
    qlist = QList([1, 2, 3])
    assert 1 == qlist[0]
    assert 3 == qlist[-1]
    pytest.raises(IndexError, lambda: qlist[3])
    pytest.raises(IndexError, lambda: qlist[-4])


def test_getitem_slice():
    qlist = QList(range(10))
    assert isinstance(qlist[:], QList)
    assert qlist == qlist[:]
    assert [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] == qlist[::-1].list()
    assert QList([0, 1, 2]) == qlist[:3]
    assert QList([0, 2, 4]) == qlist[:6:2]


def test_map():
    expected = QList(['0', '1', '2'])
    res = QList(range(3)).map(str).collect()
    assert expected == res


def test_filter():
    expected = QList([0, 2, 4])
    res = QList(range(5)).filter(lambda x: x % 2 == 0).collect()
    assert expected == res


def test_flatmap():
    expected = QList([0, 0, 1, 1])
    res = QList(range(2)).flatmap(lambda x: [x, x]).collect()
    assert expected == res, 'standard flatmap failed'

    expected = QList()
    res = QList(range(10)).flatmap(lambda x: []).collect()
    assert expected == res, 'flatmap to empty list failed'


def test_foreach():
    counter = 0

    def counter_up(x):
        nonlocal counter
        counter += 1

    QList().foreach(counter_up)
    assert 0 == counter

    QList(range(10)).foreach(counter_up)
    assert 10 == counter

    elem_sum = 0

    def side_effect_sum(x):
        nonlocal elem_sum
        elem_sum += x

    QList(range(4)).foreach(side_effect_sum)
    assert 6 == elem_sum


def test_fold():
    expected = 6
    res = QList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
    assert expected == res

    expected = '123'
    res = QList(['1', '2', '3']).fold(lambda acc, x: acc + x, '')
    assert expected == res

    expected = '321'
    res = QList(['1', '2', '3']).fold(lambda acc, x: x + acc, '')
    assert expected == res

    res = QList(range(10)).fold(lambda acc, x: 0, 0)
    assert 0 == res

    assert 0 == QList().fold(lambda acc, x: acc + x, 0)


def test_fold_right():
    expected = 6
    res = QList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
    assert expected == res

    expected = '123'
    res = QList(['1', '2', '3']).fold_right(lambda acc, x: x + acc, '')
    assert expected == res

    expected = '321'
    res = QList(['1', '2', '3']).fold_right(lambda acc, x: acc + x, '')
    assert expected == res

    res = QList(range(10)).fold_right(lambda acc, x: 0, 0)
    assert 0 == res


def test_lazy_slice():
    qlist = QList(range(10))
    assert isinstance(qlist.slice(slice(0)).collect(), QList)
    assert qlist == qlist.slice(slice(None, None)).collect()
    assert [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] == qlist.slice(slice(None, None, -1)).list()
    assert QList([0, 1, 2]) == qlist.slice(slice(3)).collect()
    assert QList([0, 2, 4]) == qlist.slice(slice(0, 6, 2)).collect()


def test_zip():
    expected = QList([(1, 0), (2, 1), (3, 2)])
    res = QList([1, 2, 3]).zip([0, 1, 2]).collect()
    assert expected == res

    expected = QList([(1, 0), (2, 1), (3, 2)])
    res = QList([1, 2, 3]).zip(range(100)).collect()
    assert expected == res

    expected = QList()
    res = QList(range(10)).zip(QList()).collect()
    assert expected == res


def test_take():
    expected = QList([0, 1, 2, 3])
    res = QList(range(10)).take(4).collect()
    assert expected == res

    expected = QList()
    res1 = QList(range(10)).take(0).collect()
    res2 = QList(range(10)).take(-1).collect()
    assert expected == res1
    assert expected == res2

    expected = QList([0, 1, 2, 3])
    res = QList(range(4)).take(100).collect()
    assert expected == res


def test_skip():
    expected = QList([2, 3, 4])
    res = QList(range(5)).skip(2).collect()
    assert expected == res

    expected = QList([0, 1, 2, 3, 4])
    res1 = QList(range(5)).skip(0).collect()
    res2 = QList(range(5)).skip(-1).collect()
    assert expected == res1
    assert expected == res2

    expected = QList()
    res = QList(range(5)).skip(100).collect()
    assert expected == res


def test_sorted():
    expected = QList(range(5))
    res = QList([0, 2, 1, 3, 4]).sorted()
    assert expected == res
    res = QList([0, 2, 1, 3, 4]).sorted(reverse=True)
    assert expected[::-1] == res

    expected = QList([(4, 'a'), (3, 'b'), (7, 'c')])
    res = QList([(3, 'b'), (4, 'a'), (7, 'c')]).sorted(key=lambda x: x[1])
    assert expected == res


def test_method_chaining():
    res = (
        QList(range(100))
        .filter(lambda x: x % 3 == 0)
        .take(10)
        .map(str)
        .skip(6)
        .zip(range(4))
        .flatmap(lambda pair: ((pair[0], n) for n in range(pair[1])))
        .fold(lambda acc, x: acc + x[1], 0)
    )
    assert 4 == res

    res = (
        QList(range(10))
        .filter(lambda x: x % 2 == 0)
        .cycle()
        .take(10)
        .collect()
    )
    assert res == QList([0, 2, 4, 6, 8, 0, 2, 4, 6, 8])

    res = (
        QList(range(10))
        .map(lambda x: x % 2 == 0)
        .filter(lambda x: x)
        .cycle()
        .take(20)
        .collect()
    )
    assert res == QList([True] * 20)


def test_enumerate():
    expected = QList([(0, 'a'), (1, 'b'), (2, 'c')])
    res = QList(['a', 'b', 'c']).enumerate().collect()
    assert res == expected

    expected = QList([(5, 'a'), (6, 'b'), (7, 'c')])
    res = QList(['a', 'b', 'c']).enumerate(start=5).collect()
    assert res == expected

    expected = QList([(-1, 'a'), (0, 'b'), (1, 'c')])
    res = QList(['a', 'b', 'c']).enumerate(start=-1).collect()
    assert res == expected

    expected = QList([0, 1, 2, 3])
    res = QList('a').cycle().enumerate().map(lambda x: x[0]).take(4).collect()
    assert res == expected

    expected = QList([(0, 'a'), (1, 'a'), (2, 'a'), (0, 'a'), (1, 'a'), (2, 'a')])
    res = QList('a').cycle().take(3).enumerate().cycle().take(6).collect()
    assert res == expected


def test_methods_are_lazy():
    qlist = QList([1, 2, 3])
    assert isinstance(qlist.map(str), Lazy)
    assert isinstance(qlist.filter(bool), Lazy)
    assert isinstance(qlist.flatmap(lambda x: [x, x]), Lazy)
    assert isinstance(qlist.zip(range(3)), Lazy)
    assert isinstance(qlist.slice(slice(3)), Lazy)
    assert isinstance(qlist.take(3), Lazy)
    assert isinstance(qlist.skip(3), Lazy)
    assert isinstance(QList([[1, 1]]).flatten(), Lazy)


def test_flatten():
    expected = QList([1, 2, 3, 1, 2, 3])
    res = QList([[1, 2, 3], [1, 2, 3]]).flatten().collect()
    assert expected == res

    expected = QList()
    res = QList([[], [], []]).flatten().collect()
    assert expected == res

    expected = QList([[1, 2], [1, 2], [1, 2]])
    res = QList([[[1, 2], [1, 2], [1, 2]]]).flatten().collect()
    assert expected == res

    try:
        QList([1, 2, 3]).flatten().collect()
    except TypeError:
        assert True
    else:
        assert False


def test_cycle():
    expected = QList([1, 2, 3, 1, 2, 3, 1])
    res = QList([1, 2, 3]).cycle().take(7).collect()
    assert expected == res

    expected = QList()
    res = QList().cycle().take(7).collect()
    assert expected == res

    expected = QList(range(3))
    res = QList(range(10)).cycle().take(3).collect()
    assert expected == res


def test_batch():
    expected = QList([QList([0, 1]), QList([2, 3]), QList([4])])
    res = QList(range(5)).batch(2).collect()
    for b1, b2 in zip(expected, res):
        assert b1 == b2

    expected = QList(range(10))
    res = QList(range(10)).batch(3).flatmap(lambda x: x).collect()
    assert expected == res

    expected = QList(range(10))
    res = QList(range(10)).batch(4).flatten().collect()
    assert expected == res

    expected = QList(range(10))
    res = QList(range(10)).batch(expected.len()).collect()[0]
    assert expected == res


def test_iter():
    expected = 0
    res = next(QList(range(10)).iter())
    assert expected == res


def test_chain():
    expected = QList([0, 1, 2, 3, 4, 5])
    res = QList(range(0, 3)).chain(range(3, 6)).collect()
    assert expected == res

    expected = QList([0, 1, 2])
    res = QList(range(0, 3)).chain([]).collect()
    assert expected == res

    expected = QList([0, 1, 2])
    res = QList([]).chain(range(0, 3)).collect()
    assert expected == res

    expected = QList()
    res = QList().chain([]).collect()
    assert expected == res


def test_merge():
    expected = QList([1, 2, 3, 4, 5, 6])
    res = QList([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right).collect()
    assert expected == res

    expected = QList([1, 2, 3])
    res = QList([1, 2, 3]).merge([], lambda left, right: False).collect()
    assert expected == res

    expected = QList([1, 2, 3])
    res = QList().merge([1, 2, 3], lambda left, right: True).collect()
    assert expected == res

    expected = QList()
    res = QList().merge([], lambda left, right: False).collect()
    assert expected == res


def test_full_flatten():
    expected = QList(['a', 'b', 'c'])
    res = QList('abc').full_flatten().collect()
    assert expected == res

    assert QList([[1, 2, 3]]).flatten().collect() == QList([[1, 2, 3]]).full_flatten().collect()

    expected = QList([97, 97, 97, "b", "b", "b", "c", "c", "c", "d", "d", "d", " "])
    res = QList([b"aaa", ["bbb"], [["ccc"], "ddd"], "", [[[" "]], []]]).full_flatten().collect()
    assert res == expected

    expected = QList(['abc', 'def', 'ghi'])
    res = QList([['abc', 'def'], 'ghi']).full_flatten(break_str=False).collect()
    assert res == expected

    expected = QList([[], ['abc'], [True, False]])
    res = QList([[], ['abc'], [True, False]]).full_flatten(preserve_type=list).collect()
    assert res == expected

    expected = QList()
    res = QList([[], [[]], [[], []]]).full_flatten().collect()
    assert res == expected

    expected = QList(['a', 'b', 'c', ['def', 'ghi']])
    res = QList(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list).collect()
    assert res == expected

    expected = QList(['abc', ['def', 'ghi']])
    res = Lazy([('abc',), ['def', 'ghi']]).full_flatten(preserve_type=list, break_str=False).collect()
    assert res == expected


def test_all():
    assert QList([1, True, [1, 2, 3]]).all()
    assert QList().all()
    assert QList([True, True, True]).all()
    assert QList([False, False, False]).all(mapper=lambda x: not x)
    assert QList(['abc', 'def', 'gdi']).all(mapper=lambda s: len(s) > 1)
    assert not QList([False, False, False]).all()
    assert not QList(['', 'a', 'aa']).all()
    assert QList(range(10)).filter(lambda x: x % 2 == 1).map(lambda x: x * 2).all(lambda x: x % 2 == 0)


def test_any():
    assert QList([1, True, [1, 2, 3]]).any()
    assert not QList().any()
    assert QList([True, False, False]).any()
    assert QList([True, True, False]).any(mapper=lambda x: not x)
    assert QList(['abc', 'def', 'gdi']).any(mapper=lambda s: len(s) > 1)
    assert not QList([False, False, False]).any()
    assert QList(['', 'a', 'aa']).any()
    assert QList(range(10)).filter(lambda x: x < 5).any(lambda x: x % 2 == 0)


def test_take_while():
    expected = QList([0, 1, 2])
    res = QList(range(10)).take_while(lambda n: n < 3).collect()
    assert res == expected

    expected = QList()
    res = QList(range(10)).take_while(lambda n: isinstance(n, str)).collect()
    assert res == expected

    expected = QList()
    res = QList().take_while(lambda x: x > 2).collect()
    assert res == expected

    expected = QList(range(10))
    res = QList(range(5)).take_while(lambda x: x < 100).chain([5, 6, 7, 8, 9]).collect()
    assert res == expected


def test_sum():
    assert QList(range(4)).sum() == 6
    assert QList([1]).sum() == 1
    assert QList().sum() is None
    assert QList(range(4)).fold(lambda acc, x: acc + x, 0) == QList(range(4)).sum()


def test_batch_by():
    expected = QList()
    res = QList().batch_by(int).collect()
    assert res == expected

    expected = QList([[0], [1], [2]])
    res = QList(range(3)).batch_by(lambda x: x).collect()
    assert res == expected

    expected = QList([['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']])
    res = QList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0]).collect()
    assert res == expected

    expected = QList([['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']])
    res = QList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1]).collect()
    assert res == expected

    expected = QList([[0, 1, 2, 3]])
    res = QList(range(4)).batch_by(lambda x: True).collect()
    assert res == expected


def test_min():
    assert QList(range(10)).min() == 0
    assert QList([]).min() is None
    assert QList(['a', 'aaa', 'aa']).min(key=len) == 'a'


def test_max():
    assert QList(range(10)).max() == 9
    assert QList([]).max() is None
    assert QList(['a', 'aaa', 'aa']).max(key=len) == 'aaa'


def test_scan():
    expected = QList([1, 3, 6])
    res = QList([1, 2, 3]).scan(lambda acc, x: acc + x, 0).collect()
    assert res == expected

    expected = QList(['1', '12', '123'])
    res = QList(['1', '2', '3']).scan(lambda acc, x: acc + x, '').collect()
    assert res == expected

    expected = QList(['1', '21', '321'])
    res = QList(['1', '2', '3']).scan(lambda acc, x: x + acc, '').collect()
    assert res == expected

    expected = QList([0, 0, 0, 0, 0])
    res = QList(range(5)).scan(lambda acc, x: 0, 0).collect()
    assert res == expected

    expected = QList()
    res = QList([]).scan(lambda acc, x: x, 0).collect()
    assert res == expected


def test_window():
    expected = QList()
    res = QList().window(2).collect()
    assert res == expected

    expected = QList()
    res = QList(range(10)).window(100).collect()
    assert res == expected

    expected = QList([[0, 1], [1, 2], [2, 3]])
    res = QList(range(4)).window(2).collect()
    assert res == expected

    expected = QList([[0, 1, 2]])
    res = QList(range(3)).window(3).collect()
    assert res == expected

    try:
        QList(range(10)).window(-4).collect()
    except Exception:
        assert True
    else:
        assert False

    expected = QList([[[0, 1, 2], [1, 2, 3]]])
    res = QList(range(4)).window(3).window(2).collect()
    assert res == expected

    expected = QList([[i] for i in range(4)])
    res = QList(range(4)).window(1).collect()
    assert res == expected

    expected = QList()
    res = QList(range(5)).window(6).collect()
    assert res == expected


def test_get():
    assert QList().get(-1) is None
    assert QList().get(0) is None
    assert QList().get(10) is None
    assert QList(range(1, 11)).get(0) == 1
    assert QList(range(1, 11)).get(9) == 10
    assert QList(range(1, 11)).get(10) is None

    assert QList().get(-1, default=100) == 100
    assert QList().get(0, default=100) == 100
    assert QList().get(10, default=100) == 100
    assert QList(range(1, 11)).get(0, default=100) == 1
    assert QList(range(1, 11)).get(9, default=100) == 10
    assert QList(range(1, 11)).get(10, default=100) == 100


