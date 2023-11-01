from typing import TypeVar, Generic, Iterable, Iterator, Callable, Generator

T = TypeVar('T')
K = TypeVar('K')


class Lazy(Generic[T]):
    def __init__(self, gen: Generator[T, None, None] | Iterator[T]):
        self.gen = gen

    def list(self) -> list[T]:
        return [elem for elem in self.gen]

    def qlist(self):
        return QList(elem for elem in self.gen)

    def filter(self, pred: Callable[[T], bool]):
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

    def fold(self, operation: Callable[[K, T], K], init: K):
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


class QList(list, Generic[T]):
    def filter(self, pred: Callable[[T], bool]) -> Lazy[T]:
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

    def fold(self, operation: Callable[[K, T], K], init: K):
        acc = init
        for elem in self:
            acc = operation(acc, elem)
        return acc

    def fold_right(self, operation: Callable[[K, T], K], init: K):
        acc = init
        for elem in self[::-1]:
            acc = operation(acc, elem)
        return acc

    def len(self):
        return len(self)

    def flatmap(self, mapper: Callable[[T], Iterable[K]]) -> Lazy[K]:
        def inner():
            for elem in self:
                yield from mapper(elem)
        return Lazy(inner())


if __name__ == '__main__':
    def triple(arg):
        return QList([arg, arg, arg])

    def reductor(prev: QList, cur):
        if not prev:
            prev.append(cur)
            return prev
        if prev[-1] != cur:
            prev.append(cur)
        return prev

    ql = QList(x for x in range(10)).flatmap(triple).flatmap(triple).fold(reductor, QList())
    print(ql)


