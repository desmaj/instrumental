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
from copy import deepcopy

from astkit import ast
from astkit.render import SourceCodeRenderer

class PragmaCondition(object):
    TAG = 'P'
    
    def __str__(self):
        return self.TAG

class UnreachableCondition(object):
    TAG = 'U'
    
    def __str__(self):
        return self.TAG

class LogicalBoolean(object):
    
    def __init__(self, modulename, label, node, pragmas):
        self.modulename = modulename
        self.label = label
        self.node = deepcopy(node)
        self.pragmas = pragmas
        self.source = SourceCodeRenderer.render(node)
        self.pins = len(node.values)
        self.conditions =\
            dict((i, set()) for i in range(self.pins + 1))
        self.literals = self._gather_literals(node)
        self._set_unreachable_conditions()
        for pragma in pragmas:
            if hasattr(pragma, 'selector'):
                pragma_label = '%s.%s' % (node.lineno, pragma.selector)
                if label == pragma_label:
                    pragma.apply(self)
    
    def _gather_literals(self, node):
        _literals = {}
        for i, value in enumerate(node.values):
            # Try to determine if the condition is a literal
            # Maybe we can do something with this information?
            try:
                literal = ast.literal_eval(value)
                _literals[i] = literal
            except ValueError:
                pass
        return _literals
    
    def _set_unreachable_conditions(self):
        for condition in self.unreachable_conditions():
            self.conditions[condition].add(UnreachableCondition)
    
    @property
    def lineno(self):
        return self.node.lineno
    
    def is_decision(self):
        return False
    
    def number_of_conditions(self, report_conditions_with_literals):
        if report_conditions_with_literals:
            return len(self.conditions)
        else:
            return len(self.conditions) - len(self.unreachable_conditions())
    
    def number_of_conditions_hit(self):
        return len([value 
                    for value in self.conditions.values()
                    if value and not value == set([UnreachableCondition])])
    
    def _is_unreachable(self, condition):
        return UnreachableCondition in self.conditions[condition]
    
    def conditions_missed(self, report_conditions_with_literals):
        if report_conditions_with_literals:
            # Return the descriptions of all of the conditions either unhit
            # or marked as unreachable
            missed = [self.description(n) for n in self.conditions
                      if (not self.conditions[n]) or self._is_unreachable(n)]
        else:
            # Return the descriptions off all conditions if neither hit nor
            # marked as unreachable
            missed = [self.description(n) for n in self.conditions
                      if not (self._is_unreachable(n) or self.conditions[n])]
        return missed
    
    def _literal_warning(self):
        return ("** One or more condition combinations may not be reachable due"
                " to the presence of a literal in the decision")
    
    def _format_condition_result(self, result, length=6):
        if result == set([UnreachableCondition]):
            return UnreachableCondition.TAG
        else:
            padding = '\n' + (' ' * length)
            return padding.join(tag for tag in sorted(result))
    
    def result(self):
        lines = []
        name = "%s -> %s:%s < %s >" % (self.__class__.__name__, self.modulename, self.label, self.source)
        lines.append("%s" % (name,))
        if self.literals:
            lines.append("")
            lines.append(self._literal_warning())
        lines.append("")
        for condition in sorted(self.conditions):
            desc = self.description(condition)
            length = len(desc) + 5
            lines.append(desc +
                         " ==> " + self._format_condition_result(self.conditions[condition],
                                                                 length=length))
        return "\n".join(lines)
    
    def decision_result(self):
        lines = []
        name = "Decision -> %s:%s < %s >" % (self.modulename, self.label, self.source,)
        lines.append("%s" % (name,))
        lines.append("")
        lines.append("T ==> %s" % self._format_condition_result(self.was_true()))
        lines.append("F ==> %s" % self._format_condition_result(self.was_false()))
        return "\n".join(lines)
    
    def merge(self, other):
        for condition, results in self.conditions.items():
            results.update(other.conditions[condition])
    
