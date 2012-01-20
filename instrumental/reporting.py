import os

from instrumental.htmlreport import HTMLCoverageReport
from instrumental.summary import ExecutionSummary
from instrumental.xmlreport import XMLCoverageReport

class ExecutionReport(object):
    
    def __init__(self, working_directory, constructs, statements, sources):
        self.working_directory = working_directory
        self.constructs = constructs
        self.statements = statements
        self.sources = sources
    
    def report(self, showall=False):
        lines = []
        lines.append("")
        lines.append("===============================================")
        lines.append("Instrumental Condition/Decision Coverage Report")
        lines.append("===============================================")
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
        lines.append("")
        lines.append("================================================")
        lines.append("Instrumental Condition/Decision Coverage Summary")
        lines.append("================================================")
        lines.append("")
        for modulename, constructs in sorted(modules.items()):
            total_conditions = sum(construct.number_of_conditions()
                                   for construct in constructs)
            hit_conditions = sum(construct.number_of_conditions_hit()
                                 for construct in constructs)
            lines.append('%s: %s/%s hit (%.0f%%)' %\
                             (modulename, hit_conditions, total_conditions,
                              hit_conditions/float(total_conditions) * 100))
        return '\n'.join(lines)
    
    def statement_summary(self):
        outlines = ["=======================================", 
                    "Instrumental Statement Coverage Summary", 
                    "=======================================",
                    "",
                    ]
        
        formatter = StatementCoverageFormatter()
        return "\n".join(outlines + [formatter.format(self.statements)])

    def write_xml_coverage_report(self, filename):
        xml_report = XMLCoverageReport(self)
        xml_report.write(filename)
    
    def write_html_coverage_report(self, directory='instrumental'):
        summary = ExecutionSummary(self.constructs, self.statements)
        html_report = HTMLCoverageReport(summary, self.sources)
        html_report.write(os.path.join(self.working_directory, directory))
    
class Chunk(object):
    
    def __init__(self, start):
        self.start = self.finish = start
    
    def extend(self):
        self.finish += 1
    
    def __str__(self):
        if self.start == self.finish:
            return str(self.start)
        elif self.start + 1 == self.finish:
            return "%s,%s" % (self.start, self.finish)
        else:
            return "%s-%s" % (self.start, self.finish)

class StatementCoverageFormatter(object):
    
    def _collapse_sequence(self, seq):
            
        chunks = []
        last_chunk = None
        for line in seq:
            if (not chunks) or (line != (chunks[-1].finish + 1)):
                chunks.append(Chunk(line))
            else:
                chunks[-1].extend()
        
        return ",".join([str(chunk) for chunk in chunks])
    
    def format(self, statements):
        header = self._make_header(statements)
        separator = self._make_separator(statements)
        lines = self._make_lines(statements)
        summary = self._make_summary(statements)
        
        return "\n".join([header, separator] + lines + [separator, summary])
    
    def _make_header(self, statements):
        longest_name_length = max(len(modulename) for modulename in statements)
        
        header = "Name" + (" " * longest_name_length)
        header = "".join([header, "Stmts"])
        header = "".join([header, (" " * 3) + "Miss"])
        header = "".join([header, (" " * 2) + "Cover"])
        header = "".join([header, (" " * 3) + "Missing"])
        
        return header
    
    def _make_separator(self, statements):
        header = self._make_header(statements)
        return "-" * len(header)
    
    def _make_line(self, modulename, lines, column_width):
        missing_lines = [line for line in sorted(lines) if not lines[line]]
        cover_pct = "%s%%" % int(100 * (len(lines) - len(missing_lines)) / float(len(lines)))
        
        line = modulename.ljust(column_width)
        line = "".join([line, str(len(lines)).rjust(5)])
        line = "".join([line, str(len(missing_lines)).rjust(7)])
        line = "".join([line, cover_pct.rjust(7)])
        line = "".join([line, 
                        (" " * 3), 
                        self._collapse_sequence(missing_lines)])
        
        return line
    
    def _make_lines(self, statements):
        longest_name_length = max(len(modulename) for modulename in statements)
        
        return [self._make_line(modulename, lines, longest_name_length + 4)
                for modulename, lines 
                in sorted(statements.items(),
                          key=lambda (name, _): name)]
    
    def _make_summary(self, statements):
        longest_name_length = max(len(modulename) for modulename in statements)
        
        total_lines = 0
        missed_lines = 0
        for lines in statements.values():
            total_lines += len(lines)
            missed_lines += len([a_line for a_line in lines
                                 if not lines[a_line]])
        covered_pct = "%.0f%%" % int(100 * float(total_lines - missed_lines) / total_lines)
        
        summary = "TOTAL".ljust(longest_name_length + 4)
        summary = "".join([summary, str(total_lines).rjust(5)])
        summary = "".join([summary, str(missed_lines).rjust(7)])
        summary = "".join([summary, covered_pct.rjust(7)])
        
        return summary
