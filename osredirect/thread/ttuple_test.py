from .zz import (
    ThreadTuple, Thread,
    close, pipe, read, write,
    eq_, TestCase,
)

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
