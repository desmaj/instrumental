# 
# Copyright (C) 2012  Matthew J Desmarais

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from copy import copy
from copy import deepcopy
import inspect
import sys

from astkit import ast

from instrumental.pragmas import PragmaFinder

def __setup_recorder(): # pragma: no cover
    from instrumental.recorder import ExecutionRecorder
    _xxx_recorder_xxx_ = ExecutionRecorder.get()

def get_setup():
    source = inspect.getsource(__setup_recorder)
    mod = ast.parse(source)
    defn = mod.body[0]
    setup = defn.body[:]
    for stmt in setup:
        stmt.lineno -= 1
    return setup

class ExecutionRecorder(object):
    DEFAULT_TAG = 'X'
    
    @classmethod
    def reset(cls):
        cls._instance = None
    
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.metadata = {}
        self.recording = False
        self.tag = None
        self._tagging = False
    
    def start(self):
        self.recording = True
    
    def stop(self):
        self.recording = False
    
    def add_metadata(self, metadata):
        self.metadata[metadata.modulename] = metadata
    
    @staticmethod
    def get_recorder_call():
        kall = ast.Call()
        kall.func = ast.Attribute(value=ast.Name(id="_xxx_recorder_xxx_",
                                                 ctx=ast.Load()),
                                  attr="record",
                                  ctx=ast.Load())
        kall.keywords = []
        return kall
    
    def record(self, arg, modulename, label, *args, **kwargs):
        if self.recording and label in self.metadata[modulename].constructs:
            kwargs['tag'] = (self.tag 
                             if self.tag is not None 
                             else self.DEFAULT_TAG)
            self.metadata[modulename].constructs[label].record(arg, 
                                                               *args, **kwargs)
        return arg
    
    def add_BoolOp(self, modulename, label, node, pragmas, parent):
        # Now wrap the individual values in recorder calls
        base_call = self.get_recorder_call()
        base_call.args = \
            [ast.Str(s=modulename, lineno=node.lineno, col_offset=node.col_offset),
             ast.Str(s=label, lineno=node.lineno, col_offset=node.col_offset)]
        for i, value in enumerate(node.values):
            recorder_call = deepcopy(base_call)
            recorder_call.args.insert(0, node.values[i])
            recorder_call.args.append(ast.copy_location(ast.Num(n=i), node.values[i]))
            node.values[i] = ast.copy_location(recorder_call, node.values[i])
        ast.fix_missing_locations(node)
        return node
    
    def add_test(self, modulename, label, node):
        base_call = ast.copy_location(self.get_recorder_call(),
                                      node)
        base_call.args = \
            [node,
             ast.Str(s=modulename, lineno=node.lineno, col_offset=node.col_offset),
             ast.Str(s=label, lineno=node.lineno, col_offset=node.col_offset)]
        ast.fix_missing_locations(base_call)
        return base_call
    
    def add_comparison(self, modulename, label, node):
        base_call = ast.copy_location(self.get_recorder_call(),
                                      node)
        base_call.args = \
            [node,
             ast.Str(s=modulename, lineno=node.lineno, col_offset=node.col_offset),
             ast.Str(s=label, lineno=node.lineno, col_offset=node.col_offset)]
        ast.fix_missing_locations(base_call)
        return base_call
    
    @staticmethod
    def get_statement_recorder_call(modulename, lineno):
        kall = ast.Call()
        kall.func = ast.Attribute(value=ast.Name(id="_xxx_recorder_xxx_",
                                                 ctx=ast.Load()),
                                  attr="record_statement",
                                  ctx=ast.Load())
        kall.args = [ast.Str(s=modulename),
                     ast.Num(n=lineno),
                     ]
        kall.keywords = []
        kall_stmt = ast.Expr(value=kall)
        return kall_stmt
    
    def record_statement(self, modulename, lineno):
        if self.recording and lineno in self.metadata[modulename].lines:
            self.metadata[modulename].lines[lineno] = True
    
    def add_statement(self, modulename, node):
        marker = self.get_statement_recorder_call(modulename, node.lineno)
        marker = ast.copy_location(marker, node)
        ast.fix_missing_locations(marker)
        return marker
    
    def merge(self, other):
        for metadata in other.metadata.values():
            if metadata.modulename not in self.metadata:
                self.add_metadata(metadata)
            else:
                self.metadata[metadata.modulename].merge(metadata)
