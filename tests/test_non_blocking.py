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

import datetime
import os
import time
import unittest

from autothread import async_threaded, async_processed
from mock import patch, Mock

if os.environ["AUTOTHREAD_UNITTEST_MODE"] == "threading":
    testfunc = async_threaded
    print("RUNNING TESTS USING MULTITHREADING")
else:
    testfunc = async_processed
    print("RUNNING TESTS USING MULTIPROCESSING")


@testfunc(n_workers=-1)
def basic(x: int, y: int) -> int:
    """doctstring"""
    time.sleep(0.5)
    return x * y


class TestAsyncBasic(unittest.TestCase):
    @testfunc(n_workers=-1)
    def basic(self, x: int, y: int) -> int:
        """doctstring"""
        time.sleep(0.5)
        return x * y

    def test_case1(self):
        for method in (basic, self.basic):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            self.assertEqual(results, [5, 10, 15, 20])
            self.assertTrue(isinstance(results[0], int))
            duration = time.time() - start
            self.assertLess(duration, 2)

    def test_case2(self):
        for method in (basic, self.basic):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, i + 1))

            self.assertEqual(results, [1, 4, 9, 16])
            self.assertTrue(isinstance(results[0], int))
            duration = time.time() - start
            self.assertLess(duration, 2)

    def test_case3(self):
        for method in (basic, self.basic):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(1, i + 1))

            self.assertEqual(results, [1, 2, 3, 4])
            self.assertTrue(isinstance(results[0], int))
            duration = time.time() - start
            self.assertLess(duration, 2)
            self.assertEqual(str(results[0]), "1")
            self.assertEqual(results[1].__repr__(), "2")


@testfunc(n_workers=-1)
def basicstr(x: int, y: int) -> str:
    """doctstring"""
    time.sleep(0.5)
    return str(x * y)


class TestAsyncStr(unittest.TestCase):
    @testfunc(n_workers=-1)
    def basicstr(self, x: int, y: int) -> str:
        """doctstring"""
        time.sleep(0.5)
        return str(x * y)

    def test_case1(self):
        for method in (basicstr, self.basicstr):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            self.assertEqual(results, ["5", "10", "15", "20"])
            self.assertTrue(isinstance(results[0], str))
            duration = time.time() - start
            self.assertLess(duration, 2)

    def test_case2(self):
        for method in (basicstr, self.basicstr):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            self.assertEqual(
                [result.split() for result in results], [["5"], ["10"], ["15"], ["20"]]
            )
            self.assertTrue(isinstance(results[0], str))
            duration = time.time() - start
            self.assertLess(duration, 2)


class A:
    def __init__(self, value):
        self.value = value


@testfunc(n_workers=-1)
def basicA(x: int, y: int) -> A:
    """doctstring"""
    time.sleep(0.5)
    return A(x * y)


class TestCustomClass(unittest.TestCase):
    @testfunc(n_workers=-1)
    def basicA(self, x: int, y: int) -> A:
        """doctstring"""
        time.sleep(0.5)
        return A(x * y)

    def test_case1(self):
        for method in (basicA, self.basicA):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            self.assertEqual(results[0].value, 5)
            self.assertTrue(isinstance(results[0], A))
            duration = time.time() - start
            self.assertLess(duration, 2)

    def test_setattr(self):
        for method in (basicA, self.basicA):
            start = time.time()
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            results[0].b = 15
            self.assertEqual(results[0].value, 5)
            self.assertEqual(results[0].b, 15)
            self.assertTrue(isinstance(results[0], A))
            duration = time.time() - start
            self.assertLess(duration, 2)


@testfunc(n_workers=-1)
def error(x: int, y: int) -> int:
    """doctstring"""
    time.sleep(0.5)
    raise TypeError()
    return x * y


class TestAsyncError(unittest.TestCase):
    @testfunc(n_workers=-1)
    def error(self, x: int, y: int) -> int:
        """doctstring"""
        time.sleep(0.5)
        raise TypeError()
        return x * y

    def test_case1(self):
        for method in (error, self.error):
            results = []
            for i in range(4):
                results.append(method(i + 1, 5))

            for result in results:
                with self.assertRaises(TypeError):
                    result += 1

    @testfunc(n_workers=-1, ignore_errors=True)
    def error_ignored(self, x: int, y: int) -> int:
        """doctstring"""
        time.sleep(0.5)
        if x == 2:
            raise TypeError()
        return x * y

    def test_case2(self):
        results = []
        for i in range(4):
            results.append(self.error_ignored(i + 1, 5))

        self.assertEqual(results, [5, None, 15, 20])


class TestBool(unittest.TestCase):
    @testfunc(n_workers=-1)
    def booltest(self, x: int, y: int) -> bool:
        """doctstring"""
        time.sleep(0.5)
        return x == y

    def test_case1(self):
        start = time.time()
        results = []
        for i in range(4):
            results.append(self.booltest(i, 2))

        self.assertTrue(results[2])
        self.assertFalse(results[0])
        duration = time.time() - start
        self.assertLess(duration, 2)


class TestObject(unittest.TestCase):
    @testfunc(n_workers=-1)
    def datetimetest(self) -> datetime.datetime:
        """doctstring"""
        output = datetime.datetime.now()
        time.sleep(0.5)
        return output

    def test_case1(self):
        results = []
        for _ in range(4):
            results.append(self.datetimetest())

        time.sleep(5)
        for result in results:
            self.assertTrue(result < datetime.datetime.now())
