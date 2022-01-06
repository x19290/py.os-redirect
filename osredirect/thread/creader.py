from .ttuple import ThreadTuple


class ConcurrentReader(ThreadTuple):
    @staticmethod
    def threads(fds, oobjs, stdin=None):
        from io import DEFAULT_BUFFER_SIZE
        from os import read
        from threading import Thread

        if not oobjs:
            return
        try:
            oobjs[0].write(r'')
        except TypeError:
            def adapt(b):
                return b
        else:
            def adapt(b):
                from ..xcodecs.utf8 import utf8decode
                return utf8decode(b)

        def pump(fd, oobj):
            while True:
                water = read(fd, DEFAULT_BUFFER_SIZE)
                if not water:
                    break
                oobj.write(adapt(water))

        if stdin:
            from os import close, write
            w = fds.__next__()
            def feed():
                for data in stdin:
                    write(w, data)
                close(w)
            yield Thread(target=feed)

        for fd, oobj in zip(fds, oobjs):
            yield Thread(target=pump, args=(fd, oobj))
