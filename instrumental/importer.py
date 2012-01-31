import imp
import os
import re
import sys

from astkit.render import SourceCodeRenderer

from instrumental.compat import ast

class ModuleLoader(object):
    
    def __init__(self, fullpath, visitor_factory):
        self.fullpath = fullpath
        self.visitor_factory = visitor_factory
    
    def _get_source(self, path):
        return file(path, 'r').read()
    
    def _get_code(self, fullname):
        ispkg = self.fullpath.endswith('__init__.py')
        code_str = self._get_source(self.fullpath)
        self.visitor_factory.recorder.add_source(fullname, code_str)
        code_tree = ast.parse(code_str)
        visitor = self.visitor_factory.create(fullname)
        new_code_tree = visitor.visit(code_tree)
        # print SourceCodeRenderer.render(new_code_tree)
        code = compile(new_code_tree, self.fullpath, 'exec')
        return ispkg, code
    
    def load_module(self, fullname):
        ispkg, code = self._get_code(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.fullpath
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = [os.path.dirname(self.fullpath)]
        exec code in mod.__dict__
        return mod

class ImportHook(object):
    
    def __init__(self, target, ignores, visitor_factory):
        self.target = target
        self.ignores = ignores
        self.visitor_factory = visitor_factory
    
    def find_module(self, fullname, path=[]):
        # print "find_module(%s, path=%r)" % (fullname, path), 'pyramid' in sys.modules
        if ((not re.match(self.target, fullname)) 
            or
            any([re.match(ignore, fullname) for ignore in self.ignores])):
            return None
        
        if not path:
            path = sys.path
        
        for directory in path:
            loader = self._loader_for_path(directory, fullname)
            if loader:
                return loader
    
    def _loader_for_path(self, directory, fullname):
        # print "loader_for_path", directory, fullname
        module_path = os.path.join(directory, fullname.split('.')[-1]) + ".py"
        if os.path.exists(module_path):
            # print "loading module", module_path
            loader = ModuleLoader(module_path, self.visitor_factory)
            return loader
        
        package_path = os.path.join(directory, fullname.split('.')[-1], '__init__.py')
        if os.path.exists(package_path):
            print "loading package", package_path
            loader = ModuleLoader(package_path, self.visitor_factory)
            return loader
        
