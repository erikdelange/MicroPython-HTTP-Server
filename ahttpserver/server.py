# Minimal HTTP server using asyncio
#
# Usage:
#
#   import uasyncio as asyncio
#
#   from httpserver import sendfile, Server
#
#   app = Server()
#
#   @app.route("GET", "/")
#   async def root(reader, writer, request):
#       writer.write(b"HTTP/1.1 200 OK\r\n")
#       writer.write(b"Connection: close\r\n")
#       writer.write(b"Content-Type: text/html\r\n")
#       writer.write(b"\r\n")
#       await writer.drain()
#       await sendfile(writer, "index.html")
#
#   loop = asyncio.get_event_loop()
#   loop.create_task(app.start())
#   loop.run_forever()
#
# Handlers for the (method, path) combinations must be decorated with @route,
# and declared before the server is started. Every handler receives a stream-
# reader and writer and a dict with all the details from the request (see
# url.py for exact content). The handler must construct and send a correct
# HTTP response. To avoid typos use response components from response.py.
# When leaving the handler the connection is closed.
# Any (method, path) combination which has not been declared using @route
# will, when received by the server, result in a 404 http error.
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

import errno

import uasyncio as asyncio

import ahttpserver.url as url


class HTTPServerError(Exception):
    pass


class Server:

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

            header = dict()

            while True:
                # read header fields and add name / value to dict 'header'
                line = await asyncio.wait_for(reader.readline(), self.timeout)

                if line in [b"", b"\r\n"]:
                    break
                else:
                    semicolon = line.find(b":")
                    if semicolon != -1:
                        name = line[0:semicolon]
                        value = line[semicolon + 1:-2].lstrip()
                        header[name] = value

            try:
                request = url.request(request_line)
            except url.InvalidRequest as e:
                writer.write(b"HTTP/1.1 400 Bad Request\r\n")
                writer.write(b"Connection: close\r\n")
                writer.write(b"Content-Type: text/html\r\n")
                writer.write(b"\r\n")
                await writer.drain()
                writer.write(repr(e).encode("utf-8"))
                return

            request["header"] = header

            # search function which is connected to (method, path)
            func = self._routes.get((request["method"], request["path"]))
            if func:
                await func(reader, writer, request)
            else:  # no function found for (method, path) combination
                writer.write(b"HTTP/1.1 404 Not Found\r\n")
                writer.write(b"Connection: close\r\n")
                writer.write(b"\r\n")

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
