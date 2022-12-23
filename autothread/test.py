# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# autothread comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.

"""
This file contains all the unittests for autothread. 
To run the unittests, run `tox -e threading,processing,coverage` from the base dir.

When contributing:
- All newly added lines must have unittest coverage
- The existing unittests are guarenteed behavior and cannot be modified to accommodate
  for new changes to autothread.
- All the tests must pass on both windows and linux
"""

import os
import time
import typing
import unittest

from autothread import multiprocessed, multithreaded, _get_workers
from mock import patch, Mock

if os.environ["AUTOTHREAD_UNITTEST_MODE"] == "threaded":
    testfunc = multithreaded
    print("RUNNING TESTS USING MULTITHREADING")
else:
    testfunc = multiprocessed
    print("RUNNING TESTS USING MULTITHPROCESSING")


@testfunc()
def basic(x: int, y: int):
    """doctstring"""
    time.sleep(0.5)
    return x * y


class TestThreadypyBasic(unittest.TestCase):
    @testfunc()
    def basic(self, x: int, y: int):
        """doctstring"""
        time.sleep(0.5)
        return x * y

    def test_basic_case1(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method([1, 2, 3, 4], 5)
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [5, 10, 15, 20])

    def test_basic_case2(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method([1, 2, 3, 4], [1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [1, 4, 9, 16])

    def test_basic_case3(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method(1, [1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [1, 2, 3, 4])


@testfunc()
def basic2(x: int, y: int = 6):
    """doctstring"""
    time.sleep(0.5)
    return x * y


class TestThreadypyKeyword(unittest.TestCase):
    def test_basic_case1(self):
        start = time.time()
        result = basic2([1, 2, 3, 4], 5)
        duration = time.time() - start

        self.assertTrue(duration < 1)
        self.assertEqual(result, [5, 10, 15, 20])

    def test_basic_case2(self):
        start = time.time()
        result = basic2([1, 2, 3, 4], y=[1, 2, 3, 4])
        duration = time.time() - start

        self.assertTrue(duration < 1)
        self.assertEqual(result, [1, 4, 9, 16])

    def test_basic_case3(self):
        start = time.time()
        result = basic2(1, [1, 2, 3, 4])
        duration = time.time() - start

        self.assertTrue(duration < 1)
        self.assertEqual(result, [1, 2, 3, 4])


@testfunc()
def basic3(x: int = 4, y: int = 6):
    """doctstring"""
    time.sleep(0.5)
    return x, y, x * y


class TestThreadypyMixedKeyword(unittest.TestCase):
    @testfunc()
    def basic3(self, x: int = 4, y: int = 6):
        """doctstring"""
        time.sleep(0.5)
        return x, y, x * y

    def test_basic_case1(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(y=[1, 2, 3, 4], x=5)
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(5, 1, 5), (5, 2, 10), (5, 3, 15), (5, 4, 20)])

    def test_basic_case2(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(x=[2, 2, 3, 4], y=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(2, 1, 2), (2, 2, 4), (3, 3, 9), (4, 4, 16)])

    def test_basic_case3(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(y=1, x=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(1, 1, 1), (2, 1, 2), (3, 1, 3), (4, 1, 4)])


@testfunc()
def extra_args_kwargs(x: int, *args, y: int = 6, **kwags):
    """doctstring"""
    time.sleep(0.5)
    return x, y, x * y


class TestThreadypyExtraArgs(unittest.TestCase):
    @testfunc()
    def extra_args_kwargs(self, x: int, *args, y: int = 6, **kwags):
        """doctstring"""
        time.sleep(0.5)
        return x, y, x * y

    def test_basic_case1(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method(5, 1e17, z=45, y=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(5, 1, 5), (5, 2, 10), (5, 3, 15), (5, 4, 20)])

    def test_basic_case2(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method([2, 2, 3, 4], [3, 3, 4, 2])
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(2, 6, 12), (2, 6, 12), (3, 6, 18), (4, 6, 24)])

    def test_basic_case3(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method(
                [1, 2, 3, 4],
                q=455,
                y=1,
            )
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(1, 1, 1), (2, 1, 2), (3, 1, 3), (4, 1, 4)])

    def test_basic_case4(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method(
                [1],
                q=455,
                y=1,
            )
            duration = time.time() - start

            self.assertTrue(duration < 1)
            self.assertEqual(result, [(1, 1, 1)])


class TestWarnings(unittest.TestCase):
    @testfunc()
    def _warnings(self, x, y: int, **kwargs):
        time.sleep(0.5)
        return x, y, x * y

    @patch("autothread.warnings.warn")
    def test_missing_type_hint(self, mock_warn):
        result = self._warnings([1, 3, 4], 2)
        self.assertEqual(result, ([1, 3, 4], 2, [1, 3, 4, 1, 3, 4]))
        mock_warn.assert_called_with(
            "Type hint for x could not be verified. Even though it is a list, it will "
            "not be used for parallelization. It is possible that the type hints of "
            "this function are incorrect. If correct, use the `_loop_params` keyword "
            "argument to specify the parameters to parallelize for."
        )

    @patch("autothread.warnings.warn")
    def test_missing_type_hint2(self, mock_warn):
        result = self._warnings(2, [1, 3, 4])
        self.assertEqual(result, ([(2, 1, 2), (2, 3, 6), (2, 4, 8)]))
        mock_warn.assert_not_called()

    @patch("autothread.warnings.warn")
    def test_missing_type_hint3(self, mock_warn):
        result = self._warnings(1, 2, z=[1, 3, 4])
        self.assertEqual(result, (1, 2, 2))
        mock_warn.assert_called_with(
            "Type hint for z could not be verified. Even though it is a list, it will "
            "not be used for parallelization. It is possible that the type hints of "
            "this function are incorrect. If correct, use the `_loop_params` keyword "
            "argument to specify the parameters to parallelize for."
        )


class TestLengthWarnings(unittest.TestCase):
    @testfunc()
    def _warnings(self, x: int, y: int, **kwargs):
        time.sleep(0.5)
        return x, y, x * y

    def test_length_error(self):
        with self.assertRaises(IndexError):
            self._warnings([1, 3, 4], [2, 2])

    @patch("autothread.warnings.warn")
    def test_length_error2(self, mock_warn):
        result = self._warnings([1, 3], 2, z=[1, 3, 4])
        self.assertEqual(result, [(1, 2, 2), (3, 2, 6)])


class TestNestedList(unittest.TestCase):
    @testfunc()
    def _test(self, x: typing.List[int], y: int):
        time.sleep(0.5)
        return x, y, max(x) * y

    def test_nested_list1(self):
        result = self._test([1, 2, 3, 4], 5)
        self.assertEqual(result, ([1, 2, 3, 4], 5, 20))

    def test_nested_list2(self):
        result = self._test([1, 2], [1, 5])
        self.assertEqual(result, [([1, 2], 1, 2), ([1, 2], 5, 10)])

    def test_nested_list3(self):
        result = self._test([[1, 2], [3, 4]], 5)
        self.assertEqual(result, [([1, 2], 5, 10), ([3, 4], 5, 20)])

    def test_nested_list4(self):
        result = self._test([[1, 2], [3, 4]], [1, 5])
        self.assertEqual(result, [([1, 2], 1, 2), ([3, 4], 5, 20)])


class TestErrors(unittest.TestCase):
    @testfunc(n_workers=-1)
    def _error_mp(self, x: int, y: int):
        if x == 2:
            time.sleep(1)
            raise ValueError()
        time.sleep(5)
        return x, y, x * y

    @testfunc(n_workers=-1)
    def _error_mt(self, x: int, y: int):
        if x == 2:
            time.sleep(1)
            raise ValueError()
        time.sleep(5)
        return x, y, x * y

    def test_raises_error(self):
        with self.assertRaises(ValueError):
            self._error_mp(list(range(20)), 16)

        with self.assertRaises(ValueError):
            self._error_mt(list(range(20)), 16)

    @testfunc(n_workers=-1)
    def _error_mt_catch(self, x: int, y: int):
        try:
            if x == 2:
                time.sleep(1)
                raise ValueError()
            for _ in range(10):
                time.sleep(0.5)
            return x, y, x * y
        except KeyboardInterrupt:
            self.cleanup_script()

    def test_throws_keyboardinterrupt(self):
        self.cleanup_script = Mock()

        with self.assertRaises(ValueError):
            self._error_mt_catch(list(range(20)), 16)

        if testfunc == multithreaded:
            self.assertTrue(self.cleanup_script.call_count == 19)
        ## TODO: verify this for multiprocessed too

    @testfunc(n_workers=2)
    def _error_mt_catch_2_workers(self, x: int, y: int):
        try:
            if x == 2:
                time.sleep(1)
                raise ValueError()
            for _ in range(10):
                time.sleep(0.5)
            return x, y, x * y
        except KeyboardInterrupt:
            self.cleanup_script2()

    def test_doesnt_create_new_threads(self):
        self.cleanup_script2 = Mock()

        with self.assertRaises(ValueError):
            self._error_mt_catch_2_workers(list(range(20)), 16)

        if testfunc == multithreaded:
            self.assertTrue(self.cleanup_script2.call_count == 2)
        ## TODO: verify this for multiprocessed too


class TestLoopParams(unittest.TestCase):
    @testfunc(n_workers=-1)
    def _test(self, x: int, y: int):
        time.sleep(0.5)
        return x, y, x * y

    def test_override_loop_params(self):
        with self.assertRaises(IndexError):
            self._test([10, 12, 5], [2])

        result = self._test([10, 12, 5], [2], _loop_params="y")

        self.assertEqual(result, [([10, 12, 5], 2, [10, 12, 5, 10, 12, 5])])

    def _test_called(self, x, y):
        return x, y, x * y

    @testfunc(n_workers=-1)
    def _test2(self, *args, **kwargs):
        time.sleep(0.5)
        return self._test_called(*args, **kwargs)

    def test_override_loop_params_args(self):
        result = self._test2([10, 12, 5], 2)
        self.assertEqual(result, ([10, 12, 5], 2, [10, 12, 5, 10, 12, 5]))
        with self.assertRaises(ValueError):
            self._test2([10, 12, 5], [2], _loop_params="y")

    @patch("autothread.warnings.warn")
    def test_kwargs(self, mock_warn):
        self._test2(x=[10, 12, 4], y=2)
        mock_warn.assert_called_with(
            "Type hint for x could not be verified. Even though it is a list, it will "
            "not be used for parallelization. It is possible that the type hints of "
            "this function are incorrect. If correct, use the `_loop_params` keyword "
            "argument to specify the parameters to parallelize for."
        )

    def test_kwargs_loop_param(self):
        result = self._test2(x=[10, 12, 4], y=2, _loop_params=["x"])
        self.assertEqual(result, [(10, 2, 20), (12, 2, 24), (4, 2, 8)])


class TestGetWorkers(unittest.TestCase):
    def test_n_workers(self):
        n_workers, mb_mem, workers_per_core = 12, None, None
        n_workers = _get_workers(n_workers, mb_mem, workers_per_core)
        self.assertEqual(n_workers, 12)

    @patch("autothread.psutil.virtual_memory")
    def test_mb_mem(self, mock_mem):
        mock_memory = Mock()
        mock_memory.total = 16000 * 1024**2
        mock_mem.return_value = mock_memory

        n_workers, mb_mem, workers_per_core = None, 1000, None
        n_workers = _get_workers(n_workers, mb_mem, workers_per_core)
        self.assertEqual(n_workers, 16)

    @patch("autothread.mp.cpu_count")
    def test_workers_per_core(self, mock_cpu_count):
        mock_cpu_count.return_value = 8

        n_workers, mb_mem, workers_per_core = None, None, 4
        n_workers = _get_workers(n_workers, mb_mem, workers_per_core)
        self.assertEqual(n_workers, 32)

    @patch("autothread.mp.cpu_count")
    def test_default(self, mock_cpu_count):
        mock_cpu_count.return_value = 8

        n_workers, mb_mem, workers_per_core = None, None, None
        n_workers = _get_workers(n_workers, mb_mem, workers_per_core)
        self.assertEqual(n_workers, 8)

    def test_multiple(self):
        n_workers, mb_mem, workers_per_core = 12, None, 8
        with self.assertRaises(ValueError):
            _get_workers(n_workers, mb_mem, workers_per_core)
