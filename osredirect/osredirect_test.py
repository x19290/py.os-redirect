from . import redirect, STDERR_BIT, STDERR, STDOUT, STDOUT_BIT
from io import BytesIO, StringIO
from os import write
from nose.tools import eq_
from unittest import TestCase

_BOTH = STDOUT_BIT | STDERR_BIT


class _Test:
    def _test(self, n):
        expected, isep, osep = map(self.adapt, (self.expected, r',', r' '))
        expected = expected.split(isep)[n]
        mems = tuple(self.memio() for _ in range(n))
        with redirect(self.fdbits, *mems) as iswriter:
            if iswriter:
                self.exec()
        actual = osep.join(y.getvalue() for y in mems)
        eq_(expected, actual)

    def test0(self):
        self._test(0)

    def test1(self):
        self._test(1)

    def test2(self):
        self._test(2)

    def test3(self):
        self._test(3)


class _0bin(_Test):
    memio = BytesIO

    @staticmethod
    def adapt(s):
        return s.encode(r'UTF-8')


class _1str(_Test):
    memio = StringIO

    @staticmethod
    def adapt(s):
        return s


class _0w1:
    expected = r',1,1 ,1  '
    fdbits = STDOUT_BIT

    @classmethod
    def exec(cls):
        write(STDOUT, br'1')


class _1w2:
    expected = r',2,2 ,2  '
    fdbits = STDERR_BIT

    @classmethod
    def exec(cls):
        write(STDERR, br'2')


class _2w1w2:
    expected = r',1,1 2,1 2 '
    fdbits = STDOUT_BIT | STDERR_BIT

    @classmethod
    def exec(cls):
        write(STDOUT, br'1')
        write(STDERR, br'2')


class T0bin0w1(_0bin, _0w1, TestCase):
    pass


class T0bin1w2(_0bin, _1w2, TestCase):
    pass


class T0bin2w1w2(_0bin, _2w1w2, TestCase):
    pass


class T1str0w1(_1str, _0w1, TestCase):
    pass


class T1str1w2(_1str, _1w2, TestCase):
    pass


class T1str2w1w2(_1str, _2w1w2, TestCase):
    pass
