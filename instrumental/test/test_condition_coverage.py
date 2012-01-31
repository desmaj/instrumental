import ast
import inspect

from astkit.render import SourceCodeRenderer as renderer

from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder

def load_module(func):
    source = inspect.getsource(func)
    normal_source =\
        "\n".join(line[12:] for line in source.splitlines(False)[1:])
    module = ast.parse(normal_source)
    return module, normal_source

class TestInstrumentation(object):
    
    def setup(self):
        # First clear out the recorder so that we'll create a new one
        ExecutionRecorder._instance = None
        self.recorder = ExecutionRecorder.get()
    
    def _load_and_compile_module(self, module_func):
        module, source = load_module(module_func)
        self.recorder.add_source(module_func.__name__, source)
        transformer = CoverageAnnotator(module_func.__name__,
                                        self.recorder)
        inst_module = transformer.visit(module)
        print renderer.render(inst_module)
        #for node in ast.walk(inst_module):
        #    print node, node.__dict__
        code = compile(inst_module, '<string>', 'exec')
        return code
    
    def test_two_pin_and_t_t(self):
        def test_module():
            a = True
            b = True
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert True == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_and_t_f(self):
        def test_module():
            a = True
            b = False
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert recorder._constructs[label].conditions[2]
    
    def test_two_pin_and_f_t(self):
        def test_module():
            a = False
            b = True
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_and_f_f(self):
        def test_module():
            a = False
            b = False
            result = a and b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_or_t_t(self):
        def test_module():
            a = True
            b = True
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert True == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        print recorder._constructs[label].pins
        assert recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_or_t_f(self):
        def test_module():
            a = True
            b = False
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert True == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        print recorder._constructs[label].pins
        assert recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_or_f_t(self):
        def test_module():
            a = False
            b = True
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert True == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        print recorder._constructs[label].pins
        assert not recorder._constructs[label].conditions[0]
        assert recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
    
    def test_two_pin_or_f_f(self):
        def test_module():
            a = False
            b = False
            result = a or b
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        print recorder._constructs[label].pins
        assert not recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert recorder._constructs[label].conditions[2]
    
    def test_three_pin_and_t_t_t(self):
        def test_module():
            a = True
            b = True
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert True == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
        assert not recorder._constructs[label].conditions[3]
    
    def test_three_pin_and_f_t_t(self):
        def test_module():
            a = False
            b = True
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
        assert not recorder._constructs[label].conditions[3]
    
    def test_three_pin_and_t_f_t(self):
        def test_module():
            a = True
            b = False
            c = True
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert recorder._constructs[label].conditions[2]
        assert not recorder._constructs[label].conditions[3]
    
    def test_three_pin_and_t_t_f(self):
        def test_module():
            a = True
            b = True
            c = False
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert not recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
        assert recorder._constructs[label].conditions[3]
    
    def test_three_pin_and_f_f_f(self):
        def test_module():
            a = False
            b = False
            c = False
            result = a and b and c
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert False == result
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[0]
        assert recorder._constructs[label].conditions[1]
        assert not recorder._constructs[label].conditions[2]
        assert not recorder._constructs[label].conditions[3]
    
    def test_instrument_if_true_result(self):
        def test_module():
            a = True
            if a:
                result = 1
            else:
                result = 7
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert result is 1
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert recorder._constructs[label].conditions[True]
        assert not recorder._constructs[label].conditions[False]
        
    def test_instrument_if_false_result(self):
        def test_module():
            a = False
            if a:
                result = 1
            else:
                result = 7
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert result is 7
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[True]
        assert recorder._constructs[label].conditions[False]
        
    def test_instrument_while_false_result(self):
        def test_module():
            a = 0
            result = 0
            while a:
                a -= 1
                result += 1
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert result is 0
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert not recorder._constructs[label].conditions[True]
        assert recorder._constructs[label].conditions[False]
        
    def test_instrument_while_with_loop_result(self):
        def test_module():
            a = 3
            result = 0
            while a:
                a -= 1
                result += 1
        code = self._load_and_compile_module(test_module)
        exec code in globals(), locals()
        assert result is 3
        
        recorder = self.recorder
        label = 1
        assert label in recorder._constructs
        assert recorder._constructs[label].conditions[True]
        assert recorder._constructs[label].conditions[False]
    
