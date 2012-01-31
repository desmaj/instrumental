import re

from instrumental.compat import ast

class PragmaNoCover(object):
    pass

valid_pragmas = {
    'no\s+cover': PragmaNoCover,
    }

class PragmaApplier(ast.NodeVisitor):
    """ Expand source-level line-pragmas relations to node-level relations
    
        This visitor starts with a mapping of source lines to the pragmas that
        should be applied to those source lines. Calling `apply` will start
        a traversal of the an AST during which source line and node
        dependencies will be used to determine to which lines the defined
        pragmas should be applied.
        
        This visitor should take into account that statements can be spread
        over multiple source lines and should produce a mapping with the
        pragmas for any given source line being applied to the line of the
        statement that contains the initial source line. (Think argument
        lists that cover more than one line).
        
        Example:
        1: if condition:
        2:     pass
        3: else: # pragma: no cover
        4:     do_something()
        
        In this example, the intent is that the 'no cover' pragma should be
        applied to the statements on the 'else' path of the 'if' statement.
        There is no "Else" node type defined by the ast module, however, so
        we need to do some math. We'll figure out that the pragma is pointing
        at the 'else' branch of the 'if' statement and augment our pragma
        mapping to say that the original pragma should be applied to all of
        the statements in the body of the 'if' statement's "orelse" attribute.
        
    """
    
    def __init__(self, pragmas, source):
        self._base_pragmas = pragmas.copy()
        self._source = source
        self._statement_end_linenos = []
    
    def apply(self):
        self._pragmas = self._base_pragmas.copy()
        
        node = ast.parse(self._source)
        
        # fix the else cases
        self.visit(node)
        
        return self._pragmas
    
    def _pragmas_for_range(self, start, end):
        line_range = xrange(start, end)
        pragma_lines = [lineno for lineno in self._pragmas
                        if self._pragmas[lineno]]
        pragmas = set()
        for lineno in line_range:
            if lineno in pragma_lines:
                pragmas.update(self._pragmas[lineno])
        return pragmas
    
    def _add_pragmas_to_body(self, pragmas, body):
        for stmt in body:
            self._pragmas[stmt.lineno].update(pragmas)
    
    def _visit_node_with_body_and_else(self, node):
        self.generic_visit(node)
        
        stmt_pragmas = self._pragmas_for_range(node.lineno, 
                                               node.body[0].lineno)
        if stmt_pragmas:
            for stmt in node.body:
                self._pragmas.setdefault(stmt.lineno, set())\
                    .update(stmt_pragmas)
        if node.orelse:
            else_pragmas = self._pragmas_for_range(node.body[-1].lineno+1, 
                                                   node.orelse[0].lineno)
            else_pragmas.update(stmt_pragmas)
            for stmt in node.orelse:
                self._pragmas.setdefault(stmt.lineno, set())\
                    .update(else_pragmas)
    visit_For = visit_If = _visit_node_with_body_and_else
    visit_While = _visit_node_with_body_and_else
    
    def _visit_node_with_body(self, node):
        self.generic_visit(node)
        
        stmt_pragmas = self._pragmas_for_range(node.lineno, 
                                               node.body[0].lineno)
        if stmt_pragmas:
            self._add_pragmas_to_body(stmt_pragmas, node.body)
    visit_FunctionDef = visit_ClassDef = visit_With = _visit_node_with_body
    visit_ExceptHandler = visit_TryFinally = _visit_node_with_body
    
    def visit_TryExcept(self, node):
        self.generic_visit(node)
        
        stmt_pragmas = self._pragmas_for_range(node.lineno, 
                                               node.body[0].lineno)
        if stmt_pragmas:
            for stmt in node.body:
                self._pragmas.setdefault(stmt.lineno, set())\
                    .update(stmt_pragmas)
        if node.orelse:
            else_pragmas = self._pragmas_for_range(node.handlers[-1].body[-1].lineno+1, 
                                                   node.orelse[0].lineno)
            else_pragmas.update(stmt_pragmas)
            for stmt in node.orelse:
                self._pragmas.setdefault(stmt.lineno, set())\
                    .update(else_pragmas)
        
class PragmaFinder(object):
    
    def __init__(self):
        pass
    
    def find_pragmas(self, source):
        pragmas = {}
        for lineno, line in enumerate(source.splitlines()):
            lineno += 1
            pragmas[lineno] = set()
            pragma_match = re.search(r'#\s*pragma:(.+)$', line)
            if pragma_match:
                pragma_text = pragma_match.group(1)
                for pragma_label, pragma in valid_pragmas.items():
                    if re.search(pragma_label, pragma_text):
                        pragmas[lineno].add(pragma)
        
        applier = PragmaApplier(pragmas, source)
        pragmas = applier.apply()
        
        return pragmas
