class ExecutionReport(object):
    
    def __init__(self, constructs):
        self.constructs = constructs
    
    def report(self, showall=False):
        lines = []
        lines.append("")
        lines.append("-----------------------------")
        lines.append("Instrumental Coverage Summary")
        lines.append("-----------------------------")
        lines.append("")
        for label, construct in sorted(self.constructs.items(),
                                       key=lambda (l, c): (c.modulename, c.lineno, l)):
            if showall or construct.conditions_missed():
                lines.append(construct.result())
                lines.append("")
        return "\n".join(lines)
    
    def summary(self):
        modules = {}
        for construct in self.constructs.values():
            constructs = modules.setdefault(construct.modulename, [])
            constructs.append(construct)
        
        lines = []
        for modulename, constructs in sorted(modules.items()):
            total_conditions = sum(construct.number_of_conditions()
                                   for construct in constructs)
            hit_conditions = sum(construct.number_of_conditions_hit()
                                 for construct in constructs)
            lines.append('%s: %s/%s hit (%.0f%%)' %\
                             (modulename, hit_conditions, total_conditions,
                              hit_conditions/float(total_conditions) * 100))
        return '\n'.join(lines)
