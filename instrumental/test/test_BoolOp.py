# This file is intended for use as a test of the instrumentation and coverage
# generation facilities. The tests should always pass.
import sys

from instrumental.samples.boolean import and_3

class TestBoolOp(object):
    
    def test_TTT(self):
        result = and_3(True, True, True)
        assert result, result
    
    def test_TFT(self):
        result = and_3(True, False, True)
        assert not result, result
    
    def test_FFT(self):
        result = and_3(False, False, True)
        assert not result, result
