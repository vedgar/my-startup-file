"""Enhancements to the built-in dir function.

Enhanced dir()-like function.

    - Search metaclass as well as instance and class.
    - Support for matching globs to dir.

        >>> class K: pass
        >>> k = K()
        >>> k.aa = 1; k.ba = 2; k.bb = 3
        >>> dir(k)
        ['__doc__', '__module__', 'aa', 'ba', 'bb']
        >>> dir(k, 'b*')
        ['ba', 'bb']

      If the glob doesn't include any of the metacharacters '*?[', it is
      treated as a regular substring match:

        >>> dir(k, 'du')
        ['__module__']


The `dir` function is designed to be monkey-patched into built-ins as a
replacement for the original. The original is accessible as `builtin_dir`.
"""

# Keep this module compatible with Python 2.4 and better.

import sys
from fnmatch import fnmatchcase

MISSING = object()
original_dir = dir  # In case this gets monkey-patched.

try:
    any
except NameError:
    # Python 2.4 compatibility.
    from backports import any


# We prefer to do case-insensitive matching with Unicode string's casefold,
# when it is available. Otherwise fall back to just lowercase.
try:
    casefold = str.casefold
except AttributeError:
    casefold = str.lower


def _pop(t, d=MISSING):
    """Pop the first item from sequence t.

    Returns both the first item and the tail of the sequence:

    >>> t = (2, 3, 4, 5)
    >>> item, t = pop(t)
    >>> print(item); print(t)
    2
    (3, 4, 5)

    If t is empty, raises IndexError unless the option second
    argument is given, in which case that it returned in place
    of the non-existent popped value.
    """
    if t:
        return t[0], t[1:]
    elif d is not MISSING:
        return d, ()
    else:
        raise IndexError('pop from empty object')


def _getattrnames(obj, meta):
    if obj is MISSING:
        # Get the locals of the caller's caller. This may not work 
        # under some implementations such as Jython.
        names = sys._getframe(2).f_locals
        # Note that calling builtin dir() won't work, because the locals it
        # sees will be those of *this* function, not the caller.
    else:
        names = original_dir(obj)
        if meta:
            if isinstance(obj, type):
                metaclass = type(obj)
            else:
                metaclass = type(type(obj))
            names.extend(dir(metaclass))
    return sorted(set(names))


def _filter(names, glob):
    # Filter names according to the glob.
    assert isinstance(glob, str)
    if not glob:
        return names
    invert = glob.startswith('!')
    if invert:
        glob = glob[1:]
    case = glob.endswith('=')
    if case:
        glob = glob[:-1]
    match = _matcher(glob, invert)
    if case:
        names = [nm for nm in names if match(nm)]
    else:
        glob = casefold(glob)
        names = [nm for nm in names if match(casefold(nm))]
    return names


def _matcher(glob, invert):
    if any(c in glob for c in '*?['):
        # Searches with metacharacters use fnmatchcase.
        # Don't use fnmatch since that is platform-dependent.
        def match(name):
            return fnmatchcase(name, glob)
    else:
        def match(name):
            return glob in name
    if invert:
        orig = match
        def match(name):
            return not orig(name)
    return match

def _filter_dunders(names, dunder):
    if dunder:
        return names
    D = '__'
    return [nm for nm in names if not (nm.startswith(D) and nm.endswith(D))]


def edir(*args, **kwargs):
    """dir([object [, glob], include_metaclass=False]) -> list of strings

    If called without any arguments, return the names in the current scope.
    Otherwise return an alphabetized list of names comprising some of the
    attributes of the given object, and of attributes reachable from it.
    If the object supplies a method named __dir__, it will be used; otherwise
    the default dir() logic is used and returns:

        - for a module object: the module's attributes;

        - for a class object:  its attributes, and recursively the
          attributes of its bases;

        - for any other object: its attributes, its class's attributes, and
          recursively the attributes of its class's base classes.

    If keyword-only argument include_metaclass is a true value, attributes
    reachable from the object's metaclass will also be include. By default,
    metaclass attributes are not included.

    If string argument `glob` is given, only attributes matching that string
    will be returned. Globs support the following metacharacters:

        - Wildcards: '?' to match a single character, '*' to match
          zero or more characters.

        - Character sets: e.g. '[abc]' to match any of 'a', 'b', 'c', or
          '[!abc]' to match any character except 'a', 'b', 'c'.

        - Reverse matching: if the glob begins with '!', the sense of the
          match is reversed to "don't match".

        - Matches are case-insensitive by default. For a case-sensitive
          match, end the glob with a '=' suffix.

    """
    obj = glob = MISSING
    if args:
        obj, args = _pop(args)
    if args:
        glob, args = _pop(args, None)
    if args:
        raise TypeError('too many arguments')
    if glob is MISSING:
        glob = kwargs.pop('glob', '')
    meta = kwargs.pop('meta', False)
    dunders = kwargs.pop('dunders', False)
    if kwargs:
        raise TypeError('unexpected keyword argument')
    names = _getattrnames(obj, meta)
    names = _filter(names, glob)
    names = _filter_dunders(names, dunders)
    return names


def ddir(*args, **kwargs):
    """dunder dir - like enhanced dir, except dunder names are shown by default."""
    if 'dunders' not in kwargs and len(args) < 2:
        kwargs['dunders'] = True
    return edir(*args, **kwargs)


