from astkit import ast

from instrumental.recorder import ExecutionRecorder

class KnownValue(object):
    pass

class TestRecorder(object):
    def setup(self):
        # Reset recorder
        ExecutionRecorder.reset()
    
    def test_construct_with_literal(self):
        recorder = ExecutionRecorder.get()
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id="foo"),
                                  ast.Str(s='""')],
                          lineno=1,
                          col_offset=0)
        recorder.add_BoolOp('somemodule', '1.1', node, [], None)
    
    def test_add_a_non_BoolOp(self):
        recorder = ExecutionRecorder.get()
        node = ast.BoolOp(op=4,
                          values=[ast.Name(id="foo"),
                                  ast.Str(s='""')],
                          lineno=1,
                          col_offset=0)
        try:
            recorder.add_BoolOp('somemodule', node, [], None)
        except TypeError as exc:
            assert "BoolOp" in str(exc), exc

