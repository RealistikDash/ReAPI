# ReAPI
And easy to use, aiohttp based framework for creating APIs.

## Why ReAPI
ReAPI is a Python module that aims with the assistance of making simple APIs in Python. It's goal is to let you focus on the important
bits of an API, managing all of the HTTP and MySQL aspects for you.
It uses the modern async/await syntax for its handlers and aims to do as much as possible asyncronously.

## Basic Example
Getting started with ReAPI is trivial! Here you can view an easy to understand example of how the basics
of ReAPI work.

```py
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
```

## MySQL
ReAPI also provides a simple manner in which to use MySQL cleanly and efficiently.

In order to take advantage of this, you must first call the `create_pool` coroutine with the details of the MySQL server.
This will then allow you to create MySQL-enabled handlers. In order to create a MySQL handler, call the `create_handler`
with the arg `use_mysql` set to true. This means that from now on, the handler will also be passed another arg with the type
of `aiomysql.Connection`.

## Todo
Here are some of the planned features.
- Regex paths in handlers.
- Improved way of setting status.

## Notes
This project is in early development. Why it's usable in its current state, plenty of features are planning to be implemented.

Additionally, this Readme will be re-written to follow an improved format.
