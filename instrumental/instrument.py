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
    
    def visit_If(self, if_):
        if_.test = self.node_factory.instrument_test(self.modulename, if_.test)
        self.generic_visit(if_)
        return if_
    
    def visit_While(self, while_):
        while_.test = self.node_factory.instrument_test(self.modulename, while_.test)
        self.generic_visit(while_)
        return while_
