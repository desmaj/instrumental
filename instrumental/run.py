import atexit
from optparse import OptionParser
from subprocess import PIPE
from subprocess import Popen
import sys

from instrumental.importer import ImportHook
from instrumental.instrument import AnnotatorFactory
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
parser.add_option('-a', '--all', dest='all',
                  action='store_true', default=False,
                  help='Show all constructs (not just those missing coverage')
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
    
    recorder = ExecutionRecorder.get()
    for target in opts.targets:
        annotator_factory = AnnotatorFactory(recorder)
        sys.meta_path.append(ImportHook(target, annotator_factory))
    
    if opts.summary or opts.report:
        def _display_reports():
            report = ExecutionReport(recorder._constructs)
            if opts.summary:
                print report.summary()
            if opts.report:
                print report.report(opts.all)
        atexit.register(_display_reports)
    
    sourcefile = args[0]
    environment = {'__name__': '__main__',
                   '__file__': sourcefile,
                   }
    sys.argv = args[:]
    execfile(sourcefile, environment)
