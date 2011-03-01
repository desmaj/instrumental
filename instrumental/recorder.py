import ast
from copy import copy
from copy import deepcopy
import inspect
import sys

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
        for label, construct in sorted(self._recorder._constructs.items(),
                                       key=lambda (l, c): (c.modulename, c.lineno, l)):
            construct_name = "%s:%s <%s>" % (construct.modulename, construct.lineno, construct.source)
            lines.append("%s" % (construct_name,))
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
        self._next_label = 1
        self._constructs = {}
    
    def next_label(self):
        label = self._next_label
        self._next_label += 1
        return label
    
    def record(self, arg, label, *args, **kwargs):
        self._constructs[label].record(arg, *args, **kwargs)
        return arg
    
    def add_BoolOp(self, modulename, node):
        if isinstance(node.op, ast.And):
            construct_klass = LogicalAnd
        elif isinstance(node.op, ast.Or):
            construct_klass = LogicalOr
        else:
            raise TypeError("Expected a BoolOp node with an op field of ast.And or ast.Or")
        construct = construct_klass(modulename, node, len(node.values))
        
        label = self.next_label()
        self._constructs[label] = construct
        
        # Now wrap the individual values in recorder calls
        base_call = self.get_recorder_call()
        base_call.args = \
            [ast.Num(n=label, lineno=node.lineno, col_offset=node.col_offset)]
        for i, value in enumerate(node.values):
            recorder_call = deepcopy(base_call)
            recorder_call.args.insert(0, node.values[i])
            recorder_call.args.append(ast.copy_location(ast.Num(n=i), node.values[i]))
            node.values[i] = ast.copy_location(recorder_call, node.values[i])
        return node
    
