import inspect

def exec_f(object_, globals_=None, locals_=None):
    if not globals_ and not locals_:
       frame = inspect.stack()[1][0]
       globals_ = frame.f_globals
       locals_ = frame.f_locals
    elif globals_ and not locals_:
        locals_ = globals_
    exec object_ in globals_, locals_
