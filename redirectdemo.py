#!/usr/bin/env python3

def main():
    from osredirect import Redirect, STDOUT_BIT

    from io import StringIO
    from os import write

    with StringIO() as b:
        with Redirect(STDOUT_BIT, b) as r:
            if r.child:
                write(1, br'abcd')
        print(b.getvalue().upper())


if __name__ == r'__main__':
    main()
