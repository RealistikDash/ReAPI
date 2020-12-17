# Import all of the necessary modules, including ReAPI.
import reapi
import asyncio

# Create the primary server object.
server = reapi.ReAPI()

# Create two simple handlers for the purpose of experimentation.
async def simple_home(req) -> str:
    """Simple hello world."""

    return "Hello, world!"

async def simple_json(req) -> dict:
    """Returns simple json."""

    return {
        "message": "Hello, world!"
    }

# The main function that starts up the server.
async def main():
    server.create_handler("/", simple_home)
    server.create_handler("/json", simple_json)

    server.config["log_conns"] = True

    await server.run()

asyncio.run(main())
