#!/usr/bin/env python3

def main():
    from osredirect import redirect, STDOUT_BIT

    from io import StringIO
    from os import write

    with StringIO() as b:
        redirect(lambda: write(1, br'abcd'), STDOUT_BIT, b)
        print(b.getvalue().upper())

    # TODO: provide it as a contextmanager
    r'''
    with StringIO() b:
        with redirect(STDOUT_BIT, b):
            write(1, br'abcd')
        print(b.getvalue().upper())
    '''


if __name__ == r'__main__':
    main()
