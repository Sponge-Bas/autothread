import autothread
import time
from time import sleep as heavyworkload

@autothread.multithreaded() # <-- This is all you need to add
def example(x: int, y: int):
    heavyworkload(1)
    return x*y

start = time.time()
result = example([1, 2, 3, 4, 5], 10)
print(result)
print("Time expired: ", time.time()-start)