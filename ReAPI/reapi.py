from aiohttp import web
from exceptions import (
    ReAPIPoolException
)
import aiomysql
import re
import asyncio
import traceback

class ReAPI:
    """The main class for your ReAPI server. It contains a large variety of
    functions and backend logic to allow for the simple creation of powerful APIs."""

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        """Loads all of the backend logic behind the server.
        
        Args:
            `loop: asyncio.AbstractEventLoop`: The event loop to be utilised by the server.
                If `None` or not set, new one will be created.
        """

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        # Creation of all of the areas to store the handlers.
        self.handlers: list = []
        self.error_handlers: dict = {
            # Include
            404: self._default_not_found,
            500: self._default_exception
        }
        # Used to assist with the clean usage of mysql pooling process.
        self.mysql_pool: aiomysql.Pool = None

        # Basic server configuration.
        self.config: dict = {
            # Whether the default error handler will show the full traceback in the message.
            "show_excpetions": True
        }

    async def create_pool(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306
    ) -> None:
        """Coroutine that is responsible for the creation the MySQL
        connection pool.

        Args:
            `host: str`: The hostname at which the MySQL server is located at.
            `user: str`: The username of the MySQL user you would like to log into.
            `password: str`: The password to use when authenticating into the user
                specified in the `user` arg.
            `database: str`: The name of the database each MySQL connection should
                default to.
        
        Note:
            This function uses aiomysql for MySQL but uses ReAPI specific exceptions
                rather than aiomysql ones.
        """

        # We run this in a try statement to use ReAPI exceptions over aiomysql ones
        # in case we ever switch out aiomysql.
        try:
            # We make the pool available to the entire class.
            self.mysql_pool = await aiomysql.create_pool(
                host= host,
                port= port,
                user= user,
                password= password,
                db= database,
                loop= self.loop
            )
        except Exception:
            # I'm uncertain of whether this is how we do it but eh.
            raise ReAPIPoolException(traceback.format_exc())
    
    async def _default_not_found(self, req: web.Request) -> dict:
        """The default 404 (not found) error page.

        Args:
            `req: aiohttp.web.Request`: The aiohttp request object. Not used here but
                added for the sake of compatibillity with other handlers.
        
        Note:
            This acts just as if a regular handler, just executed when no handler is
                found."""
        
        # Just return a simple dict.
        return {
            "status": 404,
            "message": "This page does not seem to exist!"
        }
    
    async def _default_exception(self, req: web.Resource, exc: str) -> dict:
        """ The default 500 (server error) error page.
        
        Args:
            `req: aiohttp.web.Request`: The aiohttp request object. Not used here but
                added for the sake of compatibillity with other handlers.
            `exc: str`: A string containing the full traceback of the exception.
        
        Note:
            Compared to all the other handlers, this is the only one with its own
                special argument, named `exc`. This is to allow for the easier
                debugging of common errors and for general usefullness, with
                this being an error page.
        """

        # Message variable is more complex than usual so do this.
        message = "A server-side exception has occured!"

        # If we have show full traceback on, append it onto the mesage.
        if self.config["show_excpetions"]:
            message += f"\n{traceback.format_exc()}"

        # Just return a simple dict.
        return {
            "status": 500,
            "message": message
        }
