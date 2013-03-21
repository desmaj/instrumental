from instrumental import summary
from instrumental.test import DummyConfig

class TestPackage(object):
    
    def test_tests(self):
        assert 'instrumental.tests' == summary._package('instrumental.tests')
    
    def test_summary(self):
        assert 'instrumental' == summary._package('instrumental.summary')

class DummyConstruct(object):
    
    def __init__(self, modulename, decision, conditions):
        self.modulename = modulename
        self._decision = decision
        self.conditions = conditions
    
    def is_decision(self):
        return self._decision

class TestExecutionSummary(object):
    
    def test_empty(self):
        assert summary.ExecutionSummary({}, {}, None)
    
    def test_nonempty(self):
        statements = {'instrumental': {1: True, 2: True, 4: False},
                      'instrumental.tests': {1: False, 3:True, 5:False},
                      }
        _1_1 = DummyConstruct('instrumental',
                              True, 
                              {True: set(['X']),
                               False: set(['X']),
                               })
        _1_2 = DummyConstruct('instrumental',
                              False,
                              {0: set(['X']),
                               1: set(),
                               2: set(),
                               })
        _3_1 = DummyConstruct('intrumental.test',
                              True,
                              {True: set(['X']),
                               False: set(['X']),
                               })
        _3_2 = DummyConstruct('instrumental.test',
                              False,
                              {0: set(['X']),
                               1: set(),
                               2: set(),
                               })
        conditions = {'instrumental': 
                      {'1.1': _1_1,
                       '1.2': _1_2,
                       },
                      'instrumental.tests': 
                      {'3.1': _3_1,
                       '3.2': _3_2,
                       }
                      }
        s = summary.ExecutionSummary(conditions, statements, DummyConfig())
        packages = s.packages
        assert 'instrumental' in packages
