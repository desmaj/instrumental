""" instrument.py - instruments ASTs representing Python programs
    
    We define instrument here to mean adding code that will have a side effect
    that we can measure so that we can determine when the code was executed.
    
    This is made difficult by the fact that python is so dynamic and that
    boolean operations have the properties that they do. The problems are that
    (a) the first non-True value will be returned from an and operation and the
    first non-False value will be returned from an or operation, (b) evaluation
    stops when the result of the operation has been determined.
    
"""
import ast

from astkit.render import SourceCodeRenderer

from instrumental import recorder

def force_location(tree, lineno, col_offset=0):
    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            node.lineno = lineno
            node.col_offset = col_offset

class InstrumentedNodeFactory(object):
    
    def __init__(self, recorder):
        self._recorder = recorder
    
    def instrument_node(self, modulename, node):
        if isinstance(node, ast.BoolOp):
            return self._recorder.add_BoolOp(modulename, node)
        else:
            return node
    
    def instrument_test(self, modulename, node):
        return self._recorder.add_test(modulename, node)
    
    def instrument_statement(self, modulename, node):
        return self._recorder.add_statement(modulename, node)

class AnnotatorFactory(object):
    
    def __init__(self, recorder):
        self._recorder = recorder
    
    def create(self, modulename):
        return CoverageAnnotator(modulename, self._recorder)

class CoverageAnnotator(ast.NodeTransformer):
    
    def __init__(self, modulename, recorder):
        self.modulename = modulename
        self.node_factory = InstrumentedNodeFactory(recorder)
    
    def visit_Module(self, module):
        self.generic_visit(module)
        recorder_setup = recorder.get_setup()
        for node in recorder_setup:
            force_location(node, 1)
        module.body = recorder_setup + module.body
        return module
    
    def visit_BoolOp(self, boolop):
        instrumented_node =\
            self.node_factory.instrument_node(self.modulename, boolop)
        self.generic_visit(boolop)
        return instrumented_node
    
    def _visit_stmt(self, node):
        self.generic_visit(node)
        marker = self.node_factory.instrument_statement(self.modulename, node)
        return [marker, node]
        
    def visit_AugAssign(self, augassign):
        return self._visit_stmt(augassign)
    
    def visit_Assign(self, assign):
        return self._visit_stmt(assign)
    
    def visit_Break(self, break_):
        return self._visit_stmt(break_)
    
    # def visit_ClassDef(self, defn):
    #     return self._visit_stmt(defn)
    
    def visit_Continue(self, continue_):
        return self._visit_stmt(continue_)
    
    def visit_Delete(self, delete):
        return self._visit_stmt(delete)
    
    def visit_Exec(self, exec_):
        return self._visit_stmt(exec_)
    
    # def visit_Expr(self, expr):
    #     return self._visit_stmt(expr)
    
    def visit_FunctionDef(self, defn):
        return self._visit_stmt(defn)
    
    def visit_Global(self, global_):
        return self._visit_stmt(global_)
    
    def visit_If(self, if_):
        if_.test = self.node_factory.instrument_test(self.modulename, if_.test)
        self.generic_visit(if_)
        marker = self.node_factory.instrument_statement(self.modulename, if_)
        return [marker, if_]
    
    # def visit_Import(self, import_):
    #     return self._visit_stmt(import_)
    
    # def visit_ImportFrom(self, import_):
    #     return self._visit_stmt(import_)
    
    def visit_Pass(self, pass_):
        return self._visit_stmt(pass_)
    
    def visit_Print(self, print_):
        return self._visit_stmt(print_)
    
    def visit_Raise(self, raise_):
        return self._visit_stmt(raise_)
    
    def visit_Return(self, return_):
        return self._visit_stmt(return_)
    
    # def visit_TryExcept(self, try_):
    #     return self._visit_stmt(try_)
    
    def visit_TryFinally(self, try_):
        return self._visit_stmt(try_)
    
    def visit_While(self, while_):
        while_.test = self.node_factory.instrument_test(self.modulename, while_.test)
        self.generic_visit(while_)
        marker = self.node_factory.instrument_statement(self.modulename, while_)
        return [marker, while_]

    def visit_With(self, with_):
        return self._visit_stmt(with_)
