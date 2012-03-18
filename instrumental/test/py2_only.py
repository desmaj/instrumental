from astkit import ast

#test_instrument_nodes.py
def test_Print(self):
    def test_module():
        print bar
    inst_module = self._instrument_module(test_module)
    self._assert_recorder_setup(inst_module)
    
    self._assert_record_statement(inst_module.body[2], 'test_module', 1)
    assert isinstance(inst_module.body[3], ast.Print)
    assert not inst_module.body[3].dest
    assert isinstance(inst_module.body[3].values[0], ast.Name)
    assert inst_module.body[3].values[0].id == 'bar'
    assert inst_module.body[3].nl
