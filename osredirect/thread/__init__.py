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
                return b.decode(r'UTF-8')  # TODO: use faster way

        def pump(fd, oobj):
            while True:
                water = read(fd, 8192)
                if not water:
                    break
                oobj.write(adapt(water))

        for fd, oobj in zip(fds, oobjs):
            yield Thread(target=pump, args=(fd, oobj))
