from instrumental.plugins.nose.tag_test_cases import InstrumentalTagPlugin

class FakeTest(object):
    
    def __init__(self, id, address=None):
        self._id = id
        if address is not None:
            self.address = lambda: address
    
    def id(self):
        return self._id
    
class TestPluginInstrumentalTag(object):
    
    def _makeOne(self):
        return InstrumentalTagPlugin()
    
    def test_startTest_without_address(self):
        test = FakeTest('some_fake_test')
        
        plugin = self._makeOne()
        plugin.startTest(test)
            
        from instrumental.api import Coverage
        cov = Coverage(None, '.')
        assert cov.recorder.tag == 'some_fake_test'
    
    def test_startTest_with_address(self):
        test = FakeTest('some_fake_test',
                        ['filename.py', 'SomeTestClass', 'some_fake_test'])
        
        plugin = self._makeOne()
        plugin.startTest(test)
            
        from instrumental.api import Coverage
        cov = Coverage(None, '.')
        assert cov.recorder.tag == 'SomeTestClass:some_fake_test', cov.recorder.tag
