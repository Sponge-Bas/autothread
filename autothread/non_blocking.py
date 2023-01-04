import threading
import queue
import multiprocess as mp

from autothread.common import _queuer
from typing import Union, Type, Callable, Any


class _Placeholder:
    """Base class for a non-blocking decorator that makes any function threaded"""

    ___semaphore___: Union[threading.Semaphore, mp.Semaphore] = None
    ___Queue___: Union[Type[queue.Queue], Type[mp.Queue]] = None
    ___Process___: Union[Type[threading.Thread], Type[mp.Process]] = None

    @classmethod
    def ___forwarder___(cls, attr: str) -> Callable:
        """Returns function to forward dunders to the original type

        Dunders are not processed through __getattribute__, so we need to inspect the
        originional return type and add all the dunders that are present there.
        """

        def forwarder(cls, *args, **kwargs):
            return getattr(cls.___get_response___(), attr)(*args, **kwargs)

        return forwarder

    def __init__(self, function: Callable, *args, **kwargs) -> None:
        """Initialize the placeholder

        :param function: Function to call in thread/process
        :param args: Arguments to forward to function
        :param kwargs: Keyword arguments to forward to function
        """
        self.___response_collected___ = False
        self.___queue___ = self.___Queue___()
        self.___process___ = self.___Process___(
            target=_queuer,
            args=(self.___queue___, function, self.___semaphore___, 0, False, *args),
            kwargs=kwargs,
        )
        self.___process___.start()

    def ___get_response___(self) -> Any:
        """Waits untill the thread is ready and collects its response"""
        if not self.___response_collected___:
            self.___process___.join()
            self.___response___ = list(self.___queue___.get().values())[0]
            self.___response_collected___ = True
            if isinstance(self.___response___, Exception) and getattr(
                self.___response___, "autothread_intercepted", False
            ):
                raise self.___response___
        return self.___response___

    def __getattribute__(self, __name: str) -> Any:
        """Forwards attribute request to function response

        The placeholder itself uses thrunders ("___attr___") as internal attributed. If
        the attribute is not a thrunder, wait for the response and forward it there.
        """
        if __name.startswith("___") and __name.endswith("___"):
            return object.__getattribute__(self, __name)

        return object.__getattribute__(self, "___get_response___")().__getattribute__(
            __name
        )

    def __setattr__(self, __name: str, __value: Any) -> None:
        """Forwards attribute setter to function response"""
        if __name.startswith("___") and __name.endswith("___"):
            return object.__setattr__(self, __name, __value)

        return object.__getattribute__(self, "___get_response___")().__setattr__(
            __name, __value
        )

    def __str__(self) -> str:
        """Forward __str__

        Many classes do not have the string method, in that case we just return the
        object itself
        """
        return getattr(self.___get_response___(), "__str__", self.___get_response___)()

    def __repr__(self) -> str:
        """Forward __repr__"""
        return getattr(self.___get_response___(), "__repr__", self.___get_response___)()

    def __del__(self) -> None:
        getattr(self.___get_response___(), "__del__", self.___get_response___)()
