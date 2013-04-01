import os
import pickle

class ResultStore(object):
    """ Storage for an instrumental run, including metadata and results
        
        
    """
    
    def __init__(self, base, label, filename):
        if label:
            filename = ''.join(['.instrumental.', str(label), '.cov'])
        elif not filename:
            filename = '.instrumental.cov'
        self._filename = os.path.join(base, filename)
    
    @property
    def filename(self):
        return self._filename
    
    def save(self, recorder):
        with open(self.filename, 'w') as f:
            pickle.dump(recorder, f)
    
    def load(self):
        with open(self.filename, 'r') as f:
            return pickle.load(f)

class TextSerializer(object):

    def dump(self, obj):
        return self.visit(obj)
    
    def visit(self, obj):
        klass = obj.__class__.__name__
        visitor = getattr(self, 'visit_%s' % klass)
        return visitor(obj)
    
    # metadata
    def visit_ModuleMetadata(self, md):
        out = ['ModuleMetadata', 
               ','.join('%s:%r' % (lineno, int(md.lines[lineno]))
                        for lineno in sorted(md.lines))]
        for label in sorted(md.constructs):
            out.append(self.visit(md.constructs[label]))
        return "\n".join(out) + '\n'
    
    # instrumental-specific constructs
    def visit_LogicalAnd(self, and_):
        out = ['LogicalAnd', and_.modulename, and_.label]
        out.append(self.visit(and_.node))
        out.append(','.join([self.visit(pragma) for pragma in and_.pragmas]))
        out.append(';'.join("%r:%s" % (condition, ','.join(results))
                            for condition, results in and_.conditions.items()))
        return '|'.join(out)
    
    def visit_LogicalOr(self, or_):
        out = ['LogicalOr', or_.modulename, or_.label]
        out.append(self.visit(or_.node))
        out.append(','.join([self.visit(pragma) for pragma in or_.pragmas]))
        out.append(';'.join("%r:%s" % (condition, ','.join(results))
                            for condition, results in or_.conditions.items()))
        return '|'.join(out)
    
    def visit_BooleanDecision(self, decision):
        out = ['BooleanDecision', decision.modulename, decision.label]
        out.append(self.visit(decision.node))
        out.append(','.join([self.visit(pragma) for pragma in decision.pragmas]))
        out.append(';'.join("%r:%s" % (condition, ','.join(results))
                            for condition, results
                            in decision.conditions.items()))
        return '|'.join(out)
    
    def visit_Comparison(self, comparison):
        out = ['Comparison', comparison.modulename, comparison.label]
        out.append(self.visit(comparison.node))
        out.append(','.join([self.visit(pragma) 
                             for pragma in comparison.pragmas]))
        out.append(';'.join("%r:%s" % (condition, ','.join(results))
                            for condition, results
                            in comparison.conditions.items()))
        return '|'.join(out)
    
    # ast nodes
    def visit_And(self, node):
        return 'And'
    
    def visit_BoolOp(self, node):
        out = ['BoolOp', repr(node.lineno), self.visit(node.op)]
        out += [self.visit(value) for value in node.values]
        return "'".join(out)
    
    def visit_Compare(self, node):
        out = ['Compare', repr(node.lineno)]
        nodeargs = [self.visit(node.left)]
        nodeargs.append(','.join(self.visit(op) for op in node.ops))
        nodeargs.append(','.join(self.visit(comparator) 
                                 for comparator in node.comparators))
        out.append(';'.join(nodeargs))
        return "'".join(out)
    
    def visit_Name(self, node):
        return 'Name{%s}' % str(node.id)
    
    def visit_NotEq(self, node):
        return 'NotEq'
    
    def visit_Or(self, node):
        return 'Or'

    def visit_Str(self, node):
        return 'Str{%s}'  % node.s.encode('base64')

class TextLoader(object):
    
    def load(self, string):
        pass
