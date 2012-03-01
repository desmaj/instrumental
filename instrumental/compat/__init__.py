import sys

import ast

if sys.version_info[0] < 3:
    # Learned this trick from coveragepy (thanks, Ned)
    # Since the exec statement is a syntax error in Py3,
    # we'll wrap it up in an eval'd string literal.
    eval(
        compile(
            """def exec_f(object_, globals_=None, locals_=None):
                if not globals_ and locals_:
                   frame = inspect.stack()[1][0]
                   globals_ = frame.f_globals
                   locals_ = frame.f_locals
                elif globals_ and not locals_:
                    locals_ = globals_
                exec object_ in globals_, locals_""",
            '<string>',
            'exec'
            )
        )
else:
    eval(
        compile(
            "exec_f = exec\n"
            """def execfile(path, globals_=None, locals_=None):
                    if globals_ is None:
                        globals_ = {}
                    if locals_ is None:
                        locals_ = {}
                    with open(path, 'r') as script:
                        return exec(script.read(), globals_, locals_)""",
            '<string>',
            'exec'
        )
    )
