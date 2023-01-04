import multiprocess as mp
import queue
import threading

from typing import Callable, Union


def _queuer(
    queue: Union[queue.Queue, mp.Queue],
    function: Callable,
    semaphore: Union[threading.Semaphore, mp.Semaphore],
    index: int,
    sem_pre_acquired: bool,
    *args,
    **kwargs,
):
    """Function wrapper to put the outputs in the queue

    The queuer is kept outside of the _Autothread class such that multiprocess doesn't
    have to pickle/dill the entire class.
    :param queue: Queue object to return values to
    :param function: function to forward *args and **kwrags to
    :param semaphore: Semaphore object (to limit the number of concurrent workers)
    :param index: Index to track when this thread was started
    :param sem_pre_acquired: True if semaphore already is acquired for this process
    """
    if not sem_pre_acquired:
        semaphore.acquire()
    try:
        output = function(*args, **kwargs)
    except KeyboardInterrupt:
        return
    except Exception as e:
        e.autothread_intercepted = True
        output = e
    semaphore.release()
    queue.put({index: output})
