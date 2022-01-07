#!/usr/bin/env python3


def main():
    print(_main())


def _main(argv=None):
    r'''
    To do the following doctest (>>> _main...), run:
    `python3 -m doctest redirectdemo.py`

    There should be no output.

    >>> _main(r'<>'.split())
    'AB ab'

    >>> _main(r'<> --bin-in'.split())
    'AB ab'

    >>> _main(r'<> --bin-out'.split())
    b'AB ab'

    >>> _main(r'<> --bin-out --bin-in'.split())
    b'AB ab'
    '''

    from pathlib import Path
    from sys import path as pythonpath
    pythonpath[:0] = Path(__file__).absolute().parent.parent.parent.__str__(),

    from x19290.redirect import (
        redirect, STDIN, STDOUT_BIT, STDOUT, STDERR_BIT, STDERR,
    )
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

    with MemIO() as stdout, MemIO() as stderr:
        stdin = feed,
        fsbits = STDOUT_BIT | STDERR_BIT
        with redirect(fsbits, stdout, stderr, stdin=stdin) as iswriter:
            if iswriter:
                data = read(STDIN, 8192)
                write(STDOUT, data.upper())
                write(STDERR, data.lower())
        return sep.join((stdout.getvalue(), stderr.getvalue()))


if __name__ == r'__main__':
    main()
