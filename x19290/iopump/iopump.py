from ..thread.ttuple import ThreadTuple


class IOPump(ThreadTuple):
    r'''
    an alternative to `select`, `selectors`
    '''
    @staticmethod
    def threads(*routes):
        from io import DEFAULT_BUFFER_SIZE
        from os import read
        from threading import Thread

        iobjs = tuple((fd, y) for isiobj, fd, y in routes if isiobj)
        oobjs = tuple((fd, y) for isiobj, fd, y in routes if not isiobj)

        if not oobjs and not iobjs:
            return
        if oobjs:
            try:
                oobjs[0][1].write(r'')
            except TypeError:
                def adapt(b):
                    return b
            else:
                def adapt(b):
                    from ..codecs.utf8 import utf8decode
                    return utf8decode(b)

        def readpump(fd, oobj):
            while True:
                bits = read(fd, DEFAULT_BUFFER_SIZE)
                if not bits:
                    break
                oobj.write(adapt(bits))

        for w, stdin in iobjs:
            from os import close, write
            def writepump(stdin=stdin):
                from ..codecs.utf8 import utf8encode as adapt
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

        for fd, oobj in oobjs:
            yield Thread(target=readpump, args=(fd, oobj))
