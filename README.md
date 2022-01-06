# OS Redirect

improved `contextlib.redirect_stdout`, `subprocess.call`

See:
- [redirectdemo.py](redirectdemo.py)
- [osredirect.osredirect](osredirect/osredirect/osredirect.py)
- [osredirect.stdiopump](osredirect/osredirect/stdiopump.py)

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
