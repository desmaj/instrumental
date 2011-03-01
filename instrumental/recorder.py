import ast
from copy import copy
from copy import deepcopy
import inspect
import sys

from astkit.render import SourceCodeRenderer

from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr

def __setup_recorder():
    from instrumental.recorder import ExecutionRecorder
    _xxx_recorder_xxx_ = ExecutionRecorder.get()

def get_setup():
    source = inspect.getsource(__setup_recorder)
    mod = ast.parse(source)
    defn = mod.body[0]
    setup = defn.body[:]
    for stmt in setup:
        stmt.lineno -= 1
    return setup

class ExecutionSummary(object):
    
    def __init__(self, recorder):
        self._recorder = recorder
    
    def __str__(self):
        lines = []
        lines.append("")
        lines.append("-----------------------------")
        lines.append("Instrumental Coverage Summary")
        lines.append("-----------------------------")
        lines.append("")
        for label, construct in sorted(self._recorder._constructs.items()):
            lines.append("%s:" % (label,))
            lines.append("")
            for condition in sorted(construct.conditions):
                lines.append(construct.description(condition) +\
                                 " ==> " +\
                                 str(construct.conditions[condition]))
            lines.append("")
        return "\n".join(lines)

class ExecutionRecorder(object):
    
    @staticmethod
    def get_recorder_call():
        kall = ast.Call()
        kall.func = ast.Attribute(value=ast.Name(id="_xxx_recorder_xxx_",
                                                 ctx=ast.Load(),
                                                 lineno=2, col_offset=0),
                                  attr="record",
                                  ctx=ast.Load(),
                                  lineno=2, col_offset=0)
        kall.keywords = []
        return kall
    
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._constructs = {}
    
    def record(self, arg, label, *args, **kwargs):
        self._constructs[label].record(arg, *args, **kwargs)
        return arg
    
    def add_BoolOp(self, filepath, node):
        source = SourceCodeRenderer.render(node)
        label = "%s [%s-%s] %s" %\
            (filepath, node.lineno, node.col_offset, source)
        if isinstance(node.op, ast.And):
            construct = LogicalAnd(len(node.values))
        elif isinstance(node.op, ast.Or):
            construct = LogicalOr(len(node.values))
        else:
            raise TypeError("Expected a BoolOp node with an op field of ast.And or ast.Or")
        self._constructs[label] = construct
        
        # Now wrap the individual values in recorder calls
        base_call = self.get_recorder_call()
        base_call.args = \
            [ast.Str(s=label, lineno=node.lineno, col_offset=node.col_offset)]
        for i, value in enumerate(node.values):
            recorder_call = deepcopy(base_call)
            recorder_call.args.insert(0, node.values[i])
            recorder_call.args.append(ast.copy_location(ast.Num(n=i), node.values[i]))
            node.values[i] = ast.copy_location(recorder_call, node.values[i])
        return node
    
