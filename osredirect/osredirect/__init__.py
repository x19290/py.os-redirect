from .stdiopump import StdioPump
from .osredirect import (
    redirect, Redirect, STDIN, STDERR_BIT, STDERR, STDOUT, STDOUT_BIT,
)
(
    StdioPump,
    redirect, Redirect, STDIN, STDERR_BIT, STDERR, STDOUT, STDOUT_BIT,
)  # to avoid "not used" warnings
