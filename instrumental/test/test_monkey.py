import imp
import os
import sys

from instrumental.test import DummyConfig

class TestMonkeyPatch(object):
    
    def test_monkeypatch(self):
        import imp
        from instrumental.instrument import AnnotatorFactory
        from instrumental.monkey import monkeypatch_imp
        
        original_load_module = imp.load_module
        config = DummyConfig()
        monkeypatch_imp([], [], AnnotatorFactory(config, None))
        assert original_load_module != imp.load_module

class TestLoadModule(object):
    
    def setup(self):
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder.reset()
        self._pre_test_modules = sys.modules.keys()
        self.config = DummyConfig()
    
    def teardown(self):
        _post_test_modules = sys.modules.keys()
        for modname in _post_test_modules:
            if modname not in self._pre_test_modules:
                if modname.startswith('instrumental.test.samples'):
                    del sys.modules[modname]
    
    def test_load_non_target_module(self):
        from instrumental.instrument import AnnotatorFactory
        from instrumental.monkey import load_module_factory
        from instrumental.recorder import ExecutionRecorder
        
        recorder = ExecutionRecorder.get()
        visitor_factory = AnnotatorFactory(self.config, recorder)
        load_module = load_module_factory([], 
                                          [],
                                          visitor_factory)
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.simple'
        simple_path = os.path.join(samples_directory, 'simple.py')
        simple_fh = open(simple_path, 'r')
        load_module(simple_name,
                    simple_fh,
                    simple_path,
                    ('.py', 'r', imp.PY_SOURCE)
                    )
        
        assert simple_name in sys.modules
    
    def test_load_module(self):
        from instrumental.instrument import AnnotatorFactory
        from instrumental.metadata import MetadataGatheringVisitor
        from instrumental.monkey import load_module_factory
        from instrumental.pragmas import PragmaFinder
        from instrumental.recorder import ExecutionRecorder
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.simple'
        simple_path = os.path.join(samples_directory, 'simple.py')
        simple_fh = open(simple_path, 'r')
        
        source = open(simple_path, "r").read()
        pragmas = PragmaFinder().find_pragmas(source)
        metadata = MetadataGatheringVisitor.analyze(self.config,
                                                    simple_name, 
                                                    source, 
                                                    pragmas)
        
        recorder = ExecutionRecorder.get()
        recorder.add_metadata(metadata)
        visitor_factory = AnnotatorFactory(self.config, recorder)
        load_module = load_module_factory(['instrumental.test.samples.simple'], 
                                          [],
                                          visitor_factory)
        
        load_module(simple_name,
                    simple_fh,
                    simple_path,
                    ('.py', 'r', imp.PY_SOURCE)
                    )
        
        assert simple_name in sys.modules
    
    def test_load_package(self):
        from instrumental.instrument import AnnotatorFactory
        from instrumental.metadata import MetadataGatheringVisitor
        from instrumental.monkey import load_module_factory
        from instrumental.pragmas import PragmaFinder
        from instrumental.recorder import ExecutionRecorder
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.package'
        simple_path = os.path.join(samples_directory, 'package')
        
        source = open(os.path.join(simple_path, '__init__.py'), "r").read()
        pragmas = PragmaFinder().find_pragmas(source)
        metadata = MetadataGatheringVisitor.analyze(self.config, 
                                                    simple_name, 
                                                    source, 
                                                    pragmas)
        
        recorder = ExecutionRecorder.get()
        recorder.add_metadata(metadata)
        visitor_factory = AnnotatorFactory(self.config, recorder)
        load_module = load_module_factory(['instrumental.test.samples.package'], 
                                          [],
                                          visitor_factory)
        
        load_module(simple_name,
                    None,
                    simple_path,
                    (None, None, imp.PKG_DIRECTORY)
                    )
        
        assert simple_name in sys.modules
        
