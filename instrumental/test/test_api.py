from instrumental.api import Coverage

class FakeResultStoreFactory(object):
    
    def __init__(self, expected_config, expected_basedir):
        self._expected_config = expected_config
        self._expected_basedir = expected_basedir
        self.calls = []
    
    def __call__(self, config, basedir):
        assert config == self._expected_config
        assert basedir == self._expected_basedir
        return self
    
    def save(self, recorder):
        self.calls.append(("save", recorder))
    
    def load(self, recorder):
        self.calls.append(("load", recorder))

class TestAPI(object):
    
    def _makeOne(self, config, basedir, store_factory=None):
        return Coverage(config, basedir, store_factory)
    
    def test_new_Coverage(self):
        config = object()
        basedir = "object()"
        Coverage(config, basedir)
    
    def test_save(self):
        config = object()
        basedir = 'xxx__basedir__xxx'
        
        store_factory = FakeResultStoreFactory(config, basedir)
        api = self._makeOne(config, basedir, store_factory)
        
        api.save()
        
        assert len(store_factory.calls) == 1
        assert store_factory.calls[0] == ('save', api.recorder), store_factory.calls[0]
