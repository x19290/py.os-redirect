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
    # self[i] == (pipe(), ioobj) or (None, None)
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
            # redirect STDIN, STDOUT, STDERR to pipes contained in self
            pipe, _ = self[0]
            if pipe:
                r = pipe[0]
                dup2(r, 0)  # redirect STDIN
                # for fd in STDOUT, STDIN...
                for fd, (pipe, _) in enumerate(self[1:], start=1):
                    if pipe:
                        w = pipe[1]
                        dup2(w, fd)  # redirect STDOUT/STDERR
                for pipe, _ in self:
                    if pipe:
                        # reclaim pips
                        close(pipe[0])
                        close(pipe[1])
            else:  # STDOUT, STDERR only
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
            pipe, iobj = self[0]  # first, check self[0]
            if pipe:
                r0, w0 = pipe
                yield w0, iobj
                close(r0)
                for pipe, oobj in self[1:]:  # next, check self[1:]
                    if pipe is None:
                        continue
                    r, w = pipe
                    close(w)
                    yield r, oobj
            else:
                # self[0] == (None, None), check self[1:]
                for pipe, oobj in self[1:]:  #  self[0] is None
                    if pipe is None:
                        continue
                    r, w = pipe
                    close(w)
                    yield r, oobj

        IOPump(*how()).start().join()
        status = WEXITSTATUS(wait()[1])
        if status != 0:
            raise ValueError(status)
