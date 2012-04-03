import sys

from instrumental.importer import ImportHook
from instrumental.instrument import AnnotatorFactory
from instrumental.monkey import monkeypatch_imp
from instrumental.monkey import unmonkeypatch_imp
from instrumental.recorder import ExecutionRecorder

class Coverage(object):
    
    def __init__(self):
        self.recorder = ExecutionRecorder.get()
        self._import_hooks = []

    def start(self, targets, ignores):
        annotator_factory = AnnotatorFactory(self.recorder)
        monkeypatch_imp(targets, ignores, annotator_factory)
        for target in targets:
            hook = ImportHook(target, ignores, annotator_factory)
            self._import_hooks.append(hook)
            sys.meta_path.append(hook)
        self.recorder.start()
        
    def stop(self):
        self.recorder.stop()
        for hook in self._import_hooks:
            sys.meta_path.remove(hook)
        unmonkeypatch_imp()
