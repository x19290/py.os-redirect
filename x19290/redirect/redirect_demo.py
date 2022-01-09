#!/usr/bin/env python3


def main():
    print(redirect_demo())


def redirect_demo(argv=None):
    r'''
    To do the following doctest (>>> redirect_demo...), run:
    `python3 -m doctest redirect_demo.py`

    There should be no output.

    >>> redirect_demo(r'<>'.split())
    'AB ab'

    >>> redirect_demo(r'<> --bin-in'.split())
    'AB ab'

    >>> redirect_demo(r'<> --bin-out'.split())
    b'AB ab'

    >>> redirect_demo(r'<> --bin-out --bin-in'.split())
    b'AB ab'
    '''

    from pathlib import Path
    from sys import path as pythonpath
    pythonpath[:0] = Path(__file__).absolute().parent.parent.parent.__str__(),

    from x19290.redirect import redirect, STDIN, STDOUT, STDERR
    from argparse import ArgumentParser
    from os import read, write
    if argv is None:
        from sys import argv

    argp = ArgumentParser()
    argp.add_argument(r'--bin-in', action=r'store_true')
    argp.add_argument(r'--bin-out', action=r'store_true')
    argx = argp.parse_args(argv[1:])

    if argx.bin_in:
        feed = br"Ab"
    else:
        feed = r'Ab'
    if argx.bin_out:
        from io import BytesIO as MemIO
        sep = br' '
    else:
        from io import StringIO as MemIO
        sep = r' '

    # `stdout`, `stderr` can be any writable `fileobj`
    # Data are auto-decoded by a single decoder: `default.decode` or `identity`
    # It means that `BytesIO() as stdout, StringIO() as stderr` is not allowed.
    with MemIO() as stdout, MemIO() as stderr:
        # `stdin` can be anything that yields `str` or `bytes`.
        # Data are auto-encoded by a single encoder:
        #     `default.encode` or `identity`
        # It means that, stdin = b'~', '~' is not allowed
        stdin = feed,
        with redirect(stdin, stdout, stderr) as ischild:
            # pass stdin,... stderr in this order or use std~=...
            # stdin,... stderr may be None meaning "no io"
            if ischild:  # this `if` is required
                data = read(STDIN, 8192)
                write(STDOUT, data.upper())
                write(STDERR, data.lower())
        return sep.join((stdout.getvalue(), stderr.getvalue()))


if __name__ == r'__main__':
    main()
