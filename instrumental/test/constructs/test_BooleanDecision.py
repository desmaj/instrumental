import ast

from astkit.render import SourceCodeRenderer

from instrumental.constructs import BooleanDecision

class TestBooleanDecision(object):
    
    def setup(self):
        self.node = ast.Compare(left=ast.Name(id='x'),
                                ops=[ast.Eq()],
                                comparators=[ast.Num(n=4)],
                                lineno=5, col_offset=23)
        self.modulename = 'somepackage.somemodule'
        self.label = '5.1'

    def _makeOne(self):
        return BooleanDecision(self.modulename, self.label, self.node, {})
    
    def test_a_new_one(self):
        decision = self._makeOne()
        assert self.modulename == decision.modulename
        assert 5 == decision.lineno
        assert "(x == 4)" == decision.source
        assert {True: set(),
                False: set()} == decision.conditions
    
    def test_record_True(self):
        decision = self._makeOne()
        decision.record(True, 'X')
        assert decision.conditions[True] == set('X')
        assert not decision.conditions[False]
    
    def test_record_False(self):
        decision = self._makeOne()
        decision.record(False, 'X')
        assert not decision.conditions[True]
        assert decision.conditions[False] == set('X')
    
    def test_number_of_conditions(self):
        decision = self._makeOne()
        assert 2 == decision.number_of_conditions(False)
    
    def test_number_of_conditions_hit(self):
        decision = self._makeOne()
        decision.record(False, 'X')
        assert 1 == decision.number_of_conditions_hit()
    
    def test_conditions_missed(self):
        decision = self._makeOne()
        assert 2 == decision.conditions_missed(False)
    
    def _make_expected_result(self, decision, *conditions_hit):
        node_source = SourceCodeRenderer.render(self.node)
        result_lines = []
        result_lines.append("Decision -> %s:%s < %s >" % (self.modulename,
                                                          self.label,
                                                          node_source)
                            )
        result_lines.append("")
        for condition in ("T", "F"):
            tag = 'X' if condition in conditions_hit else ''
            result_lines.append("%s ==> %s" % (condition, tag))
        return "\n".join(result_lines)
    
    def test_result_not_hit(self):
        decision = self._makeOne()
        expected = self._make_expected_result(decision)
        assert expected == decision.result(),\
            (expected, decision.result())