class LogicalAnd(LogicalBoolean):
    """ Stores the execution information for a Logical And
        
        For an and condition with n inputs, there will be
        n + 2 recordable conditions. Condition 0 indicates
        that all inputs are True. Conditions 1 though n
        indicate that the input in the numbered position
        is False and all inputs before it are True. All
        inputs after the numbered position are, in this
        case, considered to be "don't care" since they will
        never be evaluated.
    """
    
    def unreachable_conditions(self):
        """ Return the unreachable conditions for this construct
            
            Note that conditions are reported as unreachable if they cannot
            happen due to the presence of literals in the expression *and*
            if they do not represent a situation in which later inputs are
            left unevaluated because of a literal value earlier in the
            expression.
        """
        _conditions = []
        if not self.literals.get(self.pins-1, True):
            _conditions.append(0)
        for i, literal in self.literals.items():
            if literal:
                _conditions.append(i+1)
        return _conditions
    
    def record(self, value, pin, tag):
        """ Record that a value was seen for a particular pin """
        # If the pin is not the last pin in the decision and
        # the value seen is False, then we've found the pin
        # that has forced the decision False and we should
        # record that.
        if pin < (self.pins-1):
            if not value:
                self.conditions[pin+1].add(tag)
        
        # If the pin is the last pin then we'll record that
        # it either allowed the decision to be True or it
        # is the pin that has forced the decision False.
        elif pin == (self.pins-1):
            if value:
                self.conditions[0].add(tag)
            else:
                self.conditions[self.pins].add(tag)
    
    def description(self, n):
        if n == 0:
            return " ".join("T" * self.pins)
        elif n < (self.pins + 1):
            acc = ""
            if n > 1:
                acc += " ".join("T" * (n - 1)) + " "
            acc += "F"
            if self.pins - n:
                acc += " " + " ".join("*" * (self.pins - n))
            return acc
        elif n == (self.pins + 1):
            return "Other"
    
    def was_true(self):
        return self.conditions[0]
    
    def was_false(self):
        results = set()
        for n in range(1, self.pins+1):
            results.update(self.conditions[n])
        return results
    
class LogicalOr(LogicalBoolean):
    """ Stores the execution information for a Logical Or
        
        For an or condition with n inputs, there will be
        n + 2 recordable conditions. Conditions 0 though
        n indicate that the numbered position input is
        True. Condition n indicates that all inputs are
        False. Condition n + 1 is "Other".
    """
    
    def unreachable_conditions(self):
        """ Return the unreachable conditions for this construct
            
            Note that conditions are reported as unreachable if they cannot
            happen due to the presence of literals in the expression *and*
            if they do not represent a situation in which later inputs are
            left unevaluated because of a literal value earlier in the
            expression.
        """
        _conditions = []
        for i, literal in self.literals.items():
            if not literal:
                _conditions.append(i)
        if self.literals.get(self.pins-1):
            _conditions.append(self.pins)
        return _conditions
    
    def record(self, value, pin, tag):
        """ Record that a value was seen for a particular pin """
        
        # If the pin is not the last pin in the decision
        # and the value we see is True, then we've found the
        # condition that forces the decision True in this case.
        # If the value we see is False then we'll ignore it
        # since this is not a significant case.
        if pin < (self.pins-1):
            if value:
                self.conditions[pin].add(tag)
        
        # If this is the last pin then it either allowed the
        # decision to be False or forced the decision True.
        elif pin == (self.pins-1):
            if value:
                self.conditions[pin].add(tag)
            else:
                self.conditions[self.pins].add(tag)
        
    def description(self, n):
        acc = ""
        if n < self.pins:
            if n > 0:
                acc += " ".join("F" * n) + " "
            acc += "T"
            if self.pins - n - 1:
                acc += " " + " ".join("*" * (self.pins - n - 1))
            return acc
        elif n == self.pins:
            return " ".join("F" * self.pins)
        elif n == (self.pins + 1):
            return "Other"
    
    def was_true(self):
        results = set()
        for n in range(0, self.pins):
            results.update(self.conditions[n])
        return results
    
    def was_false(self):
        return self.conditions[self.pins]
    
class BooleanDecision(object):
    
    def __init__(self, modulename, label, node, pragmas):
        self.modulename = modulename
        self.label = label
        self.node = deepcopy(node)
        self.pragmas = pragmas
        self.lineno = node.lineno
        self.source = SourceCodeRenderer.render(node)
        self.conditions = {True: set(),
                           False: set()}
        for pragma in pragmas:
            if hasattr(pragma, 'selector'):
                pragma_label = '%s.%s' % (node.lineno, pragma.selector)
                if label == pragma_label:
                    pragma.apply(self)
    
    def is_decision(self):
        return True
    
    def record(self, expression, tag):
        result = bool(expression)
        self.conditions[result].add(tag)
        return result
    
    def description(self, condition):
        return str(bool(condition))[0]
    
    def was_true(self):
        return self.conditions[True]
    
    def was_false(self):
        return self.conditions[False] 
    
    def set_unreachable(self, condition):
        self.conditions[condition].add(UnreachableCondition)
    
    def number_of_conditions(self, report_conditions_with_literals):
        if report_conditions_with_literals:
            return len(self.conditions)
        
        unreachable_conditions = 0
        for condition in self.conditions:
            for result in self.conditions[condition]:
                if (result == UnreachableCondition
                    or result == PragmaCondition.TAG):
                    unreachable_conditions += 1
                    break
        return len(self.conditions) - unreachable_conditions
    
    def number_of_conditions_hit(self):
        def is_hit(results):
            if results:
                return any(not (result == UnreachableCondition
                                or result == PragmaCondition.TAG)
                           for result in results)
            return False
        
        return len([value 
                    for value in self.conditions.values() 
                    if is_hit(value)])
    
    def conditions_missed(self, report_conditions_with_literals):
        return self.number_of_conditions(report_conditions_with_literals) - self.number_of_conditions_hit()
    
    def _format_condition_result(self, result, length=6):
        padding = '\n' + (' ' * length)
        return padding.join(str(tag) for tag in sorted(result))
    
    def result(self):
        lines = []
        name = "Decision -> %s:%s < %s >" % (self.modulename, self.label, self.source)
        lines.append("%s" % (name,))
        lines.append("")
        lines.append("T ==> %s" % self._format_condition_result(self.conditions[True]))
        lines.append("F ==> %s" % self._format_condition_result(self.conditions[False]))
        return "\n".join(lines)

    def merge(self, other):
        for condition, results in self.conditions.items():
            results.update(other.conditions[condition])
    
