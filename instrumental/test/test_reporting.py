from instrumental.reporting import ExecutionReport

class FakeConstruct(object):
    
    def __init__(self, label, *conditions_hit):
        self.label = label
        self.modulename = "somemodulename"
        self.lineno = 17
        self.conditions = {True: False,
                           False: False}
        for condition in conditions_hit:
            self.conditions[condition] = True
    
    def result(self):
        return "ConstructResult(%s)" % self.label
    
class TestExecutionReport(object):
    
    def setup(self):
        self.T = FakeConstruct("True only", True)
        self.F = FakeConstruct("False only", False)
        self.TF = FakeConstruct("Both", True, False)
        self.missed = FakeConstruct("Neither")
    
    def _makeOne(self, working_directory='.', constructs={}, statements={}, sources={}):
        return ExecutionReport(working_directory, constructs, statements, sources)
        
    def test_header(self):
        expected_header = """
===============================================
Instrumental Condition/Decision Coverage Report
===============================================
"""
        
        reporter = self._makeOne()
        assert expected_header in reporter.report(), reporter.report()
    
    def test_showall_true(self):
        reporter = self._makeOne('.', {1: self.missed})
        assert "ConstructResult(Neither)" in reporter.report(True), reporter.report(True)
