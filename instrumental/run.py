import atexit
from optparse import OptionParser
from subprocess import PIPE
from subprocess import Popen
import sys

from instrumental.importer import ImportHook
from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder
from instrumental.recorder import ExecutionSummary

parser = OptionParser()
parser.add_option('-t', '--target', dest='targets',
                  action='append', default=[],
                  help='Gather coverage for these targets')

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    opts, args = parser.parse_args(sys.argv)
    
    for target in opts.targets:
        sys.meta_path.append(ImportHook(target, CoverageAnnotator()))
    
    recorder = ExecutionRecorder.get()
    summary = ExecutionSummary(recorder)
    def print_results():
        print str(summary)
    atexit.register(print_results)
    
    sourcefile = args[1]
    print sourcefile
    environment = {'__name__': '__main__',
                   }
    sys.argv = args[1:]
    execfile(sourcefile, environment)

