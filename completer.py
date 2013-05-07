"""Command line completion and history.

Install a readline completer with the following features:

* By default, use the TAB key for text completion.
* Any readline-compatible key combination can be used.
* When TAB is used for completion, pressing TAB at the start of the
  line will indent as normal.
* Choice of indenting with tabs or spaces (default is tabs).
* Enable command line history (by default, 500 lines of history).
* Enable a few other useful readline bindings.

This relies on the readline and rlcompleter modules. Under Windows, readline
does not exist, but you may be able to use the third-party pyreadline
module in its place (untested).

Put this in your PYTHONSTARTUP file to have completion enabled automatically
with the default settings:

    from completer import completer
    completer.enable()

See your system documentation for more information about readline and tab
completion.
"""

# Keep this module compatible with Python 2.4 and better.


# TODO: add "operate and go next" functionality like in bash.


try:
    # Everything depends on readline.
    import readline
except ImportError:
    # May be Windows, so try using a substitute.
    import pyreadline as readline

import atexit
import binascii
import os
import rlcompleter
import sys

# Default location of the history file.
# FIXME support XDG base directory specification.
# http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
DEFAULT_HISTFILE = "~/.pyhist"

# Set up command line completion and history:
class Completer(rlcompleter.Completer):
    """Readline tab completer with support for indenting and history.

    Call the ``instance.enable()`` method to activate.

    Use ``instance.read_history(filename)`` to read the command line
    history from the optionally given file. If no filename is given,
    defaults to ``instance.history_file``.

    Use ``instance.save_history(filename)`` to save the current state of
    the command line history to the optionally given file. If no filename is
    given, defaults to ``instance.history_file``.
    """
    def __init__(self, namespace=None,
                # Tab completion:
                complete_key=None, indent='\t', completer_query_items=30,
                # Command-line history:
                history_file=None, history_length=500,
                # Extra bindings:
                enable_extras=True,
                ):
        # This is a classic class in Python 2.x, so no super().
        rlcompleter.Completer.__init__(self, namespace)
        self.complete_key = complete_key
        self.indent = indent
        self.completer_query_items = completer_query_items
        if history_file is None:
            history_file = DEFAULT_HISTFILE
        history_file = os.path.expanduser(history_file)
        self.history_file = history_file
        self.history_length = history_length
        self.enable_extras = enable_extras

    def tab_complete(self, text, state):
        """Tab completion with support for indenting.

        At the start of a line, insert an indent. Otherwise perform a
        tab completion.
        """
        if text == '' or text.isspace():
            readline.insert_text(self.indent)
            return None
        return rlcompleter.Completer.complete(self, text, state)

    def bind_completer(self, key=None):
        """Bind the given key as the completer.

        key should be a key combination in the appropriate syntax for your
        readline library. If key is None, it defaults to the TAB key, 'tab'
        when using libreadline and '^I' when using libedit, and will also
        indent at the start of a line. Otherwise the key is used exactly as
        given, there is no special behaviour at the start of the line, and
        pressing the TAB key will insert a tab.
        """
        if key is None:
            completer = self.tab_complete
        else:
            # Remove the previous completer installed by rlcompleter.
            readline.set_completer(None)
            ns = getattr(self, 'namespace', None)
            completer = rlcompleter.Completer(ns).complete
        if self.using_libedit():
            cmd = 'bind %s rl_complete' % (key or '^I')
        else:
            cmd = '%s: complete' % (key or 'tab')
        readline.parse_and_bind(cmd)
        readline.set_completer(completer)

    def using_libedit(self):
        """Return True if the underlying readline library is libedit."""
        # This tests for the libedit library instead of libreadline, which
        # may indicate OS-X or *BSD - See http://bugs.python.org/issue10666
        # FIXME This is the canonical test as suggested by the docs, but
        # surely there is a better test than this? Perhaps something like
        # sys.platform == DARWIN?
        return 'libedit' in readline.__doc__

    def set_query_items(self, items):
        readline.parse_and_bind("set completion-query-items %d" % items)

    def bind_extras(self):
        """Set up a few assorted extra readline bindings.

        This is a fairly arbitrary set of useful things and is a bit of a
        hodge-podge, and may not work correctly on libedit-based systems.

        Binds:

            Ctrl-X o  =>  overwrite mode
            Ctrl-X d  =>  dump current bindings to the screen
            Ctrl-X i  =>  a surprising easter-egg

        """
        s = ('4e4f424f4459206578706563747320746865205'
             '370616e69736820496e717569736974696f6e21')
        if sys.version >= '3':
            s = binascii.unhexlify(bytes(s, 'ascii')).decode('ascii')
        else:
            s = s.decode('hex')
        readline.parse_and_bind(r'"\C-xi": "%s"' % s)
        readline.parse_and_bind(r'"\C-xo": overwrite-mode')
        readline.parse_and_bind(r'"\C-xd": dump-functions')

    def enable_history(self, history_file, history_length):
        """Enable command line history."""
        self.read_history(history_file)
        readline.set_history_length(history_length)
        # Save the history file when exiting.
        atexit.register(readline.write_history_file, history_file)

    def save_history(self, filename=None):
        """Save command line history to the given history file right now.

        If filename is None or not given, use the ``history_file`` instance
        attribute.
        """
        if filename is None:
            filename = self.history_file
        if filename:
            readline.write_history_file(filename)

    def read_history(self, filename=None):
        """Read history from the named file (if possible).

        If filename is None or not given, use the ``history_file`` instance
        attribute.
        """
        if filename is None:
            filename = self.history_file
        if filename:
            try:
                readline.read_history_file(filename)
            except (IOError, OSError):
                pass

    def enable(self):
        """Set tab completion and command line history."""
        self.bind_completer(self.complete_key)
        self.set_query_items(self.completer_query_items)
        if self.enable_extras:
            self.bind_extras()
        if self.history_file:
            self.enable_history(self.history_file, self.history_length)



# Create a new completer object, but don't enable completion yet.
completer = Completer()

