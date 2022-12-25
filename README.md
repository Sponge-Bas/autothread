# Autothread

Parallelization made easy.

Autothread allows you to add multithreading/multiprocessing to your functions by adding
just a single line:

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

## Usage

The `autothread.multithreaded` and `autothread.multiprocessed` decorators can be placed
in front of any function to make them threaded/multiprocessed. The only requirement
from the function (besides the regular threading and multiprocessing requirements) is
that the function has type-hinting for all the variables that you wish to vary for each thread.

The decorators take 4 arguments to configure the execution:
- `n_workers` (int): Total number of workers to run in parallel (-1 for unlimited, `None` (default) for the amount of cores).
- `mb_mem` (int): Minimum megabytes of memory for each worker, usefull when your script is memory limited.
- `workers_per_core` (int): Number of workers to run per core.
- `progress_bar` (int): Visualize how many of the tasks have started running.

## How it works
Autothread uses the type-hinting of your funtion to reliably determine which paremeters
you intend to keep constant and which parameters need to change for every thread.

In general, the argument is split over multiple threads/processes when:
- The argument is a list or tuple.
- The argument does not match the type hinting of the function.
- All the items in the argument do match the type hinting of the function.

For example
```python3
example(x = [1, 2, 3], y = 5)
```

`x` is a `List[int]`, but its original type hint is `int`. This means that `x` will be split over multiple processes while `y=5` stays constant.

```python3
example(x = [1, 2, 3], y = [4, 5, 6])
```

Now, both `x` and `y` are `List[int]` while the original type hint is `int`. This means that both 
`x` and `y` will be split over the multiple processes. This requires `x` and `y` to be of the same
length.

If autothread can't determine the original type hint (e.g. the type hint is missing, incorrect, or 
the parameter is part of `*args` or `**kwargs`), autothread will not divide the list over multiple processes. To override the autodetection of looping parameters for these cases, provide the
`_loop_params` keyword with a list of parameters you intend to change for each process when calling your function.

For an overview of more detailed behavior, check `threadpy/test.py`. This file contains all the functional tests of autothread.

## Error handling
If one of the processes fails, autothread will send a keyboard interrupt signal to all
the other running threads/processes to give them a change to handle the exit gracefully.
If you want the threads to clean things up before exiting, just intercept the `KeyboardInterrupt`
exeption and do the cleanup (just like you would in a single threaded case).

Autothread itself will exit by raising the exception of the first thread/process that failed.

## Known issues
None at the moment, please open a bug if you run into an issue.
