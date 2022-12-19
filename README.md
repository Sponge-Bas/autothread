# Threadpy

Parallelization made easy.

Threadpy allows you to add multithreading/multiprocessing to your functions by adding
just a single line:

```python
import threadpy
from time import sleep as heavyworkload

@threadpy.multithreaded() # <-- This is all you need to add
def example(x: int, y: int):
    heavyworkload(1)
    return x*y
```

Now, instead of integers, your function can take lists of integers. The function will
be repeated or each item in your list on a separate thread:
```
start = time.time()
result = example([1, 2, 3, 4, 5], 10)
print(result)
print("Time expired: ", time.time()-start)
>>> [10, 20, 30, 40, 50]
    Time expired:  1.0041766166687012
```

Threadpy uses the type-hinting of your funtion to reliably determine which paremeters
you intent to keep constant and which parameters need to change for every thread.
`threadpy.multiprocessed` functions exactly the same but will apply multiprocessing instead.