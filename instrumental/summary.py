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
import os
import sys

from instrumental.constructs import BooleanDecision

def _package(modulename):
    modulepath = '%s.py' % modulename.replace('.', os.path.sep)
    if any(os.path.exists(os.path.join(path, modulepath))
           for path in sys.path):
        return '.'.join(modulename.split('.')[:-1])
    else:
        return modulename

class BaseExecutionSummary(object):
    
    def __init__(self, conditions, statements, options):
        self.conditions = conditions
        self.statements = statements
        self.options = options
        
    @property
    def decisions(self):
        return [condition for condition in self.conditions
                if condition.is_decision()]
    
    def condition_rate(self):
        total_conditions = sum(condition.number_of_conditions(self.options.report_conditions_with_literals)
                               for condition in self.conditions)
        if not total_conditions:
            return 1.0
        hit_conditions = sum(condition.number_of_conditions_hit()
                             for condition in self.conditions)
        return hit_conditions / float(total_conditions)
    
    def decision_rate(self):
        total_conditions = sum(decision.number_of_conditions(self.options.report_conditions_with_literals)
                               for decision in self.decisions)
        if not total_conditions:
            return 1.0
        hit_conditions = sum(decision.number_of_conditions_hit()
                             for decision in self.decisions)
        return hit_conditions / float(total_conditions)
    
    def statement_rate(self):
        all_statements = []
        for modulename, statement_dict in self.statements.items():
            all_statements += statement_dict.items()
        
        total_statements = len(all_statements)
        if not total_statements:
            return 1.0
        hit_statements = sum(hit for (lineno, hit) in all_statements)
        return hit_statements / float(total_statements)


class ExecutionSummary(BaseExecutionSummary):
    
    def __init__(self, conditions, statements, options):
        self.statements = statements
        self.conditions = []
        for modulename in statements:
            self.conditions += conditions[modulename].values()
        self.options = options
        self._packages = None
    
    @property
    def packages(self):
        if self._packages is None:
            _statements = {}
            _conditions = {}
            for modulename in self.statements:
                _package_name = _package(modulename)
                
                _package_statements = \
                    _statements.setdefault(_package_name, {})
                _package_statements[modulename] = self.statements[modulename]
                
                _package_conditions = \
                    _conditions.setdefault(_package_name, [])
                for condition in self.conditions:
                    if condition.modulename == modulename:
                        _package_conditions.append(condition)
            
            self._packages = \
                dict((packagename, 
                      PackageExecutionSummary(packagename,
                                              _conditions[packagename],
                                              _statements[packagename],
                                              self.options))
                     for packagename in _statements)
        return self._packages
    
class PackageExecutionSummary(BaseExecutionSummary):
    
    def __init__(self, name, conditions, statements, options):
        super(PackageExecutionSummary, self).__init__(conditions, statements, options)
        self.name = name
        self._modules = None
    
    @property
    def modules(self):
        if self._modules is None:
            self._modules = {}
            for modulename in self.statements:
                _conditions = [condition for condition in self.conditions
                               if condition.modulename == modulename]
                self._modules[modulename] = (
                    ModuleExecutionSummary(modulename,
                                           _conditions,
                                           self.statements[modulename],
                                           self.options))
        return self._modules
    

class ModuleExecutionSummary(BaseExecutionSummary):
    
    def __init__(self, name, conditions, statements, options):
        super(ModuleExecutionSummary, self).__init__(conditions, statements, options)
        self.name = name
    
    def statement_rate(self):
        total_statements = len(self.statements)
        if not total_statements:
            return 1.0
        hit_statements = sum(hit for hit in self.statements.values())
        return hit_statements / float(total_statements)
    
