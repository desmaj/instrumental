from instrumental import constructs
from instrumental.test import DummyConfig
from instrumental.test import load_module

class TestMetadataGatheringVisitor(object):
    
    def _make_one(self):
        from instrumental.metadata import MetadataGatheringVisitor as MGV
        return MGV
    
    def _get_pragmas(self, source):
        from instrumental.pragmas import PragmaFinder
        finder = PragmaFinder()
        return finder.find_pragmas(source)
    
    def test_gather_lines(self):
        def test_module():
            a = 3
            if a == 4:
                b = 0
            else:
                b = 1
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert set([1, 2, 3, 5]) == set(metadata.lines), set(metadata.lines)
    
    def test_gather_lines__with_pragmas(self):
        def test_module():
            a = 3
            if a == 4: 
                b = 0 # pragma: no cover
            else:
                b = 1
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert set([1, 2, 5]) == set(metadata.lines), set(metadata.lines)
        
    def test_gather_constructs__if_simple_decision(self):
        def test_module():
            a = 3
            if a == 4: 
                b = 0
            else:
                b = 1
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert "2.1" in metadata.constructs, metadata.constructs
        decision = metadata.constructs["2.1"]
        assert isinstance(decision, constructs.BooleanDecision)
            
    def test_gather_constructs__ifexp_simple_decision(self):
        def test_module():
            a = 3
            b = 0 if a == 4 else 1
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert "2.1" in metadata.constructs, metadata.constructs
        decision = metadata.constructs["2.1"]
        assert isinstance(decision, constructs.BooleanDecision)
            
    def test_gather_constructs__multiple_ifexps(self):
        def test_module():
            a = 3
            b, c = 0 if a == 4 else 1, 2 if a == 2 or a == 3 else 3
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert 6 == len(metadata.constructs), metadata.constructs
        assert "2.2" in metadata.constructs, metadata.constructs
        decision = metadata.constructs["2.2"]
        assert isinstance(decision, constructs.BooleanDecision)
        assert "2.4" in metadata.constructs, metadata.constructs
        decision = metadata.constructs["2.4"]
        assert isinstance(decision, constructs.LogicalOr)
            
    def test_gather_constructs__while_simple_decision(self):
        def test_module():
            a = 3
            b = 0
            while a > 1:
                a -= 1
                b = 0
        module, source = load_module(test_module)
        pragmas = self._get_pragmas(source)
        
        metadata = self._make_one().analyze(DummyConfig(), 'modname', 'modname.py', module, pragmas)
        assert "3.1" in metadata.constructs, metadata.constructs
        decision = metadata.constructs["3.1"]
        assert isinstance(decision, constructs.BooleanDecision)

