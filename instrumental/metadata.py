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

def gather_metadata(config, recorder, targets, ignores):
    finder = SourceFinder(sys.path)
    if config.use_metadata_cache:
        metadata_cache = FileBackedMetadataCache()
    else:
        metadata_cache = DummyMetadataCache()
    for target in targets:
        for source_spec in finder.find(target, ignores):
            filepath, modulename = source_spec
            metadata = metadata_cache.fetch(filepath)
            if not metadata:
                source = open(filepath, "r").read()
                pragmas = PragmaFinder().find_pragmas(source)
                metadata = MetadataGatheringVisitor.analyze(config,
                                                            modulename,
                                                            source,
                                                            pragmas)
                metadata_cache.store(filepath, metadata)
            recorder.add_metadata(metadata)

class ModuleMetadata(object):
    
    def __init__(self, modulename, source, pragmas):
        self.modulename = modulename
        self.source = source
        self.lines = {}
        self.constructs = {}
        self.pragmas = pragmas
    
    def next_label(self, lineno):
        i = 1
        while ('%s.%s' % (lineno, i)) in self.constructs:
            i += 1
        return '%s.%s' % (lineno, i)
    
    def merge(self, other):
        if self.modulename != other.modulename:
            raise ValueError('Cannot merge metadata for different modules')
        
        for lineno in self.lines:
            self.lines[lineno] = self.lines[lineno] or other.lines[lineno]
        
        for label, construct in self.constructs.items():
            self.constructs[label].merge(other.constructs[label])

class BooleanEvaluator(ast.NodeVisitor):
    
    @classmethod
    def evaluate(cls, node):
        evaluator = cls()
        evaluator.visit(node)
        return evaluator._results
    
    def __init__(self):
        self._results = set([True, False])
    
    def _and(self, left, right):
        return left and right
    
    def _or(self, left, right):
        return left or right
    
    def _booleval(self, op, left, right):
        if isinstance(op, ast.And):
            return self._and(left, right)
        elif isinstance(op, ast.Or):
            return self._or(left, right)
        else: # pragma: no cover
            raise TypeError('Invalid operation: %s', op)
    
    def visit_BoolOp(self, node):
        for subexpr in node.values:
            subresults = BooleanEvaluator.evaluate(subexpr)
            pairs = itertools.product(self._results, subresults)
            self._results = set(self._booleval(node.op, result, subresult)
                                for result, subresult in pairs)
    
    def visit_IfExp(self, node):
        test_results = BooleanEvaluator.evaluate(node.test)
        body_results = BooleanEvaluator.evaluate(node.body)
        orelse_results = BooleanEvaluator.evaluate(node.orelse)
        
        if len(test_results) == 1:
            test_result = list(test_results)[0]
            if test_result:
                self._results = body_results
            else:
                self._results = orelse_results
        else:
            self._results = body_results | orelse_results
    
    def visit_Name(self, node):
        try:
            self._results = set([bool(ast.literal_eval(node))])
        except ValueError:
            pass
    
    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            results = BooleanEvaluator.evaluate(node.operand)
            self._results = set(not result for result in results)
        else:
            self.visit_indeterminate(node)
    
    def visit_literal(self, node):
        self._results = set([bool(ast.literal_eval(node))])
    visit_Num = visit_literal
    visit_Str = visit_literal
    
    visit_Dict = visit_literal
    visit_List = visit_literal
    visit_Set = visit_literal
    visit_Tuple = visit_literal

    def visit_True(self, node):
        self._results = set([True])
    visit_GeneratorExp = visit_True
    visit_Lambda = visit_True
    
    def visit_indeterminate(self, node):
        pass
    visit_Attribute = visit_indeterminate
    visit_BinOp = visit_indeterminate
    visit_Call = visit_indeterminate
    visit_Compare = visit_indeterminate
    visit_DictComp = visit_indeterminate
    visit_ListComp = visit_indeterminate
    visit_Repr = visit_indeterminate
    visit_SetComp = visit_indeterminate
    visit_Subscript = visit_indeterminate
    visit_Yield = visit_indeterminate
    
