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
