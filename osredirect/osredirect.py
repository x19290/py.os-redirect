from contextlib import contextmanager

STDOUT_BIT, STDERR_BIT = 1, 2
STDOUT, STDERR = 1, 2


@contextmanager
def redirect(fdbits: int, *oobjs):
    try:
        r = Redirect(fdbits, *oobjs).__enter__()
        yield r.iswriter
    finally:
        r.__exit__()


class Redirect(dict):
    def __init__(self, fdbits: int, *oobjs):
        from os import pipe

        def fds():
            bit = 1
            for _ in range(2):
                if fdbits & bit:
                    yield bit
                bit <<= 1

        fds = tuple(fds())
        oobjs += (NULL_OUT,) * (fds.__len__() - oobjs.__len__())
        self.oobjs = oobjs
        super().__init__({y: pipe() for y in fds})
 
    def __exit__(self, *_, **__):
        from .thread import ConcurrentReader
        from os import close, wait, _exit

        if self.iswriter:
            _exit(0)

        def fds():
            for r, w in self.values():
                yield r
                close(w)

        ConcurrentReader(fds(), self.oobjs).join()
        wait()

    def __enter__(self):
        from os import close, dup2, fork

        self.iswriter = iswriter = fork() == 0
        if iswriter:
            for y, (r, w) in self.items():
                dup2(w, y)
                close(w)
                close(r)
        return self


class _NullOut:
    @staticmethod
    def close():
        pass
    @staticmethod
    def write(data):
        return data.__len__()


NULL_OUT = _NullOut()
