"""Backported or re-implemented functions to Python 2.4+

"""
# This package should remain compatible with Python 2.4.

import sys


# Built-ins `all` and `any` were added in Python 2.5.
def all(iterable):
    """all(iterable) -> bool

    Return True if bool(x) is True for all values x in the iterable.

    >>> all([42, 23, 56, 12])
    True
    >>> all([42, 23, 56, 0, 12])
    False

    """
    for element in iterable:
        if not element:
            return False
    return True

def any(iterable):
    """any(iterable) -> bool

    Return True if bool(x) is True for any x in the iterable.

    >>> any([0, False, None, {}])
    False
    >>> any([0, False, None, 23, {}])
    True

    """
    for element in iterable:
        if element:
            return True
    return False


# functools.wraps was added in Python 2.5.
def wraps(func_to_wrap):
    """Return a decorator that wraps its argument.

    This is a reimplementation of functools.wraps() which copies the name,
    module, docstring and attributes of the base function to the decorated
    function. wraps() is available in the standard library from Python 2.5.

    >>> def undecorated(x):
    ...     '''This is a doc string.'''
    ...     return x+1
    ...
    >>> undecorated.__module__ = 'parrot'
    >>> undecorated.attr = 'something'
    >>> @wraps(undecorated)
    ... def decorated(x):
    ...     return undecorated(x)
    ...
    >>> decorated(3)
    4
    >>> decorated.__doc__
    'This is a doc string.'
    >>> decorated.attr
    'something'
    >>> decorated.__module__
    'parrot'
    >>> decorated.__name__
    'undecorated'

    """
    def decorator(func):
        def f(*args, **kwargs):
            return func(*args, **kwargs)
        f.__doc__ = func_to_wrap.__doc__
        try:
            f.__name__ = func_to_wrap.__name__
        except Exception:
            # Older versions of Python (2.3 and older perhaps?)
            # don't allow assigning to function __name__.
            pass
        f.__module__ = func_to_wrap.__module__
        if hasattr(func_to_wrap, '__dict__'):
            f.__dict__.update(func_to_wrap.__dict__)
        return f
    return decorator


# sys.getsizeof added in Python 2.6.
def getsizeof(obj, default=None):
    """Memory taken by some Python objects.

    This is only valid for the 32-bit implementation of CPython 2.x, and
    should be considered approximate. Supports only a few built-ins:

        - int, list, tuple, dict, str/bytes, unicode/str

    For other objects, if they have a __getsizeof__ method, that will be
    called and the result returned; otherwise if default is not None that
    will be returned. Otherwise, TypeError is raised.

    Excludes the space used by items in containers; does not take into
    account overhead of memory allocation from the operating system, or
    over-allocation by lists and dicts.
    """
    T = type(obj)
    if sys.version.startswith('2'):
        byte_type = str
        text_type = unicode
    else:
        byte_type = bytes
        text_type = str
    if T is int:
        # This only applies before int/long unification.
        kind = "fixed"
        container = False
        size = 4
    elif T is list or T is tuple:
        kind = "variable"
        container = True
        size = 4*len(obj)
    elif T is dict:
        kind = "variable"
        container = True
        size = 144
        if len(obj) > 8:
            size += 12*(len(obj)-8)
    elif T is byte_type:
        kind = "variable"
        container = False
        size = len(obj) + 1
    elif T is text_type:
        kind = "variable"
        container = False
        bytes_per_char = _get_bytes_per_char(obj)
        size = bytes_per_char*(len(obj) + 1)
    else:
        try:
            # FIXME The real sys.getsizeof implementation adds some
            # garbage collector overhead to this.
            return type(obj).__getsizeof__()
        except AttributeError:
            if default is None:
                raise TypeError("don't know about '%s' objects" % T.__name__)
            return default
    assert kind in ("fixed", "variable")
    if kind == "fixed":
        overhead = 8
    else:
        overhead = 12
    if container:
        garbage_collector = 8
    else:
        garbage_collector = 0
    malloc = 8  # In most cases.
    size += overhead + garbage_collector + malloc
    # Round up to the nearest multiple of 8 bytes.
    if size % 8:
        size = (size//8 + 1)*8
    # otherwise size is already a multiple of 8 bytes.
    assert size % 8 == 0
    return size


def _get_bytes_per_char(text):
    # Helper function determining the number of bytes per character
    # in text (Unicode) strings.
    if sys.version >= '3.3':
        # Flexible text representation.
        if not text:
            return 1
        maxchr = ord(max(text))
        if maxchr <= 0xFF:
            return 1
        elif maxchr <= 0xFFFF:
            return 2
        else:
            assert maxchr <= 0x10FFFF
            return 4
    elif sys.maxunicode == 0xFFFF:
        return 2  # Narrow build.
    else:
        assert sys.maxunicode == 0x10FFFF
        return 4  # Wide build.


# int.bit_length added in Python 2.7.
def bit_length(n):
    """Return the number of bits needed to represent int n in binary.

    >>> bit_length(37)
    6
    >>> bit_length(2375)
    12

    If n is zero, return 0:

    >>> bit_length(0)
    0

    """
    if not isinstance(n, (int, long)):
        raise TypeError('expected an int')
    if n == 0:
        return 0
    elif n < 0:
        n = -n
    assert n >= 1
    numbits = 0
    while n > 2**64:
        numbits += 64; n >>= 64
    while n:
        numbits += 1; n >>= 1
    return numbits
