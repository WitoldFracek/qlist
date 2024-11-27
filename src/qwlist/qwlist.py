from typing import TypeVar, Generic, Iterable, Callable, overload, Optional, Iterator, Type, Tuple, List
from collections import deque

T = TypeVar('T')
K = TypeVar('K')
SupportsLessThan = TypeVar("SupportsLessThan")
SupportsAdd = TypeVar("SupportsAdd")
SupportsEq = TypeVar("SupportsEq")
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
        Changes `self` into `Iterator[T]` by calling the `iter()` function.

        Returns:
            iterator over the elements of `self`.
        """
        return iter(self.gen)

    def list(self) -> List[T]:
        """
        Goes through elements of `self` collecting values into standard Python `list`.

        Returns:
            Standard Python `list` of all elements from `self`.
        """
        return [elem for elem in self.gen]

    def qlist(self) -> "QList[T]":
        """
        Goes through elements of `self` collecting values into `QList`. Same as calling `collect()`.

        Returns:
            `QList` of all elements from `self`.
        """
        return QList(elem for elem in self.gen)

    def filter(self, pred: Callable[[T], bool]):
        """
        Returns a new `Lazy` object containing all values from `self` for which
        the predicate holds true.

        Args:
            pred: `function: (T) -> bool`

        Returns:
            New `Lazy[T]` with elements for which the predicate holds true.

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
        Returns a new `Lazy` object containing all values from `self` with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns:
            New `Lazy[K]` with mapped elements from `self`.
        """
        def inner():
            for elem in self.gen:
                yield mapper(elem)
        return Lazy(inner())

    def fold(self, operation: Callable[[K, T], K], init: K) -> K:
        """
        Given the combination operator reduces `self` by processing
        its constituent parts, building up the final value.

        **Other names:** fold_left, reduce, accumulate, aggregate.

        Args:
            operation: `function: (K, T) -> K`. Given the initial value `init` applies the
                given combination operator on each element yielded by `self`,
                treating the result as the first argument in the next step.
            init (K): initial value for the combination operator.

        Returns:
            The final value created from calling the `operation` on consecutive elements of `self`.

        Examples:
            >>> Lazy([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self.gen:
            acc = operation(acc, elem)
        return acc

    def scan(self, operation: Callable[[K, T], K], state: K) -> "Lazy[K]":
        """
        Given the combination operator creates a new `Lazy[K]` object by processing
        constituent parts of `self`, yielding intermediate steps and building up the final value.
        Scan is similar to fold but returns all intermediate states instead of just the final result.

        Args:
            operation: `function: (K, T) -> K`. Given the initial `state` applies the given
             combination operator on each element yielded by the `Lazy` object, yielding the result and
             then treating it as the first argument in the next step.
            state (K): initial value for the state.

        Returns:
            Lazy[K] with all intermediate steps of the `operation`.

        Examples:
            >>> Lazy([1, 2, 3]).scan(lambda acc, x: acc + x, 0).collect()
            [1, 3, 6]
        """
        def inner(s):
            for elem in self.gen:
                s = operation(s, elem)
                yield s
        return Lazy(inner(state))

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of yielded elements.

        Args:
            action: `function: (T) -> None`

        Returns:
            `None`
        """
        for elem in self.gen:
            action(elem)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> "Lazy[K]":
        """
        Applies the mapper function to each of the yielded elements and flattens the results.

        Args:
            mapper: `function: (T) -> Iterable[K]`.

        Returns:
            New `Lazy` with elements from `self` mapped to an iterable and then flattened.

        Examples:
            >>> Lazy([1, 2]).flatmap(lambda x: [x, x]).qlist()
            [1, 1, 2, 2]
        """
        def inner():
            for elem in self.gen:
                yield from mapper(elem)
        return Lazy(inner())

    def zip(self, other: Iterable[K]) -> "Lazy[Tuple[T, K]]":
        """
        Combines `self` with the given `Iterable` elementwise as tuples.
         The returned `Lazy` objects yields at most the number of elements of
         the shorter sequence (`self` or `other`).

        Args:
            other (Iterable[K]): iterable to zip with `self`.

        Returns:
            New Lazy with pairs of elements from `self` and `other`.

        Examples:
            >>> Lazy([1, 2, 3]).zip(['a', 'b', 'c']).collect()
            [(1, 'a'), (2, 'b'), (3, 'c')]
        """
        return Lazy(zip(self.gen, other))

    def collect(self) -> "QList[T]":
        """
        Goes through elements of `self` collecting values into `QList`.

        Returns:
            `QList` of all elements from `self`.
        """
        return QList(x for x in self.gen)

    def __iter__(self):
        return iter(self.gen)

    def skip(self, n: int) -> "Lazy[T]":
        """
        Skips `n` first elements of `self`.

        Args:
            n (int): numbers of elements to skip. Should be non-negative.

        Returns:
            New `Lazy` with `n` first elements of `self` skipped.

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
        Takes `n` first elements of `self`.

        Args:
            n (int): numbers of elements to take. Should be non-negative.

        Returns:
            New `Lazy` with only `n` first elements from `self`.

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
            Concatenation of all elements from `self`.

        Raises:
            TypeError: when elements of Lazy are not iterables.

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
        Returns a new `Lazy[T]` that cycles through the elements of `self`, which means
        on achieving the last element the iteration starts from the beginning. The
        returned `Lazy` object has no end (infinite iterator) unless `self` is empty
        in which case cycle returns an empty `Lazy` object (empty iterator).

        Returns:
            Infinite `Lazy` that loops through elements of `self`, or empty iterator if `self` is emtpy.

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

    def enumerate(self, start: int = 0) -> "Lazy[Tuple[int, T]]":
        """
        Returns a new `Lazy` object with index-value pairs as its elements. Index starts at
        the given position `start` (defaults to 0).

        Args:
            start (int): starting index. Defaults to 0.

        Returns:
            New `Lazy` with pairs of index and value.

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
            size (int): size of one batch.

        Returns:
            New `Lazy` of batches (`QList`) of given `size`. Last batch may have fewer elements.

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

    def batch_by(self, grouper: Callable[[T], SupportsEq]) -> "Lazy[QList[T]]":
        """
        Batches elements of `self` based on the output of the grouper function. Elements are thrown
        to the same group as long as the grouper function returns the same key (keys must support equality checks).
        When a new key is returned a new batch (group) is created.

        Args:
            grouper (Callable[[T], SupportsEq]): `function: (T) -> SupportsEq` that provides the keys
             used to group elements, where the key type must support equality comparisons.

        Returns:
            New `Lazy[QList[T]]` with elements batched based on the `grouper` key.

        Examples:
            >>> Lazy(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0]).collect()
            [['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']]
            >>> Lazy(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1]).collect()
            [['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']]
        """
        def inner():
            it = self.iter()
            try:
                first = next(it)
            except StopIteration:
                return
            batch = QList([first])
            key = grouper(first)
            for elem in it:
                new_key = grouper(elem)
                if new_key == key:
                    batch.append(elem)
                else:
                    yield batch
                    batch = QList([elem])
                    key = new_key
            yield batch
        return Lazy(inner())

    def chain(self, other: Iterable[T]) -> "Lazy[T]":
        """
        Chains `self` with `other`, returning a new Lazy[T] with all elements from both iterables.

        Args:
            other (Iterable[T]):  an iterable of elements to be "attached" after self is exhausted.

        Returns:
            New `Lazy` with elements from `self` and `other`.

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
            other (Iterable[T]): an iterable to be merged with `self`.
            merger (Callable[[T, T], bool]): `function: (T, T) -> bool` that takes two arguments (left and right).
             If the output is True, the left argument is yielded; otherwise, the right argument is yielded.

        Returns:
            New `Lazy` containing the merged elements.

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
            mapper (Optional[Callable[[T], Booly]]): `function: (T) -> Booly` that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if all elements of `self` are `Truthy`. `False` otherwise.
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
            mapper (Optional[Callable[[T], Booly]]): `function: (T) -> Booly` that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if there is at least one element in `self` that is `Truthy`. `False` otherwise.
        """
        def identity(x):
            return x

        mapper = identity if mapper is None else mapper
        for elem in self.gen:
            if mapper(elem):
                return True
        return False

    def min(self, key: Optional[Callable[[T], SupportsLessThan]] = None) -> Optional[T]:
        """
        Returns the smallest element from `self`. If the key function is not passed, identity
        function is used in which case `T` must support `LessThan` operator.

        Args:
            key (Optional[Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan` that represents
             the relation of partial order between elements.

        Returns:
            the smallest element of `self` or `None` if `self` is empty.
        """
        def identity(x):
            return x
        key = identity if key is None else key

        it = self.iter()
        try:
            best = next(it)
        except StopIteration:
            return None
        for elem in it:
            if key(elem) < key(best):
                best = elem
        return best

    def max(self, key: Optional[Callable[[T], SupportsLessThan]] = None) -> Optional[T]:
        """
        Returns the biggest element from the iterable. If the key function is not passed, identity
        function is used in which case `T` must support `LessThan` operator.

        Args:
            key (Optional[Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan` that represents
             the relation of partial order between elements.

        Returns:
            the biggest element of `self` or `None` if `self` is empty.
        """

        def identity(x):
            return x
        key = identity if key is None else key

        it = self.iter()
        try:
            best = next(it)
        except StopIteration:
            return None
        for elem in it:
            if key(best) < key(elem):
                best = elem
        return best

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> "Lazy[T]":
        """
        When `self` is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: `Lazy[T | Iterable[T | Iterable[T | ...]]]`.


        Args:
            break_str (bool): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type]): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns:
            New `Lazy` with all nested iterables flattened to a single iterable.

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

    def take_while(self, pred: Callable[[T], bool]) -> "Lazy[T]":
        """
        Creates a new Lazy that yields elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of `self`, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function: (T) -> bool`

        Returns:
            A new `Lazy` containing elements from the original sequence, stopping at the first element for which the
             predicate returns `False`.
        """
        def inner():
            for elem in self.gen:
                if not pred(elem):
                    return
                yield elem
        return Lazy(inner())

    def window(self, window_size: int) -> "Lazy[QList[T]]":
        """
        Creates a new `Lazy` of sliding windows of size `window_size`. If `window_size`
        is greater than the total length of `self` an empty iterator is returned.

        Args:
            window_size (int): the size of the sliding window. Must be greater than 0.

        Returns:
            New `Lazy` of all sliding windows.
        """
        assert window_size > 0, f'window size must be greater than 0 but got {window_size}.'
        def inner(n: int):
            window = deque(maxlen=n)
            it = self.iter()
            try:
                for _ in range(n):
                    window.append(next(it))
            except StopIteration:
                return
            yield QList(window)
            for elem in it:
                window.append(elem)
                yield QList(window)
        return Lazy(inner(n=window_size))

    def first(self) -> Optional[T]:
        """
        Tries to access the first element of `self`. Returns `None` if `self` is empty.

        Returns:
            First element of `self` or `None` if `self` is empty.
        """
        it = self.iter()
        try:
            return next(it)
        except StopIteration:
            pass
        return None

    def get(self, index: int, default: Optional[T] = None) -> Optional[T]:
        """
        Safely gets the element on the specified index. If the index is out of bounds `default` is returned.
        This is an `O(n)` operation that consumes the iterator!

        Args:
            index (int): index of the element to take
            default (Optional[T]): value to return if the index is out of bounds. Defaults to `None`

        Returns:
            Element at the specified index or `default` if index is out of bounds.
        """
        if index < 0:
            return default
        for i, elem in self.enumerate():
            if i == index:
                return elem
        return default

    def uncons(self) -> Optional[Tuple[T, "Lazy[T]"]]:
        """
        Splits `self` into head and tail. Returns `None` if `self` is emtpy.

        Returns:
            Head and tail of `self` or `None` is `self` is empty.

        """
        it = self.iter()
        try:
            head = next(it)
        except StopIteration:
            return None
        return head, Lazy(it)

    def split_when(self, pred: Callable[[T], bool]) -> Optional[Tuple["QList[T]", "Lazy[T]"]]:
        """
        Splits the lazy sequence into two parts at the first element satisfying the predicate.
        The element that satisfies the predicate is included in the left part, which is fully evaluated,
        while the right part remains lazy, allowing for operations on infinite sequences.

        Args:
            pred (Callable[[T], bool]): `function (T) -> bool` that returns `True`
                if the element is the split point.

        Returns:
            A tuple where the first element is a fully evaluated `QList` containing all elements up to and
             including the split point, and the second element is a lazily evaluated sequence of all
             elements after the split point. Returns `None` if `self` is empty. If no element satisfies the
             predicate, the left part contains all elements from `self` and the right part is an empty lazy sequence.
        """
        left = QList()
        it = self.iter()
        for elem in it:
            left.append(elem)
            if pred(elem):
                return left, Lazy(it)
        if not left:
            return None
        return left, Lazy([])

