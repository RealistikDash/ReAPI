import re

class Handler:
    """A containing all of the handler info and basic function."""

    def __init__(self, path: str, function: object, use_mysql: bool = False):
        """Configures the handler object."""

        # Store the original path.
        self._path: str = path
        self.handler = function # Idk what type a function is.
        self.use_mysql: bool = use_mysql
    
    def matches(self, path: str) -> bool:
        """Checks if the path is equivalent to the one of the handler."""

        # Todo: Implement this with more complexity, eg abillity to do
        # /web/<userid>/stats etc
        return self._path == path
