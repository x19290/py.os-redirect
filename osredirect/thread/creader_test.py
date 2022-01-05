from .zztest import (
    ConcurrentReader, ThreadTuple,
    BytesIO, StringIO,
    close, pipe, write,
    eq_,
    Thread,
    TestCase,
)


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
