from typing import TypeVar, Iterable, Callable, overload

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")


class EagerQList(list):
    @overload
    def __getitem__(self, item: int) -> T:
        ...

    @overload
    def __getitem__(self, item: slice) -> "EagerQList[T]":
        ...

    def __getitem__(self, item):
        if isinstance(item, slice):
            return EagerQList(super().__getitem__(item))
        return super().__getitem__(item)

    def list(self) -> list[T]:
        """
        Changes EagerQList into list.

        Returns: list[T]
        """
        return list(self)

    def qlist(self) -> "QList[T]":
        """
        Changes EagerQList into Qlist.

        Returns: QList[T]
        """
        from qwlist.qwlist import QList
        return QList(self)

    def filter(self, pred: Callable[[T], bool]) -> "EagerQList[T]":
        """
        Returns a EagerQList containing all values from this EagerQList for which
        the predicate holds true.

        Args:
             pred: function (T) -> bool
        Returns: EagerQList[T]
        """
        return EagerQList(elem for elem in self if pred(elem))

    def map(self, mapper: Callable[[T], K]) -> "EagerQList[K]":
        """
        Returns a EagerQList containing all values from this EagerQList with
        the mapping function applied on them.

        Args:
            mapper: function: (T) -> K

        Returns: EagerQList[K]
        """
        return EagerQList(mapper(elem) for elem in self)

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the EagerQList elements.

        Args:
            action: function (T) -> None

        Returns: None
        """
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the EagerQList by processing
        its values, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: function: (K, T) -> K
                Given the initial value `init` applies the
                given combination operator on each element of the EagerQList,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: K

        Examples
        --------
        >>> s = EagerQList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
        6
        """
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the EagerQList by processing
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
        >>> s = EagerQList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
        6
        """
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def len(self):
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> "EagerQList[K]":
        """
        Applies the mapper function to each element of the EagerQList and flattens the results.

        Args:
            mapper: function (T) -> Iterable[K]

        Returns: EagerQList[K]

        Examples:
        --------
        >>> EagerQList([1, 2]).flatmap(lambda x: [x, x])
        [1, 1, 2, 2]
        """
        return EagerQList(x for elem in self for x in mapper(elem))

    def zip(self, other: Iterable[K]) -> "EagerQList[tuple[T, K]]":
        """
        Combines this EagerQList with the given Iterable elementwise as tuples.
         The returned EagerQList objects has at most the number of elements of
         the shorter sequence (self or Iterable).

        Args:
            other: iterable to zip with this EagerQList.

        Returns: EagerQList[tuple[T, K]]
        """
        return EagerQList(zip(self, other))

    def sorted(self, key: Callable[[T], SupportsLessThan] = lambda x: x, reverse: bool = False) -> "EagerQList[T]":
        """
        Returns a new EagerQList containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        Args:
            key: function (T) -> SupportsLessThan. Defaults to identity function (x: T) -> x
            reverse: if set to True sorts values in descending order. Defaults to False

        Returns: EagerQList[T]
        """
        return EagerQList(sorted(self, key=key, reverse=reverse))


if __name__ == '__main__':
    (
        EagerQList(x for x in range(100))
        [::-1]
        .zip([True] * 30 + [False] * 30)
        .map(lambda x: x[0] / 2 if x[1] else float(x[0]))
        .filter(lambda x: x > 46)
        .flatmap(lambda x: [x + 0j, x + 1j])
        .foreach(print)
    )
