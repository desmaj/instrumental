import base64
import json
import os
import pickle
import sys

from astkit import ast

from instrumental.constructs import (
    BooleanDecision,
    Comparison,
    LogicalAnd,
    LogicalOr,
    UnreachableCondition,
    )
from instrumental.metadata import ModuleMetadata
from instrumental.recorder import ExecutionRecorder

class ResultStore(object):
    """ Storage for an instrumental run, including metadata and results
        
        
    """
    
    def __init__(self, base, label=None, filename=None):
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
            JSONSerializer.dump(recorder, f)
            # pickle.dump(recorder, f)
    
    def load(self):
        with open(self.filename, 'r') as f:
            # return pickle.load(f)
            return JSONSerializer.load(f)

# NOTE: If JSON serialization becomes unusable for some reason, we can always
#       continure down the path this silly TextSerializer lays out. But we
#       would have to be desperate.
# class TextSerializer(object):

#     def dump(self, obj):
#         return self.visit(obj)
    
#     def visit(self, obj):
#         klass = obj.__class__.__name__
#         visitor = getattr(self, 'visit_%s' % klass)
#         return visitor(obj)
    
#     # metadata
#     def visit_ModuleMetadata(self, md):
#         out = ['ModuleMetadata', 
#                ','.join('%s:%r' % (lineno, int(md.lines[lineno]))
#                         for lineno in sorted(md.lines))]
#         for label in sorted(md.constructs):
#             out.append(self.visit(md.constructs[label]))
#         return "\n".join(out) + '\n'
    
#     # instrumental-specific constructs
#     def visit_LogicalAnd(self, and_):
#         out = ['LogicalAnd', and_.modulename, and_.label]
#         out.append(self.visit(and_.node))
#         out.append(','.join([self.visit(pragma) for pragma in and_.pragmas]))
#         out.append(';'.join("%r:%s" % (condition, ','.join(results))
#                             for condition, results in and_.conditions.items()))
#         return '|'.join(out)
    
#     def visit_LogicalOr(self, or_):
#         out = ['LogicalOr', or_.modulename, or_.label]
#         out.append(self.visit(or_.node))
#         out.append(','.join([self.visit(pragma) for pragma in or_.pragmas]))
#         out.append(';'.join("%r:%s" % (condition, ','.join(results))
#                             for condition, results in or_.conditions.items()))
#         return '|'.join(out)
    
#     def visit_BooleanDecision(self, decision):
#         out = ['BooleanDecision', decision.modulename, decision.label]
#         out.append(self.visit(decision.node))
#         out.append(','.join([self.visit(pragma) for pragma in decision.pragmas]))
#         out.append(';'.join("%r:%s" % (condition, ','.join(results))
#                             for condition, results
#                             in decision.conditions.items()))
#         return '|'.join(out)
    
#     def visit_Comparison(self, comparison):
#         out = ['Comparison', comparison.modulename, comparison.label]
#         out.append(self.visit(comparison.node))
#         out.append(','.join([self.visit(pragma) 
#                              for pragma in comparison.pragmas]))
#         out.append(';'.join("%r:%s" % (condition, ','.join(results))
#                             for condition, results
#                             in comparison.conditions.items()))
#         return '|'.join(out)
    
#     # ast nodes
#     def visit_And(self, node):
#         return 'And'
    
#     def visit_BoolOp(self, node):
#         out = ['BoolOp', repr(node.lineno), self.visit(node.op)]
#         out += [self.visit(value) for value in node.values]
#         return "'".join(out)
    
#     def visit_Compare(self, node):
#         out = ['Compare', repr(node.lineno)]
#         nodeargs = [self.visit(node.left)]
#         nodeargs.append(','.join(self.visit(op) for op in node.ops))
#         nodeargs.append(','.join(self.visit(comparator) 
#                                  for comparator in node.comparators))
#         out.append(';'.join(nodeargs))
#         return "'".join(out)
    
#     def visit_Name(self, node):
#         return 'Name{%s}' % str(node.id)
    
#     def visit_NotEq(self, node):
#         return 'NotEq'
    
#     def visit_Or(self, node):
#         return 'Or'

#     def visit_Str(self, node):
#         if sys.version_info[0] < 3:
#             string = base64.b64encode(node.s)
#         else:
#             string = base64.b64encode(bytes(node.s, 'utf8'))
#         return 'Str{%s}'  % string

class JSONSerializer(object):
    
    @classmethod
    def dump(self, obj, f):
        f.write(JSONSerializer.dumps(obj))
    
    @classmethod
    def dumps(self, obj):
        encoded = ObjectEncoder().encode(obj)
        return json.dumps(encoded)
    
    @classmethod
    def load(self, f):
        return JSONSerializer.loads(f.read())
    
    @classmethod
    def loads(self, string):
        return ObjectDecoder().decode(json.loads(string))

