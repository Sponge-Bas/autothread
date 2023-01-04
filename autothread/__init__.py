# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# autothread comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.

__author__ = "Bas de Bruijne"
__version__ = "0.0.7"

import functools
import inspect
import multiprocess as mp
import psutil
import queue
import threading
import warnings

from autothread.blocking import _Autothread
from autothread.non_blocking import _Placeholder
from typing import Callable, Union


class multithreaded:
    """Decorator to make any function multithreaded

    This decorator will allow any function to receive a list where it would initially
    receive single items. The function will be repeated for every item in that list in
    parallel and the results will be concatenated into a list and returned back.

    Example:
    ```
    import autothread
    import time
    from time import sleep as heavyworkload

    @autothread.multithreaded() # <-- This is all you need to add
    def example(x: int, y: int):
        heavyworkload(1)
        return x*y

    result = example([1, 2, 3], 5)
    print(result)
    ```
    """

    Process = threading.Thread
    Queue = queue.Queue
    Semaphore = threading.Semaphore

    def __init__(
        self,
        n_workers: int = None,
        mb_mem: int = None,
        workers_per_core: int = None,
        progress_bar: bool = False,
    ):
        """Initialize the autothread decorator

        :param n_workers: Total number of workers to run in parallel (0 for unlimited,
        (default) None for the amount of cores).
        :param mb_mem: Minimum megabytes of memory for each worker.
        :param workers_per_core: Number of workers to run per core.
        :param progress_bar: Visualize how many of the tasks are completed
        """
        if callable(n_workers):
            raise SyntaxError(
                f"{self.__class__.__name__} received an unexpected value."
                f"\n@autothread.{self.__class__.__name__}() <- Did you forget the ()?"
                f"\n{' '*(len(self.__class__.__name__)+12)}~~"
            )

        self.n_workers = self._get_workers(n_workers, mb_mem, workers_per_core)
        self.process_bar = progress_bar

    def __call__(self, function: Callable):
        decorator = _Autothread(
            function=function,
            Process=self.Process,
            Queue=self.Queue,
            Semaphore=self.Semaphore,
            n_workers=self.n_workers,
            progress_bar=self.process_bar,
        )

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return decorator(*args, **kwargs)

        wrapper.__doc__ = decorator.__doc__
        wrapper.__signature__ = decorator.__signature__

        return wrapper

    def _get_workers(self, *args):
        """Determined the number of workers to use based on the users inputs

        :param n_workers: Total number of workers to run in parallel (0 for unlimited,
        (default) None for the amount of cores).
        :param mb_mem: Minimum megabytes of memory for each worker.
        :workers_per_core: Number of workers to run per core.
        """
        if sum(not arg is None for arg in args) > 1:
            raise ValueError(
                "Please only define one of 'n_workers', 'mb_mem', 'or workers_per_core'"
            )
        n_workers, mb_mem, workers_per_core = args
        if mb_mem:
            return int(psutil.virtual_memory().total / 1024**2 // mb_mem)
        elif workers_per_core:
            return int(workers_per_core * mp.cpu_count())
        elif n_workers is None:
            return mp.cpu_count()
        else:
            return n_workers


class multiprocessed(multithreaded):
    """Decorator to make any function multiprocessed

    This decorator will allow any function to receive a list where it would initially
    receive single items. The function will be repeated for every item in that list in
    parallel and the results will be concatenated into a list and returned back.

    Example:
    ```
    import autothread
    import time
    from time import sleep as heavyworkload

    @autothread.multiprocessed() # <-- This is all you need to add
    def example(x: int, y: int):
        heavyworkload(1)
        return x*y

    result = example([1, 2, 3], 5)
    print(result)
    ```
    """

    Process = mp.Process
    Queue = mp.Queue
    Semaphore = mp.Semaphore


class async_threaded(multithreaded):
    """Decorator to make any function multithreaded in a non-blocking way

    When this decorator is added to a function, the function returns a placeholder of
    its original return value. This placeholder is very similar to a concurrent.Future,
    but does not require the async framework to be used.

    Example:
    ```
    import autothread
    import time
    from time import sleep as heavyworkload

    @autothread.async_threaded() # <-- This is all you need to add
    def example(x, y) -> int:
        heavyworkload(1)
        return x*y

    results = []
    for i in range(10):
        results.append(example(i, 1)) <-- Here, the thread is started and a placeholder is returned

    print(results) <-- this operation will be blocked untill all the threads are done
    ```
    """

    Process = threading.Thread
    Queue = queue.Queue
    Semaphore = threading.Semaphore

    def __init__(
        self,
        n_workers: int = None,
        mb_mem: int = None,
        workers_per_core: int = None,
    ):
        """Initialize the autothread decorator

        :param n_workers: Total number of workers to run in parallel (0 for unlimited,
        (default) None for the amount of cores).
        :param mb_mem: Minimum megabytes of memory for each worker.
        :param workers_per_core: Number of workers to run per core.
        """

        super().__init__(n_workers, mb_mem, workers_per_core)
        self.semaphore = self.Semaphore(
            self.n_workers if self.n_workers > 0 else int(1e9)
        )

    def __call__(self, function):
        return_type = inspect.signature(function).return_annotation
        if return_type == inspect._empty:
            warnings.warn(
                "The designed return type of this function could not be verified, which"
                " will result in a placeholder that does not act identially to the"
                " return value. Please add a return type type-hint to your function"
            )
            return_type = None

        class Placeholder(_Placeholder):
            ___semaphore___ = self.semaphore
            ___Queue___ = self.Queue
            ___Process___ = self.Process
            if not return_type is None:
                __type__ = return_type
                __name__ = return_type.__name__
                __qualname__ = return_type.__qualname__
                __metaclass__ = return_type

        overrides = (
            "__delattr__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__gt__",
            "__hash__",
            "__init_subclass__",
            "__le__",
            "__lt__",
            "__module__",
            "__ne__",
            "__reduce__",
            "__reduce_ex__",
            "__sizeof__",
            "__subclasshook__",
            "__weakref__",
        )

        if not return_type is None:
            for attr in dir(return_type):
                if (
                    attr.startswith("__")
                    and attr.endswith("__")
                    and (not hasattr(Placeholder, attr) or attr in overrides)
                ):
                    setattr(Placeholder, attr, Placeholder.___forwarder___(attr))

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return Placeholder(function, *args, **kwargs)

        return wrapper


class async_processed(async_threaded):
    """Decorator to make any function multitprocessed in a non-blocking way

    When this decorator is added to a function, the function returns a placeholder of
    its original return value. This placeholder is very similar to a concurrent.Future,
    but does not require the async framework to be used.

    Example:
    ```
    import autothread
    import time
    from time import sleep as heavyworkload

    @autothread.async_processed() # <-- This is all you need to add
    def example(x, y) -> int:
        heavyworkload(1)
        return x*y

    results = []
    for i in range(10):
        results.append(example(i, 1)) <-- Here, the thread is started and a placeholder is returned

    print(results) <-- this operation will be blocked untill all the processes are done
    ```
    """

    Process = mp.Process
    Queue = mp.Queue
    Semaphore = mp.Semaphore
