""" instrument.py - instruments ASTs representing Python programs
    
    We define instrument here to mean adding code that will have a side effect
    that we can measure so that we can determine when the code was executed.
    
    This is made difficult by the fact that python is so dynamic and that
    boolean operations have the properties that they do. The problems are that
    (a) the first non-True value will be returned from an and operation and the
    first non-False value will be returned from an or operation, (b) evaluation
    stops when the result of the operation has been determined.
    
    Because our approach is to re-write the target code so that it is
    functionally equivalent to the target code, we must take these properties
    into consideration. So the proper transformation of a three value and
    operation "a and b and c" is:
    
    >>> result = a
    >>> if result:
    >>>     result = result and b
    >>>     if result:
    >>>         result = result and c
    
    This is a series of statements and so it cannot replace the "a and b and c"
    expression. Instead, we'll have to create a guaranteed-unique local variable
    to use as the result, and we will have to preceed the statement that "owns"
    the expression with the transformation we have given above.
"""
import ast

from instrumental import recorder

def force_location(tree, lineno, col_offset=0):
    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            node.lineno = lineno
            node.col_offset = col_offset

class CoverageAnnotator(ast.NodeTransformer):
    
    def __init__(self):
        self.filepath = None
    
    def visit_Module(self, module):
        self.generic_visit(module)
        recorder_setup = recorder.get_setup()
        for node in recorder_setup:
            force_location(node, 1)
        module.body = recorder_setup + module.body
        return module
    
    def visit_BoolOp(self, boolop):
        self.generic_visit(boolop)
        execution_recorder = recorder.ExecutionRecorder.get()
        return execution_recorder.add_BoolOp(self.filepath, boolop)
