from . import redirect, STDERR_BIT, STDERR, STDOUT, STDOUT_BIT
from io import BytesIO, StringIO
from os import write
from nose.tools import eq_
from unittest import TestCase

_BOTH = STDOUT_BIT | STDERR_BIT


class _Test:
    def _test(self, exec, fdbits, expected, *mems):
        expected, sep = map(self.adapt, (expected, r' '))
        redirect(exec, fdbits, *mems)
        actual = sep.join(y.getvalue() for y in mems)
        eq_(expected, actual)

    def test00(self):
        self._test(w1, STDOUT_BIT, r'')

    def test01(self):
        self._test(w1, STDOUT_BIT, r'1', self.memio())

    def test02(self):
        memio = self.memio
        self._test(w1, STDOUT_BIT, r'1 ', memio(), memio())

    def test03(self):
        memio = self.memio
        self._test(w1, STDOUT_BIT, r'1  ', memio(), memio(), memio())

    def test10(self):
        self._test(w2, STDERR_BIT, r'')

    def test11(self):
        self._test(w2, STDERR_BIT, r'2', self.memio())

    def test12(self):
        memio = self.memio
        self._test(w2, STDERR_BIT, r'2 ', memio(), memio())

    def test13(self):
        memio = self.memio
        self._test(w2, STDERR_BIT, r'2  ', memio(), memio(), memio())

    def test20(self):
        self._test(w1w2, _BOTH, r'')

    def test21(self):
        self._test(w1w2, _BOTH, r'1', self.memio())

    def test22(self):
        memio = self.memio
        self._test(w1w2, _BOTH, r'1 2', memio(), memio())

    def test23(self):
        memio = self.memio
        self._test(w1w2, _BOTH, r'1 2 ', memio(), memio(), memio())


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
