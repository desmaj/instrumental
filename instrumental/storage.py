import os
import pickle

class ResultStore(object):
    """ Storage for an instrumental run, including metadata and results
        
        
    """
    
    def __init__(self, base, label, filename):
        if label:
            filename = ''.join(['.instrumental.', str(label), '.cov'])
        elif not filename:
            filename = '.instrumental.cov'
        self._filename = os.path.join(base, filename)
    
    @property
    def filename(self):
        return self._filename
    
    def save(self, recorder):
        with open(self.filename, 'w') as f:
            pickle.dump(recorder, f)
    
    def load(self):
        with open(self.filename, 'r') as f:
            return pickle.load(f)
