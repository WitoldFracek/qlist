import sys; sys.path.append('../src')
from src.qwlist.qwlist import QList, Lazy


def naturals():
    current = 0
    while True:
        yield current
        current += 1


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

    assert 0 == Lazy([]).fold(lambda acc, x: acc + x, 0)


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


def test_batch():
    expected = Lazy([QList([0, 1]), QList([2, 3]), QList([4])])
    res = Lazy(range(5)).batch(2).collect()
    for b1, b2 in zip(expected, res):
        assert b1 == b2

    expected = QList(range(10))
    res = Lazy(range(10)).batch(3).flatmap(lambda x: x).collect()
    assert expected == res

    expected = QList(range(10))
    res = Lazy(range(10)).batch(4).flatten().collect()
    assert expected == res

    expected = QList(range(10))
    res = QList(range(10)).batch(expected.len()).collect()[0]
    assert expected == res

    expected = QList([0, 1])
    res = next(iter(Lazy(range(10)).batch(2)))
    assert expected == res


def test_iter():
    expected = 0
    res = next(Lazy(range(10)).iter())
    assert expected == res


def test_chain():
    expected = QList([0, 1, 2, 3, 4, 5])
    res = Lazy(range(0, 3)).chain(range(3, 6)).collect()
    assert expected == res

    expected = QList([0, 1, 2])
    res = Lazy(range(0, 3)).chain([]).collect()
    assert expected == res

    expected = QList([0, 1, 2])
    res = Lazy([]).chain(range(0, 3)).collect()
    assert expected == res

    expected = QList()
    res = Lazy([]).chain([]).collect()
    assert expected == res


def test_merge():
    expected = QList([1, 2, 3, 4, 5, 6])
    res = Lazy([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right).collect()
    assert expected == res

    expected = QList([1, 2, 3])
    res = Lazy([1, 2, 3]).merge([], lambda left, right: False).collect()
    assert expected == res

    expected = QList([1, 2, 3])
    res = Lazy([]).merge([1, 2, 3], lambda left, right: True).collect()
    assert expected == res

    expected = QList()
    res = Lazy([]).merge([], lambda left, right: False).collect()
    assert expected == res


def test_full_flatten():
    expected = QList(['a', 'b', 'c'])
    res = Lazy('abc').full_flatten().collect()
    assert expected == res

    assert Lazy([[1, 2, 3]]).flatten().collect() == Lazy([[1, 2, 3]]).full_flatten().collect()

    expected = QList([97, 97, 97, "b", "b", "b", "c", "c", "c", "d", "d", "d", " "])
    res = Lazy([b"aaa", ["bbb"], [["ccc"], "ddd"], "", [[[" "]], []]]).full_flatten().collect()
    assert res == expected

    expected = QList(['abc', 'def', 'ghi'])
    res = Lazy([['abc', 'def'], 'ghi']).full_flatten(break_str=False).collect()
    assert res == expected

    expected = QList([[], ['abc'], [True, False]])
    res = Lazy([[], ['abc'], [True, False]]).full_flatten(preserve_type=list).collect()
    assert res == expected

    expected = QList()
    res = Lazy([[], [[]], [[], []]]).full_flatten().collect()
    assert res == expected

    expected = QList(['a', 'b', 'c', ['def', 'ghi']])
    res = Lazy(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list).collect()
    assert res == expected

    expected = QList(['abc', ['def', 'ghi']])
    res = Lazy([('abc',), ['def', 'ghi']]).full_flatten(preserve_type=list, break_str=False).collect()
    assert res == expected


def test_all():
    assert Lazy([1, True, [1, 2, 3]]).all()
    assert Lazy([]).all()
    assert Lazy([True, True, True]).all()
    assert Lazy([False, False, False]).all(mapper=lambda x: not x)
    assert Lazy(['abc', 'def', 'gdi']).all(mapper=lambda s: len(s) > 1)
    assert not Lazy([False, False, False]).all()
    assert not Lazy(['', 'a', 'aa']).all()


def test_any():
    assert Lazy([1, True, [1, 2, 3]]).any()
    assert not Lazy([]).any()
    assert Lazy([True, False, False]).any()
    assert Lazy([True, True, False]).any(mapper=lambda x: not x)
    assert Lazy(['abc', 'def', 'gdi']).any(mapper=lambda s: len(s) > 1)
    assert not Lazy([False, False, False]).any()
    assert Lazy(['', 'a', 'aa']).any()


def test_take_while():
    expected = QList([0, 1, 2])
    res = Lazy(range(10)).take_while(lambda n: n < 3).collect()
    assert res == expected

    expected = QList()
    res = Lazy(range(10)).take_while(lambda n: isinstance(n, str)).collect()
    assert res == expected

    expected = QList()
    res = Lazy([]).take_while(lambda x: x > 2).collect()
    assert res == expected

    expected = QList(range(10))
    res = Lazy(range(5)).take_while(lambda x: x < 100).chain([5, 6, 7, 8, 9]).collect()
    assert res == expected


def test_sum():
    assert Lazy(range(4)).sum() == 6
    assert Lazy([1]).sum() == 1
    assert Lazy([]).sum() is None
    assert Lazy(range(3)).map(str).sum() == '012'
    assert Lazy(range(4)).fold(lambda acc, x: acc + x, 0) == Lazy(range(4)).sum()


def test_batch_by():
    expected = QList()
    res = Lazy([]).batch_by(int).collect()
    assert res == expected

    expected = QList([[0], [1], [2]])
    res = Lazy(range(3)).batch_by(lambda x: x).collect()
    assert res == expected

    expected = QList([['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']])
    res = Lazy(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0]).collect()
    assert res == expected

    expected = QList([['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']])
    res = Lazy(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1]).collect()
    assert res == expected

    expected = QList([[0, 1, 2, 3]])
    res = Lazy(range(4)).batch_by(lambda x: True).collect()
    assert res == expected


