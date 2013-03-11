
class TestBooleanEvaluator(object):
    
    def _test_node(self, node, expected):
        from instrumental.metadata import BooleanEvaluator
        result = BooleanEvaluator.evaluate(node)
        assert expected == result, (expected, result)
    
    def test_BoolOp_2_pin_and_without_literals(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='b'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_and_without_literals(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='b'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_and_with_1_literal_True(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='True'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_and_with_1_literal_False(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.And(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='False'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([False])
        yield self._test_node, node, expected
    
    def test_BoolOp_2_pin_or_without_literals(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='b'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_or_without_literals(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='b'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_or_with_1_literal_True(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='True'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([True])
        yield self._test_node, node, expected
    
    def test_BoolOp_3_pin_or_with_1_literal_False(self):
        from astkit import ast
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id='a'),
                                  ast.Name(id='False'),
                                  ast.Name(id='c'),
                                  ],
                          )
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_IfExp_without_literals(self):
        from astkit import ast
        test = ast.Name(id='a')
        body = ast.Name(id='b')
        orelse = ast.Name(id='c')
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([True, False])
        yield self._test_node, node, expected

    def test_IfExp_with_literal_non_literal_test(self):
        from astkit import ast
        test = ast.Name(id='a')
        body = ast.Num(n=4)
        orelse = ast.Name(id='c')
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([True, False])
        yield self._test_node, node, expected

    def test_IfExp_with_literal_body_truthy(self):
        from astkit import ast
        test = ast.Name(id='True')
        body = ast.Num(n=4)
        orelse = ast.Name(id='c')
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([True])
        yield self._test_node, node, expected

    def test_IfExp_with_literal_body_falsy(self):
        from astkit import ast
        test = ast.Name(id='True')
        body = ast.Num(n=0)
        orelse = ast.Name(id='c')
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([False])
        yield self._test_node, node, expected

    def test_IfExp_with_literal_orelse_truthy(self):
        from astkit import ast
        test = ast.Name(id='False')
        body = ast.Name(id='b')
        orelse = ast.Num(n=4)
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([True])
        yield self._test_node, node, expected

    def test_IfExp_with_literal_orelse_falsy(self):
        from astkit import ast
        test = ast.Name(id='False')
        body = ast.Name(id='b')
        orelse = ast.Num(n=0)
        node = ast.IfExp(test=test, body=body, orelse=orelse)
        expected = set([False])
        yield self._test_node, node, expected

    def test_UnaryOp_Not_variable(self):
        from astkit import ast
        node = ast.UnaryOp(op=ast.Not(), operand=ast.Name(id='a'))
        expected = set([True, False])
        yield self._test_node, node, expected
        
    def test_UnaryOp_Not_literal_True(self):
        from astkit import ast
        node = ast.UnaryOp(op=ast.Not(), operand=ast.Name(id='True'))
        expected = set([False])
        yield self._test_node, node, expected
        
    def test_UnaryOp_Not_literal_False(self):
        from astkit import ast
        node = ast.UnaryOp(op=ast.Not(), operand=ast.Name(id='False'))
        expected = set([True])
        yield self._test_node, node, expected
        
    def test_UnaryOp_UAdd(self):
        from astkit import ast
        node = ast.UnaryOp(op=ast.UAdd(), operand=ast.Num(n=4))
        expected = set([True, False])
        yield self._test_node, node, expected
    
    def test_List_truthy(self):
        from astkit import ast
        node = ast.List(elts=[ast.Name(id='False'),
                              ])
        expected = set([True])
        yield self._test_node, node, expected
        
    def test_List_falsy(self):
        from astkit import ast
        node = ast.List(elts=[])
        expected = set([False])
        yield self._test_node, node, expected
        
    def test_True(self):
        from astkit import ast
        node = ast.Lambda(args=ast.arguments(), body=ast.Name(id='a'))
        expected = set([True])
        yield self._test_node, node, expected
