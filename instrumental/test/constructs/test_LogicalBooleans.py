import ast

from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalBoolean
from instrumental.constructs import LogicalOr
from instrumental.recorder import ExecutionRecorder

class ThreePinTestCase(object):
    
    def setup(self):
        self.modulename = 'somename'
        self.node = ast.BoolOp(values=[ast.Name(id='a'),
                                       ast.Name(id='b'),
                                       ast.Name(id='c'),
                                       ],
                               lineno=6,
                               col_offset=4)

class TwoPinTestCase(object):
    
    def setup(self):
        self.modulename = 'somename'
        self.node = ast.BoolOp(values=[ast.Name(id='a'),
                                       ast.Name(id='b'),
                                       ],
                               lineno=6,
                               col_offset=4)

class TestLogicalAnd(ThreePinTestCase):
    
    def setup(self):
        super(TestLogicalAnd, self).setup()
        self.node.op = ast.And()
    
    def _makeOne(self):
        return LogicalAnd(self.modulename, self.node)
    
    def test_constructor(self):
        assert LogicalAnd(self.modulename, self.node)
    
    def test_has_conditions(self):
        assert hasattr(self._makeOne(), 'conditions')
    
    def test_has_n_plus_2_conditions(self):
        and_ = self._makeOne()
        assert 4 == len(and_.conditions)
    
    def test_has_conditions_0_through_n_plus_1(self):
        and_ = self._makeOne()
        for i in range(4):
            assert i in and_.conditions
    
    def test_condition_0_is_all_true(self):
        and_ = self._makeOne()
        assert "T T T" == and_.description(0)
        
    def test_condition_1_is_first_pin_false(self):
        and_ = self._makeOne()
        assert "F * *" == and_.description(1), and_.description(1)
        
    def test_condition_2_is_second_pin_false(self):
        and_ = self._makeOne()
        assert "T F *" == and_.description(2), and_.description(2)
        
    def test_condition_3_is_third_pin_false(self):
        and_ = self._makeOne()
        assert "T T F" == and_.description(3), and_.description(3)
    
    def _expect_result(self, *set_conditions):
        expected_result = "\n".join(["LogicalAnd -> somename:6 < (a and b and c) >",
                                     "",
                                     "T T T ==> %s" % ("T T T" in set_conditions),
                                     "F * * ==> %s" % ("F * *" in set_conditions),
                                     "T F * ==> %s" % ("T F *" in set_conditions),
                                     "T T F ==> %s" % ("T T F" in set_conditions),
                                     ])
        return expected_result
                                     
    def test_all_true(self):
        and_ = self._makeOne()
        and_.record(True, 0)
        and_.record(True, 1)
        and_.record(True, 2)
        expected_result = self._expect_result('T T T')
        assert expected_result == and_.result()
        
    def test_F_T_T(self):
        and_ = self._makeOne()
        and_.record(False, 0)
        expected_result = self._expect_result('F * *')
        assert expected_result == and_.result(), and_.result()
        
    def test_T_F_T(self):
        and_ = self._makeOne()
        and_.record(True, 0)
        and_.record(False, 1)
        expected_result = self._expect_result('T F *')
        assert expected_result == and_.result()
        
    def test_T_T_F(self):
        and_ = self._makeOne()
        and_.record(True, 0)
        and_.record(True, 1)
        and_.record(False, 2)
        expected_result = self._expect_result('T T F')
        assert expected_result == and_.result()
        
class TestLogicalAnd2Pin(TwoPinTestCase):
    
    def setup(self):
        super(TestLogicalAnd2Pin, self).setup()
        self.node.op = ast.And()
    
    def _makeOne(self):
        return LogicalAnd(self.modulename, self.node)
    
    def test_2_pin_and_condition_0(self):
        and_ = self._makeOne()
        assert "T T" == and_.description(0)

    def test_2_pin_and_condition_1(self):
        and_ = self._makeOne()
        assert "F *" == and_.description(1)

    def test_2_pin_and_condition_2(self):
        and_ = self._makeOne()
        assert "T F" == and_.description(2)

    def test_2_pin_and_condition_3(self):
        and_ = self._makeOne()
        assert "Other" == and_.description(3)

