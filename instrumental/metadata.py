from copy import deepcopy
import fnmatch
import itertools
import os
import re
import sys

from astkit import ast

from instrumental import constructs
from instrumental.pragmas import PragmaNoCover

class ModuleMetadata(object):
    
    def __init__(self, modulename):
        self.modulename = modulename
        self.lines = []
        self.constructs = {}
    
    def next_label(self, lineno):
        i = 1
        while ('%s.%s' % (lineno, i)) in self.constructs:
            i += 1
        return '%s.%s' % (lineno, i)

class MetadataGatheringVisitor(ast.NodeVisitor):
    
    @classmethod
    def analyze(cls, modulename, module_ast, pragmas):
        metadata = ModuleMetadata(modulename)
        visitor = cls(metadata, pragmas)
        visitor.visit(module_ast)
        return visitor.metadata
    
    def __init__(self, metadata, pragmas):
        self.metadata = metadata
        self._pragmas = pragmas
        self.modifiers = []
        self.expression_context = []
    
    def _has_pragma(self, pragma, lineno):
        return any(isinstance(p, pragma) for p in self._pragmas[lineno])
    
    def generic_visit(self, node):
        if isinstance(node, ast.stmt):
            if self._has_pragma(PragmaNoCover, node.lineno):
                self.modifiers.append(PragmaNoCover)
            if PragmaNoCover not in self.modifiers:
                self.metadata.lines.append(node.lineno)
        super(MetadataGatheringVisitor, self).generic_visit(node)
        if isinstance(node, ast.stmt):
            if self._has_pragma(PragmaNoCover, node.lineno):
                self.modifiers.pop(-1)

    def _make_boolop_construct(self, node):
        if isinstance(node.op, ast.And):
            klass = constructs.LogicalAnd
        elif isinstance(node.op, ast.Or):
            klass = constructs.LogicalOr
        else:
            raise ValueError("We should have an And or Or here")
        pragmas = self._pragmas.get(node.lineno, [])
        return klass(node, pragmas)
    
    def _make_decision(self, node):
        # BoolOps will be collected elsewhere
        if not isinstance(node, ast.BoolOp):
            pragmas = self._pragmas.get(node.lineno, [])
            return constructs.BooleanDecision(node, pragmas)
    
    def visit_BoolOp(self, boolop):
        if PragmaNoCover in self.modifiers:
            return
        else:
            label = self.metadata.next_label(boolop.lineno)
            construct = self._make_boolop_construct(boolop)
            self.metadata.constructs[label] = construct
            self.expression_context.append(label)
            self.generic_visit(boolop)
            self.expression_context.pop(-1)
            
    def visit_If(self, if_):
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines.append(if_.lineno)
            label = self.metadata.next_label(if_.lineno)
            construct = self._make_decision(if_.test)
            self.metadata.constructs[str(label)] = construct
            self.generic_visit(if_)
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.pop(-1)
    
    def visit_IfExp(self, ifexp):
        label = self.metadata.next_label(ifexp.lineno)
        construct = self._make_decision(ifexp.test)
        if construct:
            self.metadata.constructs[str(label)] = construct
        self.generic_visit(ifexp)
        
    def visit_While(self, while_):
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines.append(while_.lineno)
            label = self.metadata.next_label(while_.lineno)
            construct = self._make_decision(while_.test)
            self.metadata.constructs[str(label)] = construct
            self.generic_visit(while_)
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.pop(-1)

class SourceFinder(object):
    
    def __init__(self, path):
        self.path = path
    
        
    def find(self, target, ignores):
        found = False
        for path in self.path:
            if not os.path.isdir(path):
                continue
            for filepath in self._find_target(path, target):
                found = True
                modulename = filepath[len(path)+1:-3].replace(os.path.sep, '.')
                if modulename.endswith('__init__'):
                    modulename = modulename[:-9]
                yield (filepath, modulename)
            if found:
                break
    
    def _is_python_source(self, filename):
        return filename == '__init__.py' or filename.endswith('.py')
    
    def _find_target(self, path, target):
        if '.' in target:
            prefix, suffix = target.split('.', 1)
        else:
            prefix, suffix = target, '*'
        filenames = fnmatch.filter(sorted(os.listdir(path)), prefix)
        filenames += fnmatch.filter(sorted(os.listdir(path)), prefix + '.py')
        for filename in filenames:
            filepath = os.path.join(path, filename)
            if self._is_python_source(filename):
                yield filepath
            elif os.path.isdir(filepath):
                for filepath in self._find_target(filepath, suffix):
                    yield filepath

if __name__ == '__main__':

    target = sys.argv[1]
    ignores = [sys.argv[2]] if len(sys.argv) > 2 else []
    finder = SourceFinder(sys.path)
    for source_spec in finder.find(target, ignores):
        filepath, modulename = source_spec
        print filepath, modulename
