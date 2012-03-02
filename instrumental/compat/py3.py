exec_f = exec
def execfile(path, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = {}
        if locals_ is None:
            locals_ = {}
        with open(path, 'r') as script:
            return exec(script.read(), globals_, locals_)
