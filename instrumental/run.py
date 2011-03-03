import atexit
from optparse import OptionParser
from subprocess import PIPE
from subprocess import Popen
import sys

from instrumental.importer import ImportHook
from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder
from instrumental.recorder import ExecutionReport
from instrumental.recorder import ExecutionSummary

parser = OptionParser(usage="instrumental [options] COMMAND ARG1 ARG2 ...")
parser.disable_interspersed_args()
parser.add_option('-r', '--report', dest='report',
                  action='store_true',
                  help='Print a detailed coverage report')
parser.add_option('-s', '--summary', dest='summary',
                  action='store_true',
                  help='Print a summary coverage report')
parser.add_option('-t', '--target', dest='targets',
                  action='append', default=[],
                  help=('A Python regular expression; modules with names'
                        ' matching this regular expression will be'
                        ' instrumented and have their coverage reported'))

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    
    opts, args = parser.parse_args(argv)
    
    if len(args) < 1:
        parser.print_help()
        sys.exit()
    
    for target in opts.targets:
        sys.meta_path.append(ImportHook(target, CoverageAnnotator))
    
    recorder = ExecutionRecorder.get()
    
    if opts.summary:
        summary = ExecutionSummary(recorder)
        def print_results():
            print str(summary)
        atexit.register(print_results)
    
    if opts.report:
        report = ExecutionReport(recorder)
        def print_results():
            print str(report)
        atexit.register(print_results)
    
    sourcefile = args[0]
    environment = {'__name__': '__main__',
                   }
    sys.argv = args[:]
    execfile(sourcefile, environment)
