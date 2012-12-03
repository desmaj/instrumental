from copy import deepcopy
import fnmatch
import itertools
import os
import re
import sys

from astkit import ast

from instrumental import constructs
from instrumental.pragmas import PragmaFinder
from instrumental.pragmas import PragmaNoCover

def has_docstring(defn):
    return ast.get_docstring(defn) is not None

def gather_metadata(recorder, targets, ignores):
    finder = SourceFinder(sys.path)
    for target in targets:
        for source_spec in finder.find(target, ignores):
            filepath, modulename = source_spec
            source = open(filepath, "r").read()
            pragmas = PragmaFinder().find_pragmas(source)
            metadata = MetadataGatheringVisitor.analyze(modulename,
                                                        filepath,
                                                        source,
                                                        pragmas)
            recorder.add_metadata(metadata)

class ModuleMetadata(object):
    
    def __init__(self, modulename, filepath, source, pragmas):
        self.modulename = modulename
        self.filepath = filepath
        self.source = source
        self.lines = {}
        self.constructs = {}
        self.pragmas = pragmas
    
    def is_package(self):
        return self.filepath.endswith('__init__.py')
    
    def next_label(self, lineno):
        i = 1
        while ('%s.%s' % (lineno, i)) in self.constructs:
            i += 1
        return '%s.%s' % (lineno, i)

class MetadataGatheringVisitor(ast.NodeVisitor):
    
    @classmethod
    def analyze(cls, modulename, filepath, source, pragmas):
        module_ast = ast.parse(source)
        metadata = ModuleMetadata(modulename, filepath, source, pragmas)
        visitor = cls(metadata, pragmas)
        visitor.visit(module_ast)
        return visitor.metadata
    
    def __init__(self, metadata, pragmas):
        self.metadata = metadata
        self.modifiers = []
        self.expression_context = []
    
    def _has_pragma(self, pragma, lineno):
        return any(isinstance(p, pragma) for p in self.metadata.pragmas[lineno])
    
    def generic_visit(self, node):
        if isinstance(node, ast.stmt):
            if self._has_pragma(PragmaNoCover, node.lineno):
                self.modifiers.append(PragmaNoCover)
            if PragmaNoCover not in self.modifiers:
                self.metadata.lines[node.lineno] = False
            if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
                docstring = None
                if has_docstring(node):
                    docstring = node.body.pop(0)
        super(MetadataGatheringVisitor, self).generic_visit(node)
        if isinstance(node, ast.stmt):
            if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
                if docstring:
                    node.body.insert(0, docstring)
            if self._has_pragma(PragmaNoCover, node.lineno):
                self.modifiers.pop(-1)

    def _make_boolop_construct(self, label, node):
        if isinstance(node.op, ast.And):
            klass = constructs.LogicalAnd
        elif isinstance(node.op, ast.Or):
            klass = constructs.LogicalOr
        else:
            raise ValueError("We should have an And or Or here")
        pragmas = self.metadata.pragmas.get(node.lineno, [])
        construct = klass(self.metadata.modulename, label, node, pragmas)
        for i, value in enumerate(node.values):
            # Try to determine if the condition is a literal
            # Maybe we can do something with this information?
            try:
                literal = ast.literal_eval(value)
                construct.literals[i] = literal
            except ValueError:
                pass
        return construct
    
    def _make_decision(self, label, node):
        # BoolOps will be collected elsewhere
        if not isinstance(node, ast.BoolOp):
            pragmas = self.metadata.pragmas.get(node.lineno, [])
            return constructs.BooleanDecision(self.metadata.modulename, label, node, pragmas)
    
    def visit_BoolOp(self, boolop):
        if PragmaNoCover in self.modifiers:
            return
        else:
            label = self.metadata.next_label(boolop.lineno)
            construct = self._make_boolop_construct(label, boolop)
            self.metadata.constructs[label] = construct
            self.expression_context.append(label)
            self.generic_visit(boolop)
            self.expression_context.pop(-1)
            
    def visit_If(self, if_):
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines[if_.lineno] = False
            label = self.metadata.next_label(if_.lineno)
            construct = self._make_decision(label, if_.test)
            if construct:
                self.metadata.constructs[str(label)] = construct
            self.generic_visit(if_)
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.pop(-1)
    
    def visit_IfExp(self, ifexp):
        label = self.metadata.next_label(ifexp.lineno)
        construct = self._make_decision(label, ifexp.test)
        if construct:
            self.metadata.constructs[str(label)] = construct
        self.generic_visit(ifexp)
        
    def visit_While(self, while_):
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines[while_.lineno] = False
            label = self.metadata.next_label(while_.lineno)
            construct = self._make_decision(label, while_.test)
            if construct:
                self.metadata.constructs[str(label)] = construct
            self.generic_visit(while_)
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.pop(-1)

class SourceFinder(object):
    """ Searches a given path for source files that meet criteria """
    
    def __init__(self, path):
        """ path is a list of paths that can contain source files """
        self.path = path
    
        
    def find(self, target, ignores):
        """ Find source files that look like `target` but not `ignores` """
        found = False
        for path in self.path:
            # We can only search directories
            if not os.path.isdir(path):
                continue
            
            for filepath in self._find_target(path, target, ignores):
                found = True
                modulename = filepath[len(path)+1:-3].replace(os.path.sep, '.')
                if modulename.endswith('__init__'):
                    modulename = modulename[:-9]
                if any(modulename.startswith(ignore) for ignore in ignores):
                    continue
                yield (filepath, modulename)
            if found:
                break
    
    def _is_python_source(self, filename):
        return filename == '__init__.py' or filename.endswith('.py')
    
    def _is_package_directory(self, dirname):
        return (os.path.isdir(dirname) and
                os.path.exists(os.path.join(dirname, '__init__.py')))
    
    def _find_target(self, path, target, ignores):
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
            elif self._is_package_directory(filepath):
                for filepath in self._find_target(filepath, suffix, ignores):
                    yield filepath

if __name__ == '__main__':

    target = sys.argv[1]
    ignores = [sys.argv[2]] if len(sys.argv) > 2 else []
    finder = SourceFinder(sys.path)
    for source_spec in finder.find(target, ignores):
        filepath, modulename = source_spec
        print filepath, modulename
