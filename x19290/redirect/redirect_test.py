from . import redirect, STDIN, STDERR, STDOUT
from io import BytesIO, StringIO
from os import close, dup2, fork, pipe, read, wait, write, _exit
from nose.tools import eq_
from unittest import TestCase


class _WithoutStdin:
    def _test(self, expected, *outs):
        adapt = self.adapt
        expected, sep = map(adapt, (expected, r' '))
        memio, kwargs = self.memio, {}
        for k in outs:
            kwargs[k] = memio()
        with redirect(**kwargs) as ischild:
            if ischild:
                if r'stdout' in kwargs:
                    write(STDOUT, br'1')
                if r'stderr' in kwargs:
                    write(STDERR, br'2')
        actual = sep.join(kwargs[y].getvalue() for y in outs)
        eq_(expected, actual)

    def test0(self):
        self._test(r'')

    def test1(self):
        self._test(r'1', r'stdout')

    def test2(self):
        self._test(r'1 2', r'stdout', r'stderr')


class T0bin(_WithoutStdin, TestCase):
    memio = BytesIO

    @staticmethod
    def adapt(s):
        return s.encode(r'UTF-8')


class T1str(_WithoutStdin, TestCase):
    memio = StringIO

    @staticmethod
    def adapt(s):
        return s


class T2with_stdin(TestCase):
    def _typical(self, fd):
        feed = br"abc"
        expected = feed.upper()
        stdin = feed,
        with BytesIO() as b:
            if fd == STDOUT:
                kwargs = dict(stdin=stdin, stdout=b)
            elif fd == STDERR:
                kwargs = dict(stdin=stdin, stderr=b)
            with redirect(**kwargs) as ischild:
                if ischild:
                    data = read(STDIN, feed.__len__())
                    write(fd, data.upper())
            actual = b.getvalue()
        eq_(expected, actual)

    def test0capture_stdout(self):
        self._typical(STDOUT)

    def test1capture_stderr(self):
        self._typical(STDERR)

    def test2stdin_only(self):
        r, w = pipe()
        feed = br"abc"
        stdin = feed,
        expected = feed.upper()
        if fork() == 0:
            dup2(w, STDOUT)
            close(r)
            close(w)
            with redirect(stdin=stdin) as ischild:
                if ischild:
                    data = read(STDIN, feed.__len__())
                    write(STDOUT, data.upper())
            _exit(0)
        close(w)
        actual = read(r, feed.__len__())
        eq_(expected, actual)

    def test3capture_both(self):
        feed = br"1a 2b"
        feed1, feed2 = feed.split()
        expected = feed.upper()
        stdin = feed,
        with BytesIO() as stdout, BytesIO() as stderr:
            with redirect(stdin, stdout, stderr) as ischild:
                if ischild:
                    data = read(STDIN, feed1.__len__())
                    write(STDOUT, data.upper())
                    write(STDERR, feed2.upper())
            actual = br'%s %s' % (stdout.getvalue(), stderr.getvalue())
        eq_(expected, actual)
