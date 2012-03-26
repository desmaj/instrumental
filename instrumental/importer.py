# 
# Copyright (C) 2012  Matthew J Desmarais

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import imp
import logging
import os
import re
import sys

from astkit import ast
from astkit.render import SourceCodeRenderer

from instrumental.compat import exec_f

log = logging.getLogger(__name__)

class ModuleLoader(object):
    
    def __init__(self, fullpath, visitor_factory):
        self.fullpath = fullpath
        self.visitor_factory = visitor_factory
    
    def _get_source(self, path):
        """ Get the source code from a file path """
        with open(path, 'r') as f:
            source = f.read()
        return source
    
    def _get_code(self, fullname):
        """ Get the instrumented code for a module
            
            Given a dotted module name, return a tuple that looks like
            (<is the module a package>, <module's code object instrumented>)
        """
        # packages are loaded from __init__.py files
        ispkg = self.fullpath.endswith('__init__.py')
        code_str = self._get_source(self.fullpath)
        visitor = self.visitor_factory.create(fullname, code_str)
        code_tree = ast.parse(code_str)
        new_code_tree = visitor.visit(code_tree)
        log.debug(SourceCodeRenderer.render(new_code_tree))
        code = compile(new_code_tree, self.fullpath, 'exec')
        return (ispkg, code)
    
    def load_module(self, fullname):
        ispkg, code = self._get_code(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.fullpath
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = [os.path.dirname(self.fullpath)]
        exec_f(code, mod.__dict__)
        return mod

class ImportHook(object):
    """ An implementation of an import hook per PEP 302
    """
    
    def __init__(self, target, ignores, visitor_factory):
        self.target = target
        self.ignores = ignores
        self.visitor_factory = visitor_factory
    
    def find_module(self, fullname, path=[]):
        log.debug("find_module(%s, path=%r)",fullname, path)
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
        log.debug("[loader for path] directory: %s; fullname: %s",
                  directory, fullname)
        module_path = os.path.join(directory, fullname.split('.')[-1]) + ".py"
        if os.path.exists(module_path):
            log.debug("loading module from %s", module_path)
            loader = ModuleLoader(module_path, self.visitor_factory)
            return loader
        
        package_path = os.path.join(directory, fullname.split('.')[-1], '__init__.py')
        if os.path.exists(package_path):
            loader = ModuleLoader(package_path, self.visitor_factory)
            return loader
        
