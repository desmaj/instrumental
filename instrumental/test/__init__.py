import inspect

from astkit import ast

from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder

def load_module(func):
    source = inspect.getsource(func)
    lines = source.splitlines(False)[1:]
    leading_space_count = 0
    for ch in lines[0]:
        if ch != ' ':
            break
        leading_space_count += 1
    normal_source =\
        "\n".join(line[leading_space_count:] for line in lines)
    module = ast.parse(normal_source)
    return module, normal_source

class InstrumentationTestCase(object):
    
    def setup(self):
        # First clear out the recorder so that we'll create a new one
        ExecutionRecorder.reset()
        self.recorder = ExecutionRecorder.get()
    
    def _instrument_module(self, module_func):
        module, source = load_module(module_func)
        self.recorder.add_source(module_func.__name__, source)
        transformer = CoverageAnnotator(module_func.__name__,
                                        self.recorder)
        inst_module = transformer.visit(module)
        return inst_module
    
    def _assert_recorder_setup(self, module):
        assert isinstance(module, ast.Module)
        
        assert isinstance(module.body[0], ast.ImportFrom)
        assert module.body[0].module == 'instrumental.recorder'
        assert isinstance(module.body[0].names[0], ast.alias)
        assert module.body[0].names[0].name == 'ExecutionRecorder'
        
        assert isinstance(module.body[1], ast.Assign)
        assert isinstance(module.body[1].targets[0], ast.Name)
        assert module.body[1].targets[0].id == '_xxx_recorder_xxx_'
        assert isinstance(module.body[1].value, ast.Call)
        assert isinstance(module.body[1].value.func, ast.Attribute)
        assert isinstance(module.body[1].value.func.value, ast.Name)
        assert module.body[1].value.func.value.id == 'ExecutionRecorder'
        assert module.body[1].value.func.attr == 'get'
        assert not module.body[1].value.args
        assert not module.body[1].value.keywords
        assert not module.body[1].value.starargs
        assert not module.body[1].value.kwargs
    
    def _assert_record_statement(self, statement, modname, lineno):
        assert isinstance(statement, ast.Expr), statement.__dict__
        assert isinstance(statement.value, ast.Call)
        assert isinstance(statement.value.func, ast.Attribute)
        assert isinstance(statement.value.func.value, ast.Name)
        assert statement.value.func.value.id == '_xxx_recorder_xxx_'
        assert statement.value.func.attr == 'record_statement'
        assert isinstance(statement.value.args[0], ast.Str)
        assert statement.value.args[0].s == modname
        assert isinstance(statement.value.args[1], ast.Num)
        assert statement.value.args[1].n == lineno
    
