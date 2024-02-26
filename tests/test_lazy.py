import sys; sys.path.append('../src')
from src.qwlist.qwlist import QList, Lazy
import pytest


def test_lazy_from_iterable_constructor():
    expected = Lazy([0, 1, 2])
    res = Lazy(range(3))
    for e, r in zip(expected, res):
        assert e == r


def test_conversion_to_list():
    expected = [1, 2, 3]
    res = Lazy(range(1, 4)).list()
    assert isinstance(res, list)
    assert expected == res


def test_conversion_to_qlist():
    expected = QList([1, 2, 3])
    res = Lazy(range(1, 4)).qlist()
    assert isinstance(res, QList)
    assert expected == res


def test_collect_from_lazy():
    expected = QList([1, 2, 3])
    res = expected.map(lambda x: x).collect()
    assert expected == res
    res = expected.map(lambda x: x).qlist()
    assert expected == res


def test_lazy_from_generator():
    def gen():
        yield 1
        yield 2
        yield 3
    expected = QList([1, 2, 3])
    res = Lazy(gen())
    assert expected == res.collect()


def test_lazy_operations():
    expected = QList(range(3))
    res = Lazy(range(3)).map(lambda x: x).collect()
    assert expected == res


def test_map():
    expected = QList(['0', '1', '2'])
    res = Lazy(range(3)).map(str).collect()
    assert expected == res


def test_filter():
    expected = QList([0, 2, 4])
    res = Lazy(range(5)).filter(lambda x: x % 2 == 0).collect()
    assert expected == res


def test_flatmap():
    expected = QList([0, 0, 1, 1])
    res = Lazy(range(2)).flatmap(lambda x: [x, x]).collect()
    assert expected == res, 'standard flatmap failed'

    expected = QList()
    res = Lazy(range(10)).flatmap(lambda x: []).collect()
    assert expected == res, 'flatmap to empty list failed'


def test_foreach():
    counter = 0

    def counter_up(x):
        nonlocal counter
        counter += 1

    Lazy([]).foreach(counter_up)
    assert 0 == counter

    Lazy(range(10)).foreach(counter_up)
    assert 10 == counter

    elem_sum = 0

    def side_effect_sum(x):
        nonlocal elem_sum
        elem_sum += x

    Lazy(range(4)).foreach(side_effect_sum)
    assert 6 == elem_sum


def test_fold():
    expected = 6
    res = Lazy([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
    assert expected == res

    expected = '123'
    res = Lazy(['1', '2', '3']).fold(lambda acc, x: acc + x, '')
    assert expected == res

    expected = '321'
    res = Lazy(['1', '2', '3']).fold(lambda acc, x: x + acc, '')
    assert expected == res

    res = Lazy(range(10)).fold(lambda acc, x: 0, 0)
    assert 0 == res


def test_zip():
    expected = QList([(1, 0), (2, 1), (3, 2)])
    res = Lazy([1, 2, 3]).zip([0, 1, 2]).collect()
    assert expected == res

    expected = QList([(1, 0), (2, 1), (3, 2)])
    res = Lazy([1, 2, 3]).zip(range(100)).collect()
    assert expected == res

    expected = QList()
    res = Lazy(range(10)).zip([]).collect()
    assert expected == res


def test_take():
    expected = QList([0, 1, 2, 3])
    res = Lazy(range(10)).take(4).collect()
    assert expected == res

    expected = QList()
    res1 = Lazy(range(10)).take(0).collect()
    res2 = Lazy(range(10)).take(-1).collect()
    assert expected == res1
    assert expected == res2

    expected = QList([0, 1, 2, 3])
    res = QList(range(4)).take(100).collect()
    assert expected == res


def test_skip():
    expected = QList([2, 3, 4])
    res = Lazy(range(5)).skip(2).collect()
    assert expected == res

    expected = QList([0, 1, 2, 3, 4])
    res1 = Lazy(range(5)).skip(0).collect()
    res2 = Lazy(range(5)).skip(-1).collect()
    assert expected == res1
    assert expected == res2

    expected = QList()
    res = Lazy(range(5)).skip(100).collect()
    assert expected == res


def test_enumerate():
    expected = QList([(0, 'a'), (1, 'b'), (2, 'c')])
    res = Lazy(['a', 'b', 'c']).enumerate().collect()
    assert res == expected

    expected = QList([(5, 'a'), (6, 'b'), (7, 'c')])
    res = Lazy(['a', 'b', 'c']).enumerate(start=5).collect()
    assert res == expected

    expected = QList([(-1, 'a'), (0, 'b'), (1, 'c')])
    res = Lazy(['a', 'b', 'c']).enumerate(start=-1).collect()
    assert res == expected

    expected = QList([0, 1, 2, 3])
    res = Lazy('a').cycle().enumerate().map(lambda x: x[0]).take(4).collect()
    assert res == expected

    expected = QList([(0, 'a'), (1, 'a'), (2, 'a'), (0, 'a'), (1, 'a'), (2, 'a')])
    res = Lazy('a').cycle().take(3).enumerate().cycle().take(6).collect()
    assert res == expected


def test_method_chaining():
    res = (
        Lazy(range(100))
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
        Lazy(range(10))
        .filter(lambda x: x % 2 == 0)
        .cycle()
        .take(10)
        .collect()
    )
    assert res == QList([0, 2, 4, 6, 8, 0, 2, 4, 6, 8])

    res = (
        Lazy(range(10))
        .map(lambda x: x % 2 == 0)
        .filter(lambda x: x)
        .cycle()
        .take(20)
        .collect()
    )
    assert res == QList([True] * 20)


def test_methods_are_lazy():
    lazy = Lazy([1, 2, 3])
    assert isinstance(lazy.map(str), Lazy)
    assert isinstance(lazy.filter(bool), Lazy)
    assert isinstance(lazy.flatmap(lambda x: [x, x]), Lazy)
    assert isinstance(lazy.zip(range(3)), Lazy)
    assert isinstance(lazy.take(3), Lazy)
    assert isinstance(lazy.skip(3), Lazy)


def test_lazy_into_iter():
    results = [0, 1, 2]
    for expected, elem in zip(results, Lazy(range(3))):
        assert expected == elem

    for expected, elem in zip(results, Lazy([0, 1, 2])):
        assert expected == elem

    def gen():
        yield 0; yield 1; yield 2

    for expected, elem in zip(results, Lazy(gen())):
        assert expected == elem


def test_flatten():
    expected = QList([1, 2, 3, 1, 2, 3])
    res = Lazy([[1, 2, 3], [1, 2, 3]]).flatten().collect()
    assert expected == res

    expected = QList()
    res = Lazy([[], [], []]).flatten().collect()
    assert expected == res

    expected = QList([[1, 2], [1, 2], [1, 2]])
    res = Lazy([[[1, 2], [1, 2], [1, 2]]]).flatten().collect()
    assert expected == res


def test_cycle():
    expected = QList([1, 2, 3, 1, 2, 3, 1])
    res = Lazy([1, 2, 3]).cycle().take(7).collect()
    assert expected == res

    expected = QList()
    res = Lazy([]).cycle().take(7).collect()
    assert expected == res

    expected = QList(range(3))
    res = Lazy(range(10)).cycle().take(3).collect()
    assert expected == res
