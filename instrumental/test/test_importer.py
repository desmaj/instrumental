import sys

from instrumental import importer
from instrumental import importer

class FakeRecorder(object):
    pragmas = {}
    
    def add_source(self, name, source):
        pass

class FakeSys(object):
    modules = {}

class FakeVisitor(object):
    
    def visit(self, node):
        return node

class FakeVisitorFactory(object):
    recorder = FakeRecorder()
    
    def create(self, name):
        visitor = FakeVisitor()
        return visitor

class TestModuleLoader(object):
    
    def setup(self):
        self.path = __file__
        if self.path.endswith('.pyc'):
            self.path = self.path[:-1]
        self.name = __name__
        self._fake_sys = FakeSys()
        self._old_sys = importer.sys
        importer.sys = self._fake_sys
    
    def teardown(self):
        importer.sys = self._old_sys
    
    def _makeOne(self):
        visitor_factory = FakeVisitorFactory()
        return importer.ModuleLoader(self.path, visitor_factory)
    
    def test_load_module(self):
        loader = self._makeOne()
        module = loader.load_module(self.name)
        assert module
        assert not hasattr(module, 'path')
        assert module.__name__ in self._fake_sys.modules

class TestImportHook(object):
    
    def _makeOne(self):
        self.name = __name__
        visitor_factory = FakeVisitorFactory()
        return importer.ImportHook(self.name, visitor_factory)
    
    # def test_find_module(self):
    #     hook = self._makeOne()
    #     loader = hook.find_module(self.name)
    #     assert loader
