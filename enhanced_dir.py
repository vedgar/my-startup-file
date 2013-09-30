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

builtin_dir = dir
_sentinel = object()


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

# Wrapper functions to handle case-insensitive matching and
# reversing the sense of the match.

def wrap_reverse(func):
    def inner(arg):
        return not func(arg)
    return inner

def wrap_case_insensitive(func):
    def inner(arg):
        return func(casefold(arg))
    return inner

def build_matcher(pattern):
    """Return a match function from the given pattern."""
    reverse = case_sensitive = False
    if pattern.startswith('!'):
        reverse = True
        pattern = pattern[1:]
    if pattern.endswith('='):
        case_sensitive = True
        pattern = pattern[:-1]
    if not case_sensitive:
        pattern = casefold(pattern)
    if any(c in pattern for c in '*?['):
        # Metacharacter searches use the fnmatchcase functions.
        # Don't use fnmatch since that is platform-dependent.
        def matcher(name):
            return fnmatchcase(name, pattern)
    else:
        def matcher(name):
            return pattern in name
    if case_sensitive:
        matcher = wrap_case_insensitive(matcher)
    if reverse:
        matcher = wrap_reverse(matcher)
    return matcher


def _enhanced_dir(obj, glob, include_metaclass):
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
    if obj is _sentinel:
        # Get the locals of the caller. This may not work under some
        # implementations such as Jython.
        return sorted(sys._getframe(1).f_locals)
        # Note that calling builtin dir() won't work, because the locals it
        # sees will be those of *this* function, not the caller.
    else:
        names = builtin_dir(obj)
        if include_metaclass:
            if isinstance(obj, type):
                meta = type(obj)
            else:
                meta = type(type(obj))
            names = sorted(set(names + builtin_dir(meta)))
    if glob is None or glob == '':
        # No filtering needed.
        return names
    else:
        matcher = build_matcher(glob)
        return [name for name in names if matcher(name)]


try:
    # In Python 3, we have syntax for keyword-only arguments. But since it
    # fails under Python 2, we use exec to compile it.
    exec("""\
def dir(obj=_sentinel, glob=None, *, include_metaclass=False):
    return _enhanced_dir(obj, glob, include_metaclass)
""")
except SyntaxError:
    # Python 2. Fall back to the old way of keyword-only arguments.
    def dir(obj=_sentinel, glob=None, **kwargs):
        include_metaclass = kwargs.pop('include_metaclass', False)
        if kwargs:
            raise TypeError('too many keyword arguments')
        return _enhanced_dir(obj, glob, include_metaclass)

dir.__doc__ = _enhanced_dir.__doc__


