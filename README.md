# OS level Redirect (context manager)

improved `contextlib.redirect_stdout`, `subprocess.call`

See:
- [redirect_demo.py](x19290/redirect/redirect_demo.py)
- [x19290.redirect](x19290/redirect/redirect.py)
- [StdioPump](x19290/redirect/iopump.py)

## Description

This package provides `os`-level (not `sys`-level) io redirection.

There exist `sys`-level io redirection called
`contextlib.redirect_stdout` and `contextlib.redirect_stderr`.

But:
- they are not thread-safe
- they cannot redirect file descriptors
- they are output-redirection-only

There exists another `os`-level io redirection called `subprocess.Popen`

But:
- it do not accept fileobj like `StringIO`
- pipes quickly stuck with it
