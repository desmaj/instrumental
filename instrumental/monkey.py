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
import os
import re
import sys

from astkit import ast

from instrumental.compat import exec_f

_imp_load_module = imp.load_module
def monkey_patch_imp(targets, ignores, visitor_factory):
    imp.load_module = load_module_factory(targets, ignores, visitor_factory)

def load_module_factory(targets, ignores, visitor_factory):
    def load_module(name, fh, pathname, description):
        if ((not any([re.match(target, name) for target in targets]))
            or
            (any([re.match(ignore, name) for ignore in ignores]))):
            return _imp_load_module(name, fh, pathname, description)
        else:
            suffix, mode, type = description
            ispkg = type == imp.PKG_DIRECTORY
            if ispkg:
                source = open(os.path.join(pathname, '__init__.py'), 'r').read()
            else:
                source = fh.read()
            visitor_factory.recorder.add_source(name, source)
            code_tree = ast.parse(source)
            visitor = visitor_factory.create(name)
            new_code_tree = visitor.visit(code_tree)
            code = compile(new_code_tree, pathname, 'exec')
            mod = sys.modules.setdefault(name, imp.new_module(name))
            if ispkg:
                mod.__file__ = os.path.join(pathname, '__init__.py')
                mod.__path__ = [pathname]
            else:
                mod.__file__ = pathname
            mod.__loader__ = None
            exec_f(code, mod.__dict__)
            return mod
    return load_module
