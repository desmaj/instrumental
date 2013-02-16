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

from astkit.render import SourceCodeRenderer

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
        self.literals = {}
    
    @property
    def lineno(self):
        return self.node.lineno
    
    def is_decision(self):
        return self.label.endswith('.1')
    
    def number_of_conditions(self):
        return len(self.conditions)
    
    def number_of_conditions_hit(self):
        return len([value 
                    for value in self.conditions.values()
                    if value])
    
    def conditions_missed(self):
        return self.number_of_conditions() - self.number_of_conditions_hit()
    
    def _literal_warning(self):
        return ("** One or more conditions may not be reachable due to"
                " the presence of a literal in the decision")
    
    def _format_condition_result(self, result, length=6):
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
        lines.append("T ==> %s" % self.was_true())
        lines.append("F ==> %s" % self.was_false())
        return "\n".join(lines)
    

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
        return self._format_condition_result(self.conditions[0])
    
    def was_false(self):
        results = set()
        for n in range(1, self.pins+1):
            results.update(self.conditions[n])
        return self._format_condition_result(results)
    
class LogicalOr(LogicalBoolean):
    """ Stores the execution information for a Logical Or
        
        For an or condition with n inputs, there will be
        n + 2 recordable conditions. Conditions 0 though
        n indicate that the numbered position input is
        True. Condition n indicates that all inputs are
        False. Condition n + 1 is "Other".
    """
    
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
        return self._format_condition_result(results)
    
    def was_false(self):
        return self._format_condition_result(self.conditions[self.pins])
    
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
    
    def is_decision(self):
        return True
    
    def record(self, expression, tag):
        result = bool(expression)
        self.conditions[result].add(tag)
        return result

    def number_of_conditions(self):
        return len(self.conditions)
    
    def number_of_conditions_hit(self):
        return len([value 
                    for value in self.conditions.values()
                    if value])
    
    def conditions_missed(self):
        return self.number_of_conditions() - self.number_of_conditions_hit()
    
    def _format_condition_result(self, result, length=6):
        padding = '\n' + (' ' * length)
        return padding.join(tag for tag in sorted(result))
    
    def result(self):
        lines = []
        name = "Decision -> %s:%s < %s >" % (self.modulename, self.label, self.source)
        lines.append("%s" % (name,))
        lines.append("")
        lines.append("T ==> %s" % self._format_condition_result(self.conditions[True]))
        lines.append("F ==> %s" % self._format_condition_result(self.conditions[False]))
        return "\n".join(lines)
