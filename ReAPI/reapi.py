from aiohttp import web
from .exceptions import (
    ReAPIPoolException,
    ReAPIPoolNotCreated,
    ReAPIBadWebHandler,
    ReAPIIncorrectResponseType
)
from .objects import Handler
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
            # Include default handlers.
            404: Handler(function=self._default_not_found,path=None,use_mysql=False),
            500: Handler(function=self._default_exception,path=None,use_mysql=False)
        }
        # Used to assist with the clean usage of mysql pooling process.
        self.mysql_pool: aiomysql.Pool = None

        # Basic server configuration.
        self._def_config: dict = {
            # Whether the default error handler will show the full traceback in the message.
            "show_excpetions": True,
            # Whether new connections should should be printed to console.
            "log_conns": False,
            # If dict resp has no `status`, auto add it.
            "dict_add_status": True
        }

        # We create a copy so we can restore the default config.
        self.config = self._def_config

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
    
    def create_handler(self, path: str, handler, use_mysql: bool = False) -> None:
        """Creates a handler to be used when handling requests.
        
        Args:
            `path: str`: The path of the URL at which this handler should respond.
            `handler: function`: The async function that should be used for handling
                the response.
            `use_mysql: bool`: If true, the handler is given a MySQL connection from
                the pool, which is passed as another arg.
        """

        # Running checks on the data provided first.
        # Check if the pool is created if we want to use it.
        if use_mysql and self.mysql_pool is None:
            raise ReAPIPoolNotCreated(
                "You attempted to create a MySQL handler without configuring the MySQL pool."
            )

        # Check if handler is a coro.
        if not asyncio.iscoroutinefunction(handler):
            raise ReAPIBadWebHandler(
                "The handler provided is not a coroutine function!"
            )
        
        # Create and add the handler.
        self.handlers.append(
            Handler(
                path= path,
                function= handler,
                use_mysql= use_mysql
            )
        )
    
    def reset_config(self) -> None:
        """Resets the configuration of the web server."""

        # Set it all to default.
        self.config = self._def_config
    
    def _find_handler(self, path: str) -> Handler:
        """Internal function that locates the handler with its url.
        
        Args:
            `path: str`: The URL path to search a matching handler for. 
        
        Returns handler object.
        """

        # Iterate through all handlers and check if it matches.
        for handler in self.handlers:
            if handler.matches(path):
                # If it matches, return in.
                return handler

        # Nothing found. Return.
        return
    
    def _to_aiohttp(self, obj: object) -> web.Response:
        """Converts the Python object into an aiohttp one.
        
        Args:
            `obj: object`: Any Python object to be returned.

        Returns `aiohttp.web.Response`
        """
        # So we dont check type every time
        obj_type = type(obj)
        # Check if it might already be an aiohttp object.
        if obj_type in (web.Response, web.json_response, web.FileResponse):
            return obj
        
        # If it is a dict, add some stuff and make json_response.
        if obj_type is dict:
            # If status is not in there, add it and set 200 as default.
            if self.config["dict_add_status"] and "status" not in list(obj):
                obj["status"] = 200

            # Make json resp
            return web.json_response(obj)
        
        # If it's a list, make a json body around it.
        if obj_type is list:

            return web.json_response({
                "status": 200,
                "list": obj
            })
        
        # If it's a string, just make a quick response with text.
        if obj_type is str:

            return web.Response(text=obj)
        
        # Nope... Give them an error lol.
        raise ReAPIIncorrectResponseType(f"Objects of type {obj_type} are not supported.")

    async def _handle_req(self, req: web.Request) -> web.Response:
        """Internal coroutine responsible for the handling of all requests to the api.
        
        Args:
            `req: aiohttp.web.Request`: The aiohttp request object.
            
        Returns aiohttp web response object."""

        # Search for handler that matches the request.
        handler = self._find_handler(req.path)

        # If not found, quickly set the handler to the 404 one.
        if handler is None:
            handler = self.error_handlers[404]

        # Handler execution.
        try:
            # If its a mysql handler, it gets its own stuff from pool
            if handler.use_mysql:
                async with self.mysql_pool.acquire() as conn:
                    # Pass both req and conn.
                    resp = await handler.handler(req, conn)
            else:
                # Only pass req
                resp = await handler.handler(req)
        # If there is an exception, call the handler for it.
        except Exception:
            handler = self.error_handlers[500]
            # Essentially do the same thing.
            if handler.use_mysql:
                async with self.mysql_pool.acquire() as conn:
                    # Pass both req and conn.
                    resp = await handler.handler(req, conn)
            else:
                # Only pass req
                resp = await handler.handler(req)
        
        # Log conn if we have it enabled.
        if self.config["log_conns"]:
            # Grab the ip.
            user_ip = req.headers.get("X-Real-IP")
            # Make sure its not just empty.
            if user_ip is None:
                user_ip = "UNKNOWN IP"
            print(f"[{user_ip}] -> {req.method} {req.path}")

        # Now we handle the turning of resp data to aiohttp objects.
        # TODO: Consider try statements as there is a possibillity for this to raise `ReAPIIncorrectResponseType`
        return self._to_aiohttp(resp)
    
    async def run(self, host: str = "127.0.0.1", port: int = 80):
        """Starts the server and begins a never ending loop.
        
        Args:
            `host: str`: The hostname under which to run the server.
            `port: int`: The port under which the server is to be
                ran.
        """

        # Create all the Aiohttp stuff with our handlers.
        server = web.Server(self._handle_req)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        # Start the site!
        await site.start()

        # Print that its started!
        if self.config["log_conns"]:
            print(f"ReAPI: Started on {host}:{port}//")

        # Create an unlimited loop to keep the server alive forever.
        while True:
            await asyncio.sleep(100000)
