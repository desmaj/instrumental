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

    def _makeOne(self):
        return BooleanDecision(self.modulename, self.node)
    
    def test_a_new_one(self):
        decision = self._makeOne()
        assert self.modulename == decision.modulename
        assert 5 == decision.lineno
        assert "(x == 4)" == decision.source
        assert {True: False,
                False: False} == decision.conditions
    
    def test_record_True(self):
        decision = self._makeOne()
        decision.record(True)
        assert {True: True,
                False: False} == decision.conditions
    
    def test_record_False(self):
        decision = self._makeOne()
        decision.record(False)
        assert {True: False,
                False: True} == decision.conditions
    
    def test_number_of_conditions(self):
        decision = self._makeOne()
        assert 2 == decision.number_of_conditions()
    
    def test_number_of_conditions_hit(self):
        decision = self._makeOne()
        decision.record(False)
        assert 1 == decision.number_of_conditions_hit()
    
    def test_conditions_missed(self):
        decision = self._makeOne()
        assert 2 == decision.conditions_missed()
    
    def _make_expected_result(self, decision, *conditions_hit):
        node_source = SourceCodeRenderer.render(self.node)
        result_lines = []
        result_lines.append("Decision -> %s:%s < %s >" % (self.modulename,
                                                          self.node.lineno,
                                                          node_source)
                            )
        result_lines.append("")
        for condition in ("T", "F"):
            result_lines.append("%s ==> %s" % (condition,
                                               condition in conditions_hit))
        return "\n".join(result_lines)
    
    def test_result_not_hit(self):
        decision = self._makeOne()
        expected = self._make_expected_result(decision)
        assert expected == decision.result(),\
            (expected, decision.result())
