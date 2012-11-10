"""Enhancements to the built-in dir function.

Adds support for matching globs to dir.

>>> class K: pass
>>> k = K()
>>> k.aa = 1; k.ba = 2; k.bb = 3
>>> globbing_dir(k)
['__doc__', '__module__', 'aa', 'ba', 'bb']
>>> globbing_dir(k, 'b*')
['ba', 'bb']

If the glob doesn't include any of the metacharacters '*?[', it is treated
as a substring match:

>>> globbing_dir(k, 'du')
['__module__']

"""
# Keep this module compatible with Python 2.4 and better.

import sys
from fnmatch import fnmatchcase

_sentinel = object()


try:
    any
except NameError:
    # Python 2.4 compatibility.
    from backports import any


def globbing_dir(obj=_sentinel, glob=None):
    if obj is _sentinel:
        # Get the locals of the caller.
        names = sorted(sys._getframe(1).f_locals)
        # Note that dir() won't work, because the locals it sees will
        # be those of *this* function, not the caller.
    else:
        names = dir(obj)
    if glob is None:
        return names
    # DWIM when there are no metacharacters in the glob.
    # There is no canonical list of metachars recognised by fnmatch,
    # so I just hard-code the ones fnmatch currently uses.
    if not any(metachar in glob for metachar in '*?['):
        glob = '*' + glob + '*'  # Substring match.
    return [name for name in names if fnmatchcase(name, glob)]

