from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr

class TestLogicalAnd(object):
    
    def test_constructor_takes_pin_count(self):
        assert LogicalAnd(3)
    
    def test_has_conditions(self):
        and_ = LogicalAnd(3)
        assert hasattr(and_, 'conditions')
    
    def test_has_n_plus_2_conditions(self):
        and_ = LogicalAnd(3)
        assert 5 == len(and_.conditions)
    
    def test_has_conditions_0_through_n_plus_2(self):
        and_ = LogicalAnd(3)
        for i in range(5):
            assert i in and_.conditions, (i, and_.conditions)
    
    def test_condition_0_is_all_true(self):
        and_ = LogicalAnd(3)
        assert "T T T" == and_.description(0)
        
    def test_condition_1_is_first_pin_false(self):
        and_ = LogicalAnd(3)
        assert "F * *" == and_.description(1), and_.description(1)
        
    def test_condition_2_is_second_pin_false(self):
        and_ = LogicalAnd(3)
        assert "T F *" == and_.description(2), and_.description(2)
        
    def test_condition_3_is_third_pin_false(self):
        and_ = LogicalAnd(3)
        assert "T T F" == and_.description(3), and_.description(3)
        
    def test_condition_4_is_other(self):
        and_ = LogicalAnd(3)
        assert "Other" == and_.description(4), and_.description(4)
    
    def test_2_pin_and_condition_0(self):
        and_ = LogicalAnd(2)
        assert "T T" == and_.description(0)

    def test_2_pin_and_condition_1(self):
        and_ = LogicalAnd(2)
        assert "F *" == and_.description(1)

    def test_2_pin_and_condition_2(self):
        and_ = LogicalAnd(2)
        assert "T F" == and_.description(2)

    def test_2_pin_and_condition_3(self):
        and_ = LogicalAnd(2)
        assert "Other" == and_.description(3)

class TestLogicalOr(object):
    
    def test_constructor_takes_pin_count(self):
        assert LogicalOr(3)
    
    def test_has_conditions(self):
        or_ = LogicalOr(3)
        assert hasattr(or_, 'conditions')
    
    def test_has_n_plus_2_conditions(self):
        or_ = LogicalOr(3)
        assert 5 == len(or_.conditions)
    
    def test_has_conditions_0_through_n_plus_2(self):
        or_ = LogicalOr(3)
        for i in range(5):
            assert i in or_.conditions, (i, or_.conditions)
    
    def test_condition_0_is_first_pin_true(self):
        or_ = LogicalOr(3)
        assert "T * *" == or_.description(0), or_.description(0)
        
    def test_condition_1_is_second_pin_true(self):
        or_ = LogicalOr(3)
        assert "F T *" == or_.description(1), or_.description(1)
        
    def test_condition_2_is_third_pin_true(self):
        or_ = LogicalOr(3)
        assert "F F T" == or_.description(2), or_.description(2)
        
    def test_condition_3_is_all_false(self):
        or_ = LogicalOr(3)
        assert "F F F" == or_.description(3), or_.description(3)
        
    def test_condition_4_is_other(self):
        or_ = LogicalOr(3)
        assert "Other" == or_.description(4), or_.description(4)
    
    def test_2_pin_or_condition_0(self):
        or_ = LogicalOr(2)
        assert "T *" == or_.description(0)

    def test_2_pin_or_condition_1(self):
        or_ = LogicalOr(2)
        assert "F T" == or_.description(1)

    def test_2_pin_or_condition_2(self):
        or_ = LogicalOr(2)
        assert "F F" == or_.description(2)

    def test_2_pin_or_condition_3(self):
        or_ = LogicalOr(2)
        assert "Other" == or_.description(3)

