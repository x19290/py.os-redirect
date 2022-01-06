from ..thread.ttuple import ThreadTuple


class StdioPump(ThreadTuple):
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
            def frombin(b):
                return b
            def fromstr(s):
                # from ..xcodecs.utf8 import utf8encode
                # return utf8encode(s)
                return s
        else:
            def frombin(b):
                from ..xcodecs.utf8 import utf8decode
                return utf8decode(b)
            def fromstr(s):
                return s

        def doread(fd, oobj):
            while True:
                water = read(fd, DEFAULT_BUFFER_SIZE)
                if not water:
                    break
                oobj.write(frombin(water))

        if stdin:
            from os import close, write
            w = fds.__next__()
            def dowrite():
                for water in stdin:
                    write(w, fromstr(water))
                close(w)
            yield Thread(target=dowrite)

        for fd, oobj in zip(fds, oobjs):
            yield Thread(target=doread, args=(fd, oobj))
