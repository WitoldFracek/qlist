![Qitek](cat200.png)

# Qwery List
Welcome to Qwery List (or qwlist for short) - the Python library that puts the "fun" back in functional programming
by bringing Rust-style iterators to Python!
Qwery List introduces a new way to work with lists and iterators, leveraging **lazy evaluation** to improve efficiency 
while keeping your code clean and readable.

## Why choose Qwery List?
In Python, we're accustomed to using list comprehensions and generators for lazy evaluation. 
Let's explore why Qwery List might just become your new best friend.
Consider a simple scenario: converting a list of strings to integers, filtering even numbers, and summing them up. 
Traditionally, you might write:
```python
nums = ['1', '2', '3', '4', '5', '6', '7']
s = sum([int(n) for n in nums if int(n) % 2 == 0])
```
Notice the repeated use of `int()`. Sure, casting to int is quick, but what if you were running a time-consuming 
function? You might turn to `map` and `filter`:
```python
mapped_data = map(long_taking_operation, data)
filtered_data = filter(lambda x: x % 2 == 0, mapped_data)
s = sum(filtered_data)
```
This approach is better but introduces readability challenges, especially when chaining operations:
```python
s = sum(filter(lambda x: x % 2 == 0, map(long_taking_operation, data)))
```
Readable? Barely. Maintainable? Questionable. Enter Qwery List!
```python
nums = QList(['1', '2', '3', '4', '5', '6', '7'])
s = nums.map(long_taking_operation).filter(lambda x: x % 2 == 0).sum()
```
Not only does this look cleaner, but it also flows naturally from left to right.

## From simple to sophisticated
The previous example was straightforward, and you might stick to Python's built-in tools for such cases.
But when dealing with more advanced scenarios, Qwery List truly shines. Let’s see it in action:
```python
# Pandas DataFrame with team names and IDs
teams_df = pd.DataFrame()
allowed_teams = ['Team A', 'Rascals', 'True Pythonists']

batches = (
    Lazy(teams_df.iterrows())
    .map(lambda pair: pair[1])                            # Extract the DataFrame row, ignore the index
    .map(lambda row: (row['team_name'], row['team_id']))  # Create (team_name, team_id) tuples
    .filter(lambda pair: pair[0] in allowed_teams)        # Keep only allowed teams
    .batch(20)                                            # Group into batches
)
```
Here, we used `Lazy` instead of `QList`. Why? While `QList` is an extension of Python's standard `list`, 
`Lazy` introduces true **lazy evaluation**. Operations are only computed when needed, and even the creation of the 
iterator is deferred.

Consider this infinite prime number generator:
```python
def naturals(start: int):
    current = start
    while True:
        yield current
        current += 1

primes = Lazy(naturals(2)).filter(
    lambda n: Lazy(naturals(2))
    .take_while(lambda p: p * p <= n)
    .all(lambda x: n % x != 0)
)
```
Yes, that’s an infinite iterator. And no, it won’t crash your program (unless you ask it for infinite 
output—then all bets are off). It elegantly showcases how Qwery List handles infinite iterators with grace.

## Overview of some of the unique methods
Qwery List not only allows you to use some of the standard Python built-in functions in a fluent way but also 
offers a range of unique methods that elevate your programming game. Here's a quick overview:

### Boolean Quantifiers
Both `QList` and `Lazy` have `any` and `all` methods, making it easy to evaluate boolean conditions across elements.
```python
Lazy([True, True, False]).all()            # returns False
Lazy([True, True, False]).any()            # returns True
Lazy([2, 4, 6]).all(lambda x: x % 2 == 0)  # returns True - all numbers are even
```

### Math Operations: `max` and `min`
Find the maximum or minimum value of an iterable with or without a custom key function:
```python
Lazy([1, 2, 3, 4]).max()                          # returns 4
Lazy([1, 2, 3, 4]).min()                          # returns 1
Lazy([1, 2, 3, 4]).max(key=lambda x: abs(3 - x))  # returns 1
```

### Chaining iterators
Qwery List allows you to seamlessly chain finite and infinite iterators.
```python
primes = Lazy(naturals(2)).filter(
    lambda n: Lazy(naturals(2))
    .take_while(lambda p: p * p <= n)
    .all(lambda x: n % x != 0)
)

# add three zeros at the beginning of the prime numbers
chained = Lazy([0, 0, 0]).chain(primes)
```

### Sorting capabilities
Qwery List offers a new `sorted` and `merge` methods which come in handy for dealing with ordered data.
```python
sorted_list = QList([2, 5, 3, 1, 4]).sorted()
# [1, 2, 3, 4, 5]

merged_list = QList([1, 2, 5, 7, 8]).merge([3, 4, 6, 9], lambda left, right: left < right).collect()
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### "Pure" functional style
Qwery List offers methods such as `fold` and `uncons` that are well known from functional languages.
```python
head, tail = Lazy([1, 2, 3, 4]).uncons()
# head = 1
# tail = Lazy([2, 3, 4])
```

```python
from typing import List, Dict, TypeVar
K = TypeVar('K')
V = TypeVar('V')

def update_dict(data: Dict[K, List[V]], key: K, value: V) -> Dict[K, List[V]]:
    if key in data:
        data[key].append(value)
    else:
        data[key] = [value]
    return data

values = QList([('name', 'Alex'), ('country', 'Poland'), ('name', 'David')])
data = values.fold(lambda acc, x: update_dict(acc, *x), {})
# {'name': ['Alex', 'David'], 'country': ['Poland']}
```

---

# Installation
This package is available on [PyPI](https://pypi.org/project/qwlist/)
```
pip install qwlist
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


