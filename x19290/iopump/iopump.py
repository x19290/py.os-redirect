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

        def defaultreader(fd, oobj):
            from ..codecs.default import decode
            adapt = decode
            while True:
                # normal binary read loop
                # copy data from fd to oobj
                # oobj may be text mode
                bits = read(fd, DEFAULT_BUFFER_SIZE)
                if not bits:
                    break
                try:
                    # text mode?
                    oobj.write(adapt(bits))
                except TypeError:
                    # binary mode!
                    from ..nop.identity import strictidentity
                    adapt = strictidentity
                    oobj.write(adapt(bits))
            while True:
                bits = read(fd, DEFAULT_BUFFER_SIZE)
                if not bits:
                    break
                oobj.write(adapt(bits))

        def defaultwriter(fd, iobj):
            from ..codecs.default import encode
            adapt = encode
            from os import close, write

            iobj = iobj.__iter__()
            try:
                chunk = iobj.__next__()
            except StopIteration:
                pass
            else:
                try:
                    # text mode?
                    chunk = adapt(chunk)
                except TypeError:
                    # binary mode!
                    from ..nop.identity import strictidentity
                    adapt = strictidentity
                write(fd, chunk)
            for chunk in iobj:
                write(fd, adapt(chunk))
            close(fd)

        for route in routes:
            try:
                fd, _ = route  # check if route == fd, ioobj
            except:
                # not. route itself is a target thread
                yield Thread(target=route)
            else:
                try:
                    read(fd, 0)  # check fd is readable
                except:
                    target = defaultwriter  # select defaultwriter as target
                else:
                    target = defaultreader  # select defaultreader as target
                yield Thread(target=target, args=route)
