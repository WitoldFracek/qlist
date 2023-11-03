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

As a bonus you get `len()` **method**, so no longer will you be forced to wrapp your
lists in this type of code `len(xs)` and simply call `xs.len()` (I understand it is negligibly 
slower but look how much nicer it looks!)


## Quick tutorial
Let's say we want to read numbers from a file and choose only the even ones. No problem at all!
```python
with open('path/to/file.txt', 'r') as file:
    qlist = QList(file.readlines())
even = qlist.map(int).filter(lambda x: x % 2 == 0).collect()
```
Why is there this `collect` at the end? Because all operations on the QList are lazy evaluated, 
so in order to finally apply all the operations you need to express that. (Eager evaluated module
coming soon...)

---
## Examples
Making QList from an iterable
```python
>>> QList([1, 2, 3, 4])
[1, 2, 3, 4]
```
Making QList from a generator
```python
>>> QList(x for x in range(3))
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
>>> QList(x for x in range(10)).filter(lambda x: x % 2 == 0).fold(lambda acc, x: acc + x, 0)
20
```
---

### Side note
I hereby announce that UwU, Qwery Listwu