class TestLogicalOr(ThreePinTestCase):
    
    def setup(self):
        super(TestLogicalOr, self).setup()
        self.node.op = ast.Or()
    
    def _makeOne(self):
        return LogicalOr(self.modulename, self.node)
    
    def test_has_conditions(self):
        or_ = self._makeOne()
        assert hasattr(or_, 'conditions')
    
    def test_has_n_plus_1_conditions(self):
        or_ = self._makeOne()
        assert 4 == len(or_.conditions)
    
    def test_has_conditions_0_through_n_plus_1(self):
        or_ = self._makeOne()
        for i in range(4):
            assert i in or_.conditions, (i, or_.conditions)
    
    def test_condition_0_is_first_pin_true(self):
        or_ = self._makeOne()
        assert "T * *" == or_.description(0), or_.description(0)
        
    def test_condition_1_is_second_pin_true(self):
        or_ = self._makeOne()
        assert "F T *" == or_.description(1), or_.description(1)
        
    def test_condition_2_is_third_pin_true(self):
        or_ = self._makeOne()
        assert "F F T" == or_.description(2), or_.description(2)
        
    def test_condition_3_is_all_false(self):
        or_ = self._makeOne()
        assert "F F F" == or_.description(3), or_.description(3)
        
    def test_condition_4_is_other(self):
        or_ = self._makeOne()
        assert "Other" == or_.description(4)
    
    def _expect_result(self, *set_conditions):
        expected_result = "\n".join(["LogicalOr -> somename:6 < (a or b or c) >",
                                     "",
                                     "T * * ==> %s" % ("T * *" in set_conditions),
                                     "F T * ==> %s" % ("F T *" in set_conditions),
                                     "F F T ==> %s" % ("F F T" in set_conditions),
                                     "F F F ==> %s" % ("F F F" in set_conditions),
                                     ])
        return expected_result
                                     
    def test_T_F_F(self):
        or_ = self._makeOne()
        or_.record(True, 0)
        expected_result = self._expect_result('T * *')
        assert expected_result == or_.result(), or_.result()
        
    def test_F_T_F(self):
        or_ = self._makeOne()
        or_.record(False, 0)
        or_.record(True, 1)
        expected_result = self._expect_result('F T *')
        assert expected_result == or_.result()
        
    def test_F_F_T(self):
        or_ = self._makeOne()
        or_.record(False, 0)
        or_.record(False, 1)
        or_.record(True, 2)
        expected_result = self._expect_result('F F T')
        assert expected_result == or_.result()
        
    def test_F_F_F(self):
        or_ = self._makeOne()
        or_.record(False, 0)
        or_.record(False, 1)
        or_.record(False, 2)
        expected_result = self._expect_result('F F F')
        assert expected_result == or_.result()
        
class TestLogicalOr2Pin(TwoPinTestCase):
    
    def setup(self):
        super(TestLogicalOr2Pin, self).setup()
        self.node.op = ast.Or()
    
    def _makeOne(self):
        return LogicalOr(self.modulename, self.node)
    
    def test_2_pin_or_condition_0(self):
        or_ = self._makeOne()
        assert "T *" == or_.description(0)

    def test_2_pin_or_condition_1(self):
        or_ = self._makeOne()
        assert "F T" == or_.description(1)

    def test_2_pin_or_condition_2(self):
        or_ = self._makeOne()
        assert "F F" == or_.description(2)

    def test_2_pin_or_condition_3(self):
        or_ = self._makeOne()
        assert "Other" == or_.description(3)

class TestLogicalBoolean(object):
    
    def setup(self):
        self.modulename = 'somename.subname'
        self.node = ast.BoolOp(values=[ast.Name(id='a'),
                                       ast.Name(id='b')],
                               op=ast.And(),
                               lineno=17,
                               col_offset=24,
                               )
    
    def _makeOne(self):
        return LogicalAnd(self.modulename, self.node)
    
    def test_modulename(self):
        construct = self._makeOne()
        assert self.modulename == construct.modulename
    
    def test_pins(self):
        construct = self._makeOne()
        assert 2 == construct.pins
    
    def test_source(self):
        construct = self._makeOne()
        assert "(a and b)" == construct.source
    
    def test_lineno(self):
        construct = self._makeOne()
        assert 17 == construct.lineno
    
    def test_conditions(self):
        construct = self._makeOne()
        assert {0: False,
                1: False,
                2: False,
                } == construct.conditions, construct.conditions
    
    def test_number_of_conditions(self):
        construct = self._makeOne()
        assert 3 == construct.number_of_conditions()
    
    def test_number_of_conditions_hit(self):
        construct = self._makeOne()
        assert 0 == construct.number_of_conditions_hit()
    
    def test_conditions_missed(self):
        construct = self._makeOne()
        assert 3 == construct.conditions_missed()
    
    def test_initial_result(self):
        construct = self._makeOne()
        expected_result = "\n".join(["LogicalAnd -> somename.subname:17 < (a and b) >",
                                     "",
                                     "T T ==> False",
                                     "F * ==> False",
                                     "T F ==> False",
                                     ])
        assert expected_result == construct.result()

class TestLiteralInConstruct(object):
    
    def setup(self):
        self.modulename = 'somename'
        self.node = ast.BoolOp(op=ast.Or(),
                               values=[ast.Name(id='a'),
                                       ast.Str(s='None'),
                                       ],
                               lineno=6,
                               col_offset=4)
    
    def test_presence_of_a_literal(self):
        recorder = ExecutionRecorder.get()
        recorder.add_BoolOp(self.modulename, self.node)
        construct = recorder.constructs.values()[0]
        assert "literal" in construct.result(), construct.result()
