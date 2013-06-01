"""Command line completion.

This module relies on both the ``readline`` and ``rlcompleter`` modules.
Under Windows, you may be able to use the third-party ``pyreadline`` module
(untested).

Creating a ``Completer`` instance enables readline completion:

>>> completer = Completer()  #doctest: +SKIP


By default, the TAB key is used for both indenting and completion. See
the ``Completer`` class for further instructions, including how to change
this behaviour.
"""

# Keep this module compatible with Python 2.4 and better.


# TODO: add "operate and go next" functionality like in bash.
# TODO: add filename completion.


try:
    # Everything depends on readline.
    import readline
except ImportError:
    # May be Windows, so try using a substitute.
    import pyreadline as readline

import rlcompleter


def using_libedit():
    """Return True if the underlying readline library is libedit."""
    # This tests for the libedit library instead of libreadline, which
    # may indicate OS-X or *BSD - See http://bugs.python.org/issue10666
    #
    # FIXME This is the canonical test as suggested by the docs, but
    # surely there is a better test than this? Perhaps something like
    # sys.platform == DARWIN?
    return 'libedit' in readline.__doc__


# Set up command line completion:
class Completer(rlcompleter.Completer):
    """Readline tab completer with optional support for indenting.

    All arguments to the class constructor are optional.

    namespace::
        None, or a namespace dict, to use for completions. See the
        ``rlcompleter`` module for more details.

    key::
        Key to use for completion. ``key`` should be a key combination
        written in the appropriate syntax for your readline library.
        If ``key`` is not given or is None, the default TAB key will be
        used:

            * if you are using libreadline, 'tab' will be used;
            * if you are using libedit, '^I' will be used.

        Any other choice for ``key`` will be used exactly as given, and
        it is your responsibility to ensure it is in the correct format
        for the underlying readline library.

    indent::
        String to insert for indents when the completer key is pressed
        at the start of the line. The default is to insert '\\t' (a
        literal tab). Another common choice is '    ' (four spaces). If
        you pass None or the empty string, pressing the completer key
        will *not* indent.

    query_items::
        The maximum number of items that the completer will show without
        asking first. The default is 30.

    bindings::
        A tuple of additional readline bindings to be parsed. As a
        convenience, if you have only one binding to use, you can pass
        it as a string rather than inside a tuple. See your operating
        system's readline documentation for syntax.

    """
    def __init__(self, namespace=None,
                # Tab completion:
                key=None, indent='\t', query_items=30,
                # Extra bindings to be used:
                bindings=(),
                ):
        # This is a classic class in Python 2.x, so no super().
        rlcompleter.Completer.__init__(self, namespace)
        self.key = key
        self.indent = indent
        self.query_items = query_items
        if isinstance(bindings, str):
            bindings = (bindings,)
        self.bindings = bindings
        self._enable()

    def completer(self, text, state):
        """Completer function with optional support for indenting.

        If self.indent is not empty or None, it will be used to indent at the
        start of lines.
        """
        # At the start of a line, indent.
        if self.indent and (text == '' or text.isspace()):
            return [self.indent, None][state]
        return rlcompleter.Completer.complete(self, text, state)

    def set_completer(self):
        """Set the completer."""
        # Remove the previous completer (possibly installed by rlcompleter).
        readline.set_completer(None)
        if using_libedit():
            cmd = 'bind %s rl_complete' % (self.key or '^I')
        else:
            cmd = '%s: complete' % (self.key or 'tab')
        readline.parse_and_bind(cmd)
        readline.set_completer(self.completer)

    def _enable(self):
        """Enable tab completion."""
        self.set_completer()
        readline.parse_and_bind(
            "set completion-query-items %d" % self.query_items)
        s = ('\x4e\x4f\x42\x4f\x44\x59\x20\x65\x78\x70\x65\x63\x74'
             '\x73\x20\x74\x68\x65\x20\x53\x70\x61\x6e\x69\x73\x68'
             '\x20\x49\x6e\x71\x75\x69\x73\x69\x74\x69\x6f\x6e\x21')
        readline.parse_and_bind(r'"\C-xi": "%s"' % s)
        for binding in self.bindings:
            readline.parse_and_bind(binding)

