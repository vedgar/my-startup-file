"""Execute backports as a runnable script.

Under Python 2.7 or better, call it using:

    python -m backports

Under Python 2.4-2.6, call it using:

    python backports/__main__.py


This runs self-tests using doctest. For more verbose output, pass '-v'
in the command line.
"""

if __name__ != '__main__':
    raise SystemExit('this is not importable')


import doctest
import sys

if sys.version.startswith('2'):
    import backports.backports2
    import backports.nt
    modules = (backports.backports2, backports.nt)
else:
    import backports.backports3
    modules = (backports.backports3, )


for module in modules:
    failures, tests = doctest.testmod(module)
    if tests == 0:
        print("no doctests found for module %s" % module.__name__)
    elif failures == 0:
        print("%d doctests passed for module %s" % (tests, module.__name__))


