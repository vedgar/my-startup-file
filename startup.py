# -*- coding: utf-8 -*-

#=============================================================#
#          P Y T H O N   S T A R T U P   S C R I P T          #
#=============================================================#

# Keep this module compatible with Python 2.4 and better.

from __future__ import division

# === Basic functionality ===

# Pre-import useful modules.
import math, os, sys, unicodedata

try:
    import builtins  # Python 3.x
except ImportError:
    # Python 2.x
    import __builtin__ as builtins


# Change the main prompt. Consider using '≻≻≻ '?
if sys.version_info[0] >= 3 and os.name == 'posix':
    # Make the main prompt bold in Python 3. This probably won't
    # work on Windows, put it should(?) work on any POSIX system.
    sys.ps1 = '\001\x1b[1m\002py> \001\x1b[0m\002'
else:
    sys.ps1 = 'py> '


# Include special values. Prior to Python 2.6, this was messy, platform-
# dependent, and not guaranteed to work.
try:
    INF = float('inf')
    NAN = float('nan')
except ValueError:
    # Possibly Windows prior to Python 2.6.
    try:
        INF = float('1.#INF')
        NAN = float('1.#IND')  # Indeterminate.
    except ValueError:
        # Desperate times require desperate measures...
        try:
            INF = 1e3000  # Hopefully, this should overflow to INF.
            NAN = INF-INF  # And this hopefully will give a NaN.
        except (ValueError, OverflowError):
            # Just give up.
            print('*** warning: unable to define INF and/or NAN floats ***')

# I always forget the name of an EBCDIC codec.
# This is an aide-mémoire more than anything else.
EBCDIC = 'cp500'

# Bring back reload in Python 3.
try:
    reload
except NameError:
    from imp import reload

# And reduce.
try:
    reduce
except NameError:
    from functools import reduce

# And cmp.
try:
    cmp
except NameError:
    def cmp(a, b):
        """Return negative if a<b, zero if a==b, positive if a>b."""
        return (b < a) - (a < b)

# Monkey-patch the math module *wicked grin*
try:
    # Don't touch it if already defined.
    math.tau
except AttributeError:
    math.tau = 2*math.pi  # τ = 2π

# === Add enhancements to dir() ===
try:
    sys._getframe()
except (AttributeError, NotImplementedError):
    # Not all implementations support _getframe; in particular,
    # IronPython on some platforms may not support it by default.
    print('*** warning: no frame support; enhanced dir not available ***')
else:
    try:
        from enhanced_dir import edir
        builtins.dir = edir
        del edir
    except ImportError:
        print('*** warning: enhanced dir not available ***')


# === Simple benchmarking ===
try:
    from timer import Stopwatch
except ImportError:
    print('*** warning: Stopwatch not available ***')


# === Command line completion and history ===
try:
    from tabhistory import completer, history
except ImportError:
    print('*** warning: tab completion and command line history'
          ' not available ***')
else:
    completer.bind(r'"\C-xo": overwrite-mode',
                   r'"\C-xd": dump-functions',
                   )


# === Enable and disable comprehensive tracebacks ===

# Set the USE_LARGE_TRACEBACKS global to a true value to use large tracebacks.
USE_LARGE_TRACEBACKS = False  # Default to standard tracebacks.
def _set_tb_handler():
    import cgitb
    std_handler = sys.excepthook or sys.__excepthook__
    big_handler = cgitb.Hook(display=1, logdir=None, context=5, format='text')
    def handler(etype, evalue, etb):
        if globals().get('USE_LARGE_TRACEBACKS'):
            return big_handler(etype, evalue, etb)
        else:
            return std_handler(etype, evalue, etb)
    sys.excepthook = handler

_set_tb_handler()


print("=== startup script executed ===")

