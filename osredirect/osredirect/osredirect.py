from contextlib import contextmanager

STDOUT_BIT, STDERR_BIT = 1, 2
STDIN, STDOUT, STDERR = range(3)
STDFDS = STDIN, STDOUT, STDERR


@contextmanager
def redirect(fdbits: int, *oobjs, stdin=None):
    try:
        r = Redirect(fdbits, *oobjs, stdin=stdin).__enter__()
        yield r.iswriter
    finally:
        r.__exit__()


class Redirect(dict):
    def __init__(self, fdbits: int, *oobjs, stdin=None):
        from ..null.nullio import NULL_OUT
        from os import pipe

        def fds():
            self.stdin = stdin
            if stdin:
                yield STDIN
            bit = STDOUT_BIT
            for fd in STDOUT, STDERR:
                if fdbits & bit:
                    yield fd
                bit <<= 1

        fds = tuple(fds())
        oobjs += (NULL_OUT,) * (fds.__len__() - oobjs.__len__())
        self.oobjs = oobjs
        super().__init__({y: pipe() for y in fds})

    def __enter__(self):
        from os import close, dup2, fork

        self.iswriter = iswriter = fork() == 0
        if iswriter:
            if self.stdin:
                r0, w0 = self[0]
                # {A
                dup2(r0, 0)
                # }
                # {B
                for y, (r, w) in self.items():
                    if y != STDIN:
                        dup2(w, y)
                # }
                # {C
                for r, w in self.values():
                    close(r)
                    close(w)
                # }
            else:
                for y, (r, w) in self.items():
                    dup2(w, y)
                    close(w)
                    close(r)
        return self

    def __exit__(self, *_, **__):
        from ..thread import ConcurrentReader
        from os import close, wait, _exit

        if self.iswriter:
            _exit(0)

        def fds():
            if self.stdin:
                # {E
                r0, w0 = self[0]
                yield w0
                close(r0)
                # }
                # {F
                for y in sorted(self.keys()):
                    r, w = self[y]
                    if y != STDIN:
                        close(w)
                        yield r
                # }
            else:
                for y in sorted(self.keys()):
                    r, w = self[y]
                    yield r
                    close(w)

        ConcurrentReader(fds(), self.oobjs, stdin=self.stdin).join()
        wait()
