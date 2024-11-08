from typing import TypeVar, Generic, Iterable, Callable, overload, Optional, Iterator, Type

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")
SupportsAdd = TypeVar("SupportsAdd")
Booly = TypeVar('Booly')


class Lazy(Generic[T]):
    """
    Object representing lazy evaluation of called methods.

    Calling any method **consumes** the current `Lazy` object. **Using the same object
    again may cause errors** due to the draining of the generator.

    Found in `qwlist.Lazy`

    Examples:
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
        return f'Lazy({repr(self.gen)})'

    def iter(self) -> Iterator[T]:
        """
        Changes Lazy[T] into Iterator[T].

        Returns: `Iterator[T]`
        """
        return iter(self.gen)

    def list(self) -> list[T]:
        """
        Evaluates the `Lazy` object into `list`.

        Returns: `list[T]`
        """
        return [elem for elem in self.gen]

    def qlist(self):
        """
        Evaluates the `Lazy` object into `QList`.
        Same as calling `collect()`

        Returns: `QList[T]`
        """
        return QList(elem for elem in self.gen)

    def filter(self, pred: Callable[[T], bool]):
        """
        Returns a `Lazy` object containing all values from this `Lazy` object for which
        the predicate holds true.

        Args:
            pred: `function (T) -> bool`

        Returns: `Lazy[T]`

        Examples:
            >>> Lazy([0, 1, 2, 3]).filter(lambda x: x < 2).collect()
            [0, 1]
        """
        def inner():
            for elem in self.gen:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]):
        """
        Returns a `Lazy` object containing all values from this `Lazy` object with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns: `Lazy[K]`
        """
        def inner():
            for elem in self.gen:
                yield mapper(elem)
        return Lazy(inner())

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the `Lazy` object by processing
        its constituent parts, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: `function: (K, T) -> K`. Given the initial value `init` applies the
                given combination operator on each element yielded by the Lazy object,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: `K`

        Examples:
            >>> Lazy([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self.gen:
            acc = operation(acc, elem)
        return acc

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of yielded elements.

        Args:
            action: `function (T) -> None`

        Returns: `None`
        """
        for elem in self.gen:
            action(elem)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]):
        """
        Applies the mapper function to each of the yielded elements and flattens the results.

        Args:
            mapper: `function (T) -> Iterable[K]`

        Returns: `Lazy[K]`

        Examples:
            >>> Lazy([1, 2]).flatmap(lambda x: [x, x]).qlist()
            [1, 1, 2, 2]
        """
        def inner():
            for elem in self.gen:
                yield from mapper(elem)
        return Lazy(inner())

    def zip(self, other: Iterable[K]) -> "Lazy[tuple[T, K]]":
        """
        Combines this `Lazy` object with the given `Iterable` elementwise as tuples.
         The returned `Lazy` objects yields at most the number of elements of
         the shorter sequence (`Lazy` or `Iterable`).

        Args:
            other: iterable to zip with this `Lazy` object.

        Returns:
            `Lazy[tuple[T, K]]`

        Examples:
            >>> Lazy([1, 2, 3]).zip(['a', 'b', 'c']).collect()
            [(1, 'a'), (2, 'b'), (3, 'c')]
        """
        return Lazy(zip(self.gen, other))

    def collect(self) -> "QList[T]":
        """
        Evaluates the `Lazy` object into `QList`.
        Same as calling `qlist()`

        Returns:
            `QList[T]`

        """
        return QList(x for x in self.gen)

    def __iter__(self):
        return iter(self.gen)

    def skip(self, n: int) -> "Lazy[T]":
        """
        Skips n first elements of the `Lazy` object.

        Args:
            n: numbers of elements to skip. Should be non-negative

        Returns:
            `Lazy[T]`

        Examples:
            >>> Lazy(range(10)).skip(2).collect()
            [2, 3, 4, 5, 6, 7, 8, 9]
        """
        def inner():
            for i, elem in enumerate(self.gen):
                if i >= n:
                    yield elem
        return Lazy(inner())

    def take(self, n: int) -> "Lazy[T]":
        """
        Takes n first elements of the `Lazy` object.
        Args:
            n: numbers of elements to skip. Should be non-negative

        Returns:
            `Lazy[T]`

        Examples:
            >>> Lazy(range(10)).take(2).collect()
            [0, 1]
        """
        def inner():
            for i, elem in enumerate(self.gen):
                if i >= n:
                    return None
                yield elem
        return Lazy(inner())

    def flatten(self) -> "Lazy[T]":
        """
        If `self` is a `Lazy` object of `Iterable[T]`, flatten concatenates all iterables into a
        single list and returns a `Lazy[T]` object.

        Returns:
            `Lazy[T]`

        Raises:
            TypeError when elements of Lazy are not iterables.

        Examples:
            >>> Lazy([[1, 2], [3, 4]]).flatten().collect()
            [1, 2, 3, 4]
        """

        def inner():
            for elem in self.gen:
                if not isinstance(elem, Iterable):
                    type_name = type(elem).__name__
                    raise TypeError(
                        f'could not flatten {self.__class__.__name__}[{type_name}] because {type_name} is not iterable.')
                yield from elem
        return Lazy(inner())

    def cycle(self) -> "Lazy[T]":
        """
        Returns a `Lazy[T]` that cycles through the elements of the `Lazy` object, that means
        on achieving the last element the iteration starts from the beginning. The
        returned `Lazy` object has no end (infinite iterator) unless the `Lazy` object is empty
        in which case cycle returns an empty `Lazy` object (empty iterator).

        Returns: `Lazy[T]`

        Examples:
            >>> Lazy([1, 2, 3]).cycle().take(7).collect()
            [1, 2, 3, 1, 2, 3, 1]
        """
        def inner():
            saved = []
            for elem in self.gen:
                saved.append(elem)
                yield elem
            while saved:
                for elem in saved:
                    yield elem
        return Lazy(inner())

    def enumerate(self, start: int = 0) -> "Lazy[tuple[int, T]]":
        """
        Returns a `Lazy` object with index-value pairs as its elements. Index starts at
        the given position `start` (defaults to 0).

        Returns: Lazy[tuple[int, T]]

        Examples:
            >>> Lazy(['a', 'b', 'c']).enumerate().collect()
            [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        def inner():
            for i, elem in enumerate(self, start=start):
                yield i, elem
        return Lazy(inner())

    def batch(self, size: int) -> "Lazy[QList[T]]":
        """
        Groups elements into batches of given `size`. The last batch may have fewer elements.

        Args:
            size: int - size of one batch

        Returns: Lazy[QList[T]]

        Examples:
            >>> Lazy(range(5)).batch(2).collect()
            [[0, 1], [2, 3], [4]]
        """
        assert size > 0, f'batch size must be greater then 0 but got {size}'
        def inner():
            group = QList()
            for i, elem in enumerate(self.gen, start=1):
                group.append(elem)
                if i % size == 0:
                    yield group
                    group = QList()
            if group:
                yield group
        return Lazy(inner())

    def chain(self, other: Iterable[T]) -> "Lazy[T]":
        """
        Chains `self` with `other`, returning a new Lazy[T] with all elements from both iterables.

        Args:
            other: Iterable[T] - an iterable of elements to be "attached" after self is exhausted.

        Returns: `Lazy[T]`

        Examples:
            >>> Lazy(range(0, 3)).chain(range(3, 6)).collect()
            [0, 1, 2, 3, 4, 5]
        """
        def inner():
            yield from self.gen
            yield from other
        return Lazy(inner())

    def merge(self, other: Iterable[T], merger: Callable[[T, T], bool]) -> "Lazy[T]":
        """
        Merges `self` with `other`, maintaining the order of elements based on the merger function. It starts by
         taking the first elements from `self` and `other`, calling the merger function with these elements as arguments.
         If the output is True, the first element is yielded; otherwise, the second element is yielded. If `self` is
         empty, the remaining elements from `other` are yielded, and vice versa.

        Args:
            other: Iterable[T] - an iterable to be merged with `self`.
            merger: function (T, T) -> bool - a function that takes two arguments (left and right). If the output is True,
             the left argument is yielded; otherwise, the right argument is yielded.

        Returns: `Lazy[T]` - a lazy iterable containing the merged elements.

        Examples:
            >>> QList([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right).collect()
            [1, 2, 3, 4, 5, 6]
        """
        it1 = iter(self)
        it2 = iter(other)

        try:
            elem1 = next(it1)
        except StopIteration:
            return Lazy(it2)
        try:
            elem2 = next(it2)
        except StopIteration:
            return Lazy([elem1]).chain(it1)

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
        return Lazy(inner())

    def all(self, mapper: Optional[Callable[[T], Booly]] = None) -> bool:
        """
        Goes through the entire generator and checks if all elements are `Truthy`.
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
        for elem in self.gen:
            if not mapper(elem):
                return False
        return True

    def any(self, mapper: Optional[Callable[[T], Booly]] = None) -> bool:
        """
        Goes through the entire generator and checks if any element is `Truthy`.
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
        for elem in self.gen:
            if mapper(elem):
                return True
        return False

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> "Lazy[T]":
        """
        When self is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: Lazy[T | Iterable[T | Iterable[T | ...]]].


        Args:
            break_str (bool, optional): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type], optional): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns: `Lazy[T]` with all nested iterables flattened to a single iterable.

        Examples:
            >>> Lazy(['abc', ['def', 'ghi']]).full_flatten().collect()
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

            >>> Lazy(['abc', ['def', 'ghi']]).full_flatten(break_str=False).collect()
            ['abc', 'def', 'ghi']

            >>> Lazy(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list).collect()
            ['a', 'b', 'c', ['def', 'ghi']]
        """
        def inner():
            for elem in self.gen:
                if preserve_type is not None and isinstance(elem, preserve_type):
                    yield elem
                elif isinstance(elem, str):
                    if break_str:
                        if len(elem) == 1:
                            yield elem
                        else:
                            yield from Lazy(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                    else:
                        yield elem
                elif isinstance(elem, Iterable):
                    yield from Lazy(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                else:
                    yield elem
        return Lazy(inner())

    def sum(self, init: Optional[T] = None) -> T:
        """

        Args:
            init (Optional[T]): - if set to None the first element of the iterable is the first component of the addition.
             If set to anything other than None `init` is treated as the first component of the addition. Defaults to None.

        Raises:
            Exception when called on an empty Lazy without specifying the `init` argument

        Returns: sum off all the elements starting with the init
        """
        if init is not None:
            ret = init
            for elem in self.gen:
                ret = ret + elem
            return ret
        it = iter(self.gen)
        try:
            ret = next(it)
        except StopIteration:
            raise Exception("calling sum on an empty Lazy without specifying the initial element. Either pass the init argument or call sum on nonempty Lazy")
        for elem in it:
            ret = ret + elem
        return ret

    def take_while(self, pred: Callable[[T], bool]) -> "Lazy[T]":
        """
        Creates a new Lazy that yields elements based on a predicate. Takes a function as an argument.
        Creates a new Lazy that yields elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of the iterator, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function (T) -> bool`

        Returns:
            `Lazy[T]`
        """
        def inner():
            for elem in self.gen:
                if not pred(elem):
                    return
                yield elem
        return Lazy(inner())


# ----------------- QList ----------------------------------------------


class QList(list):
    """
    `QList` is a python list extension that adds several chainable, lazy
    evaluated methods to the standard `list`.

    Found in `qwlist.QList`
    """

    @overload
    def __getitem__(self, item: slice) -> "QList[T]":
        ...

    @overload
    def __getitem__(self, item: int) -> T:
        ...

    def __getitem__(self, item):
        if isinstance(item, slice):
            return QList(super().__getitem__(item))
        return super().__getitem__(item)

    def iter(self) -> Iterator[T]:
        """
        Changes QList[T] into Iterator[T].

        Returns: `Iterator[T]`
        """
        return iter(self)

    def slice(self, s: slice) -> Lazy[T]:
        """
        Calling this method with `s` equal to `slice(3)` works similarly to
        `list[:3]` but is lazy evaluated.

        Args:
            s: slice object

        Returns: `Lazy[T]`
        """
        assert isinstance(s, slice), f"slice method argument must be a slice object. Got {type(s)}."

        def inner():
            for elem in self[s]:
                yield elem
        return Lazy(inner())

    def list(self) -> list[T]:
        """
        Changes `QList` into `list`.

        Returns: `list[T]`
        """
        return list(self)

    def eager(self) -> "EagerQList[T]":
        """
        Changes `QList` into `EagerQList`.

        Returns: `EagerQList[T]`
        """
        from .eager import EagerQList
        return EagerQList(self)

    def filter(self, pred: Callable[[T], bool]) -> Lazy[T]:
        """
        Returns a `Lazy` object containing all values from the `QList` for which
        the predicate holds true.

        Args:
             pred: `function (T) -> bool`

        Returns: `Lazy[T]`

        Examples:
            >>> QList([1, 2, 3, 4]).filter(lambda x: x < 3).collect()
            [1, 2]
        """
        def inner():
            for elem in self:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]) -> Lazy[K]:
        """
        Returns a `Lazy` object containing all values from `QList` with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns: `Lazy[K]`
        """
        def inner():
            for elem in self:
                yield mapper(elem)
        return Lazy(inner())

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the `QList` elements.

        Args:
            action: `function (T) -> None`

        Returns: `None`
        """
        for elem in self:
            action(elem)

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the `QList` by processing
        its values, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate

        Args:
            operation: `function: (K, T) -> K`
                Given the initial value `init` applies the
                given combination operator on each element of the `QList`,
                treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: `K`

        Examples:
            >>> QList([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces the `QList` by processing
        its values, building up the final value.

        Args:
            operation: `function: (K, T) -> K`
                Given the initial value `init` applies the
                given combination operator on each element of the `QList`, starting from the
                last element, treating the result as a first argument in the next step.
            init: initial value for the combination operator.

        Returns: `K`

        Examples:
            >>> QList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def len(self) -> int:
        """
        Returns the len of the `QList`

        (time complexity: `O(1)`)

        Returns: int
        """
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> Lazy[K]:
        """
        Applies the mapper function to each element of the `QList` and flattens the results.

        Args:
            mapper: `function (T) -> Iterable[K]`

        Returns: `Lazy[K]`

        Examples:
            >>> QList([1, 2]).flatmap(lambda x: [x, x]).qlist()
            [1, 1, 2, 2]
        """
        def inner():
            for elem in self:
                yield from mapper(elem)
        return Lazy(inner())

    def zip(self, other: Iterable[K]) -> Lazy[tuple[T, K]]:
        """
        Combines this `QList` with the given `Iterable` elementwise as tuples.
         The returned `Lazy` objects yields at most the number of elements of
         the shorter sequence (`self` or `Iterable`).

        Args:
            other: iterable to zip with this `QList`.

        Returns: `Lazy[tuple[T, K]]`

        Examples:
            >>> Lazy([1, 2, 3]).zip(['a', 'b', 'c']).collect()
            [(1, 'a'), (2, 'b'), (3, 'c')]
        """
        return Lazy(zip(self, other))

    def sorted(self, key: Callable[[T], SupportsLessThan] = None, reverse: bool = False) -> "QList[T]":
        """
        Returns a new `QList` containing all items from the original list in ascending order.

        A custom key function can be supplied to customize the sort order, and the reverse
        flag can be set to request the result in descending order.

        Args:
            key: `function (T) -> SupportsLessThan`. Defaults to `None`
            reverse: if set to `True` sorts values in descending order. Defaults to `False`

        Returns: `QList[T]`
        """
        return QList(sorted(self, key=key, reverse=reverse))

    def skip(self, n: int) -> Lazy[T]:
        """
        Skips n first elements of the QList.

        Args:
            n: numbers of elements to skip. Should be non-negative

        Returns: Lazy[T]

        Examples:
            >>> QList(range(10)).skip(2).collect()
            [2, 3, 4, 5, 6, 7, 8, 9]
        """
        def inner():
            for i, elem in enumerate(self):
                if i >= n:
                    yield elem
        return Lazy(inner())

    def take(self, n: int) -> Lazy[T]:
        """
        Takes n first elements of the QList.

        Args:
            n: int - numbers of elements to take. Should be non-negative

        Returns: Lazy[T]

        Examples:
            >>> QList(range(10)).take(2).collect()
            [0, 1]
        """
        def inner():
            for i, elem in enumerate(self):
                if i >= n:
                    return None
                yield elem
        return Lazy(inner())

    def flatten(self) -> Lazy[T]:
        """
        If self is a QList of Iterable[T] flatten concatenates all iterables into a
        single list and returns a Lazy[T] object

        Returns:
            `Lazy[T]`

        Raises:
            TypeError when elements of QList are not iterables.
        """
        def inner():
            for elem in self:
                if not isinstance(elem, Iterable):
                    type_name = type(elem).__name__
                    raise TypeError(f'could not flatten {self.__class__.__name__}[{type_name}] because {type_name} is not iterable.')
                yield from elem
        return Lazy(inner())

    def cycle(self) -> Lazy[T]:
        """
        Returns a `Lazy[T]` that cycles through the elements of the `QList` that means
        on achieving the last element the iteration starts from the beginning. The
        returned `Lazy` object has no end (infinite iterator) unless the `QList` is empty
        in which case cycle returns an empty `Lazy` object (empty iterator).

        Returns:
            `Lazy[T]`

        Examples:
            >>> QList([1, 2, 3]).cycle().take(7).collect()
            [1, 2, 3, 1, 2, 3, 1]
        """
        def inner():
            saved = []
            for elem in self:
                saved.append(elem)
                yield elem
            while saved:
                for elem in saved:
                    yield elem
        return Lazy(inner())

    def enumerate(self, start: int = 0) -> Lazy[tuple[int, T]]:
        """
        Returns a `Lazy` object with index-value pairs as its elements. Index starts at
        the given position `start` (defaults to 0).

        Returns: Lazy[tuple[int, T]]

        Examples:
            >>> QList(['a', 'b', 'c']).enumerate().collect()
            [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        def inner():
            for i, elem in enumerate(self, start=start):
                yield i, elem
        return Lazy(inner())

    def batch(self, size: int) -> Lazy["QList[T]"]:
        """
        Groups elements into batches of given `size`. The last batch may have fewer elements.

        Args:
            size: int - size of one batch

        Returns:
            `Lazy[QList[T]]`

        Examples:
            >>> QList(range(5)).batch(2).collect()
            [[0, 1], [2, 3], [4]]
        """
        assert size > 0, f'batch size must be greater then 0 but got {size}'
        def inner():
            for i in range(0, self.len(), size):
                yield QList(self[i:i+size])
        return Lazy(inner())

    def chain(self, other: Iterable[T]) -> Lazy[T]:
        """
        Chains `self` with `other`, returning a Lazy[T] with all elements from both iterables.

        Args:
            other: Iterable[T] - an iterable of elements to be "attached" after self is exhausted.

        Returns:
            `Lazy[T]`

        Examples:
            >>> QList(range(0, 3)).chain(range(3, 6)).collect()
            [0, 1, 2, 3, 4, 5]
        """
        def inner():
            yield from self
            yield from other
        return Lazy(inner())

    def merge(self, other: Iterable[T], merger: Callable[[T, T], bool]) -> Lazy[T]:
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
            `Lazy[T]` - a lazy iterable containing the merged elements.

        Examples:
            >>> QList([1, 3, 5]).merge([2, 4, 6], lambda left, right: left < right).collect()
            [1, 2, 3, 4, 5, 6]
        """
        it1 = iter(self)
        it2 = iter(other)

        try:
            elem1 = next(it1)
        except StopIteration:
            return Lazy(it2)
        try:
            elem2 = next(it2)
        except StopIteration:
            return Lazy([elem1]).chain(it1)

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
        return Lazy(inner())

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

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> Lazy[T]:
        """
        When self is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: Lazy[T | Iterable[T | Iterable[T | ...]]].


        Args:
            break_str (bool, optional): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type], optional): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns:
            `Lazy[T]` with all nested iterables flattened to a single iterable.

        Examples:
            >>> QList(['abc', ['def', 'ghi']]).full_flatten().collect()
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

            >>> QList(['abc', ['def', 'ghi']]).full_flatten(break_str=False).collect()
            ['abc', 'def', 'ghi']

            >>> QList(['abc', ['def', 'ghi']]).full_flatten(preserve_type=list).collect()
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
                            yield from Lazy(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                    else:
                        yield elem
                elif isinstance(elem, Iterable):
                    yield from Lazy(elem).full_flatten(break_str=break_str, preserve_type=preserve_type)
                else:
                    yield elem
        return Lazy(inner())

    def take_while(self, pred: Callable[[T], bool]) -> "Lazy[T]":
        """
        Creates a Lazy that yields elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of the iterator, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function (T) -> bool`

        Returns:
            `Lazy[T]`
        """
        def inner():
            for elem in self:
                if not pred(elem):
                    return
                yield elem
        return Lazy(inner())


if __name__ == '__main__':
    def naturals(start):
        current = start
        while True:
            yield current
            current += 1

    primes = (
        Lazy(naturals(2))
        .filter(lambda n: (
            Lazy(naturals(2))
            .take_while(lambda p: p * p <= n)
            .all(lambda x: n % x != 0)
        ))
    )
    for p in primes.skip(1000).take(10):
        print(p)

