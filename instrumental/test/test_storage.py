from astkit import ast

class TestTextStorage(object):
    # Turn off these tests because we turned off the TestSerializer
    __test__ = False
    
    def _makeOne(self):
        from instrumental.storage import TextSerializer
        return TextSerializer()
    
    def test_serialize_ModuleMetadata(self):
        from instrumental.metadata import ModuleMetadata
        from instrumental.constructs import BooleanDecision
        from instrumental.constructs import LogicalOr
        
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id="a"), ast.Name(id="b")],
                          lineno=4)
        
        decision = BooleanDecision('somemodule', '4.1', node, [])
        or_ = LogicalOr('somemodule', '4.2', node, [])
        
        md = ModuleMetadata('somemodule', '', [])
        md.lines = {1: False, 2: False, 4: True}
        md.constructs = {'4.1': decision, '4.2': or_}
        
        serializer = self._makeOne()
        actual = serializer.dump(md)
        expected = """ModuleMetadata
1:0,2:0,4:1
BooleanDecision|somemodule|4.1|BoolOp'4'Or'Name{a}'Name{b}||False:;True:
LogicalOr|somemodule|4.2|BoolOp'4'Or'Name{a}'Name{b}||0:;1:;2:
"""
        assert actual == expected, (actual, expected)
        
    def test_serialize_LogicalBoolean_Or(self):
        from instrumental.constructs import LogicalOr
        
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id="a"), ast.Name(id="b")],
                          lineno=4)
        construct = LogicalOr('somemodule', '4.2', node, [])
        
        serializer = self._makeOne()
        actual = serializer.dump(construct)
        expected = "LogicalOr|somemodule|4.2|BoolOp'4'Or'Name{a}'Name{b}||0:;1:;2:"
        assert actual == expected, (actual, expected)
    
    def test_serialize_LogicalBoolean_And(self):
        from instrumental.constructs import LogicalAnd
        
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id="a"), ast.Name(id="b")],
                          lineno=4)
        construct = LogicalAnd('somemodule', '4.2', node, [])
        
        serializer = self._makeOne()
        actual = serializer.dump(construct)
        expected = "LogicalAnd|somemodule|4.2|BoolOp'4'And'Name{a}'Name{b}||0:;1:;2:"
        assert actual == expected, (actual, expected)
    
    def test_serialize_BooleanDecision(self):
        from instrumental.constructs import BooleanDecision
        
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id="a"), ast.Name(id="b")],
                          lineno=4)
        construct = BooleanDecision('somemodule', '4.2', node, [])
        
        serializer = self._makeOne()
        actual = serializer.dump(construct)
        expected = "BooleanDecision|somemodule|4.2|BoolOp'4'And'Name{a}'Name{b}||False:;True:"
        assert actual == expected, (actual, expected)
    
    def test_serialize_Comparison(self):
        from instrumental.constructs import Comparison
        
        node = ast.Compare(left=ast.Name(id="a"),
                           ops=[ast.NotEq()],
                           comparators=[ast.Str(s="foobar")],
                           lineno=4)
        construct = Comparison('somemodule', '4.2', node, [])
        
        serializer = self._makeOne()
        actual = serializer.dump(construct)
        expected = "Comparison|somemodule|4.2|Compare'4'Name{a};NotEq;Str{Zm9vYmFy}||False:;True:"
        assert actual == expected, (actual, expected)
