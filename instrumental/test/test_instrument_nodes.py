import inspect
import sys

from astkit import ast
from astkit.render import SourceCodeRenderer as renderer

from instrumental.test import InstrumentationTestCase
from instrumental.test import load_module

class TestInstrumentNodesPython2(InstrumentationTestCase):
    
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
    
    def test_FunctionDef_with_docstring(self):
        def test_module():
            def foo():
                "I'm a little docstring"
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
        assert 3 == len(inst_module.body[3].body)
        assert isinstance(inst_module.body[3].body[0], ast.Expr)
        assert isinstance(inst_module.body[3].body[0].value, ast.Str)
        assert inst_module.body[3].body[0].value.s == "I'm a little docstring"
        self._assert_record_statement(inst_module.body[3].body[1], 'test_module', 3)
        assert isinstance(inst_module.body[3].body[2], ast.Assign)
        assert isinstance(inst_module.body[3].body[2].targets[0], ast.Name)
        assert inst_module.body[3].body[2].targets[0].id == 'bar'
        assert isinstance(inst_module.body[3].body[2].value, ast.Num)
        assert inst_module.body[3].body[2].value.n == 4
    
    def test_FunctionDef_with_docstring_and_no_cover(self):
        def test_module():
            def foo(): # pragma: no cover
                "I'm a little docstring"
                bar = 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        assert isinstance(inst_module.body[2], ast.FunctionDef)
        assert inst_module.body[2].name == 'foo'
        assert isinstance(inst_module.body[2].args, ast.arguments)
        assert not inst_module.body[2].args.args
        assert not inst_module.body[2].args.vararg
        assert not inst_module.body[2].args.kwarg
        assert not inst_module.body[2].args.defaults
        assert 2 == len(inst_module.body[2].body)
        assert isinstance(inst_module.body[2].body[0], ast.Expr)
        assert isinstance(inst_module.body[2].body[0].value, ast.Str)
        assert inst_module.body[2].body[0].value.s == "I'm a little docstring"
        assert isinstance(inst_module.body[2].body[1], ast.Assign)
        assert isinstance(inst_module.body[2].body[1].targets[0], ast.Name)
        assert inst_module.body[2].body[1].targets[0].id == 'bar'
        assert isinstance(inst_module.body[2].body[1].value, ast.Num)
        assert inst_module.body[2].body[1].value.n == 4
    
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
    
    def test_ClassDef_with_docstring(self):
        def test_module():
            class FooClass(object):
                "I'm a little docstring"
                bar = 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.ClassDef)
        assert inst_module.body[3].name == 'FooClass'
        assert isinstance(inst_module.body[3].bases[0], ast.Name)
        assert inst_module.body[3].bases[0].id == 'object'
        assert 3 == len(inst_module.body[3].body)
        assert isinstance(inst_module.body[3].body[0], ast.Expr)
        assert isinstance(inst_module.body[3].body[0].value, ast.Str)
        assert inst_module.body[3].body[0].value.s == "I'm a little docstring"
        self._assert_record_statement(inst_module.body[3].body[1], 'test_module', 3)
        assert isinstance(inst_module.body[3].body[2], ast.Assign)
        assert isinstance(inst_module.body[3].body[2].targets[0], ast.Name)
        assert inst_module.body[3].body[2].targets[0].id == 'bar'
        assert isinstance(inst_module.body[3].body[2].value, ast.Num)
        assert inst_module.body[3].body[2].value.n == 4
    
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
    
    def test_Assert(self):
        def test_module():
            assert a == 4
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.Assert)
        assert isinstance(inst_module.body[3].test, ast.Compare)
        assert isinstance(inst_module.body[3].test.left, ast.Name)
        assert inst_module.body[3].test.left.id == 'a'
        assert isinstance(inst_module.body[3].test.ops[0], ast.Eq)
        assert isinstance(inst_module.body[3].test.comparators[0], ast.Num)
        assert inst_module.body[3].test.comparators[0].n == 4
    
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
    
    def test_Break(self):
        def test_module():
            while True:
                break
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
        assert inst_module.body[3].test.args[0].id == 'True'
        assert isinstance(inst_module.body[3].test.args[1], ast.Str)
        assert inst_module.body[3].test.args[1].s == 'test_module'
        assert isinstance(inst_module.body[3].test.args[2], ast.Str)
        assert inst_module.body[3].test.args[2].s == '1.1'
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Break)
    
    def test_Continue(self):
        def test_module():
            while True:
                continue
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
        assert inst_module.body[3].test.args[0].id == 'True'
        assert isinstance(inst_module.body[3].test.args[1], ast.Str)
        assert inst_module.body[3].test.args[1].s == 'test_module'
        assert isinstance(inst_module.body[3].test.args[2], ast.Str)
        assert inst_module.body[3].test.args[2].s == '1.1'
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1], ast.Continue)
    
    if sys.version_info[0] < 3:
        from instrumental.test.py2_only import test_Print
    
    def test_For(self):
        def test_module():
            for i in [1,2,3,5]:
                return i
            else:
                return 'else'
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        assert isinstance(inst_module.body[3], ast.For)
        assert isinstance(inst_module.body[3].target, ast.Name)
        assert inst_module.body[3].target.id == 'i'
        assert isinstance(inst_module.body[3].iter, ast.List)
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Return)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Return)
    
    def test_While(self):
        def test_module():
            while i:
                return i
            else:
                return 'else'
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
        assert isinstance(inst_module.body[3].test.args[1], ast.Str)
        assert inst_module.body[3].test.args[1].s == 'test_module'
        assert isinstance(inst_module.body[3].test.args[2], ast.Str)
        assert inst_module.body[3].test.args[2].s == '1.1'
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Return)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Return)

    def test_If(self):
        def test_module():
            if i:
                return i
            else:
                return 'else'
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
        assert isinstance(inst_module.body[3].test.args[1], ast.Str)
        assert inst_module.body[3].test.args[1].s == 'test_module', inst_module.body[3].test.args[1].s
        assert isinstance(inst_module.body[3].test.args[2], ast.Str)
        assert inst_module.body[3].test.args[2].s == '1.1', inst_module.body[3].test.args[2].s
        assert not inst_module.body[3].test.keywords
        assert not hasattr(inst_module.body[3].test, 'starargs')
        assert not hasattr(inst_module.body[3].test, 'kwargs')
        self._assert_record_statement(inst_module.body[3].body[0], 'test_module', 2)
        assert isinstance(inst_module.body[3].body[1],ast.Return)
        self._assert_record_statement(inst_module.body[3].orelse[0], 'test_module', 4)
        assert isinstance(inst_module.body[3].orelse[1],ast.Return)
    
    def test_Module_with_docstring(self):
        def test_module():
            """ I am a docstring
                I span more than one line """
            if u:
                return u
            else:
                return 'else'
        inst_module = self._instrument_module(test_module)
        assert ast.get_docstring(inst_module)
        self._assert_recorder_setup(inst_module, 1)
    
    def test_Module_with_future_import(self):
        from instrumental.instrument import CoverageAnnotator
        from instrumental.metadata import MetadataGatheringVisitor
        from instrumental.pragmas import PragmaFinder
        
        source = """from __future__ import with_statement
if u:
    return u
else:
    return 'else'
"""
        module = ast.parse(source)
        pragmas = PragmaFinder().find_pragmas(source)
        metadata = MetadataGatheringVisitor.analyze('somemodule', 
                                                    'somemodule.py',
                                                    source, pragmas)
        self.recorder.add_metadata(metadata)
        transformer = CoverageAnnotator('somemodule',
                                        self.recorder)
        inst_module = transformer.visit(module)
        
        assert isinstance(inst_module.body[0], ast.ImportFrom)
        assert module.body[0].module == '__future__'
        assert isinstance(module.body[0].names[0], ast.alias)
        assert module.body[0].names[0].name == 'with_statement'
        self._assert_recorder_setup(inst_module, 1)
    
    def test_Module_with_docstring_and_future_import(self):
        from instrumental.instrument import CoverageAnnotator
        from instrumental.metadata import MetadataGatheringVisitor
        from instrumental.pragmas import PragmaFinder
        
        source = """'a docstring am I'
from __future__ import with_statement
if u:
    return u
else:
    return 'else'
"""
        module = ast.parse(source)
        pragmas = PragmaFinder().find_pragmas(source)
        metadata = MetadataGatheringVisitor.analyze('somemodule', 
                                                    'somemodule.py',
                                                    source, pragmas)
        self.recorder.add_metadata(metadata)
        transformer = CoverageAnnotator('somemodule',
                                        self.recorder)
        inst_module = transformer.visit(module)
        
        
        assert isinstance(inst_module.body[1], ast.ImportFrom)
        assert module.body[1].module == '__future__'
        assert isinstance(module.body[1].names[0], ast.alias)
        assert module.body[1].names[0].name == 'with_statement'
        self._assert_recorder_setup(inst_module, 2)
    
