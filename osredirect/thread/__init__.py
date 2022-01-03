class ThreadTuple(tuple):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, cls.contents(*args, **kwargs))
        for y in self:
            y.start()
        return self

    def join(self):
        for y in self:
            y.join()


class ConcurrentReader(ThreadTuple):
    @staticmethod
    def contents(fds, oobjs):
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
                from ..codecs.utf8 import utf8decode
                return utf8decode(b)

        def pump(fd, oobj):
            while True:
                water = read(fd, DEFAULT_BUFFER_SIZE)
                if not water:
                    break
                oobj.write(adapt(water))

        for fd, oobj in zip(fds, oobjs):
            yield Thread(target=pump, args=(fd, oobj))