class Comparison(object):
    
    def __init__(self, modulename, label, node, pragmas):
        self.modulename = modulename
        self.label = label
        self.node = deepcopy(node)
        self.pragmas = pragmas
        self.lineno = node.lineno
        self.source = SourceCodeRenderer.render(node)
        self.conditions = {True: set(),
                           False: set()}
        self._set_unreachable_condition()
        
        for pragma in pragmas:
            if hasattr(pragma, 'selector'):
                pragma_label = '%s.%s' % (node.lineno, pragma.selector)
                if label == pragma_label:
                    pragma.apply(self)
    
    def _set_unreachable_condition(self):
        self._unreachable_condition = self.unreachable_condition()
        if self._unreachable_condition is not None:
            self.conditions[self._unreachable_condition].add(
                UnreachableCondition)
    
    def unreachable_condition(self):
        try:
            _left = ast.literal_eval(self.node.left)
            _right = ast.literal_eval(self.node.comparators[0])
            if isinstance(self.node.ops[0], ast.Eq):
                condition = _left != _right
            elif isinstance(self.node.ops[0], ast.NotEq):
                condition = _left == _right
            elif isinstance(self.node.ops[0], ast.Lt):
                condition = _left >= _right
            elif isinstance(self.node.ops[0], ast.LtE):
                condition = _left > _right
            elif isinstance(self.node.ops[0], ast.Gt):
                condition = _left <= _right
            elif isinstance(self.node.ops[0], ast.GtE):
                condition = _left < _right
            elif isinstance(self.node.ops[0], ast.Is):
                condition = _left is not _right
            elif isinstance(self.node.ops[0], ast.IsNot):
                condition = _left is _right
            elif isinstance(self.node.ops[0], ast.In):
                condition = _left not in _right
            elif isinstance(self.node.ops[0], ast.NotIn):
                condition = _left in _right
            return condition
        except ValueError as exc:
            pass
    
    def is_decision(self):
        return False
    
    def record(self, expression, tag):
        result = bool(expression)
        self.conditions[result].add(tag)
        return result
    
    def description(self, condition):
        return str(bool(condition))[0]
    
    def was_true(self):
        return self.conditions[True]
    
    def was_false(self):
        return self.conditions[False] 
    
    def set_unreachable(self, condition):
        self.conditions[condition].add(UnreachableCondition)
    
    def number_of_conditions(self, report_conditions_with_literals):
        if report_conditions_with_literals:
            return len(self.conditions)
        
        unreachable_conditions = 0
        for condition in self.conditions:
            for result in self.conditions[condition]:
                if (result == UnreachableCondition
                    or result == PragmaCondition.TAG):
                    unreachable_conditions += 1
                    break
        return len(self.conditions) - unreachable_conditions
    
    def number_of_conditions_hit(self):
        def is_hit(results):
            if results:
                return any(not (result == UnreachableCondition
                                or result == PragmaCondition.TAG)
                           for result in results)
            return False
        
        return len([value 
                    for value in self.conditions.values() 
                    if is_hit(value)])
    
    def conditions_missed(self, report_conditions_With_literals):
        return self.number_of_conditions(report_conditions_With_literals) - self.number_of_conditions_hit()
    
    def _format_condition_result(self, result, length=6):
        padding = '\n' + (' ' * length)
        return padding.join(str(tag) for tag in sorted(result))
    
    def result(self):
        lines = []
        name = "Compare -> %s:%s < %s >" % (self.modulename, self.label, self.source)
        lines.append("%s" % (name,))
        lines.append("")
        lines.append("T ==> %s" % self._format_condition_result(self.conditions[True]))
        lines.append("F ==> %s" % self._format_condition_result(self.conditions[False]))
        return "\n".join(lines)
    
    def merge(self, other):
        for condition, results in self.conditions.items():
            results.update(other.conditions[condition])
