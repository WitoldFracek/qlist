# Qwery List
QList is a small library introducing a new way to use higher order functions
with lists, with **lazy evaluation**. It also aims to address ugly 
python list methods such as map, filter and reduce. Whoever invented this:
```python
xs = ['1', '2', '3', '4']
s = reduce(lambda acc, x: acc + x, filter(lambda x: x < 3, map(int, xs)), 0)
```
must reevaluate their life choices (yes, I am being cocky and most likely dumdum) but listen
to me first and look what the world of lazy evaluation has to offer!
```python
xs = QList(['1', '2', '3', '4'])
s = xs.map(int).filter(lambda x: x < 3).fold(lambda acc, x: acc + x, 0)
```

As a bonus you get `len()` **method**, so no longer will you be forced to wrap your
lists in this type of code `len(xs)` and simply call `xs.len()` (I understand it is negligibly 
slower but look how much nicer it looks!)

## Quick tutorial
Let's say we want to read numbers from a file and choose only the even ones. No problem at all!
```python
from qwlist import QList

with open('path/to/file.txt', 'r') as file:
    qlist = QList(file.readlines())
even = qlist.map(int).filter(lambda x: x % 2 == 0).collect()
```
Why is there this `collect` at the end? Because all operations on the QList are **lazy evaluated**, 
so in order to finally apply all the operations you need to express that.

There is also an eagerly evaluated `EagerQList` in case all the actions performed on the list should
be evaluated instantaneously. This object is in the `qwlist.eager` module, but it is also
possible to transform `QList` into `EagerQList` simply by calling `eager()`
```python
>>> from qwlist import QList
>>> QList(range(3)).eager().map(str)
['0', '1', '2']
```
EagerQList has the same methods that QList has (`filter`, `map`, `foreach`, ...) but not lazy evaluated so
there is no need to call `collect` at the end.

---
## Examples
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
>>> QList(range(10)).filter(lambda x: x % 2 == 0).fold(lambda acc, x: acc + x, 0)
20
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
let double_xs: Vec<i32> = xs.iter().map(|&x| x * 2).collect();
println!("{double_xs:?}");
// [2, 4, 6, 8]
```

</td>
<td>

```python
xs = QList([1, 2, 3, 4])
double_xs = xs.map(lambda x: x * 2).collect()
print(double_xs)
# [2, 4, 6, 8]
```

</td>
</tr>
</table>

---
## Story behind this whole idea
Prime idea? **Vicious mockery**! \
During studying, I had to do a lot of list comprehensions in Python, alongside
methods such as `map` or `filter` and although they are quite powerful, using them
in Python is just annoying. Combining them makes you read the code in an unnatural order going
from right to left. That is the main reason that for a long time I preferred simple for-loops
as opposed to using mentioned methods. Until one day my teacher asked the whole class why no one is using
list comprehensions and higher order functions. \
"Do you guys know python?" he asked tendentiously. \
"I would use those functions if they were nicer" I thought.\
During that period I also learnt Rust and immediately fell for it. Especially with how convenient
it is to replace for-loops with method calls. And that's how the idea for a python package
**qwlist** was born.


I hereby announce that UwU, Qwery Listwu!

