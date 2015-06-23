"""Enhanced dir function.

``edir`` is an enhanced replacement for the builtin ``dir`` with the
following features:

- By default, matches the behaviour of the builtin ``dir``:

    >>> edir(23) == dir(23)
    True

- Filter names which match a glob or substring:

    >>> class K(object): pass
    >>> k = K()
    >>> k.aa = 1; k.ba = 2; k.bb = 3; k.ab = 4
    >>> edir(k, 'b*')
    ['ba', 'bb']

- Substring matching if the glob lacks metacharacters:

    >>> edir(k, 'dul')
    ['__module__']

- Optionally filter out dunder methods with a keyword-only argument:

    >>> edir(k, dunders=False)
    ['aa', 'ab', 'ba', 'bb']

- When running in the Python interactive interpreter, the dunder filter
  is configurable by setting a flag on the ``edir`` object. You can
  choose between "default on" and "default off":

    * If ``edir.dunders`` is missing or a true value, dunder methods
      are returned by default;
    * If ``edir.dunders`` is a false value, dunder methods are
      suppressed by default.

  This intentionally only works in the interactive interpreter.

- Optionally search the object's metaclass with a keyword-only argument:

    >>> 'mro' in edir(None, meta=False)
    False
    >>> 'mro' in edir(None, meta=True)
    True


The ``edir`` function is designed to optionally shadow or monkey-patch
the builtin ``dir`` function, if desired. This should be done from the
user's startup file.
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


def _interactive():
    return hasattr(sys, 'ps1')


def _ismagic(s):
    return s.startswith('_')


def _isdunder(s):
    D = '__'
    return s.startswith(D) and s.endswith(D)


def _pop(t, d=MISSING):
    """Pop the first item from sequence t.

    Returns both the first item and the tail of the sequence:

    >>> t = (2, 3, 4, 5)
    >>> item, t = _pop(t)
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
    """Return a list of attribute names of obj.

    If meta is a true value, the object's metaclass attributes will
    also be included.
    """
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
    invert = case_sensitive = False
    if glob.startswith('!='):
        invert = case_sensitive = True
        glob = glob[2:]
    elif glob.startswith('!'):
        invert = True
        glob = glob[1:]
    elif glob.startswith('='):
        case_sensitive = True
        glob = glob[1:]
    if not case_sensitive:
        glob = casefold(glob)
    match = _matcher(glob, invert)
    if case_sensitive:
        names = [nm for nm in names if match(nm)]
    else:
        names = [nm for nm in names if match(casefold(nm))]
    return names


def _matcher(glob, invert):
    """Factory function returning a match function.

    >>> f = _matcher("", False)
    >>> type(f) is type(lambda: None)
    True

    """
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


def _filter_magic(names, omit):
    """Keep or omit magic (private and dunder) names.

    >>> L = ['a', '_b', 'c_', '__d__']
    >>> _filter_magic(L, 0)
    ['a', '_b', 'c_', '__d__']
    >>> _filter_magic(L, 1)
    ['a', '_b', 'c_']
    >>> _filter_magic(L, 2)
    ['a', 'c_']

    """
    if omit not in (0, 1, 2):
        raise ValueError('omit must be one of 0, 1 or 2')
    if omit == 2:
        return [nm for nm in names if not _ismagic(nm)]
    elif omit == 1:
        return [nm for nm in names if not _isdunder(nm)]
    else:
        assert omit == 0
        return names


def edir(*args, **kwargs):
    """edir([object [, glob] [, omit=2] [, meta=False]])

    Enhanced version of the ``dir`` builtin which takes four optional
    arguments:

        object      The object whose attribute names will be returned.
                    (Positional only.)

        glob        Return names matching this glob or substring.
                    (Positional or keyword.)

        omit        Omit magic (private and dunder) names.
                    (Keyword only.)

                    With ``omit=0``, no magic names are omitted. For
                    compatibility with the built-in ``dir``, this is
                    the default. In interactive mode, that default can
                    be customised. (See below.)

                    With ``omit=1``, dunder names (e.g. "__str__") will
                    be omitted. With ``omit=2``, all names beginning
                    with one or more underscores (e.g. "_private") will
                    be omitted.

                    If not supplied, the default value for ``omit`` is
                    0. Only when Python is running in the interactive
                    interpreter, if the ``edir.omit`` attribute exists,
                    it is taken as the default.

        meta        If a true value, include attributes of the object's
                    metaclass, otherwise, don't (the default).
                    (Keyword only.)

    If the object is not given, return the names in the current scope.
    Otherwise return an alphabetized list of names comprising some of the
    attributes of the given object, and of attributes reachable from it.
    If the object supplies a method named __dir__, it will be used;
    otherwise the default dir() logic is used and returns:

        - for a module object: the module's attributes;

        - for a class object:  its attributes, and recursively the
          attributes of its bases;

        - for any other object: its attributes, its class's attributes, and
          recursively the attributes of its class's base classes.

    If string argument ``glob`` is given, only attributes matching that
    string will be returned. Matches are case-insensitive by default.
    Globs support the following metacharacters:

        - Wildcards: '?' to match a single character, '*' to match
          zero or more characters.

        - Character sets: e.g. '[abc]' to match any of 'a', 'b', 'c',
          or '[!abc]' to match any character except 'a', 'b', 'c'.

        - Reverse matching: if the glob begins with '!' or '!=', the
          sense of the match is reversed to "don't match".

        - Case-sensitive matching: if the glob begins with '=' or '!=',
          perform a case-sensitive match.

    If ``glob`` contains no metacharacters, a straight substring match
    is performed.

    If keyword-only argument ``dunders`` is a false value, dunder names
    like "__str__" are suppressed. If it is a true value (the usual
    default), they are included. If not given, the default depends on
    whether we are running in the interactive interpeter or not. In
    interactive mode, the default is taken from ``edir.dunders`` if it
    exists, and True otherwise; in non-interactive mode, ``edir.dunders``
    is ignored and the default is always True.

    If keyword-only argument ``meta`` is a true value, attributes reachable
    from the object's metaclass will also be included. By default,
    metaclass attributes are not included.

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
    omit = kwargs.pop('omit', None)
    if omit is None:
        # Credit, or blame, for this to Cameron Simpson, who makes a
        # good(?) case that having a configurable default is harmful
        # when running non-interactively.
        if _interactive():
            # Get the default from a flag on the function. We use an
            # attribute rather than setting a global variable for two
            # reasons: encapsulation, and convenience.
            omit = getattr(edir, 'omit', 0)
        else:
            omit = 0
    if kwargs:
        raise TypeError('unexpected keyword argument')
    if obj is MISSING:
        # Get the locals of the caller's caller. This may not work 
        # under some implementations such as Jython.
        # Note that calling builtin dir() won't work, because the locals it
        # sees will be those of *this* function, not the caller.
        names = sorted(sys._getframe(1).f_locals)
    else:
        names = _getattrnames(obj, meta)
    names = _filter(names, glob)
    names = _filter_magic(names, omit)
    return names

