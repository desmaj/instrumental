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

from instrumental.constructs import LogicalBoolean
from instrumental.htmlreport import HTMLCoverageReport
from instrumental.summary import ExecutionSummary
from instrumental.xmlreport import XMLCoverageReport

class ExecutionReport(object):
    
    def __init__(self, working_directory, metadata, options):
        self.working_directory = working_directory
        self.metadata = metadata
        self.options = options
    
    def report(self, showall=False):
        lines = []
        lines.append("")
        lines.append("===============================================")
        lines.append("Instrumental Condition/Decision Coverage Report")
        lines.append("===============================================")
        lines.append("")
        no_missed_conditions = True
        def _key_func(pair):
            label, _ = pair
            lineno, index = label.split('.')
            return (int(lineno), int(index))
        for modulename, metadata in sorted(self.metadata.items()):
            for label, construct in sorted(metadata.constructs.items(),
                                           key=_key_func):
                if showall or construct.conditions_missed(self.options.report_conditions_with_literals):
                    no_missed_conditions = False
                    lines.append(construct.result())
                    lines.append("")
        if no_missed_conditions:
            lines.append(" Full coverage. Good job!")
            lines.append("")
        return "\n".join(lines)
    
    def summary(self):
        lines = []
        lines.append("")
        lines.append("================================================")
        lines.append("Instrumental Condition/Decision Coverage Summary")
        lines.append("================================================")
        lines.append("")
        for modulename, metadata in sorted(self.metadata.items()):
            total_conditions = sum(construct.number_of_conditions(self.options.report_conditions_with_literals)
                                   for construct in metadata.constructs.values())
            hit_conditions = sum(construct.number_of_conditions_hit()
                                 for construct in metadata.constructs.values())
            if not total_conditions:
                lines.append('%s: 0/0 hit (---)' % modulename)
            else:
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
        statements = dict((modulename, self.metadata[modulename].lines)
                          for modulename in self.metadata)
        return "\n".join(outlines + [formatter.format(statements)])

    def write_xml_coverage_report(self, filename):
        xml_report = XMLCoverageReport(self.working_directory, self.metadata, self.options)
        xml_report.write(filename)
    
    def write_html_coverage_report(self, directory='instrumental-result-html'):
        conditions = {}
        statements = {}
        sources = {}
        for modulename in self.metadata:
            conditions[modulename] = self.metadata[modulename].constructs
            statements[modulename] = self.metadata[modulename].lines
            sources[modulename] = self.metadata[modulename].source
        summary = ExecutionSummary(conditions, statements, self.options)
        html_report = HTMLCoverageReport(summary, sources)
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
        if lines:
            cover_pct = "%s%%" % int(100 * (len(lines) - len(missing_lines)) / float(len(lines)))
        else:
            cover_pct = "100%"
        
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
                          key=lambda pair: pair[0])]
    
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
