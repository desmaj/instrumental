import ast
from copy import copy
from copy import deepcopy
import inspect
import sys

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
        for label, construct in self._recorder._constructs.items():
            lines.append("%s: %s" % (label, construct.__class__.__name__))
            lines.append("\tT T T => %s" % construct._executed[(True, True, True)])
            lines.append("\tF T T => %s" % construct._executed[(False, True, True)])
            lines.append("\tT F T => %s" % construct._executed[(True, False, True)])
            lines.append("\tT T F => %s" % construct._executed[(True, True, False)])
            lines.append("\tOther => %s" % construct._executed[Other])
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
        kall.lineno = 2
        kall.col_offset = 0
        return kall
    
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._constructs = {}
    
    def record(self, label, *args):
        return self._constructs[label].record(*args)
    
    def add_BoolOp(self, node):
        label = "%s-%s" % (node.lineno, node.col_offset)
        if isinstance(node.op, ast.And):
            construct = _And(node)
        elif isinstance(node.op, ast.Or):
            construct = _Or(node)
        else:
            raise TypeError("Expected a BoolOp node with an op field of ast.And or ast.Or")
        self._constructs[label] = construct
        
        base_call = self.get_recorder_call()
        base_call.args = \
            [ast.Str(s=label, lineno=node.lineno, col_offset=node.col_offset)] +\
            [deepcopy(arg) for arg in node.values]
        return base_call

class Other: pass

class _LogicalBoolean(object):
    
    def _render(self, node):
        return str(node)
    
    def summary(self):
        acc = [self._render(self._node)]
        for condition, result in self._executed.items():
            acc.append("%s ==> %s" % (str(condition), result))
        return "\n".join(acc)
    
class _And(_LogicalBoolean):
    
    def __init__(self, node):
        self._node = node
        self._executed = {}
        pin_count = len(node.values)
        
        all_T = [True] * pin_count
        self._executed[tuple(all_T)] = False
        for i in range(pin_count):
            condition = copy(all_T)
            condition[i] = False
            self._executed[tuple(condition)] = False
        self._executed[Other] = False
    
    def record(self, *args):
        if args in self._executed:
            self._executed[args] = True
        else:
            self._executed[Other] = True
        return all(args)
    
class _Or(object):
    
    def __init__(self, node):
        self._node = node
        self._executed = {}
        pin_count = len(node.values)
        
        all_F = [False] * pin_count
        self._executed[tuple(all_F)] = False
        for i in range(pin_count):
            condition = copy(all_F)
            condition[i] = True
            self._executed[tuple(condition)] = False
        self._executed[Other] = False
    
    def record(self, *args):
        if args in self._executed:
            self._executed[args] = True
        else:
            self._executed[Other] = True
        return any(args)
    
