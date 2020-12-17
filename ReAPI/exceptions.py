# The file containing the main exceptions used within the server.

class ReAPIPoolException(Exception):
    """Raised when ReAPI is unable to create a MySQL connection pool for any reason."""
    pass
