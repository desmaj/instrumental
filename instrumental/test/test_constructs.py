from astkit import ast

from instrumental.constructs import BooleanDecision
from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr


class TestLogicalAnd(object):
    
    def _makeOne(self):
        node = ast.BoolOp(values=[ast.Name(id='a'),
                                  ast.Name(id='b')],
                          op=ast.And(),
                          col_offset=12,
                          lineno=3)
        construct = LogicalAnd('somemodule', '3.1', node, {})
        return construct
    
    def test_and_as_decision(self):
        construct = self._makeOne()
        assert construct.is_decision()
    
    def test_and_was_true(self):
        construct = self._makeOne()
        assert not construct.was_true()
    
    def test_and_was_false(self):
        construct = self._makeOne()
        assert not construct.was_false()
    
    def test_decision_result(self):
        construct = self._makeOne()
        expected = """Decision -> somemodule:3.1 < (a and b) >

T ==> 
F ==> """
        assert expected == construct.decision_result(), (expected, construct.decision_result())


class TestLogicalOr(object):
    
    def _makeOne(self):
        node = ast.BoolOp(values=[ast.Name(id='a'),
                                  ast.Name(id='b')],
                          op=ast.Or(),
                          col_offset=12,
                          lineno=3)
        construct = LogicalOr('somemodule', '3.1', node, {})
        return construct
    
    def test_or_as_decision(self):
        construct = self._makeOne()
        assert construct.is_decision()
    
    def test_or_was_true(self):
        construct = self._makeOne()
        assert not construct.was_true()
    
    def test_or_was_false(self):
        construct = self._makeOne()
        assert not construct.was_false()
    
    def test_decision_result(self):
        construct = self._makeOne()
        expected = """Decision -> somemodule:3.1 < (a or b) >

T ==> 
F ==> """
        assert expected == construct.decision_result(), (expected, construct.decision_result())


class TestBooleanDecision(object):
    
    def _makeOne(self):
        node = ast.Name(id="j",
                        col_offset=12,
                        lineno=3)
        construct = BooleanDecision('somemodule', '3.1', node, {})
        return construct
        
    def test_decision_result(self):
        construct = self._makeOne()
        expected = """Decision -> somemodule:3.1 < j >

T ==> 
F ==> """
        assert expected == construct.result(), (expected, construct.result())


