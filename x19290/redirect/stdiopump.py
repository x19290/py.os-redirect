from ..thread.ttuple import ThreadTuple


class StdioPump(ThreadTuple):
    @staticmethod
    def threads(*routes):
        from io import DEFAULT_BUFFER_SIZE
        from os import read
        from threading import Thread

        i = tuple((fd, ioobj) for iobj, fd, ioobj in routes if iobj)
        o = tuple((fd, ioobj) for iobj, fd, ioobj in routes if not iobj)

        if not o and not i:
            return
        if o:
            try:
                o[0][1].write(r'')
            except TypeError:
                def adapt(b):
                    return b
            else:
                def adapt(b):
                    from ..xcodecs.utf8 import utf8decode
                    return utf8decode(b)

        def readpump(fd, oobj):
            while True:
                bits = read(fd, DEFAULT_BUFFER_SIZE)
                if not bits:
                    break
                oobj.write(adapt(bits))

        for w, stdin in i:
            from os import close, write
            def writepump(stdin=stdin):
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
            yield Thread(target=writepump)

        for fd, oobj in o:
            yield Thread(target=readpump, args=(fd, oobj))
