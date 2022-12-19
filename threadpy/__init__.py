# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# threadpy comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.

import inspect
import multiprocessing as mp
import psutil
import queue
import threading
import typeguard
import warnings

from typing import List, Union, Optional, Tuple, Dict


def _checks_type(value, type_hint):
    """Check if a value corresponds to a type hint

    :param value: Value to check type hint for
    :param type_hint: Type hint to validate
    """
    try:
        typeguard.check_type("foo", value, type_hint)
        return True
    except TypeError:
        return False


_random_string = "54c1cfbf-32d4-4f2c-bff8-e70d2481dfca"


def _queuer(queue, function, index, *args, **kwargs):
    """Function wrapper to put the outputs in the queue"""
    try:
        output = function(*args, **kwargs)
    except Exception as e:
        # return unlikely object containing the error in case the function itself
        # returns an error
        output = {_random_string: e}
    queue.put({index: output})


_is_listy = lambda x: isinstance(x, list) or isinstance(x, tuple)


class _Multiprocessed:
    """Decorator class that transforms a function into a multi processed
    function simply by adding a single decorator."""

    def __init__(self, function, Process, Queue, n_workers):
        """Initialize the decorator

        :param function: function to decorate
        """
        self._Process = Process
        self._Queue = Queue
        self._function = function
        self.n_workers = n_workers
        self._params = inspect.signature(self._function).parameters

    @property
    def __signature__(self):
        """Updates the __doc__ and __signature__ to match the received function"""
        signature = inspect.signature(self._function)
        new_params = []
        for k in self._params:
            param = self._params[k]
            if param.__str__().startswith("*"):
                if not param.__str__().startswith("**"):
                    new_params.append(param)
                continue
            new_params.append(
                inspect.Parameter(
                    name=k,
                    kind=param.kind,
                    default=param.default,
                    annotation=Union[List[param.annotation], param.annotation],
                )
            )
        new_params.append(
            inspect.Parameter(
                name="_loop_params",
                kind=inspect._ParameterKind(3),
                default=None,
                annotation=Optional[List[str]],
            )
        )
        for k in self._params:
            if self._params[k].__str__().startswith("**"):
                new_params.append(self._params[k])

        return signature.replace(parameters=new_params)

    @property
    def __doc__(self):
        if self._function.__doc__:
            return self._function.__doc__ + (
                "\n This function is automatically parallelized using threadpy. Any of this"
                " function's arguments can be substituted with a list and this function "
                "will be repeated for each item in that list."
            )

    def __call__(self, *args, **kwargs):
        """Call the function

        :param args: Arguments to forward to the function
        :param kwargs: Keyword argumented to forward
        """
        self._queue = self._Queue(maxsize=self.n_workers)
        self._processes = []
        loop_params = kwargs.pop("_loop_params", None)
        self._merge_args(args, kwargs)
        self._loop_params = self._get_loop_params(loop_params)
        self._verify_loop_params(self._loop_params)

        if not self._loop_params:  # just run the function as normal
            return self._function(*args, **kwargs)

        n_threads = self._arg_lengths[self._loop_params[0]]
        for i in range(n_threads):
            args = [self._queue, self._function, i]
            for k, v in self._kwargs.items():
                value = v["value"][i] if k in self._loop_params else v["value"]
                if v["is_kwarg"]:
                    self._extra_kwargs[k] = value
                else:
                    args.append(value)
            args.extend(self._extra_args)
            if n_threads == 1:
                return self._function(*args[3:], **self._extra_kwargs)
            p = self._Process(target=_queuer, args=args, kwargs=self._extra_kwargs)
            p.start()
            self._processes.append(p)

        return self._collect_results()

    def _merge_args(self, args: Tuple, kwargs: Dict):
        """Merge args into kwargs

        Since we know the keyword names, it it easier to keep track of only the kwargs
        by merging the args into it. The *arg and **kwargs present in the original
        function cannot be captured here, we leave those in self._extra_(kw)args.

        :param args: List of arguments
        :param kwargs: Dict of keyword arguments
        """
        self._arg_names = list(self._params.keys())
        self._kwargs = {}
        self._extra_args = []
        self._extra_kwargs = {}
        for i, v in enumerate(args):
            if self._params[self._arg_names[i]].__str__().startswith("*"):
                self._extra_args = args[i:]
                break
            self._kwargs[self._arg_names[i]] = {"value": v, "is_kwarg": False}
        for k, v in kwargs.items():
            if not k in self._params:
                self._extra_kwargs[k] = v
            else:
                self._kwargs[k] = {"value": v, "is_kwarg": True}

        self._arg_lengths = {}
        for i, (k, v) in enumerate(self._kwargs.items()):
            length = len(v["value"]) if _is_listy(v["value"]) else None
            self._arg_lengths[k] = length

    def _get_loop_params(self, loop_params: Optional[List[str]]):
        """Determine which arguments will be split into the different threads

        If '_loop_params' is not defined, we will determine which parameters should be
        split into the threads by checking the values against their type hints. If a
        list is provided whose contents match the original type hint, we will assume
        that this parameter needs to be split into the separate threads.

        :param loop_params: Override list of loop_parameters provided by user
        """
        if loop_params:
            if not _is_listy(loop_params):
                loop_params = [loop_params]
            return loop_params

        _type_warning = (
            "Type hint for {k} could not be verified. Even though it is a list, it will"
            " not be used for parallelization. It is possible that the type hints of "
            "this function are incorrect. If correct, use the `_loop_params` keyword "
            "argument to specify the parameters to parallelize for."
        )
        loop_params = []
        for k, v in self._kwargs.items():
            if not k in self._params and _is_listy(v["value"]):
                warnings.warn(_type_warning.format(k=k))
                continue
            type_hint = self._params[k].annotation
            if _checks_type(v["value"], type_hint):
                continue
            elif _is_listy(v["value"]) and all(
                _checks_type(_v, type_hint) for _v in v["value"]
            ):
                loop_params.append(k)
            elif _is_listy(v["value"]):
                warnings.warn(_type_warning.format(k=k))
            # else: Type hint is incorrect but not list-y, we will just ignore it
        for k, v in self._extra_kwargs.items():
            if _is_listy(v):
                warnings.warn(_type_warning.format(k=k))
        return loop_params

    def _verify_loop_params(self, loop_params: List[str]):
        """Make sure that the loop params are valid

        The loop parameters are valid if:
        1) They are all provided by the user
        2) They are all of the same length

        :param loop_params: List of loop_parameters provided by _get_loop_params
        """
        for param in loop_params:
            if not param in self._kwargs:
                raise ValueError(
                    f"'{param}' is specified as loop parameter but does not "
                    " exist for this function or is not provided. Choose one "
                    f"of {list(self._kwargs)}"
                )
        if any(
            self._arg_lengths[param] != self._arg_lengths[loop_params[0]]
            for param in loop_params
        ):
            raise IndexError(
                f"Input for parallelization is ambiguous. {loop_params} are "
                "all lists but are of different lengths. It is possible that the type "
                "hints of this function are incorrect. If they are not, use the "
                "`_loop_params` keyword argument to specify the parameters to "
                "parallelize for."
            )
        return loop_params

    def _collect_results(self):
        """Collect the results from the queue and raise possible errors

        The queue does not return items in order if the processing times are different
        for different parameters. The queue will return (N, output) where N is its
        original place in the queue that must be sorted.
        """
        result = {}
        for process in self._processes:
            process.join()
            result.update(self._queue.get())
        result = [v[1] for v in sorted(result.items())]
        for res in result:
            if isinstance(res, dict) and isinstance(res.get(_random_string), Exception):
                raise res[_random_string]
        return result


