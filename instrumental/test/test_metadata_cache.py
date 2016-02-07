import contextlib
import datetime
import os
import shutil
import time

from instrumental import util
from instrumental.metadata import FileBackedMetadataCache
from instrumental.metadata import ModuleMetadata

@contextlib.contextmanager
def monkeypatch_now(when):
    old_now = util.now
    util.now = lambda: when
    yield
    util.now = old_now

class TestFileBackedMetadataCache(object):
    CACHE_PATH = '.instrumental.cache'
    
    def setup(self):
        self._dirty_paths = []# self.CACHE_PATH]
    
    def teardown(self):
        for path in self._dirty_paths:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    def _make_one(self):
        return FileBackedMetadataCache()
    
    def _make_metadata(self, filepath):
        return ModuleMetadata(filepath,
                              source = "",
                              pragmas = {})

    def _touch_file(self, filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        open(filepath, 'w').close()
    
    def test_new_cache(self):
        cache = self._make_one()
    
    def test_initialize(self):
        cache = self._make_one()
        cache.initialize()
        
        assert os.path.exists(self.CACHE_PATH)
    
    def test_item_presence_when_present_and_valid(self):
        cache = self._make_one()
        cache.initialize()
        
        filepath = os.path.join(os.getcwd(), 'path/to/module.py')
        self._touch_file(filepath)
        self._dirty_paths.append(filepath)
        
        meta = self._make_metadata(filepath)
        timestamp = datetime.datetime.now() + datetime.timedelta(seconds=1)
        with monkeypatch_now(timestamp):
            cache.store(filepath, meta)
        cached_metadata = cache.fetch(filepath)
        assert cached_metadata
    
    def test_item_absence_when_present_and_stale(self):
        cache = self._make_one()
        cache.initialize()
        
        filepath = os.path.join(os.getcwd(), 'path/to/module.py')
        self._touch_file(filepath)
        self._dirty_paths.append(filepath)
        
        meta = self._make_metadata(filepath)
        timestamp = datetime.datetime.now() + datetime.timedelta(seconds=-2)
        with monkeypatch_now(timestamp):
            cache.store(filepath, meta)
        self._touch_file(filepath)
        cached_metadata = cache.fetch(filepath)
        assert not cached_metadata
