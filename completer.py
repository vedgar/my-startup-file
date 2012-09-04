"""Command line completion and history."""

# Keep this module compatible with Python 2.4 and better.

try:
    # Everything depends on readline.
    import readline
except ImportError:
    # May be Windows. Try using a substitute.
    import pyreadline as readline

import binascii
import os
import rlcompleter
import sys

# Location of the history file.
hist_file = os.path.join(os.path.expanduser("~"), ".pyhist")

# Set up command line completion and history.
class Completer(rlcompleter.Completer):
    """Enables TAB insertion if there is no text for completion."""
    def __init__(self, tab='\t'):
        self.tab = tab
        self._hist_file = hist_file
        rlcompleter.Completer.__init__(self)
    def complete(self, text, state):
        if text == '' or text.isspace():
            readline.insert_text(self.tab)
            return None
        else:
            return rlcompleter.Completer.complete(self, text, state)
    @property
    def hist_file(self):
        return self._hist_file

completer = Completer()

# Bind the TAB key to the completer. The way you do it depends on the
# underlying readline library.
if 'libedit' in readline.__doc__:
    # May be OS-X or *BSD. See http://bugs.python.org/issue10666
    # FIXME is there a better test than this?
    # Perhaps use something like sys.platform == DARWIN?
    cmd = "bind ^I rl_complete"
else:
    cmd = "tab: complete"

readline.parse_and_bind(cmd)
readline.set_completer(completer.complete)

s = ('4e4f424f4459206578706563747320746865205'
     '370616e69736820496e717569736974696f6e21')
if sys.version >= '3':
    s = binascii.unhexlify(bytes(s, 'ascii')).decode('ascii')
else:
    s = s.decode('hex')
# The next few bindings may not work correctly on libedit-based systems.
readline.parse_and_bind(r'"\C-xi": "%s"' % s)
readline.parse_and_bind(r'"\C-xo": overwrite-mode')
readline.parse_and_bind("set completion-query-items 30")

# Restore history file (if any) and set the length.
try:
    readline.read_history_file(hist_file)
except (IOError, OSError):
    pass
readline.set_history_length(500)

# And save the history file when leaving.
import atexit
atexit.register(readline.write_history_file, hist_file)

# Clean up after ourselves.
# (Don't delete readline, rlcompleter or completer.)
del atexit, binascii, cmd, hist_file, s

