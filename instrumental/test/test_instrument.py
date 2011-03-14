from instrumental.instrument import force_location

class FakeNode(object):
    _fields = []

class TestForceLocation(object):
    
    def test_force_single_node(object):
        node = FakeNode()
        node.lineno = 5
        node.col_offset = 28
        
        force_location(node, 3)
        
        assert 3 == node.lineno
        assert 0 == node.col_offset
