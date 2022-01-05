#!/usr/bin/env python3

def main():
    from osredirect import redirect, STDOUT_BIT

    from io import StringIO
    from os import write

    with StringIO() as b:
        with redirect(STDOUT_BIT, b) as iswriter:
            if iswriter:
                write(1, br'abcd')
        print(b.getvalue().upper())


if __name__ == r'__main__':
    main()
