

class User:
    
    
    def init(self, user, password):
        self.username  = user
        self.password = password
        
        
    
    def __str__(self):
        return '%s' % self.username