from . import Redirect, STDERR_BIT, STDERR, STDOUT, STDOUT_BIT
from io import BytesIO, StringIO
from os import write
from nose.tools import eq_
from unittest import TestCase

_BOTH = STDOUT_BIT | STDERR_BIT


class _Test:
    def _test(self, exec, fdbits, expected, nmems):
        expected, sep = map(self.adapt, (expected, r' '))
        mems = tuple(self.memio() for _ in range(nmems))
        with Redirect(fdbits, *mems) as r:
            if r.child:
                exec()
        actual = sep.join(y.getvalue() for y in mems)
        eq_(expected, actual)

    def test00(self):
        self._test(w1, STDOUT_BIT, r'', 0)

    def test01(self):
        self._test(w1, STDOUT_BIT, r'1', 1)

    def test02(self):
        self._test(w1, STDOUT_BIT, r'1 ', 2)

    def test03(self):
        self._test(w1, STDOUT_BIT, r'1  ', 3)

    def test10(self):
        self._test(w2, STDERR_BIT, r'', 0)

    def test11(self):
        self._test(w2, STDERR_BIT, r'2', 1)

    def test12(self):
        self._test(w2, STDERR_BIT, r'2 ', 2)

    def test13(self):
        self._test(w2, STDERR_BIT, r'2  ', 3)

    def test20(self):
        self._test(w1w2, _BOTH, r'', 0)

    def test21(self):
        self._test(w1w2, _BOTH, r'1', 1)

    def test22(self):
        self._test(w1w2, _BOTH, r'1 2', 2)

    def test23(self):
        self._test(w1w2, _BOTH, r'1 2 ', 3)


class T0bin(_Test, TestCase):
    memio = BytesIO

    @staticmethod
    def adapt(s):
        return s.encode(r'UTF-8')


class T1str(_Test, TestCase):
    memio = StringIO

    @staticmethod
    def adapt(s):
        return s


def w1():
    write(STDOUT, br'1')


def w2():
    write(STDERR, br'2')


def w1w2():
    w1()
    w2()
