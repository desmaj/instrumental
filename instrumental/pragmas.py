import ast
import re

class PragmaNoCover(object):
    pass

valid_pragmas = {
    'no cover': PragmaNoCover,
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
    
    def is_stmt(self, node):
        return any([isinstance(node, ast.FunctionDef),
                    isinstance(node, ast.ClassDef),
                    isinstance(node, ast.Return),
                    isinstance(node, ast.Delete),
                    isinstance(node, ast.Assign),
                    isinstance(node, ast.AugAssign),
                    isinstance(node, ast.Print),
                    isinstance(node, ast.For),
                    isinstance(node, ast.While),
                    isinstance(node, ast.If),
                    isinstance(node, ast.With),
                    isinstance(node, ast.Raise),
                    isinstance(node, ast.TryExcept),
                    isinstance(node, ast.TryFinally),
                    isinstance(node, ast.Assert),
                    isinstance(node, ast.Import),
                    isinstance(node, ast.ImportFrom),
                    isinstance(node, ast.Exec),
                    isinstance(node, ast.Global),
                    isinstance(node, ast.Expr),
                    isinstance(node, ast.Pass),
                    isinstance(node, ast.excepthandler),
                    ])
    def apply(self):
        self._pragmas = self._base_pragmas.copy()
        
        node = ast.parse(self._source)
        
        # fix the else cases
        self.visit(node)
        
        # fix pragmas floating across multiline statements
        statements = []
        for node in ast.walk(node):
            if self.is_stmt(node):
                statements.append(node)
        if statements:
            statements.sort(key=lambda node: node.lineno)
            
            for index, statement in enumerate(statements[:-1]):
                for lineno in self._pragmas:
                    if index < len(statements)-1:
                        next_line = statements[index+1].lineno
                    else:
                        next_line = len(self._source.splitlines())
                    if statement.lineno <= lineno < next_line:
                        self._pragmas[statement.lineno] = self._pragmas[lineno]
                        if lineno != statement.lineno:
                            self._pragmas[lineno] = []
        
        return self._pragmas
    
    def _visit_ElseHavingNode(self, node):
        if node.orelse:
            else_range = range(node.body[-1].lineno+1,
                               node.orelse[0].lineno)
            for lineno in self._pragmas:
                if lineno in else_range:
                    for else_lineno in [elsenode.lineno
                                        for elsenode
                                        in node.orelse]:
                        self._pragmas[else_lineno] = self._pragmas[lineno]
                    self._pragmas[lineno] = []
        self.generic_visit(node)
    
    visit_If = visit_For = visit_TryExcept = visit_While = _visit_ElseHavingNode
    
class PragmaFinder(object):
    
    def __init__(self):
        pass
    
    def find_pragmas(self, source):
        pragmas = {}
        for lineno, line in enumerate(source.splitlines()):
            lineno += 1
            pragmas[lineno] = []
            pragma_match = re.search(r'# pragma:(.+)$', line)
            if pragma_match:
                pragma_text = pragma_match.group(1)
                for pragma_label, pragma in valid_pragmas.items():
                    if pragma_label in pragma_text:
                        pragmas[lineno].append(pragma)
        
        # applier = PragmaApplier(pragmas, source)
        # pragmas = applier.apply()
        
        return pragmas
