from astkit import ast

from instrumental.compat import exec_f
from instrumental.recorder import ExecutionRecorder
from instrumental.test import DummyConfig
from instrumental.test import InstrumentationTestCase

class TestPragmaFinder(object):
    
    def setup(self):
        from instrumental.pragmas import PragmaFinder
        self.finder = PragmaFinder()
    
    def test_pragma_no_cover(self):
        from instrumental.pragmas import PragmaNoCover
        source = """
acc = 1
acc += 2
if add_three:
    acc += 3 # pragma: no cover
acc += 4
"""
        pragmas = self.finder.find_pragmas(source)
        assert 6 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert not pragmas[4]
        assert pragmas[5], pragmas
        assert isinstance(list(pragmas[5])[0], PragmaNoCover)
        assert not pragmas[6]
    
    def test_pragma_nocover(self):
        from instrumental.pragmas import PragmaNoCover
        source = """
acc = 1
acc += 2
if add_three:
    acc += 3 # pragma: nocover
acc += 4
"""
        pragmas = self.finder.find_pragmas(source)
        assert 6 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert not pragmas[4]
        assert pragmas[5], pragmas
        assert isinstance(list(pragmas[5])[0], PragmaNoCover)
        assert not pragmas[6]
    
    def test_pragma_no_cover_on_FunctionDefn(self):
        from instrumental.pragmas import PragmaNoCover
        source = """
def somefunc(args): # pragma: nocover
    return 'howdy'
"""
        pragmas = self.finder.find_pragmas(source)
        assert 3 == len(pragmas), pragmas
        assert not pragmas[1]
        assert pragmas[2], pragmas
        assert isinstance(list(pragmas[2])[0], PragmaNoCover)
        assert pragmas[3], pragmas
        assert isinstance(list(pragmas[3])[0], PragmaNoCover)
    
    def test_pragma_no_cond_T(self):
        from instrumental.pragmas import PragmaNoCondition
        source = """
acc = 1
acc += 2
if add_three: # pragma: no cond(T)
    acc += 3
acc += 4
"""
        pragmas = self.finder.find_pragmas(source)
        assert 6 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert 1 == len(pragmas[4])
        pragma_4 = list(pragmas[4])[0]
        assert isinstance(pragma_4, PragmaNoCondition)
        assert pragma_4.conditions == ['T']
        assert not pragmas[5]
        assert not pragmas[6]

    def test_pragma_no_cond_T_F(self):
        from instrumental.pragmas import PragmaNoCondition
        source = """
acc = 1
acc += 2
if add_three and add_four: # pragma: no cond(T F)
    acc += 3
acc += 4
"""
        pragmas = self.finder.find_pragmas(source)
        assert 6 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert 1 == len(pragmas[4])
        pragma_4 = list(pragmas[4])[0]
        assert isinstance(pragma_4, PragmaNoCondition)
        assert pragma_4.conditions == ['T F']
        assert not pragmas[5]
        assert not pragmas[6]

    def test_pragma_no_cond_multiple_conditions(self):
        from instrumental.pragmas import PragmaNoCondition
        source = """
acc = 1
acc += 2
if add_three and add_four: # pragma: no cond(T F,F T)
    acc += 3
acc += 4
"""
        pragmas = self.finder.find_pragmas(source)
        assert 6 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert 1 == len(pragmas[4])
        pragma_4 = list(pragmas[4])[0]
        assert isinstance(pragma_4, PragmaNoCondition)
        assert sorted(pragma_4.conditions) == ['F T', 'T F']
        assert not pragmas[5]
        assert not pragmas[6]
    
    def test_pragma_no_cond_with_condition_selector(self):
        from instrumental.pragmas import PragmaNoCondition
        source = """
acc = 1
acc += 2
tot, err = a and b, c or d # pragma: no cond[.2](T F)
assert tot or err
"""
        pragmas = self.finder.find_pragmas(source)
        assert 5 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert 1 == len(pragmas[4])
        pragma_4_2 = list(pragmas[4])[0]
        assert isinstance(pragma_4_2, PragmaNoCondition)
        assert pragma_4_2.conditions == ['T F']
        assert not pragmas[5]
    
    def test_pragma_no_cond_with_full_selector(self):
        from instrumental.pragmas import PragmaNoCondition
        source = """# pragma: no cond[4.2](T F)
acc = 1
acc += 2
tot, err = a and b, c or d
assert tot or err
"""
        pragmas = self.finder.find_pragmas(source)
        assert 5 == len(pragmas), pragmas
        assert not pragmas[1]
        assert not pragmas[2]
        assert not pragmas[3]
        assert 1 == len(pragmas[4])
        pragma_4_2 = list(pragmas[4])[0]
        assert isinstance(pragma_4_2, PragmaNoCondition)
        assert pragma_4_2.selector == '2'
        assert pragma_4_2.conditions == ['T F']
        assert not pragmas[5]
    
