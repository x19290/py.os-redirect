STDOUT_BIT, STDERR_BIT = 1, 2
STDOUT, STDERR = 1, 2


def redirect(exec, fdbits: int, *oobjs):
    from .thread import ConcurrentReader
    from os import close, dup2, fork, pipe, wait, _exit

    def fds():
        bit = 1
        for _ in range(2):
            if fdbits & bit:
                yield bit
            bit <<= 1

    fds = tuple(fds())
    oobjs += (NULL_OUT,) * (fds.__len__() - oobjs.__len__())
    pipes = {y: pipe() for y in fds}
    if fork() == 0:
        for y, (r, w) in pipes.items():
            dup2(w, y)
            close(w)
            close(r)
        exec()  # may not return
        _exit(0)

    def fds():
        for r, w in pipes.values():
            yield r
            close(w)

    ConcurrentReader(fds(), oobjs).join()
    wait()


class _NullOut:
    @staticmethod
    def close():
        pass
    @staticmethod
    def write(data):
        return data.__len__()


NULL_OUT = _NullOut()
