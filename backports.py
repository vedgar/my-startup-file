"""Backported or re-implemented functions from Python 2.5+ to 2.4.

"""


# builtins `all` and `any` were added in Python 2.5.
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



# `functools.wraps` was added in Python 2.5.
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


if __name__ == '__main__':
    import doctest
    failures, tests = doctest.testmod()
    if tests == 0:
        print("no doctests found")
    elif failures == 0:
        print("%d doctests passed." % tests)


