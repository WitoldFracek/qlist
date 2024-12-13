In 2024 I challenged myself to use the **qwlist** library whenever it was suitable for solving problems
in [Advent Of Code](https://adventofcode.com/2024). You can find my solutions [here](https://github.com/WitoldFracek/AdventOfCode2024).
In this document, I showcase a few examples of how qwlist simplified my approach during the challenge.

To read input data efficiently, I created the following helper function in my `utils.py` file:
```python
def read_lines(path: str | Path) -> Generator[str, None, None]:
    with open(path, 'r', encoding='utf8') as file:
        for line in file:
            yield line.strip()

```

## Day 1
Below is an example of how I solved Day 1 challenge. 
Comments indicate the type of elements returned at each step of the chain.
```python
def collect_numbers(acc, pair):
    left, right = acc
    left.append(pair[0])
    right.append(pair[1])
    return left, right

def sol_a() -> int:
    left, right = (
        Lazy(read_lines('./input.txt'))              # Item = str
        .map(lambda line: line.split(' '))           # Item = List[str]
        .map(lambda x: (int(x[0]), int(x[-1])))      # Item = Tuple[int ,int]
        .fold(collect_numbers, (QList(), QList()))
    )
    return (
        left                                        # Item = int
        .sorted()                                   # Item = int
        .zip(right.sorted())                        # Item = Tuple[int, int]
        .map(lambda pair: abs(pair[0] - pair[1]))   # Item = int
        .sum()
    )
```

## Day 2
On Day 2, I used the [`window`](https://witoldfracek.github.io/qlist/qlist/#src.qwlist.qwlist.QList.window) 
method to create windows of two elements used for calculating the difference between them.
Additionally, the [`all`](https://witoldfracek.github.io/qlist/qlist/#src.qwlist.qwlist.QList.all) 
method helped to check constraints.
```python
def is_correct_seq(seq: QList[int]) -> bool:
    diffs = seq.window(2).map(lambda w: w[0] - w[1]).collect()
    if diffs.all(lambda x: 0 < x < 4):
        return True
    if diffs.all(lambda x: -4 < x < 0):
        return True
    return False

def sol_a() -> int:
    return (
        Lazy(read_lines('./input.txt'))                         # Item = str
        .map(lambda x: QList(x.split(' ')).map(int).collect())  # Item = QList[int]
        .filter(is_correct_seq)                                 # Item = QList[int]
        .collect()
        .len()
    )
```
## Day 4
The [`flatmap`](https://witoldfracek.github.io/qlist/qlist/#src.qwlist.qwlist.QList.flatmap) 
method helped determine XMAS and SAMX sequences within rows and columns of the input.

#### Searching horizontally
```python
def search_horizontal(data: QList[str]) -> int:
     return (
        data                                                # Item = str
        .flatmap(lambda l:
            Lazy(l)                                         # Item = str
            .window(4)                                      # Item = QList[str]
            .map(lambda b: b.sum())                         # Item = str
            .filter(lambda s: s == 'XMAS' or s == 'SAMX')   # Item = str
        )                                                   # Item = str
        .collect()
        .len()
    )
```
#### Searching vertically
```python
def search_vertical(data: QList[str]) -> int:
    return (
        Lazy(zip(*data))                                    # Item = Tuple[str, ...]
        .map(Lazy)                                          # Item = Lazy[str]
        .flatmap(lambda l:
            l.window(4)                                     # Item = QList[str]
             .map(lambda b: b.sum())                        # Item = str
             .filter(lambda s: s == 'XMAS' or s == 'SAMX')  # Item = str
        )                                                   # Item = str
        .collect()
        .len()
    )
```

## Day 7
Day 7 is particularly interesting due to the use of the [`flat_fold`](https://witoldfracek.github.io/qlist/lazy/#src.qwlist.qwlist.Lazy.flat_fold)
method, also known as `monadic_fold` or `foldM` (for example in [Haskell](https://www.haskell.org/)).
It allowed me to generate all possible outcomes of applying addition and multiplication operators to a list of numbers.

Let's say our input list looks like this: `[2, 5]`. 
For this two values we can either add them up or multiply so the resulting list would have
two elements as well `[2+5, 2*5]`. If we had three elements in the list there would be four possible combinations. 
For input `[2, 5, 3]` the result would be `[2+5+3, 2+5*3, 2*5+3, 2*5*3]` (in day 7's problem the order of operators 
was not the standard multiplication before addition but going from left to right).

[`flat_fold`](https://witoldfracek.github.io/qlist/lazy/#src.qwlist.qwlist.Lazy.flat_fold)
and [`any`](https://witoldfracek.github.io/qlist/lazy/#src.qwlist.qwlist.Lazy.any)
allows for an easy implementation of this solution, and lazy evaluation allows for early returns when a
suitable score is found (`any` will return as soon as it finds truthy element).

What I personally like a lot about this approach is that I didn't hve to make changes in the code
for the B variant of this problem. Solving it was as easy as passing one additional operator.
```python
def is_solvable(target: int, args: QList[int], operations: Iterable[Callable[[int, int], int]]) -> bool:
    return (
        args                                                                    # Item = int
        .skip(1)                                                                # Item = int
        .flat_fold(lambda acc, x: [op(acc, x) for op in operations], args[0])   # Item = int
        .any(lambda x: x == target)
    )

def parse_line(line: str) -> Tuple[int, QList[int]]:
    target, numbers = line.split(':')
    numbers = QList(numbers.split(' ')).filter(lambda x: x != '').map(int).collect()
    return int(target), numbers

def sol_a() -> int:
    operators = [int.__add__, int.__mul__]
    return (
        Lazy(read_lines('./input.txt'))                                 # Item = str
        .map(parse_line)                                                # Item = Tuple[int, QList[int]]
        .filter(lambda pair: is_solvable(pair[0], pair[1], operators))  # Item = Tuple[int, QList[int]]
        .map(lambda pair: pair[0])                                      # Item = int
        .collect()
        .sum()
    )

def sol_b() -> int:
    operators = [int.__add__, int.__mul__, lambda a, b: int(f'{a}{b}')]
    return (
        Lazy(read_lines('./input.txt'))                                 # Items = str
        .map(parse_line)                                                # Item = Tuple[int, QList[int]
        .filter(lambda pair: is_solvable(pair[0], pair[1], operators))  # Item = Tuple[int, QList[int]
        .map(lambda pair: pair[0])                                      # Item = int
        .collect()
        .sum()
    )
```