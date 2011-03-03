import ast
import imp
import os
import re
import sys

from astkit.render import SourceCodeRenderer

class ModuleLoader(object):
    
    def __init__(self, fullpath, visitor_factory):
        self.fullpath = fullpath
        self.visitor_factory = visitor_factory
    
    def _get_code(self, fullname):
        ispkg = self.fullpath.endswith('__init__.py')
        code_str = file(self.fullpath, 'r').read()
        code_tree = ast.parse(code_str)
        visitor = self.visitor_factory(fullname)
        new_code_tree = visitor.visit(code_tree)
        #print ast.dump(new_code_tree, include_attributes=True)
        #with file('.source', 'w') as f:
        #    f.write("************%s\n" % self.fullpath)
        #    f.write(SourceCodeRenderer.render(new_code_tree) + "\n\n\n")
        #SourceCodeRenderer.render(new_code_tree)
        #print "Instrumented %s" % fullname
        code = compile(new_code_tree, self.fullpath, 'exec')
        #print "Compiled %s" % fullname
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
    
    def __init__(self, target, visitor_factory):
        self.target = target
        self.visitor_factory = visitor_factory
    
    def find_module(self, fullname, path=[]):
        #print "find_module(%s, path=%r)" % (fullname, path)
        if not re.match(self.target, fullname):
            return None
        
        if path:
            for directory in path:
                module_path = os.path.join(directory, fullname.split('.')[-1]) + ".py"
                if os.path.exists(module_path):
                    loader = ModuleLoader(module_path, self.visitor_factory)
                    return loader
                
                package_path = os.path.join(directory, fullname.split('.')[-1], '__init__.py')
                if os.path.exists(package_path):
                    loader = ModuleLoader(package_path, self.visitor_factory)
                    return loader
