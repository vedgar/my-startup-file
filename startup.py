# -*- coding: utf-8 -*-

#=============================================================#
#          P Y T H O N   S T A R T U P   S C R I P T          #
#=============================================================#

# Keep this module compatible with Python 2.4 and better.

from __future__ import division

# === Basic functionality ===

# Pre-import useful modules.
import math, os, sys

try:
    import builtins  # Python 3.x
except ImportError:
    # Python 2.x
    import __builtin__ as builtins


# Change the main prompt.
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

# Bring back reload in Python 3.
try:
    reload
except NameError:
    from imp import reload

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

# === Add globbing to dir() ===
try:
    sys._getframe()
except (AttributeError, NotImplementedError):
    # Not all implementations support _getframe; in particular,
    # IronPython does not support it by default.
    print('*** warning: no frame support; globbing dir not available ***')
else:
    try:
        from enhanced_dir import globbing_dir as dir
    except ImportError:
        print('*** warning: globbing dir not available ***')


# === Simple benchmarking ===
try:
    from timer import Timer
except ImportError:
    print('*** warning: Timer not available ***')


# === Command line completion and history ===
try:
    import history
except ImportError:
    print('*** warning: command line history not available ***')
else:
    history = history.History()

try:
    import completer
except ImportError:
    print('*** warning: command line completion not available ***')
else:
    completer = completer.Completer(
                    bindings=(r'"\C-xo": overwrite-mode',
                              r'"\C-xd": dump-functions',
                              )
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