class MetadataGatheringVisitor(ast.NodeVisitor):
    
    @classmethod
    def analyze(cls, config, modulename, source, pragmas):
        module_ast = ast.parse(source)
        metadata = ModuleMetadata(modulename, source, pragmas)
        visitor = cls(config, metadata, pragmas)
        visitor.visit(module_ast)
        return visitor.metadata
    
    def __init__(self, config, metadata, pragmas):
        self.config = config
        self.metadata = metadata
        self.modifiers = []
        self.gather = True
        self._context = []
    
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
        pragmas = self.metadata.pragmas.get(node.lineno, [])
        construct = constructs.BooleanDecision(self.metadata.modulename,
                                               label, node, pragmas)
        possible_results = BooleanEvaluator.evaluate(node)
        if True not in possible_results:
            construct.set_unreachable(True)
        if False not in possible_results:
            construct.set_unreachable(False)
        return construct
    
    def _make_comparison(self, label, node):
        pragmas = self.metadata.pragmas.get(node.lineno, [])
        construct = constructs.Comparison(self.metadata.modulename, 
                                          label, node, pragmas)
        return construct
    
    def visit_Module(self, module):
        if has_docstring(module):
            module.body.pop(0)
        self.generic_visit(module)
    
    def visit_Assert(self, assert_):
        if self.config.instrument_assertions:
            if isinstance(assert_.test, ast.BoolOp):
                label = self.metadata.next_label(assert_.lineno)
                construct = self._make_decision(label, assert_.test)
                self.metadata.constructs[label] = construct
                self._context.append(construct)
            self.generic_visit(assert_)
            if isinstance(assert_.test, ast.BoolOp):
                self._context.pop()
    
    def visit_assignment(self, assign):
        if isinstance(assign.value, ast.BoolOp):
            label = self.metadata.next_label(assign.lineno)
            construct = self._make_decision(label, assign.value)
            self.metadata.constructs[label] = construct
            self._context.append(construct)
        self.generic_visit(assign)
        if isinstance(assign.value, ast.BoolOp):
            self._context.pop()
    visit_Assign = visit_AugAssign = visit_assignment
    
    def visit_BoolOp(self, boolop):
        label = self.metadata.next_label(boolop.lineno)
        construct = self._make_boolop_construct(label, boolop)
        self.metadata.constructs[label] = construct
        self._context.append(construct)
        self.generic_visit(boolop)
        self._context.pop()
    
    def visit_Compare(self, compare):
        if self.config.instrument_comparisons:
            label = self.metadata.next_label(compare.lineno)
            construct = self._make_comparison(label, compare)
            self.metadata.constructs[label] = construct
            self._context.append(construct)
        self.generic_visit(compare)
        if self.config.instrument_comparisons:
            self._context.pop()
    
    def visit_If(self, if_):
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines[if_.lineno] = False
            label = self.metadata.next_label(if_.lineno)
            construct = self._make_decision(label, if_.test)
            self.metadata.constructs[str(label)] = construct
            self._context.append(construct)
            self.generic_visit(if_)
            self._context.pop()
        if self._has_pragma(PragmaNoCover, if_.lineno):
            self.modifiers.pop(-1)
    
    def visit_IfExp(self, ifexp):
        if self.gather:
            label = self.metadata.next_label(ifexp.lineno)
            construct = self._make_decision(label, ifexp.test)
            self.metadata.constructs[str(label)] = construct
            self._context.append(construct)
        self.generic_visit(ifexp)
        if self.gather:
            self._context.pop()
    
    def visit_While(self, while_):
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.append(PragmaNoCover)
        if PragmaNoCover not in self.modifiers:
            self.metadata.lines[while_.lineno] = False
            label = self.metadata.next_label(while_.lineno)
            construct = self._make_decision(label, while_.test)
            self.metadata.constructs[str(label)] = construct
            self._context.append(construct)
            self.generic_visit(while_)
            self._context.pop()
        if self._has_pragma(PragmaNoCover, while_.lineno):
            self.modifiers.pop(-1)

class SourceFinder(object):
    """ Searches a given path for source files that meet criteria """
    
    def __init__(self, path):
        """ path is a list of paths that can contain source files """
        self.path = path
        if '.' not in self.path:
            self.path.append('.')
    
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
        return filename.endswith('.py')
    
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

class DummyMetadataCache(BaseMetadataCache):
    
    def _init_storage(self):
        pass
    
    def _store(self, filepath, record):
        pass
    
    def _fetch(self, filepath):
        return None

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
        sys.stdout.write(filepath + ', ' + modulename + '\n')
