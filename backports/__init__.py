# This package should remain compatible with Python 2.4.

import sys

if sys.version < '3':
    from backports.backports2 import *
else:
    from backports.backports3 import *


