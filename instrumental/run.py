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
import atexit
from optparse import OptionParser
import os
from subprocess import PIPE
from subprocess import Popen
import sys

from instrumental.compat import execfile
from instrumental.importer import ImportHook
from instrumental.instrument import AnnotatorFactory
from instrumental.monkey import monkey_patch_imp
from instrumental.recorder import ExecutionRecorder
from instrumental.reporting import ExecutionReport

parser = OptionParser(usage="instrumental [options] COMMAND ARG1 ARG2 ...")
parser.disable_interspersed_args()
parser.add_option('-r', '--report', dest='report',
                  action='store_true',
                  help='Print a detailed coverage report')
parser.add_option('-s', '--summary', dest='summary',
                  action='store_true',
                  help='Print a summary coverage report')
parser.add_option('-S', '--statements', dest='statements',
                  action='store_true',
                  help='Print a summary statement coverage report')
parser.add_option('-x', '--xml', dest='xml',
                  action='store_true',
                  help='Create a cobertura-compatible xml coverage report')
parser.add_option('--html', dest='html',
                  action='store_true',
                  help='Create an html coverage report')
parser.add_option('-a', '--all', dest='all',
                  action='store_true', default=False,
                  help='Show all constructs (not just those missing coverage')
parser.add_option('-t', '--target', dest='targets',
                  action='append', default=[],
                  help=('A Python regular expression; modules with names'
                        ' matching this regular expression will be'
                        ' instrumented and have their coverage reported'))
parser.add_option('-i', '--ignore', dest='ignores',
                  action='append', default=[],
                  help=('A Python regular expression; modules with names'
                        ' matching this regular expression will be'
                        ' ignored and not have their coverage reported'))

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    
    opts, args = parser.parse_args(argv)
    
    if len(args) < 1:
        parser.print_help()
        sys.exit()
    
    if not opts.targets:
        sys.stdout.write("No targets specified. Use the '-t' option to specify packages to cover")
        sys.exit()
    
    recorder = ExecutionRecorder.get()
    annotator_factory = AnnotatorFactory(recorder)
    monkey_patch_imp(opts.targets, opts.ignores, annotator_factory)
    for target in opts.targets:
        sys.meta_path.append(ImportHook(target, opts.ignores, annotator_factory))
    
    xml_filename = os.path.abspath('instrumental.xml')
    
    sourcefile = args[0]
    environment = {'__name__': '__main__',
                   '__file__': sourcefile,
                   }
    sys.argv = args[:]
    try:
        here = os.getcwd()
        execfile(sourcefile, environment)
    finally:
        if any([opts.summary,
                opts.report,
                opts.statements,
                opts.xml,
                opts.html]):
            sys.stdout.write("\n")
            report = ExecutionReport(here, recorder.constructs, recorder.statements, recorder.sources)
            if opts.summary:
                sys.stdout.write(report.summary() + "\n")
            if opts.report:
                sys.stdout.write(report.report(opts.all) + "\n")
            if opts.statements:
                sys.stdout.write(report.statement_summary() + "\n")
            if opts.xml:
                report.write_xml_coverage_report(xml_filename)
            if opts.html:
                report.write_html_coverage_report()
            print
