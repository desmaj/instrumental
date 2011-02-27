import atexit
from subprocess import PIPE
from subprocess import Popen
import sys

from instrumental.importer import ImportHook
from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder
from instrumental.recorder import ExecutionSummary

def main():
    targets = sys.argv[1:]
    for target in targets:
        sys.meta_path.append(ImportHook(target, CoverageAnnotator()))
    
    recorder = ExecutionRecorder.get()
    summary = ExecutionSummary(recorder)
    def print_results():
        print str(summary)
    atexit.register(print_results)
    
    nosetests = Popen(['which', 'nosetests'], 
                      stdout=PIPE).communicate()[0][:-1]
    
    environment = {'__name__': '__main__',
                   }
    execfile(nosetests, environment)
    
