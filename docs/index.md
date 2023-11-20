![Qitek](cat200.png)

# Qwery List

Qwery List is a small library introducing a new way to use higher order functions
with lists, with **lazy evaluation**. 

### Quick comparison
#### The standard python way
```python
xs = ['1', '2', '3', '4']
s = reduce(
    lambda acc, x: acc + x,
    filter(
        lambda x: x < 3,
        map(
            int,
            xs
        )
    )
    ,0
)
```
#### Qwery List way
```python
xs = QList(['1', '2', '3', '4'])
s = (
    xs
    .map(int)
    .filter(lambda x: x < 3)
    .fold(lambda acc, x: acc + x, 0)
)
```
Chaining methods makes code much more readable and follows the natural flow
of reading left to right. 
As a bonus you get `len()` **method**, so no longer will you be forced to wrapp your
lists in this type of code `len(xs)` and simply call `xs.len()` (I understand it is negligibly 
slower but look how much nicer it looks!)

---

# Installation
This package is available on [PyPI](https://pypi.org/project/qwlist/)
```
pip install qwlist
```

---

# Quick tutorial
Let's say we want to read numbers from a file and choose only the even ones. No problem at all!
```python
from qwlist import QList

with open('path/to/file.txt', 'r') as file:
    qlist = QList(file.readlines())

even = (
    qlist
    .map(int)
    .filter(lambda x: x % 2 == 0)
    .collect()
)
```
Why is there this `collect` at the end? Because all operations on the QList are **lazy evaluated**, 
so in order to finally apply all the operations you need to express that.

There is also an eagerly evaluated `EagerQList` in case all the actions performed on the list should
be evaluated instantaneously. This object is in the `qwlist.eager` module, but it is also
possible to transform `QList` into `EagerQList` simply by calling `eager()`
```python
from qwlist import QList

xs = (
    QList(range(3))
    .eager()
    .map(str)
)
print(xs)  # ['0', '1', '2']
```
EagerQList has the same methods that QList has (`filter`, `map`, `foreach`, ...) but not lazy evaluated so
there is no need to call `collect` at the end.

---
# Examples
Making QList from an iterable
```python
>>> QList([1, 2, 3, 4])
[1, 2, 3, 4]
```
Making QList from a generator
```python
>>> QList(range(3))
[0, 1, 2]
```
Making a list of pairs: `int` and `str`
```python
>>> qlist = QList([1, 2, 3])
>>> qlist.zip(qlist.map(str)).collect()
[(1, '1'), (2, '2'), (3, '3')]
```
Summing only the even numbers
```python
s = (
    QList(range(10))
    .filter(lambda x: x % 2 == 0)
    .fold(lambda acc, x: acc + x, 0)
)
print(s)  # 20
```
---

## Side note
This syntax resembles **Rust** syntax:

<table>
<tr>
<th>Rust</th>
<th>Python</th>
</tr>
<tr>
<td>

```rust
let xs = vec![1, 2, 3, 4];
let double_xs: Vec<i32> = xs
    .iter()
    .map(|&x| x * 2)
    .collect();
println!("{double_xs:?}");
// [2, 4, 6, 8]

```

</td>
<td>

```python
xs = QList([1, 2, 3, 4])
double_xs = (
    xs
    .map(lambda x: x * 2)
    .collect()
)
print(double_xs)
# [2, 4, 6, 8]
```

</td>
</tr>
</table>


