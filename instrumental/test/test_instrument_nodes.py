import inspect

from astkit.render import SourceCodeRenderer as renderer

from instrumental.compat import ast
from instrumental.instrument import CoverageAnnotator
from instrumental.recorder import ExecutionRecorder

def load_module(func):
    source = inspect.getsource(func)
    normal_source =\
        "\n".join(line[12:] for line in source.splitlines(False)[1:])
    module = ast.parse(normal_source)
    return module, normal_source

class TestInstrumentNodesPython2(object):
    
    def setup(self):
        # First clear out the recorder so that we'll create a new one
        ExecutionRecorder._instance = None
        self.recorder = ExecutionRecorder.get()
    
    def _instrument_module(self, module_func):
        module, source = load_module(module_func)
        self.recorder.add_source(module_func.__name__, source)
        transformer = CoverageAnnotator(module_func.__name__,
                                        self.recorder)
        inst_module = transformer.visit(module)
        print renderer.render(inst_module)
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
        assert isinstance(statement, ast.Expr)
        assert isinstance(statement.value, ast.Call)
        assert isinstance(statement.value.func, ast.Attribute)
        assert isinstance(statement.value.func.value, ast.Name)
        assert statement.value.func.value.id == '_xxx_recorder_xxx_'
        assert statement.value.func.attr == 'record_statement'
        assert isinstance(statement.value.args[0], ast.Str)
        assert statement.value.args[0].s == modname
        assert isinstance(statement.value.args[1], ast.Num)
        assert statement.value.args[1].n == lineno
    
    def test_simple_module(self):
        def test_module():
            a = True
            b = True
            result = a and b
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
    def test_FunctionDef(self):
        def test_module():
            def foo():
                bar = 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.FunctionDef)
        assert inst_module.body[3].name == 'foo'
        assert isinstance(inst_module.body[3].args, ast.arguments)
        assert not inst_module.body[3].args.args
        assert not inst_module.body[3].args.vararg
        assert not inst_module.body[3].args.kwarg
        assert not inst_module.body[3].args.defaults
        assert 2 == len(inst_module.body[3].body)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Assign)
        assert isinstance(inst_module.body[3].body[1].targets[0], ast.Name)
        assert inst_module.body[3].body[1].targets[0].id == 'bar'
        assert isinstance(inst_module.body[3].body[1].value, ast.Num)
        assert inst_module.body[3].body[1].value.n == 4
    
    def test_ClassDef(self):
        def test_module():
            class FooClass(object):
                bar = 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.ClassDef)
        assert inst_module.body[3].name == 'FooClass'
        assert isinstance(inst_module.body[3].bases[0], ast.Name)
        assert inst_module.body[3].bases[0].id == 'object'
        assert 2 == len(inst_module.body[3].body)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Assign)
        assert isinstance(inst_module.body[3].body[1].targets[0], ast.Name)
        assert inst_module.body[3].body[1].targets[0].id == 'bar'
        assert isinstance(inst_module.body[3].body[1].value, ast.Num)
        assert inst_module.body[3].body[1].value.n == 4
    
    def test_Return(self):
        def test_module():
            def foo():
                return 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.FunctionDef)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Return)
        assert isinstance(inst_module.body[3].body[1].value, ast.Num)
        assert inst_module.body[3].body[1].value.n == 4
    
    def test_Delete(self):
        def test_module():
            def foo():
                del bar
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.FunctionDef)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Delete)
        assert isinstance(inst_module.body[3].body[1].targets[0], ast.Name)
        assert inst_module.body[3].body[1].targets[0].id == 'bar'
    
    def test_Assign(self):
        def test_module():
            a = True
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.Assign)
        assert isinstance(inst_module.body[3].targets[0], ast.Name)
        assert inst_module.body[3].targets[0].id == 'a'
        assert isinstance(inst_module.body[3].value, ast.Name)
        assert inst_module.body[3].value.id == 'True'
    
    def test_AugAssign(self):
        def test_module():
            a += 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.AugAssign)
        assert isinstance(inst_module.body[3].target, ast.Name)
        assert inst_module.body[3].target.id == 'a'
        assert isinstance(inst_module.body[3].op, ast.Add)
        assert isinstance(inst_module.body[3].value, ast.Num)
        assert inst_module.body[3].value.n == 4
    
    def test_Print(self):
        def test_module():
            print bar
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.Print)
        assert not inst_module.body[3].dest
        assert isinstance(inst_module.body[3].values[0], ast.Name)
        assert inst_module.body[3].values[0].id == 'bar'
        assert inst_module.body[3].nl
    
    def test_For(self):
        def test_module():
            for i in [1,2,3,5]:
                print i
            else:
                print 'else'
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.For)
        assert isinstance(inst_module.body[3].target, ast.Name)
        assert inst_module.body[3].target.id == 'i'
        assert isinstance(inst_module.body[3].iter, ast.List)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Print)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Print)
    
    def test_While(self):
        def test_module():
            while i:
                print i
            else:
                print 'else'
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.While)
        assert isinstance(inst_module.body[3].test, ast.Call)
        assert isinstance(inst_module.body[3].test.func, ast.Attribute)
        assert isinstance(inst_module.body[3].test.func.value, ast.Name)
        assert inst_module.body[3].test.func.value.id == '_xxx_recorder_xxx_'
        assert inst_module.body[3].test.func.attr == 'record'
        assert isinstance(inst_module.body[3].test.args[0], ast.Name)
        assert inst_module.body[3].test.args[0].id == 'i'
        assert isinstance(inst_module.body[3].test.args[1], ast.Num)
        assert inst_module.body[3].test.args[1].n == 1
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Print)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Print)

    def test_If(self):
        def test_module():
            if i:
                print i
            else:
                print 'else'
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.If)
        assert isinstance(inst_module.body[3].test, ast.Call)
        assert isinstance(inst_module.body[3].test.func, ast.Attribute)
        assert isinstance(inst_module.body[3].test.func.value, ast.Name)
        assert inst_module.body[3].test.func.value.id == '_xxx_recorder_xxx_'
        assert inst_module.body[3].test.func.attr == 'record'
        assert isinstance(inst_module.body[3].test.args[0], ast.Name)
        assert inst_module.body[3].test.args[0].id == 'i'
        assert isinstance(inst_module.body[3].test.args[1], ast.Num)
        assert inst_module.body[3].test.args[1].n == 1
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Print)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Print)
