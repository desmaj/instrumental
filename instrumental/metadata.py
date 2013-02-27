from copy import deepcopy
import fnmatch
import itertools
import os
import pickle
import re
import sys
import time

from astkit import ast

from instrumental import constructs
from instrumental import util
from instrumental.pragmas import PragmaFinder
from instrumental.pragmas import PragmaNoCover

def has_docstring(defn):
    return ast.get_docstring(defn) is not None

def gather_metadata(recorder, targets, ignores):
    finder = SourceFinder(sys.path)
    metadata_cache = FileBackedMetadataCache()
    for target in targets:
        for source_spec in finder.find(target, ignores):
            filepath, modulename = source_spec
            metadata = metadata_cache.fetch(filepath)
            if not metadata:
                source = open(filepath, "r").read()
                pragmas = PragmaFinder().find_pragmas(source)
                metadata = MetadataGatheringVisitor.analyze(modulename,
                                                            filepath,
                                                            source,
                                                            pragmas)
                metadata_cache.store(filepath, metadata)
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
        self.expression_context = [None]
    
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
        pragmas = self.metadata.pragmas.get(node.lineno, [])
        construct = klass(self.metadata.modulename, label, node, pragmas)
        return construct
    
    def _make_decision(self, label, node):
        # BoolOps and Compares will be collected elsewhere
        if not (isinstance(node, ast.BoolOp) or isinstance(node, ast.Compare)):
            pragmas = self.metadata.pragmas.get(node.lineno, [])
            return constructs.BooleanDecision(self.metadata.modulename, label, node, pragmas)
    
    def visit_Module(self, module):
        docstring = None
        if has_docstring(module):
            docstring = module.body.pop(0)
        self.generic_visit(module)
    
    def visit_BoolOp(self, boolop):
        label = self.metadata.next_label(boolop.lineno)
        construct = self._make_boolop_construct(label, boolop)
        self.metadata.constructs[label] = construct
        self.expression_context.append(construct)
        self.generic_visit(boolop)
        self.expression_context.pop(-1)
    
    def visit_Compare(self, compare):
        construct = None
        if not isinstance(self.expression_context[-1], 
                          constructs.LogicalBoolean):
            label = self.metadata.next_label(compare.lineno)
            pragmas = self.metadata.pragmas.get(compare.lineno, [])
            construct = constructs.BooleanDecision(self.metadata.modulename, label, compare, pragmas)
            self.metadata.constructs[label] = construct
        self.expression_context.append(construct)
        self.generic_visit(compare)
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
                self.expression_context.append(construct)
            self.generic_visit(if_)
            if construct:
                self.expression_context.pop(-1)
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.pop(-1)
    
    def visit_IfExp(self, ifexp):
        label = self.metadata.next_label(ifexp.lineno)
        construct = self._make_decision(label, ifexp.test)
        if construct:
            self.metadata.constructs[str(label)] = construct
            self.expression_context.append(construct)
        self.generic_visit(ifexp)
        if construct:
            self.expression_context.pop(-1)
    
    def visit_While(self, while_):
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines[while_.lineno] = False
            label = self.metadata.next_label(while_.lineno)
            construct = self._make_decision(label, while_.test)
            if construct:
                self.expression_context.append(construct)
                self.metadata.constructs[str(label)] = construct
            self.generic_visit(while_)
            if construct:
                self.expression_context.pop(-1)
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


class BaseMetadataCache(object):
    
    def initialize(self):
        self._init_storage()
    
    def store(self, filepath, meta):
        now = util.now()
        record = {'timestamp': now,
                  'metadata': meta}
        self._store(filepath, record)
    
    def fetch(self, filepath):
        file_mtime = os.stat(filepath).st_mtime
        cached_record = self._fetch(filepath)
        if not cached_record:
            return
        timestamp = time.mktime(cached_record['timestamp'].timetuple())
        if file_mtime < timestamp:
            return cached_record['metadata']
    
class FileBackedMetadataCache(BaseMetadataCache):
    
    def __init__(self):
        super(FileBackedMetadataCache, self).__init__()
        self._working_directory = os.path.join(os.getcwd(), '.instrumental.cache')
        
    def _init_storage(self):
        if not os.path.exists(self._working_directory):
            os.mkdir(self._working_directory)
    
    def _store(self, filepath, record):
        if filepath.startswith('/'):
            filepath = filepath[1:]
        cache_file_path = os.path.join(self._working_directory, filepath)
        if not os.path.exists(os.path.dirname(cache_file_path)):
            os.makedirs(os.path.dirname(cache_file_path))
        with open(cache_file_path, 'wb') as cache_file:
            pickle.dump(record, cache_file)
    
    def _fetch(self, filepath):
        if filepath.startswith('/'):
            filepath = filepath[1:]
        cache_file_path = os.path.join(self._working_directory, filepath)
        if not os.path.exists(cache_file_path):
            return None
        with open(cache_file_path, 'rb') as cache_file:
            record = pickle.load(cache_file)
        return record


if __name__ == '__main__': # pragma: no cover

    target = sys.argv[1]
    ignores = [sys.argv[2]] if len(sys.argv) > 2 else []
    finder = SourceFinder(sys.path)
    for source_spec in finder.find(target, ignores):
        filepath, modulename = source_spec
        print filepath, modulename
