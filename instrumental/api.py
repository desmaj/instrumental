import os
import sys
import uuid

from instrumental.importer import ImportHook
from instrumental.instrument import AnnotatorFactory
from instrumental.metadata import gather_metadata
from instrumental.monkey import monkeypatch_imp
from instrumental.monkey import unmonkeypatch_imp
from instrumental.storage import ResultStore
from instrumental.recorder import ExecutionRecorder

class Coverage(object):
    uuid_environ_key = 'COVERAGE_UUID'
    
    def __init__(self, config, basedir, store_factory=None, coverage_uuid=None):
        if coverage_uuid is not None:
            self.uuid = coverage_uuid
        else:
            self.uuid = self._establish_uuid()
        self._config = config
        self._basedir = basedir
        self._import_hooks = []
        if store_factory is None:
            store_factory = self._get_store
        self._store_factory = store_factory
    
    def _establish_uuid(self):
        if self.uuid_environ_key in os.environ:
            return os.environ[self.uuid_environ_key]
        else:
            os.environ[self.uuid_environ_key] = str(uuid.uuid4())
            return os.environ[self.uuid_environ_key]
    
    def _maybe_label(self, should_label):
        if should_label:
            return ('p%s' % os.getpid())
    
    def _get_store(self, config, basedir):
        filename = config.file
        label = self._maybe_label(config.label)
        return ResultStore(basedir, label, filename)
    
    @property
    def recorder(self):
        return ExecutionRecorder.get(self.uuid)
    
    def start(self, targets, ignores):
        gather_metadata(self._config, self.recorder, targets, ignores)
        annotator_factory = AnnotatorFactory(self._config, self.recorder)
        monkeypatch_imp(targets, ignores, annotator_factory)
        for target in targets:
            hook = ImportHook(target, ignores, annotator_factory)
            self._import_hooks.append(hook)
            sys.meta_path.insert(0, hook)
        self.recorder.start()
    
    @property
    def started(self):
        return self.recorder.recording
    
    def stop(self):
        self.recorder.stop()
        for hook in self._import_hooks:
            sys.meta_path.remove(hook)
        unmonkeypatch_imp()
    
    def start_context(self, label):
        self.recorder.tag = label
    
    def stop_context(self):
        self.recorder.tag = None
    
    def save(self):
        store = self._store_factory(self._config, self._basedir)
        store.save(self.recorder)
    
    def load(self):
        store = self._store_factory(self._config, self._basedir)
        return store.load()
