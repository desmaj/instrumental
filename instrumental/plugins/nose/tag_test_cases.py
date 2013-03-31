import logging

# REMIND: Can't import instrumental here or it'll throw off coverage results
#         when using the nose coverage plugin since coverage isn't setup yet.

from nose.plugins import Plugin

class InstrumentalTagPlugin(Plugin):
    name = 'instrumental-tag'
    
    def help(self):
        return 'Tags each test case for use with instrumental'
    
    def startTest(self, test):
        from instrumental.api import Coverage
        if hasattr(test, 'address'):
            tag = ':'.join(test.address()[1:])
        else:
            tag = test.id()
        cov = Coverage(None, '.')
        cov.start_context(tag)
    
    def stopTest(self, test):
        from instrumental.api import Coverage
        cov = Coverage(None, '.')
        cov.stop_context()
