# The file containing the main exceptions used within the server.

class ReAPIPoolException(Exception):
    """Raised when ReAPI is unable to create a MySQL connection pool for any reason."""
    pass

class ReAPIPoolNotCreated(Exception):
    """Raised when ReAPI is attempting to use the MySQL pool while it is not set."""
    pass

class ReAPIBadWebHandler(Exception):
    """Raised when the handler is unsuitable for use."""
    pass

class ReAPIIncorrectResponseType(Exception):
    """Raised when the response type is not suitable."""
    pass
