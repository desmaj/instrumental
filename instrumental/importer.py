import ast
import imp
import os
import sys

class ModuleLoader(object):
    
    def __init__(self, fullpath, visitor):
        self.fullpath = fullpath
        self.visitor = visitor
    
    def _get_code(self, fullname):
        ispkg = self.fullpath.endswith('__init__.py')
        code_str = file(self.fullpath, 'r').read()
        code_tree = ast.parse(code_str)
        new_code_tree = self.visitor.visit(code_tree)
        print "Instrumented %s" % fullname
        code = compile(new_code_tree, self.fullpath, 'exec')
        return ispkg, code
    
    def load_module(self, fullname):
        ispkg, code = self._get_code(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.fullpath
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
        exec code in mod.__dict__
        return mod

class ImportHook(object):
    
    def __init__(self, target, visitor, reload_imported=False):
        self.target = target
        self.visitor = visitor
        for module in sys.modules:
            if module.split('.')[0] == target:
                if sys.modules[module] and reload_imported:
                    self._reload_module(sys.modules[module])
        
    def _reload_module(self, module):
        fullpath = module.__file__
        if fullpath.endswith('.pyc'):
            fullpath = fullpath[:-1]
        loader = ModuleLoader(fullpath, self.visitor)
        loader.load_module(module.__name__)
    
    def find_module(self, fullname, path=[]):
        #print "find_module(%s, path=%r)" % (fullname, path)
        if not fullname.split('.')[0] == self.target:
            return None
        
        if path:
            for directory in path:
                module_path = os.path.join(directory, fullname.split('.')[-1]) + ".py"
                if os.path.exists(module_path):
                    loader = ModuleLoader(module_path, self.visitor)
                    return loader
                
                package_path = os.path.join(directory, fullname.split('.')[-1], '__init__.py')
                if os.path.exists(package_path):
                    loader = ModuleLoader(package_path, self.visitor)
                    return loader
