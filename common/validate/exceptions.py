
class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__()
        self.message = message

    def __str__(self):
        return str(self.message)

    def __repr__(self):
        return repr(self.message)
        
