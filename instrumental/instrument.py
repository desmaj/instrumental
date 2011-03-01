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

class CoverageAnnotator(ast.NodeTransformer):
    
    def __init__(self):
        self.modulename = None
    
    def visit_Module(self, module):
        self.generic_visit(module)
        recorder_setup = recorder.get_setup()
        for node in recorder_setup:
            force_location(node, 1)
        module.body = recorder_setup + module.body
        return module
    
    def visit_BoolOp(self, boolop):
        execution_recorder = recorder.ExecutionRecorder.get()
        result = execution_recorder.add_BoolOp(self.modulename, boolop)
        self.generic_visit(boolop)
        return result