def _get_workers(*args):
    """Determined the number of workers to use based on the users inputs

    :param n_workers: Total number of workers to run in parallel (0 for unlimited,
    (default) None for the amount of cores).
    :param mb_mem: Minimum megabytes of memory for each worker.
    :workers_per_core: Number of workers to run per core.
    """
    if sum(not arg is None for arg in args) > 1:
        raise ValueError(
            "Please only define either 'n_workers', 'mb_mem', 'or workers_per_core'."
        )
    mb_mem, n_workers, workers_per_core = args
    if mb_mem:
        return int(psutil.virtual_memory().total / 1024**2 // mb_mem)
    elif workers_per_core:
        return int(workers_per_core * mp.cpu_count())
    elif n_workers is None:
        return mp.cpu_count()
    elif n_workers == -1:
        return 0
    else:
        return n_workers


def multiprocessed(
    n_workers: int = None, mb_mem: int = None, workers_per_core: float = None
):
    """Decorator to make any function multiprocessed

    This decorator will allow any function to receive a list where it would initially
    receive single items. The function will be repeated for every item in that list in
    parallel and the results will be concatenated into a list and returned back.

    :param n_workers: Total number of workers to run in parallel (0 for unlimited,
    (default) None for the amount of cores).
    :param mb_mem: Minimum megabytes of memory for each worker.
    :workers_per_core: Number of workers to run per core.
    """

    def _decorator(function):
        decorator = _Multiprocessed(
            function,
            mp.Process,
            mp.Queue,
            _get_workers(n_workers, mb_mem, workers_per_core),
        )

        def wrapper(*args, **kwargs):
            return decorator(*args, **kwargs)

        wrapper.__doc__ = decorator.__doc__
        wrapper.__signature__ = decorator.__signature__

        return wrapper

    return _decorator


def multithreaded(
    n_workers: int = None, mb_mem: int = None, workers_per_core: int = None
):
    """Decorator to make any function multithreaded

    This decorator will allow any function to receive a list where it would initially
    receive single items. The function will be repeated for every item in that list in
    parallel and the results will be concatenated into a list and returned back.

    :param n_workers: Total number of workers to run in parallel (0 for unlimited,
    (default) None for the amount of cores).
    :param mb_mem: Minimum megabytes of memory for each worker.
    :workers_per_core: Number of workers to run per core.
    """

    def _decorator(function):
        decorator = _Multiprocessed(
            function,
            threading.Thread,
            queue.Queue,
            _get_workers(n_workers, mb_mem, workers_per_core),
        )

        def wrapper(*args, **kwargs):
            return decorator(*args, **kwargs)

        wrapper.__doc__ = decorator.__doc__
        wrapper.__signature__ = decorator.__signature__
        return wrapper

    return _decorator
