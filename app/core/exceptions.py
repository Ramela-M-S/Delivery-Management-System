
class FastapiException(Exception):
    """Raised for app errors"""

class EntityNotFound(FastapiException):
    pass