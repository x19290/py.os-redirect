from .iopump import StdioPump
from .redirect import redirect, Redirect, STDIN, STDERR, STDOUT
(
    StdioPump, redirect, Redirect, STDIN, STDERR, STDOUT,
)  # to avoid "not used" warnings
