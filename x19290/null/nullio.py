def _known():
    from io import BytesIO

    return set(y for y in dir(BytesIO) if not y.startswith(r'_'))

class _NullOut:
    @staticmethod
    def _nop(*_, **__):
        pass

    close = flush = write = _nop


NULL_OUT = _NullOut()


class _Null:
    known = _known()

    def __getattr__(self, name: str):
        try:
            ret = self.__getattribute__(r'_%s__' % name)
        except AttributeError:
            if name not in self.known:
                error = AttributeError
            else:
                from io import UnsupportedOperation as error
            raise error(name)
        else:
            return lambda *_, **__: ret

    @classmethod
    def read(cls, *_, **__):
        return cls.empty

    @classmethod
    def write(cls, data):
        expected = cls.empty.__class__
        actual = data.__class__
        if not issubclass(actual, expected):
            raise TypeError(
                r"a %s-like object is required, not '%s'"
            %
                (expected.__name__, actual.__name__),
            )

    getvalue = readline = read

    _close__ = _flush = None
    _seek__ = _truncate__ = _tell__ = 0
    _readable__ = _seekable__ = _writable__ = True


class _Bin(_Null):
    empty = br''


class _Str(_Null):
    empty = r''


NULL_BIN, NULL_STR = _Bin(), _Str()
