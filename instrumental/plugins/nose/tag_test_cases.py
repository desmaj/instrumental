import logging

# REMIND: Can't import instrumental here or it'll throw off coverage results
#         when using the nose coverage plugin since coverage isn't setup yet.
# from instrumental.recorder import ExecutionRecorder

from nose.plugins import Plugin

class InstrumentalTagPlugin(Plugin):
    name = 'instrumental-tag'
    
    def help(self):
        return 'Tags each test case for use with instrumental'
    
    def startTest(self, test):
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder.get().tag = ':'.join(test.address()[1:])
    
    def stopTest(self, test):
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder.get().tag = None
