from . import ConcurrentReader, ThreadTuple
from io import BytesIO, StringIO
from os import close, pipe, read, write
from nose.tools import eq_
from threading import Thread
from unittest import TestCase


class T0ThreadTuple(TestCase):
    def test0(self):
        r, w = pipe()
        actual = []
        feed = br'abcd'
        expected = list(feed)

        class ProdCons(ThreadTuple):
            @staticmethod
            def contents():
                def prod():
                    for y in feed:
                        write(w, br'%c' % y)
                    close(w)

                def cons():
                    while True:
                        c = read(r, 1)
                        if not c:
                            break
                        actual.append(ord(c))

                yield from (Thread(target=y) for y in (prod, cons))

        ProdCons().join()
        eq_(expected, actual)


class _1:
    @classmethod
    def setUpClass(cls):
        io = cls.io
        cls.a, cls.b = io(), io()

    def test0(self):
        times = 32
        ar, aw = pipe()
        br, bw = pipe()
        ab = self.ab
        getbytes = self.getbytes

        class Writers(ThreadTuple):
            @staticmethod
            def contents():
                def writeloop(ofd, c):
                    for _ in range(times):
                        write(ofd, getbytes(c))
                    close(ofd)

                for ofd, c in zip((aw, bw), ab):
                    yield Thread(target=writeloop, args=(ofd, c))

        a, b = self.a, self.b
        writers = Writers()
        readers = ConcurrentReader((ar, br), (a, b))
        writers.join()
        readers.join()

        expected = ab[0:1] * times, ab[1:2] * times
        actual = a.getvalue(), b.getvalue()
        eq_(expected, actual)


class T1ConcurrentReader0bytes(_1, TestCase):
    io = BytesIO
    ab = br'ab'

    @staticmethod
    def getbytes(b):
        return bytes((b,))


class T1ConcurrentReader1str(_1, TestCase):
    io = StringIO
    ab = r'ab'

    @staticmethod
    def getbytes(s):
        return s.encode(r'UTF-8')
