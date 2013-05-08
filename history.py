import atexit
import readline
import os


class History(object):
    """Enable and control command line history.

    Some examples of usage:

    - Create a History object with a default history file:

    >>> history = History()

    - Read any saved history lines, and write history lines back again
    on exiting:

    >>> history.enable()

    - Display the last few history lines, with line numbers:

    >>> history(3)
    120: do_this()
    121: do_that()
    122: do_something_else()

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

    def enable(self, filename=None, length=None):
        """Enable writing of command line history and read the history
        file into the history buffer.

        If ``filename`` is given, history is read from it, and on exit,
        history will be written back to it. If it is not given, the
        instance attribute ``history_file`` is used as the default.

        If ``length`` is given, the history will be limited to that
        many lines when writing back to the file. Use a negative number
        for unlimited lines. If it is not given, the instance attribute
        ``history_length`` is used as the default.
        """
        if filename is None:
            filename = self.history_file
        if length is None:
            length = self.history_length
        self.read_history(filename)
        readline.set_history_length(length)
        # Save the history file when exiting.
        atexit.register(readline.write_history_file, filename)

    def read_history(self, filename=None):
        """Read history from the named file (if possible).

        If filename is None or not given, use the ``history_file``
        instance attribute.

        History lines read are appended to the current history buffer.
        To replace the current buffer, use the ``load_history`` method
        instead.
        """
        if filename is None:
            filename = self.history_file
        try:
            readline.read_history_file(filename)
        except (IOError, OSError):
            pass

    def load_history(self, filename=None):
        """Clear the current history buffer, then load history from
        the named file (if possible).

        If filename is None or not given, use the ``history_file``
        instance attribute.
        """
        self.clear()
        self.read_history(filename)

    def clear(self):
        """Clear the current history buffer."""
        readline.clear_history()
        
    def write_history(self, filename=None):
        """Write command line history to the named file without waiting
        for program exit.

        If ``filename`` is None or not given, use the ``history_file``
        instance attribute.
        """
        if filename is None:
            filename = self.history_file
        readline.write_history_file(filename)

    def get_history_lines(self, start=1, end=None):
        """Yield history lines between ``start`` and ``end`` inclusive.

        Unlike Python indexes, the readline history lines are numbered
        from 1. If not given, ``start`` defaults to 1, and ``end``
        defaults to the current history length.
        """
        if end is None:
            end = readline.get_current_history_length()
        get = readline.get_history_item
        return (get(i) for i in range(start, end+1))
        
    def __call__(self, count=None, show_line_numbers=True):
        """Print the latest ``count`` lines from the history.

        If ``count`` is None or not given, a default number of lines
        is shown, given by the attribute MAX_LINES_TO_SHOW. Use a
        negative count to show unlimited lines.

        By default, line numbers are shown.
        """
        if count is None:
            count = self.MAX_LINES_TO_SHOW
        end = readline.get_current_history_length()
        if count < 0:
            start = 1
        else:
            start = end - count + 1
        nums = range(start, end+1)
        lines = self.get_history_lines(start, end)            
        if show_line_numbers:
            template = "{lineno:3d}:  {line}"
        else:
            template = "{line}"
        for i, line in zip(nums, lines):
            print(template.format(lineno=i, line=line))

