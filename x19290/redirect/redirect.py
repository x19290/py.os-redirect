from contextlib import contextmanager

STDIN, STDOUT, STDERR = range(3)


@contextmanager
def redirect(stdin=None, stdout=None, stderr=None):
    try:
        r = Redirect(stdin, stdout, stderr).__enter__()
        yield r.ischild
    finally:
        r.__exit__()


class Redirect(tuple):
    def __new__(cls, stdin=None, stdout=None, stderr=None):
        from os import pipe

        def contents():
            for ioobj in stdin, stdout, stderr:
                yield (pipe() if ioobj else None), ioobj

        return super().__new__(cls, contents())

    def __enter__(self):
        from os import close, dup2, fork

        self.ischild = ischild = fork() == 0
        if ischild:
            pipe, _ = self[0]
            if pipe:
                # {A
                dup2(pipe[0], 0)
                # }
                # {B
                for fd, (pipe, _) in enumerate(self[1:], start=1):
                    if pipe:
                        dup2(pipe[1], fd)
                # }
                # {C
                for pipe, _ in self:
                    if pipe:
                        close(pipe[0])
                        close(pipe[1])
                # }
            else:
                for fd, (pipe, _) in enumerate(self):
                    if pipe:
                        r, w = pipe
                        dup2(w, fd)
                        close(w)
                        close(r)
        return self

    def __exit__(self, *_, **__):
        from ..iopump import IOPump
        from os import close, wait, _exit, WEXITSTATUS

        if self.ischild:
            _exit(0)

        def how():
            pipe, iobj = self[0]
            if pipe:
                # {E
                r0, w0 = pipe
                yield w0, iobj
                close(r0)
                # }
                # {F
                for pipe, oobj in self[1:]:
                    if pipe is None:
                        continue
                    r, w = pipe
                    close(w)
                    yield r, oobj
                # }
            else:
                for pipe, oobj in self[1:]:
                    if pipe is None:
                        continue
                    r, w = pipe
                    close(w)
                    yield r, oobj

        IOPump(*how()).start().join()
        status = WEXITSTATUS(wait()[1])
        if status != 0:
            raise ValueError(status)