class ObjectEncoder(object):
    
    @classmethod
    def encode(cls, obj):
        encoder = cls()
        method = getattr(encoder, 'encode_%s' % obj.__class__.__name__)
        return method(obj)
    
    def encode_ExecutionRecorder(self, recorder):
        result = {'__python_class__': 'ExecutionRecorder',
                  'metadata': {}}
        for modulename in recorder.metadata:
            result['metadata'][modulename] = (
                self.encode_ModuleMetadata(recorder.metadata[modulename]))
        return result
    
    def encode_ModuleMetadata(self, md):
        return {'__python_class__': 'ModuleMetadata',
                'modulename': md.modulename,
                'source': md.source,
                'lines': md.lines,
                'constructs': dict((label, self.encode(construct))
                                   for label, construct
                                   in md.constructs.items())}
    
    def encode_conditions(self, conditions):
        encoded = {}
        for condition, results in conditions.items():
            encoded_results = []
            for result in results:
                if result == UnreachableCondition:
                    result = '__unreachable__'
                encoded_results.append(result)
            encoded[int(condition)] = encoded_results
        return encoded
    
    def encode_LogicalOr(self, or_):
        return {'__python_class__': 'LogicalOr',
                'modulename': or_.modulename,
                'label': or_.label,
                'node': self.encode_Node(or_.node),
                'conditions': self.encode_conditions(or_.conditions)}
    
    def encode_LogicalAnd(self, and_):
        return {'__python_class__': 'LogicalAnd',
                'modulename': and_.modulename,
                'label': and_.label,
                'node': self.encode_Node(and_.node),
                'conditions': self.encode_conditions(and_.conditions)}
    
    def encode_BooleanDecision(self, decision):
        return {'__python_class__': 'BooleanDecision',
                'modulename': decision.modulename,
                'label': decision.label,
                'node': self.encode_Node(decision.node),
                'conditions': self.encode_conditions(decision.conditions)}
    
    def encode_Comparison(self, comparison):
        return {'__python_class__': 'Comparison',
                'modulename': comparison.modulename,
                'label': comparison.label,
                'node': self.encode_Node(comparison.node),
                'conditions': self.encode_conditions(comparison.conditions)}
    
    def encode_Node(self, node):
        result = {'__python_class__': node.__class__.__name__}
        for key, value in node.__dict__.items():
            if isinstance(value, list):
                result[key] = [self.encode_Node(elt) for elt in value]
            elif value.__class__.__name__ in dir(ast):
                result[key] = self.encode_Node(value)
            else:
                result[key] = value
        return result

class ObjectDecoder(object):
    
    @classmethod
    def decode(cls, d):
        decoder = cls()
        method = getattr(decoder, 'decode_%s' % d['__python_class__'])
        return method(d)
    
    def decode_ExecutionRecorder(self, d):
        recorder = ExecutionRecorder()
        for modulename in d['metadata']:
            md = self.decode_ModuleMetadata(d['metadata'][modulename])
            recorder.add_metadata(md)
        return recorder
    
    def decode_ModuleMetadata(self, d):
        md = ModuleMetadata(d['modulename'],
                            d['source'],
                            [])
        md.lines = dict((int(lineno), result)
                        for lineno, result in d['lines'].items())
        md.constructs = {}
        for key, value in d['constructs'].items():
            md.constructs[key] = ObjectDecoder.decode(value)
        return md
    
    def decode_conditions(self, conditions):
        decoded = {}
        for condition, results in conditions.items():
            decoded_results = set()
            for result in results:
                if result == '__unreachable__':
                    result = UnreachableCondition
                decoded_results.add(result)
            decoded[int(condition)] = decoded_results
        return decoded
    
    def decode_LogicalOr(self, d):
        or_ = LogicalOr(d['modulename'],
                        d['label'],
                        self.decode_Node(d['node']),
                        [])
        or_.conditions = self.decode_conditions(d['conditions'])
        return or_
    
    def decode_LogicalAnd(self, d):
        and_ = LogicalAnd(d['modulename'],
                        d['label'],
                        self.decode_Node(d['node']),
                        [])
        and_.conditions = self.decode_conditions(d['conditions'])
        return and_
    
    def decode_BooleanDecision(self, d):
        decision = BooleanDecision(d['modulename'],
                                   d['label'],
                                   self.decode_Node(d['node']),
                                   [])
        decision.conditions = self.decode_conditions(d['conditions'])
        return decision
    
    def decode_Comparison(self, d):
        comparison = Comparison(d['modulename'],
                                d['label'],
                                self.decode_Node(d['node']),
                                [])
        comparison.conditions = self.decode_conditions(d['conditions'])
        return comparison
    
    def decode_Node(self, d):
        node = getattr(ast, d['__python_class__'])()
        for key, value in d.items():
            if isinstance(value, list):
                value = [self.decode_Node(elt) for elt in value]
            elif isinstance(value, dict):
                value = self.decode_Node(value)
            setattr(node, key, value)
        return node
