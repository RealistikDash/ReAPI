import re

class Handler:
    """A containing all of the handler info and basic function."""

    def __init__(self, path: str, function: object, use_mysql: bool = False):
        """Configures the handler object."""

        # Store the original path.
        self._path: str = path