class TestPragmaNoCondition(InstrumentationTestCase):
    
    def setup(self):
        self.config = DummyConfig()
        ExecutionRecorder.reset()
        ExecutionRecorder.get().start()
    
    def teardown(self):
        ExecutionRecorder.get().stop()        
    
    @property
    def recorder(self):
        return ExecutionRecorder.get()
    
    def test_conditions_are_ignored(self):
        import re
        from astkit import ast
        from instrumental.constructs import LogicalAnd
        from instrumental.pragmas import no_cond
        from instrumental.pragmas import PragmaNoCondition
        node = ast.BoolOp(values=[ast.Name(id="x"), ast.Name(id="y")],
                          op=ast.And(),
                          lineno=17,
                          col_offset=1)
        match = re.match(no_cond, 'no cond(T F,F *)')
        pragma = PragmaNoCondition(match)
        construct = LogicalAnd('<string>', '17.1', node, set([pragma]))
        assert '(x and y)' == construct.source
        assert 3 == construct.number_of_conditions(False)
        assert "T T" == construct.description(0)
        assert "F *" == construct.description(1)
        assert "T F" == construct.description(2)
        
        # T T
        construct.record(True, 0, '*')
        construct.record(True, 1, '*')
        
        assert not construct.conditions_missed(False)
        assert construct.conditions[0] == set(['*'])
        assert construct.conditions[1] == set(['P'])
        assert construct.conditions[2] == set(['P'])
    
    def test_roundtrip_with_full_selector(self):
        def dummy_module():
            # pragma: no cond[5.3](F *)
            a = True
            b = False
            c = False
            e = a and b or c
        mod = self._instrument_module(dummy_module)
        code = compile(mod, '<string>', 'exec')
        exec_f(code, globals())
        assert not e
        
        construct = self.recorder.metadata['dummy_module'].constructs['5.3']
        assert construct.source == '(a and b)', construct.source
        assert construct.conditions_missed(False)
        assert construct.conditions[0] == set([]) # T T
        assert construct.conditions[1] == set(['P']) # F *
        assert construct.conditions[2] == set([self.recorder.DEFAULT_TAG]) # T F
        
    def test_roundtrip_with_expression_selector(self):
        def dummy_module():
            a = True
            b = False
            c = False
            e = a and b or c # pragma: no cond[.3](F *)
        mod = self._instrument_module(dummy_module)
        code = compile(mod, '<string>', 'exec')
        exec_f(code, globals())
        assert not e
        
        construct = self.recorder.metadata['dummy_module'].constructs['4.3']
        assert construct.source == '(a and b)'
        assert construct.conditions_missed(False)
        assert construct.conditions[0] == set([]) # T T
        assert construct.conditions[1] == set(['P']) # F *
        assert construct.conditions[2] == set([self.recorder.DEFAULT_TAG]) # T F
        
    def test_conditions_are_ignored_for_decision(self):
        import re
        from astkit import ast
        from instrumental.constructs import BooleanDecision
        from instrumental.pragmas import no_cond
        from instrumental.pragmas import PragmaNoCondition
        node = ast.Name(id="x",
                        lineno=17,
                        col_offset=1)
        match = re.match(no_cond, 'no cond(T)')
        pragma = PragmaNoCondition(match)
        construct = BooleanDecision('<string>', '17.1', node, set([pragma]))
        assert 'x' == construct.source
        assert 1 == construct.number_of_conditions(False)
        assert "T" == construct.description(True)
        assert "F" == construct.description(False)
        
        # T T
        construct.record(False, '*')
        
        assert not construct.conditions_missed(False)
        assert construct.conditions[True] == set(['P'])
        assert construct.conditions[False] == set(['*'])
    
