import imp
import os
import sys

class TestMonkeyPatch(object):
    
    def test_monkeypatch(self):
        import imp
        from instrumental.instrument import AnnotatorFactory
        from instrumental.monkey import monkey_patch_imp
        
        original_load_module = imp.load_module
        monkey_patch_imp([], [], AnnotatorFactory(None))
        assert original_load_module != imp.load_module

class TestLoadModule(object):
    
    def setup(self):
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder._instance = None
        self._pre_test_modules = sys.modules.keys()
    
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
        visitor_factory = AnnotatorFactory(recorder)
        load_module = load_module_factory([], 
                                          [],
                                          visitor_factory)
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.simple'
        simple_path = os.path.join(samples_directory, 'simple.py')
        simple_fh = file(simple_path, 'r')
        load_module(simple_name,
                    simple_fh,
                    simple_path,
                    ('.py', 'r', imp.PY_SOURCE)
                    )
        
        assert simple_name in sys.modules
    
    def test_load_module(self):
        from instrumental.instrument import AnnotatorFactory
        from instrumental.monkey import load_module_factory
        from instrumental.recorder import ExecutionRecorder
        
        recorder = ExecutionRecorder.get()
        visitor_factory = AnnotatorFactory(recorder)
        load_module = load_module_factory(['instrumental.test.samples.simple'], 
                                          [],
                                          visitor_factory)
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.simple'
        simple_path = os.path.join(samples_directory, 'simple.py')
        simple_fh = file(simple_path, 'r')
        load_module(simple_name,
                    simple_fh,
                    simple_path,
                    ('.py', 'r', imp.PY_SOURCE)
                    )
        
        assert simple_name in sys.modules
    
    def test_load_package(self):
        from instrumental.instrument import AnnotatorFactory
        from instrumental.monkey import load_module_factory
        from instrumental.recorder import ExecutionRecorder
        
        recorder = ExecutionRecorder.get()
        visitor_factory = AnnotatorFactory(recorder)
        load_module = load_module_factory(['instrumental.test.samples.package'], 
                                          [],
                                          visitor_factory)
        
        import instrumental.test.samples
        samples_directory = os.path.dirname(instrumental.test.samples.__file__)
        simple_name = 'instrumental.test.samples.package'
        simple_path = os.path.join(samples_directory, 'package')
        load_module(simple_name,
                    None,
                    simple_path,
                    (None, None, imp.PKG_DIRECTORY)
                    )
        
        assert simple_name in sys.modules
        