# ---------------------------------------------- QList ----------------------------------------------

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

    def slice(self, s: slice) -> Lazy[T]:
        """
        Calling this method with `s` equal to `slice(3)` works similarly to
        `list[:3]` but is lazy evaluated.

        Args:
            s: slice object

        Returns:
            `Lazy[T]`
        """
        assert isinstance(s, slice), f"slice method argument must be a slice object. Got {type(s)}."

        def inner():
            for elem in self[s]:
                yield elem
        return Lazy(inner())

    def list(self) -> List[T]:
        """
        Changes `QList` into standard Python `list`.

        Returns:
            Standard Python `list`.
        """
        return list(self)

    def eager(self) -> "EagerQList[T]":
        """
        Changes `QList` into `EagerQList`.

        Returns:
            Eagerly evaluated version of `QList`.
        """
        from .eager import EagerQList
        return EagerQList(self)

    def filter(self, pred: Callable[[T], bool]) -> Lazy[T]:
        """
        Returns a `Lazy` object containing all values from `self` for which
        the predicate holds true.

        Args:
            pred: `function: (T) -> bool`

        Returns:
            New `Lazy[T]` with elements for which the predicate holds true.

        Examples:
            >>> QList([0, 1, 2, 3]).filter(lambda x: x < 2).collect()
            [0, 1]
        """
        def inner():
            for elem in self:
                if pred(elem):
                    yield elem
        return Lazy(inner())

    def map(self, mapper: Callable[[T], K]) -> Lazy[K]:
        """
        Returns a `Lazy` object containing all values from `self` with
        the mapping function applied on them.

        Args:
            mapper: `function: (T) -> K`

        Returns:
            New `Lazy[K]` with mapped elements from `self`.
        """
        def inner():
            for elem in self:
                yield mapper(elem)
        return Lazy(inner())

    def foreach(self, action: Callable[[T], None]):
        """
        Applies the given function to each of the `QList` elements.

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

        **Other names:** fold_left, reduce, accumulate, aggregate.

        Args:
            operation: `function: (K, T) -> K`. Given the initial value `init` applies the
                given combination operator on each element yielded by `self`,
                treating the result as the first argument in the next step.
            init (K): initial value for the combination operator.

        Returns:
            The final value created from calling the `operation` on consecutive elements of `self`.

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
            >>> QList([1, 2, 3]).fold_right(lambda acc, x: acc + x, 0)
            6
        """
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def scan(self, operation: Callable[[K, T], K], state: K) -> "Lazy[K]":
        """
        Given the combination operator creates a `Lazy[K]` object by processing
        constituent parts of `self`, yielding intermediate steps and building up the final value.
        Scan is similar to fold but returns all intermediate states instead of just the final result.

        Args:
            operation: `function: (K, T) -> K`. Given the initial `state` applies the given
             combination operator on each element yielded by the `Lazy` object, yielding the result and
             then treating it as the first argument in the next step.
            state (K): initial value for the state.

        Returns:
            New `Lazy[K]` with all intermediate steps of the `operation`.

        Examples:
            >>> QList([1, 2, 3]).scan(lambda acc, x: acc + x, 0).collect()
            [1, 3, 6]
        """
        def inner(s):
            for elem in self:
                s = operation(s, elem)
                yield s
        return Lazy(inner(state))

    def len(self) -> int:
        """
        Returns the length of `self`.

        (time complexity: `O(1)`)

        Returns:
            Length of the `QList`
        """
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> Lazy[K]:
        """
        Applies the mapper function to each of the yielded elements and flattens the results.

        Args:
            mapper: `function: (T) -> Iterable[K]`.

        Returns:
            New `Lazy` with elements from `self` mapped to an iterable and then flattened.

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
        Combines `self` with the given `Iterable` elementwise as tuples.
         The returned `Lazy` objects yields at most the number of elements of
         the shorter sequence (`self` or `other`).

        Args:
            other (Iterable[K]): iterable to zip with `self`.

        Returns:
            New `Lazy` with pairs of elements from `self` and `other`.

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
            key (Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan`. Defaults to `None`.
            reverse (bool): if set to `True` sorts values in descending order. Defaults to `False`.

        Returns:
            Sorted `QList`.
        """
        return QList(sorted(self, key=key, reverse=reverse))

    def skip(self, n: int) -> Lazy[T]:
        """
        Skips `n` first elements of `self`.

        Args:
            n (int): numbers of elements to skip. Should be non-negative.

        Returns:
            New `Lazy` with `n` first elements of `self` skipped.

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
        Takes `n` first elements of `self`.

        Args:
            n (int): numbers of elements to take. Should be non-negative.

        Returns:
            New `Lazy` with only `n` first elements from `self`.

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
        If `self` is a `QList` object of `Iterable[T]`, flatten concatenates all iterables into a
        single list and returns a `Lazy[T]` object.

        Returns:
            Concatenation of all elements from `self`.

        Raises:
            TypeError: when elements of Lazy are not iterables.

        Examples:
            >>> QList([[1, 2], [3, 4]]).flatten().collect()
            [1, 2, 3, 4]
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
        Returns a `Lazy[T]` that cycles through the elements of `self`, which means
        on achieving the last element the iteration starts from the beginning. The
        returned `Lazy` object has no end (infinite iterator) unless `self` is empty
        in which case cycle returns an empty `Lazy` object (empty iterator).

        Returns:
            Infinite `Lazy` that loops through elements of `self`, or empty iterator if `self` is emtpy.

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

        Args:
            start (int): starting index. Defaults to 0.

        Returns:
            New `Lazy` with pairs of index and value.

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
            size (int): size of one batch.

        Returns:
            New `Lazy` of batches (`QList`) of given `size`. Last batch may have fewer elements.

        Examples:
            >>> QList(range(5)).batch(2).collect()
            [[0, 1], [2, 3], [4]]
        """
        assert size > 0, f'batch size must be greater then 0 but got {size}'
        def inner():
            for i in range(0, self.len(), size):
                yield QList(self[i:i+size])
        return Lazy(inner())

    def batch_by(self, grouper: Callable[[T], SupportsEq]) -> "Lazy[QList[T]]":
        """
        Batches elements of `self` based on the output of the grouper function. Elements are thrown
        to the same group as long as the grouper function returns the same key (keys must support equality checks).
        When a new key is returned a new batch (group) is created.

        Args:
            grouper (Callable[[T], SupportsEq]): `function: (T) -> SupportsEq` that provides the keys
             used to group elements, where the key type must support equality comparisons.

        Returns:
            New `Lazy[QList[T]]` with elements batched based on the `grouper` key.

        Examples:
            >>> QList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[0]).collect()
            [['a1'], ['b1', 'b2'], ['a2', 'a3'], ['b3']]
            >>> QList(['a1', 'b1', 'b2', 'a2', 'a3', 'b3']).batch_by(lambda s: s[1]).collect()
            [['a1', 'b1'], ['b2', 'a2'], ['a3', 'b3']]
        """
        def inner():
            if self.len() == 0:
                return
            batch = QList([self[0]])
            key = grouper(self[0])
            for elem in self[1:]:
                new_key = grouper(elem)
                if new_key == key:
                    batch.append(elem)
                else:
                    yield batch
                    batch = QList([elem])
                    key = new_key
            if batch:
                yield batch
        return Lazy(inner())

    def chain(self, other: Iterable[T]) -> Lazy[T]:
        """
        Chains `self` with `other`, returning a new `Lazy[T]` with all elements from both iterables.

        Args:
            other (Iterable[T]):  an iterable of elements to be "attached" after `self` is exhausted.

        Returns:
            New `Lazy` with elements from `self` and `other`.

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
            other (Iterable[T]): an iterable to be merged with `self`.
            merger (Callable[[T, T], bool]): `function: (T, T) -> bool` that takes two arguments (left and right).
             If the output is True, the left argument is yielded; otherwise, the right argument is yielded.

        Returns:
            New `Lazy` containing the merged elements.

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
            mapper (Optional[Callable[[T], Booly]]): `function: (T) -> Booly` that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if all elements of `self` are `Truthy`. `False` otherwise.
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
        Goes through the entire generator and checks if any element is `Truthy`.
        `Booly` is a type that evaluates to something that is either `True` (`Truthy`) or `False` (`Falsy`).
        For example in Python an empty list evaluates to `False` (empty list is `Falsy`).

        Args:
            mapper (Optional[Callable[[T], Booly]]): `function: (T) -> Booly` that maps `T` to `Booly` which is a type that
             can be interpreted as either True or False. If not passed, identity function is used.

        Returns:
            `True` if there is at least one element in `self` that is `Truthy`. `False` otherwise.
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
            key (Optional[Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan` that represents
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
        Returns the biggest element from `self`. If the key function is not passed, identity
        function is used in which case `T` must support `LessThan` operator.

        Args:
            key (Optional[Callable[[T], SupportsLessThan]): `function: (T) -> SupportsLessThan` that represents
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

    def full_flatten(self, break_str: bool = True, preserve_type: Optional[Type] = None) -> Lazy[T]:
        """
        When `self` is an iterable of nested iterables, all the iterables are flattened to a single iterable.
        Recursive type annotation of `self` may be imagined to look like this: `QList[T | Iterable[T | Iterable[T | ...]]].`


        Args:
            break_str (bool): If `True`, strings are flattened into individual characters. Defaults to `True`.
            preserve_type (Optional[Type]): Type to exclude from flattening (i.e., treated as non-iterable). For example,
             setting this to `str` makes `break_str` effectively `False`. Defaults to `None`.

        Returns:
            New `Lazy` with all nested iterables flattened to a single iterable.

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
        Creates a `Lazy` that yields elements based on a predicate. Takes a function as an argument.
        It will call this function on each element of `self`, and yield elements while the function
        returns `True`. After `False` is returned, iteration stops, and the rest of the elements is ignored.

        Args:
            pred (Callable[[T], bool]): `function: (T) -> bool`

        Returns:
            New `Lazy` containing elements from the original sequence, stopping at the first element for which the
             predicate returns `False`.
        """
        def inner():
            for elem in self:
                if not pred(elem):
                    return
                yield elem
        return Lazy(inner())

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

    def window(self, window_size: int) -> "Lazy[QList[T]]":
        """
        Creates a `Lazy` of sliding windows of size `window_size`. If `window_size`
        is greater than the total length of `self` an empty iterator is returned.

        Args:
            window_size (int): the size of the sliding window. Must be greater than 0.

        Returns:
            New `Lazy` of all sliding windows.
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
            yield QList(window)
            for elem in self[n:]:
                window.append(elem)
                yield QList(window)
        return Lazy(inner(n=window_size))


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
    split = primes.split_when(lambda x: x > 10)
    if split is not None:
        left, right = split
        print(left)
        print(right.take(10).collect())

