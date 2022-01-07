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
            def adapt(b):
                return b
        else:
            def adapt(b):
                from ..xcodecs.utf8 import utf8decode
                return utf8decode(b)

        def doread(fd, oobj):
            while True:
                bits = read(fd, DEFAULT_BUFFER_SIZE)
                if not bits:
                    break
                oobj.write(adapt(bits))

        if stdin:
            from os import close, write
            w = fds.__next__()
            def dowrite(stdin=stdin):
                from ..xcodecs.utf8 import utf8encode as adapt
                stdin = stdin.__iter__()
                try:
                    chunk = stdin.__next__()
                except StopIteration:
                    pass
                else:
                    try:
                        bits = adapt(chunk)
                    except TypeError:
                        bits = chunk
                        def adapt(b):
                            return b
                    write(w, bits)
                for chunk in stdin:
                    write(w, adapt(chunk))
                close(w)
            yield Thread(target=dowrite)

        for fd, oobj in zip(fds, oobjs):
            yield Thread(target=doread, args=(fd, oobj))
