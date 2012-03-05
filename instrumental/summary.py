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
import sys

from instrumental.constructs import BooleanDecision

def _package(modulename):
    return sys.modules[modulename].__package__

class BaseExecutionSummary(object):
    
    def __init__(self, conditions, statements):
        self.decisions = dict((label, condition) for label, condition in conditions.items()
                              if isinstance(condition, BooleanDecision))
        self.conditions = conditions
        self.statements = statements
        
    def condition_rate(self):
        total_conditions = sum(condition.number_of_conditions()
                               for label, condition in self.conditions.items())
        if not total_conditions:
            return 1.0
        hit_conditions = sum(condition.number_of_conditions_hit()
                             for label, condition in self.conditions.items())
        return hit_conditions / float(total_conditions)
    
    def decision_rate(self):
        total_conditions = sum(decision.number_of_conditions()
                               for label, decision in self.decisions.items())
        if not total_conditions:
            return 1.0
        hit_conditions = sum(decision.number_of_conditions_hit()
                             for label, decision in self.decisions.items())
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
    
    def __init__(self, conditions, statements):
        super(ExecutionSummary, self).__init__(conditions, statements)
        self._packages = None
    
    @property
    def packages(self):
        if self._packages is None:
            _statements = {}
            _conditions = {}
            for modulename in self.statements:
                _package_statements = \
                    _statements.setdefault(_package(modulename), {})
                _package_statements[modulename] = self.statements[modulename]
                _package_conditions = \
                    _conditions.setdefault(_package(modulename), {})
                _package_conditions.update(\
                    dict((label, condition) 
                         for label, condition in self.conditions.items()
                         if condition.modulename == modulename)
                    )
                    
            self._packages = \
                dict((packagename, 
                      PackageExecutionSummary(packagename,
                                              _conditions[packagename],
                                              _statements[packagename]))
                     for packagename in _statements)
        return self._packages

        
class PackageExecutionSummary(BaseExecutionSummary):
    
    def __init__(self, name, conditions, statements):
        super(PackageExecutionSummary, self).__init__(conditions, statements)
        self.name = name
        self._modules = None
    
    @property
    def modules(self):
        if self._modules is None:
            _conditions = dict((modulename,
                                dict((label, condition) 
                                     for label, condition in self.conditions.items()
                                     if modulename == condition.modulename))
                                for modulename in self.statements)
            self._modules = \
                dict((modulename,
                      ModuleExecutionSummary(modulename,
                                             _conditions[modulename],
                                             self.statements[modulename]))
                      for modulename in self.statements)
        return self._modules


class ModuleExecutionSummary(BaseExecutionSummary):
    
    def __init__(self, name, conditions, statements):
        self.name = name
        super(ModuleExecutionSummary, self).__init__(conditions, statements)
    
    def statement_rate(self):
        total_statements = len(self.statements)
        hit_statements = sum(hit for (lineno, hit) in self.statements.items())
        return hit_statements / float(total_statements)

