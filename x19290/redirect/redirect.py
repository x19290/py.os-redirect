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
            for y in stdin, stdout, stderr:
                yield None if y is None else (pipe(), y)

        return super().__new__(cls, contents())

    def __enter__(self):
        from os import close, dup2, fork

        self.ischild = ischild = fork() == 0
        if ischild:
            stdin = self[0]
            if stdin:
                pipe = stdin[0]
                # {A
                dup2(pipe[0], 0)
                # }
                # {B
                for fd, route in enumerate(self[1:], start=1):
                    if route:
                        pipe = route[0]
                        dup2(pipe[1], fd)
                # }
                # {C
                for route in self:
                    if route:
                        pipe = route[0]
                        close(pipe[0])
                        close(pipe[1])
                # }
            else:
                for fd, route in enumerate(self):
                    if route:
                        r, w = route[0]
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
            stdin = self[0]
            if stdin:
                pipe, iobj = stdin
                # {E
                r0, w0 = pipe
                yield True, w0, iobj
                close(r0)
                # }
                # {F
                for route in self[1:]:
                    if route is None:
                        continue
                    pipe, oobj = route
                    r, w = pipe
                    close(w)
                    yield False, r, oobj
                # }
            else:
                for route in self[1:]:
                    if route is None:
                        continue
                    pipe, oobj = route
                    r, w = pipe
                    close(w)
                    yield False, r, oobj

        IOPump(*how()).join()
        status = WEXITSTATUS(wait()[1])
        if status != 0:
            raise ValueError(status)
