"""Enable and control command-line history.

This module relies on the ``readline`` module. When ``readline`` is not
available, e.g. under Windows, it may work using the third-party
``pyreadline`` module (untested).

Any text file can be used as a history file, each line in the file is
considered one history command.

Creating a ``History`` instance enables command-line history, reads in any
contents of the history file, and prepares to write history back to that
file when Python exits. Calling ``History()`` with no arguments uses the
default history file:

>>> history = History()  #doctest: +SKIP


See the ``History`` class for details on the arguments accepted.

You can display the last few commands by calling the instance:

>>> history(4)  #doctest: +SKIP
119: x = spam(23) + eggs(42)
120: do_this()
121: do_that()
122: do_something_else()


You can read lines from a history file at any time. The ``read_history``
method keeps any existing lines in the current history buffer; the
``load_history`` method replaces the current buffer.

You can write the current history buffer to a file at any time by calling
the ``write_history`` method. The number of lines written is controlled
by the readline ``set_history_length`` function.
"""

# Keep this module compatible with Python 2.4 and better.


try:
    # Everything depends on readline.
    import readline
except ImportError:
    # May be Windows, so try using a substitute.
    import pyreadline as readline

import atexit
import os


class History(object):
    """Enable and control command-line history.

    Arguments:

    history_file::
        Name of the history file to use. If not given, the attribute
        DEFAULT_HISTORY_FILE (defaults to '.python_history' in the
        user's home directory) is used.

    history_length::
        The maximum number of lines which will be saved to the history
        file. If not given, the attribute DEFAULT_HISTORY_LENGTH
        (defaults to 500) is used.

    """

    DEFAULT_HISTORY_FILE = '~/.python_history'
    DEFAULT_HISTORY_LENGTH = 500
    MAX_LINES_TO_SHOW = 10  # Use < 0 for unlimited.

    def __init__(self, history_file=None, history_length=None):
        if history_file is None:
            history_file = self.DEFAULT_HISTORY_FILE
        history_file = os.path.expanduser(history_file)
        self.history_file = history_file
        if history_length is None:
            history_length = self.DEFAULT_HISTORY_LENGTH
        self.history_length = history_length
        self._enable()
        
    def _enable(self):
        filename = self.history_file
        self.read_history(filename)
        readline.set_history_length(self.history_length)
        # Save the history file when exiting.
        atexit.register(readline.write_history_file, filename)

    def read_history(self, filename=None):
        """Read history from the named file (if possible).

        If filename is None or not given, use the ``history_file``
        instance attribute.

        History lines read are appended to the current history buffer.
        To replace the current buffer, use the ``load_history`` method.
        """
        if filename is None:
            filename = self.history_file
        try:
            readline.read_history_file(os.path.expanduser(filename))
        except (IOError, OSError):
            pass

    def load_history(self, filename=None):
        """Clear the current history buffer, then load history from
        the named file (if possible).

        If filename is None or not given, use the ``history_file``
        instance attribute.

        To read history lines without overwriting the current buffer,
        use the ``read_history`` method.
        """
        readline.clear_history()
        self.read_history(filename)

    def write_history(self, filename=None):
        """Write command line history to the named file without waiting
        for program exit.

        If ``filename`` is None or not given, use the ``history_file``
        instance attribute.
        """
        if filename is None:
            filename = self.history_file
        readline.write_history_file(os.path.expanduser(filename))

    def get_history_lines(self, start=1, end=None):
        """Yield history lines between ``start`` and ``end`` inclusive.

        Unlike Python indexes, the readline history lines are numbered
        from 1. If not given, ``start`` defaults to 1, and ``end``
        defaults to the current history length.
        """
        get = readline.get_history_item
        if end is None:
            end = readline.get_current_history_length()
        return (get(i) for i in range(start, end+1))
        
    def __call__(self, count=None, show_line_numbers=True):
        """Print the latest ``count`` lines from the history.

        If ``count`` is None or not given, a default number of lines
        is shown, given by the attribute MAX_LINES_TO_SHOW. Use a
        negative count to show unlimited lines.

        If ``show_line_numbers`` is true (the default), each history
        line is preceeded by the line number.
        """
        if count is None:
            count = self.MAX_LINES_TO_SHOW
        end = readline.get_current_history_length()
        if count < 0:
            start = 1
        else:
            start = max(end - count + 1, 1)
        nums = range(start, end+1)
        lines = self.get_history_lines(start, end)
        if show_line_numbers:
            # Can't use {} formatting as we have to support 2.4 and 2.5.
            template = "%(lineno)3d:  %(line)s"
        else:
            template = "%(line)s"
        for i, line in zip(nums, lines):
            print(template % {'lineno':i, 'line':line})

