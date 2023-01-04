# Autothread - Non-Blocking Decorators
Autothreads non-blocking decorators are the easiest way to fit threading/multiprocessing into your existing projects by making use of a non-blocking architecture very similar to async programming:

```python
import autothread
import time
from time import sleep as heavyworkload

@autothread.async_threaded() # <-- This is all you need to add
def example(x, y) -> int:
    print(f"{x} started")
    heavyworkload(1)
    print(f"{x} finished")
    return x*y

print("Queueing threads")
start = time.time()
results = []
for i in range(5):
    results.append(example(i, 10))

print("Waiting for results")
print(results)
print("Time expired: ", time.time()-start)
 
>>> Queueing threads
>>> 0 started
>>> 1 started
>>> 2 started
>>> 3 started
>>> 4 started
>>> Waiting for results
>>> 0 finished
>>> 4 finished
>>> 2 finished
>>> 1 finished
>>> 3 finished
>>> [0, 10, 20, 30, 40]
>>> Time expired:  1.0017051696777344
```

`autothread.async_processed` works in the same way but uses multiprocessing instead of threading.
## Usage

The `autothread.async_threaded` and `autothread.async_processed` decorators can be placed
in front of any function to make them threaded/multiprocessed. 

The decorators take 3 arguments to configure the execution:
- `n_workers` (int): Total number of workers to run in parallel (-1 for unlimited, `None` (default) for the amount of cores).
- `mb_mem` (int): Minimum megabytes of memory for each worker, usefull when your script is memory limited.
- `workers_per_core` (int): Number of workers to run per core.

## How it works
Autothread uses the return-type type-hinting of your method to determine what type of result you are expecting to receive from your function. When the function is called, autothread will return a `_Placeholder` instance. This placeholder is very similar to a `concurrent.Future` but works without async programming. Instead, the `_Placeholder` will block the script when it is called for the second time.

```python
# Start the thread and receive the placeholder
placeholder = example(i, 10)

# When any operation is performed on the placeholder, it will block until the thread is
# completed and replace itself with the return value of the function

placeholder += 5
print(placeholder)
```

Since autothread knows the return-type of your function, in can generate a placeholder that behaves identially to the final object. The only operation for which the placeholder is different from the final object is `type`:

```python
placeholder = example(i, 10)

type(placeholder) == int
>>> False

# Instead use isinstance:
isinstance(placeholder, int)
>>> True
```

## Error handling
Autothread makes the calling of the function non-blocking, but blocks the code untill the
function is done when the fist operation is performed on the functions return value. This means
that any error that comes up will be raised on the first operation on the return value.