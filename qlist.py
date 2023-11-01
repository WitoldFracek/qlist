from typing import TypeVar, Generic, Iterable, Iterator, Callable, Generator

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")


class Lazy(Generic[T]):
    """
    Object representing lazy evaluation of called methods.

    Warning:
    -------
    -------

    Calling any method consumes the current Lazy object. Using the same object
    again may cause errors due to the draining of the generator.

    Example:
    -------
    -------

    .. sourcecode::

        qlist = QList([1, 2, 3, 4])
        filtered = qlist.filter(lambda x: x < 3)
        mapped_str = filtered.map(str)
        mapped_float = filtered.map(float)
        print(mapped_float.qlist())    # prints [1.0, 2.0]
        print(mapped_str.qlist())    # prints []
    """
    def __init__(self, gen: Iterable[T]):
        self.gen = gen

    def list(self) -> list[T]:
        return [elem for elem in self.gen]

    def qlist(self):
        return QList(elem for elem in self.gen)

    def filter(self, pred: Callable[[T], bool]):
        """
        Returns a Lazy object containing all values from this Lazy object for which
        the predicate holds true.
        :param pred: function from T to bool
        """
        def inner():
            for elem in self.gen:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]):
        def inner():
            for elem in self.gen:
                yield mapper(elem)
        return Lazy(inner())

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        acc = init
        for elem in self.gen:
            acc = operation(acc, elem)
        return acc

    def foreach(self, action: Callable[[T], None]):
        for elem in self.gen:
            action(elem)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]):
        def inner():
            for elem in self.gen:
                yield from mapper(elem)
        return Lazy(inner())

    def collect(self):
        return QList(x for x in self.gen)

    def __iter__(self):
        return iter(self.gen)


class QList(list, Generic[T]):
    def filter(self, pred: Callable[[T], bool]) -> Lazy[T]:
        """
        Returns a Lazy object containing all values from the QList for which
        the predicate holds true.

        :param pred: function from T to bool
        """
        def inner():
            for elem in self:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]) -> Lazy[K]:
        def inner():
            for elem in self:
                yield mapper(elem)
        return Lazy(inner())

    def foreach(self, action: Callable[[T], None]):
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K) -> K:
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def len(self) -> int:
        """
        Returns the len of the QList

        (time complexity: O(1))
        """
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> Lazy[K]:
        def inner():
            for elem in self:
                yield from mapper(elem)
        return Lazy(inner())

    def sort(self, key: Callable[[T], SupportsLessThan] = lambda x: x, reverse=False):
        """
        Returns a new QList containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        !! Overrides the default `sort` method in the `list` object !!
        :param key:
        :param reverse:
        :return: sorted QList
        """
        return QList(sorted(self, key=key, reverse=reverse))


if __name__ == '__main__':
    qlist = QList([1, 2, 3, 4])
    filtered = qlist.filter(lambda x: x < 3)
    mapped_str = filtered.map(str)
    mapped_float = filtered.map(float)
    print(mapped_float.collect())
    print(mapped_str.collect())



