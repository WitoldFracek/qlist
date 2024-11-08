from typing import TypeVar, Iterable, Callable, overload, Iterator, Optional, Type

from src.qwlist import QList

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")
SupportsAdd = TypeVar("SupportsAdd")
Booly = TypeVar('Booly')


class EagerQList(list):
    """
    `EagerQList` is a python list extension that adds several chainable, methods to the standard `list`.

    Found in `qwlist.eager.EagerQList`
    """
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

    def iter(self) -> Iterator[T]:
        """
        Changes EagerQList[T] into Iterator[T].

        Returns: `Iterator[T]`
        """
        return iter(self)

    def list(self) -> list[T]:
        """
        Changes `EagerQList` into `list`.

        Returns: `list[T]`
        """
        return list(self)

    def qlist(self) -> "QList[T]":
        """
        Changes `EagerQList` into `Qlist`.

        Returns: `QList[T]`
        """
        return QList(self)

    def filter(self, pred: Callable[[T], bool]) -> "EagerQList[T]":
        """
        Returns an `EagerQList` containing all values from this `EagerQList` for which
        the predicate holds true.

        Args:
             pred: `function (T) -> bool`

        Returns: `EagerQList[T]`

        Examples:
            >>> EagerQList([1, 2, 3, 4]).filter(lambda x: x < 3)
            [1, 2]
        """
        return EagerQList(elem for elem in self if pred(elem))

    def map(self, mapper: Callable[[T], K]) -> "EagerQList[K]":
        """
        Returns an `EagerQList` containing all values from this `EagerQList` with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns: `EagerQList[K]`
        """
        return EagerQList(mapper(elem) for elem in self)

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the `EagerQList` elements.

        Args:
            action: `function (T) -> None`

        Returns: `None`
        """
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the `EagerQList` by processing
        its values, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: `function: (K, T) -> K`
                Given the initial value `init` applies the
                given combination operator on each element of the EagerQList,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: `K`

        Examples:
            >>> s = EagerQList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the `EagerQList` by processing
        its values, building up the final value.

        Args:
            operation: `function: (K, T) -> K`
                Given the initial value `init` applies the
                given combination operator on each element of the EagerQList, starting from the
                last element, treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: `K`

        Examples:
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
        Applies the mapper function to each element of the `EagerQList` and flattens the results.

        Args:
            mapper: `function (T) -> Iterable[K]`

        Returns: `EagerQList[K]`

        Examples:
            >>> EagerQList([1, 2]).flatmap(lambda x: [x, x])
            [1, 1, 2, 2]
        """
        return EagerQList(x for elem in self for x in mapper(elem))

    def zip(self, other: Iterable[K]) -> "EagerQList[tuple[T, K]]":
        """
        Combines this `EagerQList` with the given `Iterable` elementwise as tuples.
         The returned `EagerQList` objects has at most the number of elements of
         the shorter sequence (`self` or `Iterable`).

        Args:
            other: iterable to zip with this `EagerQList`.

        Returns: `EagerQList[tuple[T, K]]`
        """
        return EagerQList(zip(self, other))

    def sorted(self, key: Callable[[T], SupportsLessThan] = None, reverse: bool = False) -> "EagerQList[T]":
        """
        Returns a new `EagerQList` containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        Args:
            key: `function (T) -> SupportsLessThan`. Defaults to `None`
            reverse: if set to `True` sorts values in descending order. Defaults to `False`

        Returns: `EagerQList[T]`
        """
        return EagerQList(sorted(self, key=key, reverse=reverse))

    def flatten(self) -> "EagerQList[T]":
        """
        If self is a `EagerQList` of `Iterable[T]` flatten concatenates all iterables into a
        single list and returns a new `EagerQList[T]`.

        Returns:
            `EagerQList[T]`

        Raises:
            TypeError when elements of Lazy are not iterables.
        """
        def inner():
            for elem in self:
                if not isinstance(elem, Iterable):
                    type_name = type(elem).__name__
                    raise TypeError(f'could not flatten {self.__class__.__name__}[{type_name}] because {type_name} is not iterable.')
                yield from elem
        return EagerQList(inner())

    def enumerate(self, start: int = 0) -> "EagerQList[tuple[int, T]]":
        """
        Returns a `Lazy` object with index-value pairs as its elements. Index starts at
        the given position `start` (defaults to 0).

        Returns: Lazy[tuple[int, T]]

        Examples:
            >>> EagerQList(['a', 'b', 'c']).enumerate()
            [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        def inner():
            for i, elem in enumerate(self, start=start):
                yield i, elem
        return EagerQList(inner())

    def batch(self, size: int) -> "EagerQList[EagerQList[T]]":
        """
        Groups elements into batches of given `size`. The last batch may have fewer elements.

        Args:
            size: int - size of one batch

        Returns: EagerQList[EagerQList[T]]

        Examples:
            >>> EagerQList(range(5)).batch(2)
            [[0, 1], [2, 3], [4]]
        """
        assert size > 0, f'batch size must be greater then 0 but got {size}'

        def inner():
            for i in range(0, self.len(), size):
                yield EagerQList(self[i:i + size])

        return EagerQList(inner())

    def chain(self, other: Iterable[T]) -> "EagerQList[T]":
        """
        Chains `self` with `other`, returning a new EagerQList with all elements from both iterables.

        Args:
            other: Iterable[T] - an iterable of elements to be "attached" after self is exhausted.

        Returns: `EagerQList[T]`

        Examples:
            >>> EagerQList(range(0, 3)).chain(range(3, 6))
            [0, 1, 2, 3, 4, 5]
        """
        def inner():
            yield from self
            yield from other
        return EagerQList(inner())


    def merge(self, other: Iterable[T], merger: Callable[[T, T], bool]) -> "EagerQList[T]":
        """
        Merges `self` with `other`, maintaining the order of elements based on the merger function. It starts by
         taking the first elements from `self` and `other`, calling the merger function with these elements as arguments.
         If the output is True, the first element is yielded; otherwise, the second element is yielded. If `self` is
         empty, the remaining elements from `other` are yielded, and vice versa.

        Args:
            other: Iterable[T] - an iterable to be merged with `self`.
            merger: function (T, T) -> bool - a function that takes two arguments (left and right). If the output is True,
        the left argument is yielded; otherwise, the right argument is yielded.

        Returns: `EagerQList[T]` - EagerQList containing the merged elements.

        Examples:
            >>> EagerQList([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right)
            [1, 2, 3, 4, 5, 6]
        """
        it1 = iter(self)
        it2 = iter(other)

        try:
            elem1 = next(it1)
        except StopIteration:
            return EagerQList(it2)
        try:
            elem2 = next(it2)
        except StopIteration:
            return EagerQList([elem1]).chain(it1)

        def inner():
            left = elem1
            right = elem2
            while True:
                if merger(left, right):
                    yield left
                    try:
                        left = next(it1)
                    except StopIteration:
                        yield right
                        yield from it2
                        return
                else:
                    yield right
                    try:
                        right = next(it2)
                    except StopIteration:
                        yield left
                        yield from it1
                        return
        return EagerQList(inner())

    def all(self, mapper: Optional[Callable[[T], Booly]] = None) -> bool:
        """
        Goes through the entire list and checks if all elements are `Truthy`.
        `Booly` is a type that evaluates to something that is either `True` (`Truthy`) or `False` (`Falsy`).
        For example in Python an empty list evaluates to `False` (empty list is `Falsy`).

        Args:
            mapper (Optional[Callable[[T], Booly]]): function that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if all elements of the `Lazy` are `Truthy`. `False` otherwise.
        """
        def identity(x):
            return x
        mapper = identity if mapper is None else mapper
        for elem in self:
            if not mapper(elem):
                return False
        return True

    def any(self, mapper: Optional[Callable[[T], Booly]] = None) -> bool:
        """
        Goes through the entire list and checks if any element is `Truthy`.
        `Booly` is a type that evaluates to something that is either `True` (`Truthy`) or `False` (`Falsy`).
        For example in Python an empty list evaluates to `False` (empty list is `Falsy`).

        Args:
            mapper (Optional[Callable[[T], Booly]]): function that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if there is at least one element in the `Lazy` that is `Truthy`. `False` otherwise.
        """
        def identity(x):
            return x

        mapper = identity if mapper is None else mapper
        for elem in self:
            if mapper(elem):
                return True
        return False

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> "EagerQList[T]":
        """
        When self is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: Lazy[T | Iterable[T | Iterable[T | ...]]].


        Args:
            break_str (bool, optional): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type], optional): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns:
            `EagerQList[T]` with all nested iterables flattened to a single iterable.

        Examples:
            >>> EagerQList(['abc', ['def', 'ghi']]).full_flatten()
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

            >>> EagerQList(['abc', ['def', 'ghi']]).full_flatten(break_str=False)
            ['abc', 'def', 'ghi']

            >>> EagerQList(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list)
            ['a', 'b', 'c', ['def', 'ghi']]
        """

        def inner():
            for elem in self:
                if preserve_type is not None and isinstance(elem, preserve_type):
                    yield elem
                elif isinstance(elem, str):
                    if break_str:
                        if len(elem) == 1:
                            yield elem
                        else:
                            yield from EagerQList(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                    else:
                        yield elem
                elif isinstance(elem, Iterable):
                    yield from EagerQList(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                else:
                    yield elem
        return EagerQList(inner())

    def take_while(self, pred: Callable[[T], bool]) -> "Lazy[T]":
        """
        Creates a new EagerQList that contains elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of the iterator, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function (T) -> bool`

        Returns:
            `EagerQList[T]`
        """
        def inner():
            for elem in self:
                if not pred(elem):
                    return
                yield elem
        return EagerQList(inner())

if __name__ == '__main__':
    EagerQList([[1, 2], 3]).flatten().foreach(print)