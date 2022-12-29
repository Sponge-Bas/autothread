# Autothread

Parallelization made easy.

Autothread contains a collection of decorators that make it as easy as possible to add
threading or multiprocessing to your projects. Autothread has two types of decorators: blocking and non-blocking.

## Non-blocking
Autothreads non-blocking decorators are the easiest way to add threading/multiprocessing to your
project. You just need to add a single decorator, which changes your function to calculate in
the background instead of blocking the script.

```python
import autothread
import time
from time import sleep as heavyworkload

@autothread.async_threaded() # <-- This is all you need to add
def example(x, y) -> int:
    heavyworkload(1)
    return x*y

start = time.time()
results = []
for i in range(5):
    results.append(example(i, 10)) # the thread is started

print(results) # autothread waits for the thread to end and gives you the result
print("Time expired: ", time.time()-start)
>>> [0, 10, 20, 30, 40]
    Time expired:  1.002363681793213
```

`autothread.async_processed` works in the same way but uses multiprocessing instead of threading.
More info can be found in the [non-blocking README](https://github.com/Basdbruijne/autothread/blob/main/docs/README_non_blocking.md).

## Blocking
The blocking decorators of autothread change the function slightly, but give you more control
over when the function is executed:

```python
import autothread
import time
from time import sleep as heavyworkload

@autothread.multithreaded() # <-- This is all you need to add
def example(x: int, y: int):
    heavyworkload(1)
    return x*y

@autothread.multiprocessed() # <-- Or to use multiprocessing
def example2(x: int, y: int):
    heavyworkload(1)
    return x*y
```

Now, instead of integers, your function can take lists of integers. The function will
be repeated or each item in your list on a separate thread/process:
```python3
start = time.time()
result = example([1, 2, 3, 4, 5], 10)
print(result)
print("Time expired: ", time.time()-start)
>>> [10, 20, 30, 40, 50]
    Time expired:  1.0041766166687012
```

More info can be found in the [blocking README](https://github.com/Basdbruijne/autothread/blob/main/docs/README_blocking.md).

## Installing

You can install autothread using:
```
pip install autothread
```

Or by cloning the source:
```
git clone https://github.com/Basdbruijne/autothread.git
cd autothread
pip install -e .
```

## Known issues
None at the moment, please open a bug if you run into an issue.
