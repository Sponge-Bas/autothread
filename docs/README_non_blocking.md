# Autothread - Non-Blocking Decorators
Autothreads non-blocking decorators make it even easier to fit threading/multiprocessing into your existing projects by making use of a non-blocking architecture very similar to async programming:

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
    results.append(example(i, 10))

print(results)
print("Time expired: ", time.time()-start)
>>> [0, 10, 20, 30, 40]
    Time expired:  1.002363681793213
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
Autothread uses the return-type type-hinting of your method to determine what type of result
you are expecting to receive from your function. When the function is called, autothread will 
return a `_Placeholder` instance. This placeholder is very similar to a `concurrent.Future` but works
without async programming. Instead, the `_Placeholder` will block the script when it is called for the second time.

```python
# Start the thread and receive the placeholder
placeholder = example(i, 10)

# When any operation is performed on the placeholder, it will block until the thread is
# completed and replace itself with the return value of the function

placeholder += 5
print(placeholder)
```

## Error handling
Autothread makes the calling of the function non-blocking, but blocks the code untill the
function is done when the fist operation is performed on the functions return value. This means
that any error that comes up will be raised on the first operation on the return value.