from .iopump import IOPump
from ..thread.zz import (
    ThreadTuple, Thread,
    BytesIO, StringIO,
    close, pipe, write,
    eq_, TestCase,
)


class _Test:
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
            def threads():
                def writeloop(ofd, c):
                    for _ in range(times):
                        write(ofd, getbytes(c))
                    close(ofd)

                for ofd, c in zip((aw, bw), ab):
                    yield Thread(target=writeloop, args=(ofd, c))

        a, b = self.a, self.b
        writers = Writers()
        readers = IOPump((False, ar, a), (False, br, b))
        writers.join()
        readers.join()

        expected = ab[0:1] * times, ab[1:2] * times
        actual = a.getvalue(), b.getvalue()
        eq_(expected, actual)


class T0bytes(_Test, TestCase):
    io = BytesIO
    ab = br'ab'

    @staticmethod
    def getbytes(b):
        return bytes((b,))


class T1str(_Test, TestCase):
    io = StringIO
    ab = r'ab'

    @staticmethod
    def getbytes(s):
        return s.encode(r'UTF-8')
