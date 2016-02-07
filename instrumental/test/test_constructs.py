import re

from astkit import ast

from instrumental import pragmas

from instrumental.constructs import BooleanDecision
from instrumental.constructs import Comparison
from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr
from instrumental.constructs import PragmaCondition
from instrumental.constructs import UnreachableCondition


class TestLogicalBoolean(object):
    
    def _makeOne(self, selector='3.1', pragmas=[]):
        node = ast.BoolOp(values=[ast.Name(id='a'),
                                  ast.Name(id='False')],
                          op=ast.And(),
                          col_offset=12,
                          lineno=3)
        construct = LogicalAnd('somemodule', selector, node, pragmas)
        return construct
    
    def test_unreachable_condition_renders_as_U(self):
        construct = self._makeOne()
        expected = """LogicalAnd -> somemodule:3.1 < (a and False) >

** One or more condition combinations may not be reachable due to the presence of a literal in the decision

T T ==> U
F * ==> 
T F ==> """
        assert expected == construct.result(), (expected, construct.result())
        
    
class TestLogicalAnd(object):
    
    def _makeOne(self, selector='3.1', pragmas=[]):
        node = ast.BoolOp(values=[ast.Name(id='a'),
                                  ast.Name(id='b')],
                          op=ast.And(),
                          col_offset=12,
                          lineno=3)
        construct = LogicalAnd('somemodule', selector, node, pragmas)
        return construct
    
    def test_and_as_decision(self):
        construct = self._makeOne()
        assert not construct.is_decision()
    
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

    def test_pragma_application(self):
        selector = '3.1'
        pattern = pragmas.no_cond
        pragma_match = re.match(pattern, 'no cond[3.1](T F)')
        pragma = pragmas.PragmaNoCondition(pragma_match)
        construct = self._makeOne(selector='3.1', pragmas=[pragma])
        assert construct.conditions[2] == set([pragma.NO_COND_TAG]),(
            (construct.conditions))

class TestLogicalOr(object):
    
    def _makeOne(self, selector='3.1', pragmas=[]):
        node = ast.BoolOp(values=[ast.Name(id='a'),
                                  ast.Name(id='b')],
                          op=ast.Or(),
                          col_offset=12,
                          lineno=3)
        construct = LogicalOr('somemodule', selector, node, pragmas)
        return construct
    
    def test_or_as_decision(self):
        construct = self._makeOne()
        assert not construct.is_decision()
    
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

    def test_pragma_application(self):
        selector = '3.1'
        pattern = pragmas.no_cond
        pragma_match = re.match(pattern, 'no cond[3.1](T *)')
        pragma = pragmas.PragmaNoCondition(pragma_match)
        construct = self._makeOne(selector='3.1', pragmas=[pragma])
        assert construct.conditions[0] == set([pragma.NO_COND_TAG]),(
            (construct.conditions))


class TestBooleanDecision(object):
    
    def _makeOne(self, selector='3.1', pragmas=[]):
        node = ast.Name(id="j",
                        col_offset=12,
                        lineno=3)
        construct = BooleanDecision('somemodule', selector, node, pragmas)
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
        assert 'F' == construct.description(False)
    
    def test_was_true_when_it_wasnt(self):
        construct = self._makeOne()
        assert not construct.was_true()
    
    def test_was_true_when_it_was(self):
        construct = self._makeOne()
        construct.conditions[True] = 'X'
        assert construct.was_true()
    
    def test_was_false_when_it_wasnt(self):
        construct = self._makeOne()
        assert not construct.was_false()
    
    def test_was_false_when_it_was(self):
        construct = self._makeOne()
        construct.conditions[False] = 'X'
        assert construct.was_false()
    
    def _makeOneWithLiteral(self):
        node = ast.Name(id="'j'",
                        col_offset=12,
                        lineno=3)
        construct = BooleanDecision('somemodule', '3.1', node, [])
        return construct
        
    def test_number_of_conditions_when_reporting_literals(self):
        construct = self._makeOneWithLiteral()
        assert 2 == construct.number_of_conditions(True)
        
    def test_pragma_application(self):
        selector = '3.1'
        pattern = pragmas.no_cond
        pragma_match = re.match(pattern, 'no cond[3.1](T)')
        pragma = pragmas.PragmaNoCondition(pragma_match)
        construct = self._makeOne(selector='3.1', pragmas=[pragma])
        assert construct.conditions[True] == set([pragma.NO_COND_TAG]),(
            (construct.conditions))
    
    def test_set_unreachable(self):
        construct = self._makeOne()
        construct.set_unreachable(True)
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition


