from .nullio import NULL_BIN, NULL_STR
from io import UnsupportedOperation
from nose.tools import eq_, raises
from unittest import TestCase


class _Test:
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


class T0bin(_Test, TestCase):
    null = NULL_BIN
    compatible, incompatible = br'', r''


class T1str(_Test, TestCase):
    null = NULL_STR
    compatible, incompatible = r'', br''
