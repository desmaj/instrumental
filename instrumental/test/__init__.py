import inspect
import os
import shutil

from astkit import ast

from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder

def get_normalized_source(func):
    source = inspect.getsource(func)
    source_lines = source.splitlines(False)[1:]
    base_indentation = 0
    while source_lines[0][base_indentation] == ' ':
        base_indentation += 1
    normal_source =\
        "\n".join(line[base_indentation:] for line in source_lines)
    return normal_source

def load_module(func):
    normal_source = get_normalized_source(func)
    module = ast.parse(normal_source)
    return module, normal_source

class DummyConfig(object):
    instrument_assertions = True
    instrument_comparisons = True
    use_metadata_cache = False

class InstrumentationTestCase(object):
    
    def setup(self):
        # First clear out the recorder so that we'll create a new one
        ExecutionRecorder.reset()
        self.recorder = ExecutionRecorder.get()
        self.config = DummyConfig()
    
    def _instrument_module(self, module_func):
        from instrumental.metadata import MetadataGatheringVisitor
        from instrumental.pragmas import PragmaFinder
        module, source = load_module(module_func)
        pragmas = PragmaFinder().find_pragmas(source)
        metadata = MetadataGatheringVisitor.analyze(self.config,
                                                    module_func.__name__, 
                                                    source, pragmas)
        self.recorder.add_metadata(metadata)
        transformer = CoverageAnnotator(self.config,
                                        module_func.__name__,
                                        self.recorder)
        inst_module = transformer.visit(module)
        # print renderer.render(inst_module)
        return inst_module
    
    def _assert_recorder_setup(self, module, starting_lineno=0):
        assert isinstance(module, ast.Module)
        
        assert isinstance(module.body[starting_lineno], ast.ImportFrom)
        assert module.body[starting_lineno].module == 'instrumental.recorder'
        assert isinstance(module.body[starting_lineno].names[0], ast.alias)
        assert module.body[starting_lineno].names[0].name == 'ExecutionRecorder'
        
        assert isinstance(module.body[starting_lineno+1], ast.Assign)
        assert isinstance(module.body[starting_lineno+1].targets[0], ast.Name)
        assert module.body[starting_lineno+1].targets[0].id == '_xxx_recorder_xxx_'
        assert isinstance(module.body[starting_lineno+1].value, ast.Call)
        assert isinstance(module.body[starting_lineno+1].value.func, ast.Attribute)
        assert isinstance(module.body[starting_lineno+1].value.func.value, ast.Name)
        assert module.body[starting_lineno+1].value.func.value.id == 'ExecutionRecorder'
        assert module.body[starting_lineno+1].value.func.attr == 'get'
        assert not module.body[starting_lineno+1].value.args
        assert not module.body[starting_lineno+1].value.keywords
        assert not module.body[starting_lineno+1].value.starargs
        assert not module.body[starting_lineno+1].value.kwargs
    
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

def setup():
    if os.path.exists('.instrumental.cache'):
        shutil.rmtree('.instrumental.cache')
