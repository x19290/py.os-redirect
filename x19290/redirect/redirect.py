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
        from ..null.nullio import NULL_OUT
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
                r0 = stdin[0][0]
                # {A
                dup2(r0, 0)
                # }
                # {B
                for fd, redirect in enumerate(self[1:], start=1):
                    if redirect:
                        pipe = redirect[0]
                        dup2(pipe[1], fd)
                # }
                # {C
                for fd, redirect in enumerate(self):
                    if redirect:
                        pipe = redirect[0]
                        close(pipe[0])
                        close(pipe[1])
                # }
            else:
                for fd, redirect in enumerate(self):
                    if redirect:
                        r, w = redirect[0]
                        dup2(w, fd)
                        close(w)
                        close(r)
        return self

    def __exit__(self, *_, **__):
        from .stdiopump import StdioPump
        from os import close, wait, _exit, WEXITSTATUS

        if self.ischild:
            _exit(0)

        def routes():
            stdin = self[0]
            if stdin:
                pipe, iobj = stdin
                # {E
                r0, w0 = pipe
                yield True, w0, iobj
                close(r0)
                # }
                # {F
                for redirect in self[1:]:
                    if redirect is None:
                        continue
                    pipe, oobj = redirect
                    r, w = pipe
                    close(w)
                    yield False, r, oobj
                # }
            else:
                for redirect in self[1:]:
                    if redirect is None:
                        continue
                    pipe, oobj = redirect
                    r, w = pipe
                    close(w)
                    yield False, r, oobj

        StdioPump(*routes()).join()
        status = WEXITSTATUS(wait()[1])
        if status != 0:
            raise ValueError(status)