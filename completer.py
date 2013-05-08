"""Command line completion.

Install a readline completer with the following features:

* By default, use the TAB key for text completion.
* Any readline-compatible key combination can be used.
* When TAB is used for completion, pressing TAB at the start of the
  line will indent as normal.
* Choice of indenting with tabs or spaces (default is tabs).
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

import rlcompleter


# Set up command line completion:
class Completer(rlcompleter.Completer):
    """Readline tab completer with support for indenting.

    Call the ``instance.enable()`` method to activate.
    """
    def __init__(self, namespace=None,
                # Tab completion:
                complete_key=None, indent='\t', completer_query_items=30,
                # Extra bindings:
                enable_extras=True,
                ):
        # This is a classic class in Python 2.x, so no super().
        rlcompleter.Completer.__init__(self, namespace)
        self.complete_key = complete_key
        self.indent = indent
        self.completer_query_items = completer_query_items
        self.enable_extras = enable_extras

    def tab_complete(self, text, state):
        """Tab completion with support for indenting.

        At the start of a line, insert an indent. Otherwise perform a
        tab completion.
        """
        # TODO: Add filename completion.
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
        #
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
        s = ('\x4e\x4f\x42\x4f\x44\x59\x20\x65\x78\x70\x65\x63\x74'
             '\x73\x20\x74\x68\x65\x20\x53\x70\x61\x6e\x69\x73\x68'
             '\x20\x49\x6e\x71\x75\x69\x73\x69\x74\x69\x6f\x6e\x21')
        readline.parse_and_bind(r'"\C-xi": "%s"' % s)
        readline.parse_and_bind(r'"\C-xo": overwrite-mode')
        readline.parse_and_bind(r'"\C-xd": dump-functions')

    def enable(self):
        """Set tab completion."""
        self.bind_completer(self.complete_key)
        self.set_query_items(self.completer_query_items)
        if self.enable_extras:
            self.bind_extras()



# Create a new completer object, but don't enable completion yet.
completer = Completer()

