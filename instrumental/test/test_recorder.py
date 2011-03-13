from instrumental.recorder import ExecutionRecorder
from instrumental.recorder import ExecutionReport
from instrumental.recorder import ExecutionSummary

class FakeRecorder(object):
    
    def __init__(self, constructs):
        self._constructs = \
            dict((label, construct)
                 for label, construct in enumerate(constructs)
                 )

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
    
class TestExecutionSummary(object):
    
    def setup(self):
        self.T = FakeConstruct("True only", True)
        self.F = FakeConstruct("False only", False)
        self.TF = FakeConstruct("Both", True, False)
        self.missed = FakeConstruct("Neither")
    
    def _makeOne(self, constructs=[], showall=False):
        recorder = FakeRecorder(constructs)
        print recorder._constructs
        return ExecutionSummary(recorder, showall)
        
    def test_header(self):
        expected_header = """
-----------------------------
Instrumental Coverage Summary
-----------------------------
"""
        
        summary = self._makeOne()
        assert expected_header in str(summary)
    
    def test_showall_true(self):
        summary = self._makeOne([self.missed], True)
        assert "ConstructResult(Neither)" in str(summary), str(summary)
