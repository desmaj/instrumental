import ast

from instrumental import recorder

def force_location(tree, lineno, col_offset=0):
    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            node.lineno = lineno
            node.col_offset = col_offset

class Instrumenter(ast.NodeTransformer):
    
    def visit_Module(self, module):
        self.generic_visit(module)
        recorder_setup = recorder.get_setup()
        for node in recorder_setup:
            force_location(node, 1)
        module.body = recorder_setup + module.body
        return module
    
    def visit_BoolOp(self, boolop):
        execution_recorder = recorder.ExecutionRecorder.get()
        return execution_recorder.add_BoolOp(boolop)
