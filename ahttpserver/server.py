# Minimal HTTP server using asyncio
#
# Usage:
#
#   import uasyncio as asyncio
#
#   from ahttpserver import HTTPServer, sendfile
#
#   app = HTTPServer()
#
#   @app.route("GET", "/")
#   async def root(reader, writer, request):
#       response = HTTPResponse(200, "text/html", close=True)
#       await response.send(writer)
#       await sendfile(writer, "index.html")
#
#   loop = asyncio.get_event_loop()
#   loop.create_task(app.start())
#   loop.run_forever()
#
# Handlers for the (method, path) combinations must be decorated with @route,
# and declared before the server is started. Every handler receives a stream-
# reader and writer and a object with details from the request (see url.py
# for exact content). The handler must construct and send a correct HTTP
# response. To avoid typos use response components from response.py.
# When leaving the handler the connection is closed.
# Any (method, path) combination which has not been declared using @route
# will, when received by the server, result in a 404 HTTP error.
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

import errno

import uasyncio as asyncio

from .response import HTTPResponse
from .url import HTTPRequest, InvalidRequest


class HTTPServerError(Exception):
    pass


class HTTPServer:

    def __init__(self, host="0.0.0.0", port=80, backlog=5, timeout=30):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.timeout = timeout
        self._server = None
        self._routes = dict()  # stores link between (method, path) and function to execute

    def route(self, method="GET", path="/"):
        """ Decorator which connects method and path to the decorated function. """

        if (method, path) in self._routes:
            raise HTTPServerError(f"route{(method, path)} already registered")

        def wrapper(function):
            self._routes[(method, path)] = function

        return wrapper

    async def _handle_request(self, reader, writer):
        try:
            request_line = await asyncio.wait_for(reader.readline(), self.timeout)

            if request_line in [b"", b"\r\n"]:
                print(f"empty request line from {writer.get_extra_info('peername')[0]}")
                return

            print(f"request_line {request_line} from {writer.get_extra_info('peername')[0]}")

            try:
                request = HTTPRequest(request_line)
            except InvalidRequest as e:
                while True:
                    # read and discard header fields
                    if await asyncio.wait_for(reader.readline(), self.timeout) in [b"", b"\r\n"]:
                        break
                response = HTTPResponse(400, "text/plain", close=True)
                await response.send(writer)
                writer.write(repr(e).encode("utf-8"))
                return

            while True:
                # read header fields and add name / value to dict 'header'
                line = await asyncio.wait_for(reader.readline(), self.timeout)

                if line in [b"", b"\r\n"]:
                    break
                else:
                    if line.find(b":") != -1:
                        name, value = line.split(b':', 1)
                        request.header[name] = value.strip()

            # search function which is connected to (method, path)
            func = self._routes.get((request.method, request.path))
            if func:
                await func(reader, writer, request)
            else:  # no function found for (method, path) combination
                response = HTTPResponse(404)
                await response.send(writer)

        except asyncio.TimeoutError:
            pass
        except Exception as e:
            if e.args[0] == errno.ECONNRESET:  # connection reset by client
                pass
            else:
                raise e
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def start(self):
        print(f'HTTP server started on {self.host}:{self.port}')
        self._server = await asyncio.start_server(self._handle_request, self.host, self.port, self.backlog)

    async def stop(self):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            print("HTTP server stopped")
        else:
            print("HTTP server was not started")
