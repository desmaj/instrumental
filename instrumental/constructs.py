from astkit.render import SourceCodeRenderer

class LogicalBoolean(object):
    
    def __init__(self, modulename, node):
        self.modulename = modulename
        self.lineno = node.lineno
        self.source = SourceCodeRenderer.render(node)
        self.pins = len(node.values)
        self.conditions =\
            dict((i, False) for i in range(self.pins + 1))
        self.literals = {}
    
    def number_of_conditions(self):
        return len(self.conditions)
    
    def number_of_conditions_hit(self):
        return len([value 
                    for value in self.conditions.values()
                    if value])
    
    def conditions_missed(self):
        return self.number_of_conditions() - self.number_of_conditions_hit()
    
    def _literal_warning(self):
        return ("** One or more conditions maybe not be reachable due to"
                " the presence of a literal in the decision")
        
    def result(self):
        lines = []
        name = "%s:%s < %s >" % (self.modulename, self.lineno, self.source)
        lines.append("%s" % (name,))
        if self.literals:
            lines.append("")
            lines.append(self._literal_warning())
        lines.append("")
        for condition in sorted(self.conditions):
            lines.append(self.description(condition) +\
                             " ==> " +\
                             str(self.conditions[condition]))
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
    
    def record(self, value, pin):
        if pin < (self.pins-1):
            if not value:
                self.conditions[pin+1] = True
        elif pin == (self.pins-1):
            if value:
                self.conditions[0] = True
            else:
                self.conditions[self.pins] = True
    
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
        
class LogicalOr(LogicalBoolean):
    """ Stores the execution information for a Logical Or
        
        For an or condition with n inputs, there will be
        n + 2 recordable conditions. Conditions 0 though
        n indicate that the numbered position input is
        True. Condition n indicates that all inputs are
        False. Condition n + 1 is "Other".
    """
    
    def record(self, value, pin):
        if pin < (self.pins-1):
            if value:
                self.conditions[pin] = True
        elif pin == (self.pins-1):
            if value:
                self.conditions[pin] = True
            else:
                self.conditions[self.pins] = True
    
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
    
class BooleanDecision(object):
    
    def __init__(self, modulename, node):
        self.modulename = modulename
        self.lineno = node.lineno
        self.source = SourceCodeRenderer.render(node)
        self.conditions = {True: False,
                           False: False}
        
    def record(self, expression):
        result = bool(expression)
        self.conditions[result] = True
        return result

    def number_of_conditions(self):
        return len(self.conditions)
    
    def number_of_conditions_hit(self):
        return len([value 
                    for value in self.conditions.values()
                    if value])
    
    def conditions_missed(self):
        return self.number_of_conditions() - self.number_of_conditions_hit()
    
    def result(self):
        lines = []
        name = "%s:%s < %s >" % (self.modulename, self.lineno, self.source)
        lines.append("%s" % (name,))
        lines.append("")
        lines.append("T ==> %r" % self.conditions[True])
        lines.append("F ==> %r" % self.conditions[False])
        return "\n".join(lines)
