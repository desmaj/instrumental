import logging

from instrumental.recorder import ExecutionRecorder

from nose.plugins import Plugin

class InstrumentalTagPlugin(Plugin):
    name = 'instrumental-tag'
    
    def help(self):
        return 'Tags each test case for use with instrumental'
    
    def configure(self, options, conf):
        super(InstrumentalTagPlugin, self).configure(options, conf)
        if not self.enabled:
            return
    
    def startTest(self, test):
        ExecutionRecorder.get().tag = ':'.join(test.address()[1:])
    
    def stopTest(self, test):
        ExecutionRecorder.get().tag = None
    
