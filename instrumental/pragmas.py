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
    
    def apply(self):
        self._pragmas = self._base_pragmas.copy()
        
        node = ast.parse(self._source)
        
        # fix the else cases
        self.visit(node)
        
        return self._pragmas
    
    def visit_If(self, if_):
        self.generic_visit(if_)
        if if_.orelse:
            for lineno in self._pragmas:
                if not self._pragmas[lineno]:
                    continue
                if if_.body[-1].lineno < lineno <= if_.orelse[0].lineno:
                    for orelse_stmt in if_.orelse:
                        self._pragmas[orelse_stmt.lineno] = self._pragmas[lineno]
    
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
        
        applier = PragmaApplier(pragmas, source)
        pragmas = applier.apply()
        
        return pragmas
