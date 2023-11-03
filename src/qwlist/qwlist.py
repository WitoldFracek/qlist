from typing import TypeVar, Generic, Iterable, Iterator, Callable, Generator, Union, overload

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
    >>> qlist = QList([1, 2, 3, 4])
    >>> filtered = qlist.filter(lambda x: x < 3)
    >>> mapped_str = filtered.map(str)
    >>> mapped_float = filtered.map(float)
    >>> print(mapped_float.qlist())  # prints [1.0, 2.0]
    >>> print(mapped_str.qlist())    # prints []
    """
    def __init__(self, gen: Iterable[T]):
        """
        Args:
            gen (Iterable[T]): generator used to yield values on collecting items.
        """
        self.gen = gen

    def __repr__(self) -> str:
        return f'Lazy({self.gen})'

    def list(self) -> list[T]:
        """
        Evaluates the Lazy object into list.

        Returns: list[T]
        """
        return [elem for elem in self.gen]

    def qlist(self):
        """
        Evaluates the Lazy object into QList.

        Returns: QList[T]
        """
        return QList(elem for elem in self.gen)

    def filter(self, pred: Callable[[T], bool]):
        """
        Returns a Lazy object containing all values from this Lazy object for which
        the predicate holds true.

        Args:
            pred: function (T) -> bool

        Returns: Lazy[T]
        """
        def inner():
            for elem in self.gen:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]):
        """
        Returns a Lazy object containing all values from this Lazy object with
        the mapping function applied on them.

        Args:
            mapper: function: (T) -> K

        Returns: Lazy[K]
        """
        def inner():
            for elem in self.gen:
                yield mapper(elem)
        return Lazy(inner())

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the Lazy object by processing
        its constituent parts, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: function: (K, T) -> K. Given the initial value `init` applies the
                given combination operator on each element yielded by the Lazy object,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: K

        Examples
        --------
        >>> s = QList([1, 2, 3]).map(float).fold(lambda acc, x: acc + x, 0.0)
        6.0
        """
        acc = init
        for elem in self.gen:
            acc = operation(acc, elem)
        return acc

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of yielded elements.

        Args:
            action: function (T) -> None

        Returns: None
        """
        for elem in self.gen:
            action(elem)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]):
        """
        Applies the mapper function to each of the yielded elements and flattens the results.

        Args:
            mapper: function (T) -> Lazy[K]

        Returns: Lazy[K]

        Examples:
        --------
        >>> QList([1, 2]).map(str).flatmap(lambda x: [x, x]).qlist()
        ['1', '1', '2', '2']
        """
        def inner():
            for elem in self.gen:
                yield from mapper(elem)
        return Lazy(inner())

    def zip(self, other: Iterable[K]) -> "Lazy[tuple[T, K]]":
        """
        Combines this Lazy object with the given Iterable elementwise as tuples.
         The returned Lazy objects yields at most the number of elements of
         the shorter sequence (Lazy or Iterable).

        Args:
            other: iterable to zip with this QList.

        Returns: Lazy[tuple[T, K]]
        """
        return Lazy(zip(self.gen, other))

    def collect(self):
        """
        Same as calling qlist()

        Returns: QList[T]

        """
        return QList(x for x in self.gen)

    def __iter__(self):
        return iter(self.gen)


class QList(list):

    @overload
    def __getitem__(self, item: slice) -> "QList[T]":
        ...

    @overload
    def __getitem__(self, item: int) -> T:
        ...

    def __getitem__(self, item) -> T:
        if isinstance(item, slice):
            return QList(super().__getitem__(item))
        return super().__getitem__(item)

    def slice(self, s: slice) -> Lazy[T]:
        """
        Calling this method with `slice(3)` works similarly to
        `list[:3]` but is lazy evaluated.

        Args:
            s: slice object

        Returns: Lazy[T]
        """
        assert isinstance(s, slice), f"slice method argument must be a slice object. Got {type(s)}."

        def inner():
            for elem in self[s]:
                yield elem
        return Lazy(inner())

    def list(self) -> list[T]:
        """
        Changes QList into list.

        Returns: list[T]
        """
        return list(self)

    def filter(self, pred: Callable[[T], bool]) -> Lazy[T]:
        """
        Returns a Lazy object containing all values from the QList for which
        the predicate holds true.

        Args:
             pred: function (T) -> bool
        Returns: Lazy[T]
        """
        def inner():
            for elem in self:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]) -> Lazy[K]:
        """
        Returns a Lazy object containing all values from QList with
        the mapping function applied on them.

        Args:
            mapper: function: (T) -> K

        Returns: Lazy[K]
        """
        def inner():
            for elem in self:
                yield mapper(elem)
        return Lazy(inner())

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the QList elements.

        Args:
            action: function (T) -> None

        Returns: None
        """
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the QList by processing
        its values, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: function: (K, T) -> K
                Given the initial value `init` applies the
                given combination operator on each element of the QList,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: K

        Examples
        --------
        >>> s = QList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
        6
        """
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the QList by processing
        its values, building up the final value.

        Args:
            operation: function: (K, T) -> K
                Given the initial value `init` applies the
                given combination operator on each element of the QList, starting from the
                last element, treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: K

        Examples
        --------
        >>> s = QList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
        6
        """
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def len(self) -> int:
        """
        Returns the len of the QList

        (time complexity: O(1))

        Returns: int
        """
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> Lazy[K]:
        """
        Applies the mapper function to each element of the QList and flattens the results.

        Args:
            mapper: function (T) -> Lazy[K]

        Returns: Lazy[K]

        Examples:
        --------
        >>> QList([1, 2]).flatmap(lambda x: [x, x]).qlist()
        [1, 1, 2, 2]
        """
        def inner():
            for elem in self:
                yield from mapper(elem)
        return Lazy(inner())

    def zip(self, other: Iterable[K]) -> Lazy[tuple[T, K]]:
        """
        Combines this QList with the given Iterable elementwise as tuples.
         The returned Lazy objects yields at most the number of elements of
         the shorter sequence (self or Iterable).

        Args:
            other: iterable to zip with this QList.

        Returns: Lazy[tuple[T, K]]
        """
        return Lazy(zip(self, other))

    def sorted(self, key: Callable[[T], SupportsLessThan] = lambda x: x, reverse: bool = False) -> "QList[T]":
        """
        Returns a new QList containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        Args:
            key: function (T) -> SupportsLessThan. Defaults to identity function (x: T) -> x
            reverse: if set to True sorts values in descending order. Defaults to False

        Returns: QList[T]
        """
        return QList(sorted(self, key=key, reverse=reverse))


if __name__ == '__main__':
    (
        QList(x for x in range(100))
        [::-1]
        .slice(slice(20, 80))
        .zip([True] * 30 + [False] * 30)
        .map(lambda x: x[0] / 2 if x[1] else float(x[0]))
        .filter(lambda x: x > 46)
        .flatmap(lambda x: [x + 0j, x + 1j])
        .foreach(print)
    )