class TestComparison(object):
    
    def _makeOne(self, selector='3.1', pragmas={}):
        node = ast.Compare(left=ast.Name(id='a'),
                           ops=[ast.Eq()],
                           comparators=[ast.Name(id='b')],
                           col_offset=12,
                           lineno=3)
        construct = Comparison('somemodule', selector, node, pragmas)
        return construct
    
    def test_decision_result(self):
        construct = self._makeOne()
        expected = """Compare -> somemodule:3.1 < (a == b) >

T ==> 
F ==> """
        assert expected == construct.result(), (expected, construct.result())
        
    def test_description_of_T(self):
        construct = self._makeOne()
        assert 'T' == construct.description(True)

    def test_description_of_F(self):
        construct = self._makeOne()
        assert 'F' == construct.description(False)

    def test_was_true_when_it_wasnt(self):
        construct = self._makeOne()
        assert not construct.was_true()
    
    def test_was_true_when_it_was(self):
        construct = self._makeOne()
        construct.conditions[True] = 'X'
        assert construct.was_true()
    
    def test_was_false_when_it_wasnt(self):
        construct = self._makeOne()
        assert not construct.was_false()
    
    def test_was_false_when_it_was(self):
        construct = self._makeOne()
        construct.conditions[False] = 'X'
        assert construct.was_false()

    def _makeOneWithLiteral(self, op=ast.Eq(),
                            left=ast.Num(n=4), right=ast.Num(n=4)):
        node = ast.Compare(left=left,
                           ops=[op],
                           comparators=[right],
                           col_offset=12,
                           lineno=3)
        construct = Comparison('somemodule', '3.1', node, {})
        return construct
    
    def test_number_of_conditions_when_reporting_literals(self):
        construct = self._makeOneWithLiteral()
        assert 2 == construct.number_of_conditions(True)
    
    def test_number_of_conditions_when_not_reporting_literals(self):
        construct = self._makeOneWithLiteral()
        assert 1 == construct.number_of_conditions(False)
    
    def test_pragma_application(self):
        selector = '3.1'
        pattern = pragmas.no_cond
        pragma_match = re.match(pattern, 'no cond[3.1](T)')
        pragma = pragmas.PragmaNoCondition(pragma_match)
        construct = self._makeOne(selector='3.1', pragmas=[pragma])
        assert construct.conditions[True] == set([pragma.NO_COND_TAG]),(
            (construct.conditions))

    def test_set_unreachable(self):
        construct = self._makeOne()
        construct.set_unreachable(True)
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_Eq(self):
        construct = self._makeOneWithLiteral(ast.Eq())
        condition = list(construct.conditions[False])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_NotEq(self):
        construct = self._makeOneWithLiteral(ast.NotEq())
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_Lt(self):
        construct = self._makeOneWithLiteral(ast.Lt())
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_LtE(self):
        construct = self._makeOneWithLiteral(ast.LtE())
        condition = list(construct.conditions[False])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_Gt(self):
        construct = self._makeOneWithLiteral(ast.Gt())
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_GtE(self):
        construct = self._makeOneWithLiteral(ast.GtE())
        condition = list(construct.conditions[False])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_Is(self):
        construct = self._makeOneWithLiteral(ast.Is())
        condition = list(construct.conditions[False])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_IsNot(self):
        construct = self._makeOneWithLiteral(ast.IsNot())
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_In(self):
        construct = self._makeOneWithLiteral(ast.In(), right=ast.List(elts=[]))
        condition = list(construct.conditions[True])[0]
        assert condition == UnreachableCondition
    
    def test_unreachable_NotIn(self):
        construct = self._makeOneWithLiteral(ast.NotIn(), right=ast.List(elts=[]))
        condition = list(construct.conditions[False])[0]
        assert condition == UnreachableCondition
    

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
    
class TestPragmaCondition(object):
    
    def test_str(self):
        assert 'P' == str(PragmaCondition())
