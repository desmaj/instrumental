import sys

import ast

if sys.version_info[0] < 3:
    # Learned this trick from coveragepy (thanks, Ned)
    # Since the exec statement is a syntax error in Py3,
    # we'll wrap it up in an eval'd string literal.
    eval(
        compile(
            "def exec_f(object_, globals_={}, locals_={}):"
            "    exec object_ in globals_, locals_"
            )
        )
else:
    exec_f = exec
    def execfile(path, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = {}
        if locals_ is None:
            locals_ = {}
        with open(path, 'r') as script:
            return exec(script.read(), globals_, locals_)
