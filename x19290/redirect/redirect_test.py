from . import redirect, STDIN, STDERR, STDOUT
from io import BytesIO, StringIO
from os import close, dup2, fork, pipe, read, wait, write, _exit
from nose.tools import eq_
from unittest import TestCase


class _WithoutStdin:
    def _test(self, n):
        expected, isep, osep = map(self.adapt, (self.expected, r',', r' '))
        expected = expected.split(isep)[n]
        mems = tuple(self.memio() for _ in range(n))
        outs = self.outs
        kwargs = dict(stdin=None, stdout=None, stderr=None)
        for k, m in zip(outs, mems):
            kwargs[k] = m
        with redirect(**kwargs) as ischild:
            if ischild:
                if kwargs[r'stdout']:
                    write(STDOUT, br'1')
                if kwargs[r'stderr']:
                    write(STDERR, br'2')
        actual = (kwargs[y] for y in outs)
        actual = osep.join(y.getvalue() for y in actual if y)
        eq_(expected, actual)

    def test0(self):
        self._test(0)

    def test1(self):
        self._test(1)

    def test2(self):
        self._test(2)


class _0bin(_WithoutStdin):
    memio = BytesIO

    @staticmethod
    def adapt(s):
        return s.encode(r'UTF-8')


class _1str(_WithoutStdin):
    memio = StringIO

    @staticmethod
    def adapt(s):
        return s


class _0w1:
    expected = r',1,1'
    outs = r'stdout',


class _1w2:
    expected = r',2,2'
    outs = r'stderr',


class _2w1w2:
    expected = r',1,1 2'
    outs = r'stdout', r'stderr'


class T0bin0w1(_0bin, _0w1, TestCase):
    pass


class T0bin1w2(_0bin, _1w2, TestCase):
    pass


class T0bin2w1w2(_0bin, _2w1w2, TestCase):
    pass


class T1str0w1(_1str, _0w1, TestCase):
    pass


class T1str1w2(_1str, _1w2, TestCase):
    pass


class T1str2w1w2(_1str, _2w1w2, TestCase):
    pass


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
