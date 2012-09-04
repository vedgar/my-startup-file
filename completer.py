"""Command line completion and history."""

# Keep this module compatible with Python 2.4 and better.

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
DEFAULT_HISTFILE = "~/.pyhist"

# Set up command line completion and history:
class Completer(rlcompleter.Completer):
    """Readline completer.

    * Uses the TAB key for text completion.
    * At the start of the line, TAB key inserts a tab character.
    * Sets Ctrl-X-O to toggle overwrite mode.
    * Enables command line history.

    Call the completer.run() method to activate text completion and history.
    """
    def __init__(self, histfile=None, histlen=500, tab='\t', items=30):
        if histfile is None:
            histfile = DEFAULT_HISTFILE
        histfile = os.path.expanduser(histfile)
        self.histfile = histfile
        self.histlen = histlen
        self.tab = tab
        self.items = items
        rlcompleter.Completer.__init__(self)

    def complete(self, text, state):
        if text == '' or text.isspace():
            readline.insert_text(self.tab)
            return None
        else:
            return rlcompleter.Completer.complete(self, text, state)

    def bind_tab(self):
        # Bind the TAB key to the completer. The way to do this depends on
        # the underlying readline library.
        if 'libedit' in readline.__doc__:
            # May be OS-X or *BSD. See http://bugs.python.org/issue10666
            # FIXME is there a better test than this?
            # Perhaps use something like sys.platform == DARWIN?
            cmd = "bind ^I rl_complete"
        else:
            cmd = "tab: complete"
        readline.parse_and_bind(cmd)
        readline.set_completer(self.complete)

    def bind_others(self):
        # Bind assorted other useful things. This is a bit of a hodge-podge.
        s = ('4e4f424f4459206578706563747320746865205'
             '370616e69736820496e717569736974696f6e21')
        if sys.version >= '3':
            s = binascii.unhexlify(bytes(s, 'ascii')).decode('ascii')
        else:
            s = s.decode('hex')
        # FIXME The next few bindings may not work correctly on
        # libedit-based systems.
        readline.parse_and_bind(r'"\C-xi": "%s"' % s)
        readline.parse_and_bind(r'"\C-xo": overwrite-mode')
        readline.parse_and_bind("set completion-query-items %d" % self.items)

    def save_history(self, filename=None):
        """Save command line history to the history file."""
        if filename is None:
            filename = self.histfile
        if filename:
            readline.write_history_file(filename)

    def read_history(self, filename=None):
        """Read the history file (if any)."""
        if filename is None:
            filename = self.histfile
        if filename:
            try:
                readline.read_history_file(filename)
            except (IOError, OSError):
                pass

    def run(self):
        """Set tab completion and command line history."""
        self.bind_tab()
        self.bind_others()
        self.read_history()
        # Set the maximum length for the history file.
        readline.set_history_length(self.histlen)
        # Save the history file when leaving.
        atexit.register(readline.write_history_file, self.histfile)


# Create a new completer object, but don't enable completion yet.
completer = Completer()

