import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from astkit import ast

from instrumental.constructs import BooleanDecision
from instrumental.constructs import Comparison
from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr
from instrumental.constructs import UnreachableCondition
from instrumental.metadata import ModuleMetadata
from instrumental.recorder import ExecutionRecorder

class TestObjectEncoder(object):
    
    def test_encode_Node_flat(self):
        from instrumental.storage import ObjectEncoder as OE
        
        node = ast.Name(id="var", lineno=4, offset=14)
        result = OE().encode_Node(node)
        
        assert result == {'__python_class__': 'Name',
                          'id': 'var',
                          'lineno': 4,
                          'offset': 14,
                          }
    
    def test_encode_Node_nested(self):
        from instrumental.storage import ObjectEncoder as OE
        
        node = ast.Name(id="var", lineno=4, offset=14,
                        context=ast.Load())
        result = OE().encode_Node(node)
        
        assert result == {'__python_class__': 'Name',
                          'id': 'var',
                          'lineno': 4,
                          'offset': 14,
                          'context': {'__python_class__': 'Load'},
                          }
    
    def test_encode_Node_with_list_attribute(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.Compare(left=ast.Name(id='a'),
                           ops=[ast.Eq()],
                           comparators=[ast.Num(n=4)])
        result = OE().encode_Node(node)
        
        expected = {'__python_class__': 'Compare',
                    'left': {'__python_class__': 'Name',
                             'id': 'a'},
                    'ops': [{'__python_class__': 'Eq'}],
                    'comparators': [{'__python_class__': 'Num',
                                     'n': 4}],
                    }
        
        assert result == expected, (result, expected)
    
    def test_encode_BooleanDecision(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.Compare(left=ast.Name(id='a'),
                           ops=[ast.Eq()],
                           comparators=[ast.Num(n=4)],
                           lineno=4)
        construct = BooleanDecision('somemodule', '4.1', node, [])
        construct.conditions = {False: set(), True: set(['X'])}
        result = OE().encode(construct)
        
        expected = {'__python_class__': 'BooleanDecision',
                    'modulename': 'somemodule',
                    'label': '4.1',
                    'node': {'__python_class__': 'Compare',
                             'left': {'__python_class__': 'Name',
                                      'id': 'a'},
                             'ops': [{'__python_class__': 'Eq'}],
                             'comparators': [{'__python_class__': 'Num',
                                              'n': 4}],
                             'lineno': 4,
                             },
                    'conditions': {0: [], 1: ['X']},
                    }
        
        assert result == expected
    
    def test_encode_Comparison(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.Compare(left=ast.Name(id='a'),
                           ops=[ast.Eq()],
                           comparators=[ast.Num(n=4)],
                           lineno=4)
        construct = Comparison('somemodule', '4.2', node, [])
        construct.conditions = {False: set(), True: set(['X'])}
        result = OE().encode(construct)
        
        expected = {'__python_class__': 'Comparison',
                    'modulename': 'somemodule',
                    'label': '4.2',
                    'node': {'__python_class__': 'Compare',
                             'left': {'__python_class__': 'Name',
                                      'id': 'a'},
                             'ops': [{'__python_class__': 'Eq'}],
                             'comparators': [{'__python_class__': 'Num',
                                              'n': 4}],
                             'lineno': 4,
                             },
                    'conditions': {0: [], 1: ['X']},
                    }
        
        assert result == expected
    
    def test_encode_LogicalAnd(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalAnd('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']), 
                                2: set([UnreachableCondition])}
        result = OE().encode(construct)
        
        expected = {'__python_class__': 'LogicalAnd',
                    'modulename': 'somemodule',
                    'label': '4.2',
                    'node': {'__python_class__': 'BoolOp',
                             'op': {'__python_class__': 'And'},
                             'values': [{'__python_class__': 'Name',
                                         'id': 'a'},
                                        {'__python_class__': 'Name',
                                         'id': 'b'}],
                             'lineno': 4,
                             },
                    'conditions': {0: [], 1: ['X'], 2: ['__unreachable__']},
                    }
        
        assert result == expected
    
    def test_encode_LogicalOr(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']), 2: set()}
        result = OE().encode(construct)
        
        expected = {'__python_class__': 'LogicalOr',
                    'modulename': 'somemodule',
                    'label': '4.2',
                    'node': {'__python_class__': 'BoolOp',
                             'op': {'__python_class__': 'Or'},
                             'values': [{'__python_class__': 'Name',
                                         'id': 'a'},
                                        {'__python_class__': 'Name',
                                         'id': 'b'}],
                             'lineno': 4,
                             },
                    'conditions': {0: [], 1: ['X'], 2: []},
                    }
        
        assert result == expected
    
    def test_encode_ModuleMetadata(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']), 2: set()}
        metadata = ModuleMetadata('somemodule', 'somesource', [])
        metadata.lines = {1: False, 2: False, 4: True}
        metadata.constructs = {'4.2': construct}
        result = OE().encode(metadata)
        
        expected_construct = {'__python_class__': 'LogicalOr',
                              'modulename': 'somemodule',
                              'label': '4.2',
                              'node': {'__python_class__': 'BoolOp',
                                       'op': {'__python_class__': 'Or'},
                                       'values': [{'__python_class__': 'Name',
                                                   'id': 'a'},
                                                  {'__python_class__': 'Name',
                                                   'id': 'b'}],
                                       'lineno': 4,
                                       },
                              'conditions': {0: [], 1: ['X'], 2: []},
                              }
        expected = {'__python_class__': 'ModuleMetadata',
                    'modulename': 'somemodule',
                    'source': 'somesource',
                    'lines': {1: False, 2: False, 4: True},
                    'constructs': {'4.2': expected_construct},
                    }
        
        assert result == expected, (result, expected)

    def test_Encode_ExecutionRecorder(self):
        from instrumental.storage import ObjectEncoder as OE
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']), 2: set()}
        metadata = ModuleMetadata('somemodule', 'somesource', [])
        metadata.lines = {1: False, 2: False, 4: True}
        metadata.constructs = {'4.2': construct}
        recorder = ExecutionRecorder()
        recorder.add_metadata(metadata)
        
        result = OE().encode(recorder)
        
        expected_construct = {'__python_class__': 'LogicalOr',
                              'modulename': 'somemodule',
                              'label': '4.2',
                              'node': {'__python_class__': 'BoolOp',
                                       'op': {'__python_class__': 'Or'},
                                       'values': [{'__python_class__': 'Name',
                                                   'id': 'a'},
                                                  {'__python_class__': 'Name',
                                                   'id': 'b'}],
                                       'lineno': 4,
                                       },
                              'conditions': {0: [], 1: ['X'], 2: []},
                              }
        expected_metadata = {'__python_class__': 'ModuleMetadata',
                             'modulename': 'somemodule',
                             'source': 'somesource',
                             'lines': {1: False, 2: False, 4: True},
                             'constructs': {'4.2': expected_construct},
                             }
        expected = {'__python_class__': 'ExecutionRecorder',
                    'metadata': {'somemodule': expected_metadata},
                    }
        
        assert result == expected, (result, expected)

class TestJSONSerializer(object):
    
    def test_roundtrip(self):
        from instrumental.storage import JSONSerializer
        
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']),
                                2: set([UnreachableCondition])}
        metadata = ModuleMetadata('somemodule', 'somesource', [])
        metadata.lines = {1: False, 2: False, 4: True}
        metadata.constructs = {'4.2': construct}
        recorder = ExecutionRecorder()
        recorder.add_metadata(metadata)
        
        f = StringIO()
        
        JSONSerializer.dump(recorder, f)
        
        f.seek(0)
        
        got_recorder = JSONSerializer.load(f)
        
        got_metadata = got_recorder.metadata['somemodule']
        assert got_metadata.modulename == 'somemodule'
        assert got_metadata.source == 'somesource'
        assert got_metadata.lines == {1: False, 2: False, 4: True},(
            got_metadata.lines)
        
        got_construct = got_metadata.constructs['4.2']
        assert got_construct.modulename == 'somemodule'
        assert got_construct.label == '4.2'
        assert got_construct.conditions == {0: set(),
                                            1: set(['X']),
                                            2: set([UnreachableCondition])}
        
        got_node = got_construct.node
        assert isinstance(got_node.op, ast.Or)
        assert isinstance(got_node.values[0], ast.Name)
        assert got_node.values[0].id == 'a'
        assert isinstance(got_node.values[1], ast.Name)
        assert got_node.values[1].id == 'b'
        assert got_node.lineno == 4

class TestObjectDecoder(object):
    
    def test_decode_Node(self):
        from instrumental.storage import ObjectDecoder as OD
        
        d = {'__python_class__': 'BoolOp',
             'op': {'__python_class__': 'Or'},
             'values': [{'__python_class__': 'Name',
                         'id': 'a'},
                        {'__python_class__': 'Name',
                         'id': 'b'},
                        ],
             'lineno': 4}
        
        node = OD().decode_Node(d)
        
        assert isinstance(node, ast.BoolOp)
        assert isinstance(node.op, ast.Or)
        assert isinstance(node.values[0], ast.Name)
        assert node.values[0].id == 'a'
        assert isinstance(node.values[1], ast.Name)
        assert node.values[1].id == 'b'
        assert node.lineno == 4

    def test_decode_BooleanDecision(self):
        from instrumental.storage import ObjectDecoder as OD
        
        n = {'__python_class__': 'BoolOp',
             'op': {'__python_class__': 'Or'},
             'values': [{'__python_class__': 'Name',
                         'id': 'a'},
                        {'__python_class__': 'Name',
                         'id': 'b'},
                        ],
             'lineno': 4,
             }
        d = {'__python_class__': 'BooleanDecision',
             'modulename': 'somemodule',
             'label': '4.2',
             'node': n,
             'conditions': {False: [], True: ['X']},
             }
        
        decision = OD.decode(d)
        
        assert isinstance(decision, BooleanDecision)
        assert decision.modulename == 'somemodule'
        assert decision.label == '4.2'
        assert decision.conditions == {False: set(), True: set(['X'])}
        
        assert isinstance(decision.node, ast.BoolOp)
        assert isinstance(decision.node.op, ast.Or)
        assert isinstance(decision.node.values[0], ast.Name)
        assert decision.node.values[0].id == 'a'
        assert isinstance(decision.node.values[1], ast.Name)
        assert decision.node.values[1].id == 'b'
        assert decision.node.lineno == 4
        
    def test_decode_Comparison(self):
        from instrumental.storage import ObjectDecoder as OD
        
        n = {'__python_class__': 'Compare',
             'left': {'__python_class__': 'Name', 'id': 'a'},
             'ops': [{'__python_class__': 'Eq'}],
             'comparators': [{'__python_class__': 'Num',
                              'n': 4}],
             'lineno': 4,
             }
        d = {'__python_class__': 'Comparison',
             'modulename': 'somemodule',
             'label': '4.2',
             'node': n,
             'conditions': {False: [], True: ['X']},
             }
        
        decision = OD.decode(d)
        
        assert isinstance(decision, Comparison)
        assert decision.modulename == 'somemodule'
        assert decision.label == '4.2'
        assert decision.conditions == {False: set(), True: set(['X'])}
        
        assert isinstance(decision.node, ast.Compare)
        assert isinstance(decision.node.left, ast.Name)
        assert decision.node.left.id == 'a'
        assert isinstance(decision.node.ops[0], ast.Eq)
        assert isinstance(decision.node.comparators[0], ast.Num)
        assert decision.node.comparators[0].n == 4
        assert decision.node.lineno == 4
        
    def test_decode_LogicalAnd(self):
        from instrumental.storage import ObjectDecoder as OD
        
        n = {'__python_class__': 'BoolOp',
             'op': {'__python_class__': 'And'},
             'values': [{'__python_class__': 'Name',
                         'id': 'a'},
                        {'__python_class__': 'Name',
                         'id': 'b'},
                        ],
             'lineno': 4,
             }
        d = {'__python_class__': 'LogicalAnd',
             'modulename': 'somemodule',
             'label': '4.2',
             'node': n,
             'conditions': {0: [], 1: ['X'], 2: ['__unreachable__']},
             }
        
        decision = OD.decode(d)
        
        assert isinstance(decision, LogicalAnd)
        assert decision.modulename == 'somemodule'
        assert decision.label == '4.2'
        assert decision.conditions == {0: set(), 1: set(['X']),
                                       2: set([UnreachableCondition])}
        
        assert isinstance(decision.node, ast.BoolOp)
        assert isinstance(decision.node.op, ast.And)
        assert isinstance(decision.node.values[0], ast.Name)
        assert decision.node.values[0].id == 'a'
        assert isinstance(decision.node.values[1], ast.Name)
        assert decision.node.values[1].id == 'b'
        assert decision.node.lineno == 4
        
    def test_decode_LogicalOr(self):
        from instrumental.storage import ObjectDecoder as OD
        
        n = {'__python_class__': 'BoolOp',
             'op': {'__python_class__': 'Or'},
             'values': [{'__python_class__': 'Name',
                         'id': 'a'},
                        {'__python_class__': 'Name',
                         'id': 'b'},
                        ],
             'lineno': 4,
             }
        d = {'__python_class__': 'LogicalOr',
             'modulename': 'somemodule',
             'label': '4.2',
             'node': n,
             'conditions': {0: [], 1: ['X'], 2: ['__unreachable__']},
             }
        
        decision = OD.decode(d)
        
        assert isinstance(decision, LogicalOr)
        assert decision.modulename == 'somemodule'
        assert decision.label == '4.2'
        assert decision.conditions == {0: set(), 1: set(['X']),
                                       2: set([UnreachableCondition])}
        
        assert isinstance(decision.node, ast.BoolOp)
        assert isinstance(decision.node.op, ast.Or)
        assert isinstance(decision.node.values[0], ast.Name)
        assert decision.node.values[0].id == 'a'
        assert isinstance(decision.node.values[1], ast.Name)
        assert decision.node.values[1].id == 'b'
        assert decision.node.lineno == 4
        

class TestResultStore(object):
    
    def _makeOne(self, base, label, filename):
        from instrumental.storage import ResultStore
        return ResultStore(base, label, filename)
    
    def test_with_label(self):
        base = '.'
        label = 'p99999'
        filename = None
        
        store = self._makeOne(base, label, filename)
        
        expected_filename = './.instrumental.p99999.cov'
        assert store.filename == expected_filename
    
    def test_with_filename(self):
        base = '.'
        label = None
        filename = '.instrumental.me.cov'
        
        store = self._makeOne(base, label, filename)
        
        expected_filename = './.instrumental.me.cov'
        assert store.filename == expected_filename
    
    def test_with_neither(self):
        base = '.'
        label = None
        filename = None
        
        store = self._makeOne(base, label, filename)
        
        expected_filename = './.instrumental.cov'
        assert store.filename == expected_filename
    
    def test_roundtrip(self):
        from instrumental.storage import ResultStore
        
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'), ast.Name(id='b')],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        construct.conditions = {0: set(), 1: set(['X']),
                                2: set([UnreachableCondition])}
        metadata = ModuleMetadata('somemodule', 'somesource', [])
        metadata.lines = {1: False, 2: False, 4: True}
        metadata.constructs = {'4.2': construct}
        recorder = ExecutionRecorder()
        recorder.add_metadata(metadata)
        
        store = self._makeOne('.', 'testing', None)
        store.save(recorder)
        got_recorder = store.load()
        os.remove(store.filename)
        
        got_metadata = got_recorder.metadata['somemodule']
        assert got_metadata.modulename == 'somemodule'
        assert got_metadata.source == 'somesource'
        assert got_metadata.lines == {1: False, 2: False, 4: True},(
            got_metadata.lines)
        
        got_construct = got_metadata.constructs['4.2']
        assert got_construct.modulename == 'somemodule'
        assert got_construct.label == '4.2'
        assert got_construct.conditions == {0: set(),
                                            1: set(['X']),
                                            2: set([UnreachableCondition])}
        
        got_node = got_construct.node
        assert isinstance(got_node.op, ast.Or)
        assert isinstance(got_node.values[0], ast.Name)
        assert got_node.values[0].id == 'a'
        assert isinstance(got_node.values[1], ast.Name)
        assert got_node.values[1].id == 'b'
        assert got_node.lineno == 4


