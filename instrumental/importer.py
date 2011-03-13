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
    
    def _get_source(self, path):
        return file(path, 'r').read()
    
    def _get_code(self, fullname):
        ispkg = self.fullpath.endswith('__init__.py')
        code_str = self._get_source(self.fullpath)
        code_tree = ast.parse(code_str)
        visitor = self.visitor_factory.create(fullname)
        new_code_tree = visitor.visit(code_tree)
        #print SourceCodeRenderer.render(new_code_tree)
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
    
    def __init__(self, target, visitor_factory):
        self.target = target
        self.visitor_factory = visitor_factory
    
    def find_module(self, fullname, path=[]):
        #print "find_module(%s, path=%r)" % (fullname, path)
        if not re.match(self.target, fullname):
            return None
        
        if not path:
            path = sys.path
        
        for directory in path:
            return self._loader_for_path(directory, fullname)
    
    def _loader_for_path(self, directory, fullname):
        module_path = os.path.join(directory, fullname.split('.')[-1]) + ".py"
        if os.path.exists(module_path):
            loader = ModuleLoader(module_path, self.visitor_factory)
            return loader
        
        package_path = os.path.join(directory, fullname.split('.')[-1], '__init__.py')
        if os.path.exists(package_path):
            loader = ModuleLoader(package_path, self.visitor_factory)
            return loader
        
