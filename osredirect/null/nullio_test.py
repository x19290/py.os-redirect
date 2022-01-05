from .nullio import NULL_BIN, NULL_OUT, NULL_STR
from io import UnsupportedOperation
from nose.tools import eq_, raises
from unittest import TestCase


class T0out(TestCase):
    @raises(AttributeError)
    def test0read(self):
        NULL_OUT.read

    def test1close(self):
        expected = None
        actual = NULL_OUT.close(0, 1, 2, 3, 4)
        eq_(expected, actual)

    def test1flush(self):
        expected = None
        actual = NULL_OUT.flush(0, 1, 2, 3, 4)
        eq_(expected, actual)

    def test1write(self):
        expected = None
        actual = NULL_OUT.write(0, 1, 2, 3, 4)
        eq_(expected, actual)


class _1typed:
    @raises(AttributeError)
    def test0xyz(self):
        self.null.xyz

    @raises(AttributeError)
    def test1checkClosed(self):
        self.null._checkClosed

    @raises(UnsupportedOperation)
    def test2fileno(self):
        self.null.fileno

    @raises(TypeError)
    def test3write0incompatible(self):
        self.null.write(self.incompatible)

    def test3write1compatible(self):
        expected = None
        actual = self.null.write(self.compatible)
        eq_(expected, actual)


class T1typed0bin(_1typed, TestCase):
    null = NULL_BIN
    compatible, incompatible = br'', r''


class T1typed1str(_1typed, TestCase):
    null = NULL_STR
    compatible, incompatible = r'', br''
