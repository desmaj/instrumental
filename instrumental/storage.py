import os
import pickle

class ResultStore(object):
    """ Storage for an instrumental run, including metadata and results
        
        
    """
    
    def __init__(self):
        self.filename = os.path.join(os.getcwd(), '.instrumental.cov')
        
    def save(self, recorder):
        with open(self.filename, 'w') as f:
            pickle.dump(recorder, f)
    
    def load(self):
        with open(self.filename, 'r') as f:
            return pickle.load(f)
