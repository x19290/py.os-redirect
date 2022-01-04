# OS Redirect

accurate output (stdout, stderr) redirection

## Description

[osredirect](osredirect/__init__.py) provides an `os` level redirection
not like `sys` level ones (contextlib.redirect_stdout,...)

It also is thread-safe.

## Parts

- `redirect()`:  
  See [redirectdemo.py](redirectdemo.py).

- [osredirect.thread](osredirect/thread/__init__.py):  
  In this package, classes ConcurrentReader, ThreadTuple are.

  `redirect` must watch multiple inputs, but it does not use
  `select` like facilities that are too platform-specific.

  It uses straightforward threading instead.
  ConcurrentReader() watches multiple input (`fds`) and pumps them to `oobjs`.

  ThreadTuple is abstracted from ConcurrentReader.

## More docs

- [concern.md](0more-docs/concern.md)
