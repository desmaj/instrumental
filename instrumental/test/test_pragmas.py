from astkit import ast

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

class TestPragmaNoCondition(object):
    
    def test_conditions_are_ignored(self):
        import re
        from astkit import ast
        from instrumental.constructs import LogicalAnd
        from instrumental.pragmas import PragmaNoCondition
        node = ast.BoolOp(values=[ast.Name(id="x"), ast.Name(id="y")],
                          op=ast.And(),
                          lineno=17,
                          col_offset=4)
        construct = LogicalAnd('<string>', node, None)
        match = re.match(r'(T F,F \*)', 'T F,F *')
        pragma = PragmaNoCondition(match)
        construct = pragma(construct)
        assert '(x and y)' == construct.source
        assert 3 == construct.number_of_conditions()
        assert "T T" == construct.description(0)
        assert "F *" == construct.description(1)
        assert "T F" == construct.description(2)
        
        # T T
        construct.record(True, 0)
        construct.record(True, 1)
        
        assert not construct.conditions_missed()

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
