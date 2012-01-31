from instrumental.importer import ImportHook

class TestImportHook(object):
    
    def setup(self):
        self.visitor_factory = object()
        self.recorder = object()
    
    def _makeOne(self, target, ignores=[]):
        return ImportHook(target, ignores, self.visitor_factory)
    
    def test_exactly_matching_target(self):
        hook = self._makeOne('pyramid')
        
    