def test_min():
    assert Lazy(range(10)).min() == 0
    assert Lazy([]).min() is None
    assert Lazy(['a', 'aaa', 'aa']).min(key=len) == 'a'


def test_max():
    assert Lazy(range(10)).max() == 9
    assert Lazy([]).max() is None
    assert Lazy(['a', 'aaa', 'aa']).max(key=len) == 'aaa'


def test_scan():
    expected = QList([1, 3, 6])
    res = Lazy([1, 2, 3]).scan(lambda acc, x: acc + x, 0).collect()
    assert res == expected

    expected = QList(['1', '12', '123'])
    res = Lazy(['1', '2', '3']).scan(lambda acc, x: acc + x, '').collect()
    assert res == expected

    expected = QList(['1', '21', '321'])
    res = Lazy(['1', '2', '3']).scan(lambda acc, x: x + acc, '').collect()
    assert res == expected

    expected = QList([0, 0, 0, 0, 0])
    res = Lazy(range(5)).scan(lambda acc, x: 0, 0).collect()
    assert res == expected

    expected = QList()
    res = Lazy([]).scan(lambda acc, x: x, 0).collect()
    assert res == expected


def test_window():
    expected = QList()
    res = Lazy([]).window(2).collect()
    assert res == expected

    expected = QList()
    res = Lazy(range(10)).window(100).collect()
    assert res == expected

    expected = QList([[0, 1], [1, 2], [2, 3]])
    res = Lazy(range(4)).window(2).collect()
    assert res == expected

    expected = QList([[0, 1, 2]])
    res = Lazy(range(3)).window(3).collect()
    assert res == expected

    try:
        Lazy(range(10)).window(-4).collect()
    except Exception:
        assert True
    else:
        assert False

    expected = QList([[[0, 1, 2], [1, 2, 3]]])
    res = Lazy(range(4)).window(3).window(2).collect()
    assert res == expected

    expected = QList([[i] for i in range(4)])
    res = Lazy(range(4)).window(1).collect()
    assert res == expected

    expected = QList()
    res = Lazy(range(5)).window(6).collect()
    assert res == expected


def test_first():
    assert Lazy(range(10)).first() == 0
    assert Lazy([]).first() is None


def test_get():
    assert Lazy([]).get(-1) is None
    assert Lazy([]).get(0) is None
    assert Lazy([]).get(10) is None
    assert Lazy(range(1, 11)).get(0) == 1
    assert Lazy(range(1, 11)).get(9) == 10
    assert Lazy(range(1, 11)).get(10) is None

    assert Lazy([]).get(-1, default=100) == 100
    assert Lazy([]).get(0, default=100) == 100
    assert Lazy([]).get(10, default=100) == 100
    assert Lazy(range(1, 11)).get(0, default=100) == 1
    assert Lazy(range(1, 11)).get(9, default=100) == 10
    assert Lazy(range(1, 11)).get(10, default=100) == 100


def test_uncons():
    assert Lazy([]).uncons() is None

    expected = (0, QList([1, 2, 3]))
    head, tail = Lazy(range(4)).uncons()
    res = (head, tail.collect())
    assert res == expected

    expected = (0, QList())
    head, tail = Lazy([0]).uncons()
    res = (head, tail.collect())
    assert res == expected

    assert Lazy(range(4)).filter(lambda x: x > 5).uncons() is None

    nat = Lazy(naturals())
    head, tail = nat.uncons()
    assert head == 0
    head, tail = tail.uncons()
    assert head == 1
    head, tail = tail.uncons()
    assert head == 2


def test_split_when():
    assert Lazy([]).split_when(lambda x: True) is None

    expected = (QList([0]), QList([1, 2, 3]))
    left, right = Lazy(range(4)).split_when(lambda x: True)
    res = (left, right.collect())
    assert res == expected

    expected = (QList([0, 1, 2]), QList([3, 4, 5]))
    left, right = Lazy(range(6)).split_when(lambda x: x == 2)
    res = (left, right.collect())
    assert res == expected

    expected = (QList([0, 1, 2]), QList())
    left, right = Lazy(range(3)).split_when(lambda x: x == 2)
    res = (left, right.collect())
    assert res == expected

    left, right = Lazy(naturals()).split_when(lambda x: x == 2)
    assert left == QList([0, 1, 2])
    left, right = right.split_when(lambda x: x == 5)
    assert left == QList([3, 4, 5])