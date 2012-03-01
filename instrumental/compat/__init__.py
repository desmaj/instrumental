import sys

import ast

if sys.version_info[0] < 3:
    from instrumental.compat.py2 import *
else:
    from instrumental.compat.py3 import *
