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


    def test_description_of_T(self):
        construct = self._makeOne()
        assert 'T' == construct.description(True)

    def test_description_of_F(self):
        construct = self._makeOne()
        assert 'T' == construct.description(True)

class TestUnreachableConditions(object):
    
    def _makeNode(self, op, conditions):
        return ast.BoolOp(values=conditions,
                          op=op)
    
    def _makeAnd(self, *conditions):
        node = self._makeNode(ast.And(), conditions)
        return LogicalAnd('somemodule', '3.1', node, {})
    
    def _makeOr(self, *conditions):
        node = self._makeNode(ast.Or(), conditions)
        return LogicalOr('somemodule', '3.1', node, {})
    
    def _test(self, expected, ctor, conditions):
        construct = ctor(*conditions)
        assert expected == construct.unreachable_conditions(),(
            expected, construct.unreachable_conditions())
    
    def test_And_without_literals(self):
        yield self._test, [], self._makeAnd, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_And_with_True_first_pin(self):
        yield self._test, [1], self._makeAnd, (
            ast.Name(id='True'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_And_with_False_first_pin(self):
        yield self._test, [], self._makeAnd, (
            ast.Name(id='False'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_And_with_True_second_pin(self):
        yield self._test, [2], self._makeAnd, (
            ast.Name(id='a'), ast.Name(id='True'), ast.Name(id='c'))
    
    def test_And_with_False_second_pin(self):
        yield self._test, [], self._makeAnd, (
            ast.Name(id='a'), ast.Name(id='False'), ast.Name(id='c'))
    
    def test_And_with_True_third_pin(self):
        yield self._test, [3], self._makeAnd, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='True'))
    
    def test_And_with_False_third_pin(self):
        yield self._test, [0], self._makeAnd, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='False'))
    
    def test_Or_without_literals(self):
        yield self._test, [], self._makeOr, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_Or_with_True_first_pin(self):
        yield self._test, [], self._makeOr, (
            ast.Name(id='True'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_Or_with_False_first_pin(self):
        yield self._test, [0], self._makeOr, (
            ast.Name(id='False'), ast.Name(id='b'), ast.Name(id='c'))
    
    def test_Or_with_True_second_pin(self):
        yield self._test, [], self._makeOr, (
            ast.Name(id='a'), ast.Name(id='True'), ast.Name(id='c'))
    
    def test_Or_with_False_second_pin(self):
        yield self._test, [1], self._makeOr, (
            ast.Name(id='a'), ast.Name(id='False'), ast.Name(id='c'))
    
    def test_Or_with_True_third_pin(self):
        yield self._test, [3], self._makeOr, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='True'))
    
    def test_Or_with_False_third_pin(self):
        yield self._test, [2], self._makeOr, (
            ast.Name(id='a'), ast.Name(id='b'), ast.Name(id='False'))
    