class TestInstrumentationWithPragmas(InstrumentationTestCase):
    
    def test_ClassDef(self):
        def test_module():
            foo = 7
            class FooClass(object): # pragma: no cover
                bar = 4
            baz = 8
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        
        assert isinstance(inst_module.body[3], ast.Assign)
        assert isinstance(inst_module.body[3].targets[0], ast.Name)
        assert inst_module.body[3].targets[0].id == 'foo'
        assert isinstance(inst_module.body[3].value, ast.Num)
        assert inst_module.body[3].value.n == 7
        
        assert isinstance(inst_module.body[4], ast.ClassDef), inst_module.body[4]
        assert inst_module.body[4].name == 'FooClass'
        assert isinstance(inst_module.body[4].bases[0], ast.Name)
        assert inst_module.body[4].bases[0].id == 'object'
        
        assert 1 == len(inst_module.body[4].body)
        assert isinstance(inst_module.body[4].body[0], ast.Assign)
        assert isinstance(inst_module.body[4].body[0].targets[0], ast.Name)
        assert inst_module.body[4].body[0].targets[0].id == 'bar'
        assert isinstance(inst_module.body[4].body[0].value, ast.Num)
        assert inst_module.body[4].body[0].value.n == 4
        
        self._assert_record_statement(inst_module.body[5], 'test_module', 4)
        
        assert isinstance(inst_module.body[6], ast.Assign)
        assert isinstance(inst_module.body[6].targets[0], ast.Name)
        assert inst_module.body[6].targets[0].id == 'baz'
        assert isinstance(inst_module.body[6].value, ast.Num)
        assert inst_module.body[6].value.n == 8

    def test_FunctionDef(self):
        def test_module():
            foo = 7
            def foo_func(): # pragma: no cover
                bar = 4
            baz = 8
        inst_module = self._instrument_module(test_module)
        self._assert_recorder_setup(inst_module)
        
        self._assert_record_statement(inst_module.body[2], 'test_module', 1)
        
        assert isinstance(inst_module.body[3], ast.Assign)
        assert isinstance(inst_module.body[3].targets[0], ast.Name)
        assert inst_module.body[3].targets[0].id == 'foo'
        assert isinstance(inst_module.body[3].value, ast.Num)
        assert inst_module.body[3].value.n == 7
        
        assert isinstance(inst_module.body[4], ast.FunctionDef), inst_module.body[4]
        assert inst_module.body[4].name == 'foo_func'
        assert not inst_module.body[4].args.args
        assert not inst_module.body[4].args.kwarg
        assert not inst_module.body[4].decorator_list
        
        assert 1 == len(inst_module.body[4].body)
        assert isinstance(inst_module.body[4].body[0], ast.Assign)
        assert isinstance(inst_module.body[4].body[0].targets[0], ast.Name)
        assert inst_module.body[4].body[0].targets[0].id == 'bar'
        assert isinstance(inst_module.body[4].body[0].value, ast.Num)
        assert inst_module.body[4].body[0].value.n == 4
        
        self._assert_record_statement(inst_module.body[5], 'test_module', 4)
        
        assert isinstance(inst_module.body[6], ast.Assign)
        assert isinstance(inst_module.body[6].targets[0], ast.Name)
        assert inst_module.body[6].targets[0].id == 'baz'
        assert isinstance(inst_module.body[6].value, ast.Num)
        assert inst_module.body[6].value.n == 8
