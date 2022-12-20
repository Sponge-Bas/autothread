import time
import typing
import unittest

from autothread import multiprocessed, multithreaded
from mock import patch


@multithreaded()
def basic(x: int, y: int):
    """doctstring"""
    time.sleep(0.05)
    return x * y


class TestThreadypyBasic(unittest.TestCase):
    @multithreaded()
    def basic(self, x: int, y: int):
        """doctstring"""
        time.sleep(0.05)
        return x * y

    def test_basic_case1(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method([1, 2, 3, 4], 5)
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [5, 10, 15, 20])

    def test_basic_case2(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method([1, 2, 3, 4], [1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [1, 4, 9, 16])

    def test_basic_case3(self):
        for method in (basic, self.basic):
            start = time.time()
            result = method(1, [1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [1, 2, 3, 4])


@multithreaded()
def basic2(x: int, y: int = 6):
    """doctstring"""
    time.sleep(0.05)
    return x * y


class TestThreadypyKeyword(unittest.TestCase):
    def test_basic_case1(self):
        start = time.time()
        result = basic2([1, 2, 3, 4], 5)
        duration = time.time() - start

        self.assertTrue(duration < 0.1)
        self.assertEqual(result, [5, 10, 15, 20])

    def test_basic_case2(self):
        start = time.time()
        result = basic2([1, 2, 3, 4], y=[1, 2, 3, 4])
        duration = time.time() - start

        self.assertTrue(duration < 0.1)
        self.assertEqual(result, [1, 4, 9, 16])

    def test_basic_case3(self):
        start = time.time()
        result = basic2(1, [1, 2, 3, 4])
        duration = time.time() - start

        self.assertTrue(duration < 0.1)
        self.assertEqual(result, [1, 2, 3, 4])


@multithreaded()
def basic3(x: int = 4, y: int = 6):
    """doctstring"""
    time.sleep(0.05)
    return x, y, x * y


class TestThreadypyMixedKeyword(unittest.TestCase):
    @multithreaded()
    def basic3(self, x: int = 4, y: int = 6):
        """doctstring"""
        time.sleep(0.05)
        return x, y, x * y

    def test_basic_case1(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(y=[1, 2, 3, 4], x=5)
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [(5, 1, 5), (5, 2, 10), (5, 3, 15), (5, 4, 20)])

    def test_basic_case2(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(x=[2, 2, 3, 4], y=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [(2, 1, 2), (2, 2, 4), (3, 3, 9), (4, 4, 16)])

    def test_basic_case3(self):
        for method in (basic3, self.basic3):
            start = time.time()
            result = method(y=1, x=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [(1, 1, 1), (2, 1, 2), (3, 1, 3), (4, 1, 4)])


@multithreaded()
def extra_args_kwargs(x: int, *args, y: int = 6, **kwags):
    """doctstring"""
    time.sleep(0.05)
    return x, y, x * y


class TestThreadypyExtraArgs(unittest.TestCase):
    @multithreaded()
    def extra_args_kwargs(self, x: int, *args, y: int = 6, **kwags):
        """doctstring"""
        time.sleep(0.05)
        return x, y, x * y

    def test_basic_case1(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method(5, 1e17, z=45, y=[1, 2, 3, 4])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [(5, 1, 5), (5, 2, 10), (5, 3, 15), (5, 4, 20)])

    def test_basic_case2(self):
        for method in (extra_args_kwargs, self.extra_args_kwargs):
            start = time.time()
            result = method([2, 2, 3, 4], [3, 3, 4, 2])
            duration = time.time() - start

            self.assertTrue(duration < 0.1)
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

            self.assertTrue(duration < 0.1)
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

            self.assertTrue(duration < 0.1)
            self.assertEqual(result, [(1, 1, 1)])


class TestWarnings(unittest.TestCase):
    @multiprocessed()
    def _warnings(self, x, y: int, **kwargs):
        time.sleep(0.05)
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
    @multiprocessed()
    def _warnings(self, x: int, y: int, **kwargs):
        time.sleep(0.05)
        return x, y, x * y

    def test_length_error(self):
        with self.assertRaises(IndexError):
            self._warnings([1, 3, 4], [2, 2])

    @patch("autothread.warnings.warn")
    def test_length_error2(self, mock_warn):
        result = self._warnings([1, 3], 2, z=[1, 3, 4])
        self.assertEqual(result, [(1, 2, 2), (3, 2, 6)])


class TestNestedList(unittest.TestCase):
    @multiprocessed()
    def _test(self, x: typing.List[int], y: int):
        time.sleep(0.05)
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
