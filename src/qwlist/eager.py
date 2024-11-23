from collections import deque
from typing import TypeVar, Iterable, Callable, overload, Iterator, Optional, Type, Tuple, List
from .qwlist import QList

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")
SupportsAdd = TypeVar("SupportsAdd")
SupportsEq = TypeVar("SupportsEq")
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

    def get(self, index: int, default: Optional[T] = None) -> Optional[T]:
        """
        Safely gets the element on the specified index. If the index is out of bounds `default` is returned.

        Args:
            index (int): index of the element to take
            default (Optional[T]): value to return if the index is out of bounds. Defaults to `None`

        Returns:
            Element at the specified index or `default` if index is out of bounds.

        """
        if index < 0 or index >= self.len():
            return default
        return self[index]

    def iter(self) -> Iterator[T]:
        """
        Changes `self` into `Iterator[T]` by calling the `iter()` function.

        Returns:
            iterator over the elements of `self`.
        """
        return iter(self)

    def list(self) -> List[T]:
        """
        Changes `EagerQList` into standard Python `list`.

        Returns:
            Standard Python `list`.
        """
        return list(self)

    def qlist(self) -> "QList[T]":
        """
        Changes `EagerQList` into `Qlist`.

        Returns:
            `QList` of all elements from `self`.
        """
        return QList(self)

    def filter(self, pred: Callable[[T], bool]) -> "EagerQList[T]":
        """
        Returns a new `EagerQList` containing all values from `self` for which
        the predicate holds true.

        Args:
            pred: `function: (T) -> bool`

        Returns:
            New `EagerQList[T]` with elements for which the predicate holds true.

        Examples:
            >>> EagerQList([0, 1, 2, 3]).filter(lambda x: x < 2)
            [0, 1]
        """
        return EagerQList(elem for elem in self if pred(elem))

    def map(self, mapper: Callable[[T], K]) -> "EagerQList[K]":
        """
        Returns an `EagerQList` containing all values from `self` with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns:
            New `EagerQList[K]` with mapped elements from `self`.
        """
        return EagerQList(mapper(elem) for elem in self)

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the `EagerQList` elements.

        Args:
            action: `function: (T) -> None`

        Returns:
            `None`
        """
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces `self` by processing
        its constituent parts, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: `function: (K, T) -> K`. Given the initial value `init` applies the
                given combination operator on each element yielded by `self`,
                treating the result as the first argument in the next step.
            init (K): initial value for the combination operator.

        Returns:
            The final value created from calling the `operation` on consecutive elements of `self`.

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
        Given the combination operator reduces `self` by processing
        its constituent parts, building up the final value.

        Args:
            operation: `function: (K, T) -> K`
                Given the initial value `init` applies the
                given combination operator on each element of `self`, starting from the
                last element, treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns:
            The final value created from calling the `operation` on consecutive elements of `self`
             starting from the last element.

        Examples:
            >>> s = EagerQList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def scan(self, operation: Callable[[K, T], K], state: K) -> "EagerQList[K]":
        """
        Given the combination operator creates a new `EagerQList[K]` by processing
        constituent parts of `self`, yielding intermediate steps and building up the final value.
        Scan is similar to fold but returns all intermediate states instead of just the final result.

        Args:
            operation: `function: (K, T) -> K`. Given the initial `state` applies the given
             combination operator on each element yielded by the `Lazy` object, yielding the result and
             then treating it as the first argument in the next step.
            state (K): initial value for the state.

        Returns:
            New `EagerQList[K]` with all intermediate steps of the `operation`.

        Examples:
            >>> EagerQList([1, 2, 3]).scan(lambda acc, x: acc + x, 0)
            [1, 3, 6]
        """
        def inner(s):
            for elem in self:
                s = operation(s, elem)
                yield s
        return EagerQList(inner(state))

    def len(self) -> int:
        """
        Returns the length of `self`.

        (time complexity: `O(1)`)

        Returns:
            Length of the `EagerQList`
        """
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> "EagerQList[K]":
        """
        Applies the mapper function to each of the yielded elements and flattens the results.

        Args:
            mapper: `function: (T) -> Iterable[K]`.

        Returns:
            New `EagerQList` with elements from `self` mapped to an iterable and then flattened.

        Examples:
            >>> EagerQList([1, 2]).flatmap(lambda x: [x, x]).qlist()
            [1, 1, 2, 2]
        """
        return EagerQList(x for elem in self for x in mapper(elem))

    def zip(self, other: Iterable[K]) -> "EagerQList[Tuple[T, K]]":
        """
        Combines `self` with the given `Iterable` elementwise as tuples.
         The returned `EagerQList` contains at most the number of elements of
         the shorter sequence (`self` or `other`).

        Args:
            other (Iterable[K]): iterable to zip with `self`.

        Returns:
            New `EagerQList` with pairs of elements from `self` and `other`.

        Examples:
            >>> EagerQList([1, 2, 3]).zip(['a', 'b', 'c'])
            [(1, 'a'), (2, 'b'), (3, 'c')]
        """
        return EagerQList(zip(self, other))

    def sorted(self, key: Callable[[T], SupportsLessThan] = None, reverse: bool = False) -> "EagerQList[T]":
        """
        Returns a new `EagerQList` containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        Args:
            key (Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan`. Defaults to `None`.
            reverse: if set to `True` sorts values in descending order. Defaults to `False`.

        Returns:
            Sorted `EagerQList`.
        """
        return EagerQList(sorted(self, key=key, reverse=reverse))

    def flatten(self) -> "EagerQList[T]":
        """
        If self is a `EagerQList` of `Iterable[T]` flatten concatenates all iterables into a
        single list and returns a new `EagerQList[T]`.

        Returns:
            `EagerQList[T]`

        Raises:
            TypeError: when elements of Lazy are not iterables.
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
        Returns a new `EagerQList` with index-value pairs as its elements. Index starts at
        the given position `start` (defaults to 0).

        Args:
            start (int): starting index. Defaults to 0.

        Returns:
            New `EagerQList` with pairs of index and value.

        Examples:
            >>> QList(['a', 'b', 'c']).enumerate().collect()
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
            size (int): size of one batch

        Returns:
            New `EagerQList` of batches (`EagerQList`) of given `size`.
             Last batch may have fewer elements.

        Examples:
            >>> EagerQList(range(5)).batch(2)
            [[0, 1], [2, 3], [4]]
        """
        assert size > 0, f'batch size must be greater then 0 but got {size}'

        def inner():
            for i in range(0, self.len(), size):
                yield EagerQList(self[i:i + size])

        return EagerQList(inner())

    def batch_by(self, grouper: Callable[[T], SupportsEq]) -> "EagerQList[EagerQList[T]]":
        """
        Batches elements of `self` based on the output of the grouper function. Elements are thrown
        to the same group as long as the grouper function returns the same key (keys must support equality checks).
        When a new key is returned a new batch (group) is created.

        Args:
            grouper (Callable[[T], SupportsEq]): `function: (T) -> SupportsEq` that provides the keys
             used to group elements, where the key type must support equality comparisons.

        Returns:
            New `EagerQList[EagerQList[T]]` with elements batched based on the `grouper` key.

        Examples:
            >>> EagerQList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0])
            [['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']]
            >>> EagerQList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1])
            [['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']]
        """
        def inner():
            if self.len() == 0:
                return
            batch = EagerQList([self[0]])
            key = grouper(self[0])
            for elem in self[1:]:
                new_key = grouper(elem)
                if new_key == key:
                    batch.append(elem)
                else:
                    yield batch
                    batch = EagerQList([elem])
                    key = new_key
            if batch:
                yield batch
        return EagerQList(inner())

    def chain(self, other: Iterable[T]) -> "EagerQList[T]":
        """
        Chains `self` with `other`, returning a new `EagerQList[T]` with all elements from both iterables.

        Args:
            other (Iterable[T]):  an iterable of elements to be "attached" after `self` is exhausted.

        Returns:
            New `EagerQList` with elements from `self` and `other`.

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

        Returns:
            New `EagerQList` containing the merged elements.

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

    def min(self, key: Optional[Callable[[T], SupportsLessThan]] = None) -> Optional[T]:
        """
        Returns the smallest element from `self`. If the key function is not passed, identity
        function is used in which case `T` must support `LessThan` operator.

        Args:
            key (Optional[Callable[[T], SupportsLessThan]): function `(T) -> SupportsLessThan` that represents
             the relation of partial order between elements.

        Returns:
            The smallest element from `self` or `None` if `self` is empty.
        """

        def identity(x):
            return x

        key = identity if key is None else key

        if self.len() == 0:
            return None
        best = self[0]
        for elem in self[1:]:
            if key(elem) < key(best):
                best = elem
        return best

    def max(self, key: Optional[Callable[[T], SupportsLessThan]] = None) -> Optional[T]:
        """
        Returns the biggest element from the iterable. If the key function is not passed, identity
        function is used in which case `T` must support `LessThan` operator.

        Args:
            key (Optional[Callable[[T], SupportsLessThan]): function `(T) -> SupportsLessThan` that represents
             the relation of partial order between elements.

        Returns:
            the biggest element from `self` or `None` if `self` is empty.
        """

        def identity(x):
            return x

        key = identity if key is None else key

        if self.len() == 0:
            return None
        best = self[0]
        for elem in self[1:]:
            if key(best) < key(elem):
                best = elem
        return best

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> "EagerQList[T]":
        """
        When `self` is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: `EagerQList[T | Iterable[T | Iterable[T | ...]]]`.


        Args:
            break_str (bool): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type]): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns:
            New `EagerQList` with all nested iterables flattened to a single iterable.

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

    def take_while(self, pred: Callable[[T], bool]) -> "EagerQList[T]":
        """
        Creates a new `EagerQList` that contains elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of the iterator, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function: (T) -> bool`

        Returns:
            New `EagerQList` containing elements from the original sequence, stopping at the first element for which the
             predicate returns `False`.
        """
        def inner():
            for elem in self:
                if not pred(elem):
                    return
                yield elem
        return EagerQList(inner())

    def sum(self) -> Optional[SupportsAdd]:
        """
        Sums all the elements and returns the sum. Returns `None` if `self` is empty.
        Elements of `self` must support addition.

        Returns:
            The sum of all elements of `self`.
        """
        it = self.iter()
        acc = None
        try:
            acc = next(it)
        except StopIteration:
            return acc
        for elem in it:
            acc = acc + elem
        return acc

    def window(self, window_size: int) -> "EagerQList[EagerQList[T]]":
        """
        Creates a new `EagerQList` of sliding windows of size `window_size`. If `window_size`
        is greater than the total length of `self` an empty iterator is returned.

        Args:
            window_size (int): the size of the sliding window. Must be greater than 0.

        Returns:
            New `EagerQList` of all sliding windows.
        """
        assert window_size > 0, f'window size must be greater than 0 but got {window_size}.'
        def inner(n: int):
            if self.len() < n:
                return
            if self.len() == n:
                yield self
                return
            window = deque(maxlen=n)
            for elem in self[:n]:
                window.append(elem)
            yield EagerQList(window)
            for elem in self[n:]:
                window.append(elem)
                yield EagerQList(window)
        return EagerQList(inner(n=window_size))

if __name__ == '__main__':
    print(EagerQList([1, 2, 3]).window(2))