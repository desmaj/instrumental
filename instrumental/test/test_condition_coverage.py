import sys

from astkit.render import SourceCodeRenderer as renderer

from instrumental.compat import exec_f
from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder
from instrumental.test import DummyConfig
from instrumental.test import load_module

class TestInstrumentation(object):
    
    def setup(self):
        # First clear out the recorder so that we'll create a new one
        ExecutionRecorder.reset()
        self.recorder = ExecutionRecorder.get()
        self.recorder.start()
    
    def teardown(self):
        self.recorder.stop()
    
    def _load_and_compile_module(self, module_func):
        module, source = load_module(module_func)
        from instrumental.pragmas import PragmaFinder
        pragmas = PragmaFinder().find_pragmas(source)
        from instrumental.metadata import MetadataGatheringVisitor
        config = DummyConfig()
        self.recorder.add_metadata(MetadataGatheringVisitor.analyze(config,
                                                                    module_func.__name__,
                                                                    source, 
                                                                    pragmas))
        # self.recorder.add_source(module_func.__name__, source)
        transformer = CoverageAnnotator(config,
                                        module_func.__name__,
                                        self.recorder)
        inst_module = transformer.visit(module)
        sys.stdout.write(renderer.render(inst_module) + "\n")
        code = compile(inst_module, '<string>', 'exec')
        return code
    
    def _verify_conditions(self, module, label, expected):
        construct = self.recorder.metadata[module.__name__].constructs[label]
        tag = self.recorder.DEFAULT_TAG
        for i, value in enumerate(expected):
            if expected[i]:
                assert tag in construct.conditions[i], construct.conditions[i]
            else:
                assert not construct.conditions[i], construct.conditions[i]
    
    def test_two_pin_and_t_t(self):
        def test_module():
            a = True
            b = True
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert True == result
        
        self._verify_conditions(test_module, '3.2', 
                                [True, False, False])
    
    def test_two_pin_and_t_f(self):
        def test_module():
            a = True
            b = False
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '3.2', 
                                [False, False, True])
    
    def test_two_pin_and_f_t(self):
        def test_module():
            a = False
            b = True
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '3.2', 
                                [False, True, False])
    
    def test_two_pin_and_f_f(self):
        def test_module():
            a = False
            b = False
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '3.2', 
                                [False, True, False])
    
    def test_two_pin_or_t_t(self):
        def test_module():
            a = True
            b = True
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert True == result
        
        self._verify_conditions(test_module, '3.2', 
                                [True, False, False])
    
    def test_two_pin_or_t_f(self):
        def test_module():
            a = True
            b = False
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert True == result
        
        self._verify_conditions(test_module, '3.2', 
                                [True, False, False])
    
    def test_two_pin_or_f_t(self):
        def test_module():
            a = False
            b = True
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert True == result
        
        self._verify_conditions(test_module, '3.2', 
                                [False, True, False])
    
    def test_two_pin_or_f_f(self):
        def test_module():
            a = False
            b = False
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '3.2', 
                                [False, False, True])
    
    def test_three_pin_and_t_t_t(self):
        def test_module():
            a = True
            b = True
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert True == result
        
        self._verify_conditions(test_module, '4.2', 
                                [True, False, False, False])
    
    def test_three_pin_and_f_t_t(self):
        def test_module():
            a = False
            b = True
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '4.2', 
                                [False, True, False, False])
    
    def test_three_pin_and_t_f_t(self):
        def test_module():
            a = True
            b = False
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '4.2', 
                                [False, False, True, False])
    
    def test_three_pin_and_t_t_f(self):
        def test_module():
            a = True
            b = True
            c = False
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '4.2', 
                                [False, False, False, True])
    
    def test_three_pin_and_f_f_f(self):
        def test_module():
            a = False
            b = False
            c = False
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert False == result
        
        self._verify_conditions(test_module, '4.2', 
                                [False, True, False, False])
    
    def test_instrument_if_true_result(self):
        def test_module():
            a = True
            if a:
                result = 1
            else:
                result = 7
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 1
        
        self._verify_conditions(test_module, '2.1', [False, True])
        
    def test_instrument_if_false_result(self):
        def test_module():
            a = False
            if a:
                result = 1
            else:
                result = 7
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 7
        
        self._verify_conditions(test_module, '2.1', [True, False])
        
    def test_instrument_while_false_result(self):
        def test_module():
            a = 0
            result = 0
            while a:
                a -= 1
                result += 1
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 0
        
        self._verify_conditions(test_module, '3.1', [True, False])
        
    def test_instrument_while_with_loop_result(self):
        def test_module():
            a = 3
            result = 0
            while a:
                a -= 1
                result += 1
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 3
        
        self._verify_conditions(test_module, '3.1', [True, True])
            
    def test_instrument_ifexp_true(self):
        def test_module():
            a = 3
            result = 1 if a == 3 else 4
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 1
        
        self._verify_conditions(test_module, '2.1', [False, True])
    
    def test_instrument_ifexp_false(self):
        def test_module():
            a = 3
            result = 1 if a != 3 else 4
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        assert result is 4
        
        self._verify_conditions(test_module, '2.1', [True, False])
    
    def test_instrument_ifexp_true_and_false(self):
        def test_module():
            def test_func(arg):
                return 1 if arg == 3 else 4
            test_func(3)
            test_func(2)
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        
        self._verify_conditions(test_module, '2.1', [True, True])
    
    def test_instrument_ifexp_with_boolop(self):
        def test_module():
            def test_func(a, b):
                return 1 if a and b else 4
            test_func(True, False)
    
        code = self._load_and_compile_module(test_module)
        exec_f(code, globals())
        
        self._verify_conditions(test_module, '2.2', [False, False, True])
