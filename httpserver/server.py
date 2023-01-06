# Minimal HTTP server
#
# Usage:
#
#   from httpserver import HTTPServer, sendfile, CONNECTION_CLOSE
#
#   app = HTTPServer()

#   @app.route("GET", "/")
#   def root(conn, request):
#       response = HTTPResponse(200, "text/html", close=True)
#       response.send(conn)
#       sendfile(conn, "index.html")
#
#   app.start()
#
# Handlers for the (method, path) combinations must be decorated with @route,
# and declared before the server is started (via a call to start).
# Every handler receives the connection socket and an object with all the
# details from the request (see url.py for exact content). The handler must
# construct and send a correct HTTP response. To avoid typos use the
# HTTPResponse component from response.py.
# When leaving the handler the connection will be closed, unless the return
# code of the handler is CONNECTION_KEEP_ALIVE.
# Any (method, path) combination which has not been declared using @route
# will, when received by the server, result in a 404 HTTP error.
# The server cannot be stopped unless an alert is raised. A KeyboardInterrupt
# will cause a controlled exit.
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

import errno
import socket
from micropython import const

from .response import HTTPResponse
from .url import HTTPRequest, InvalidRequest

CONNECTION_CLOSE = const(0)
CONNECTION_KEEP_ALIVE = const(1)


class HTTPServerError(Exception):
    pass


class HTTPServer:

    def __init__(self, host="0.0.0.0", port=80, backlog=5, timeout=30):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.timeout = timeout
        self._routes = dict()  # stores link between (method, path) and function to execute

    def route(self, method="GET", path="/"):
        """ Decorator which connects method and path to the decorated function. """

        if (method, path) in self._routes:
            raise HTTPServerError(f"route{(method, path)} already registered")

        def wrapper(function):
            self._routes[(method, path)] = function

        return wrapper

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((self.host, self.port))
        server.listen(self.backlog)

        print(f"HTTP server started on {self.host}:{self.port}")

        while True:
            try:
                conn, addr = server.accept()
                conn.settimeout(self.timeout)

                request_line = conn.readline()
                if request_line is None:
                    raise OSError(errno.ETIMEDOUT)

                if request_line in [b"", b"\r\n"]:
                    print(f"empty request line from {addr[0]}")
                    conn.close()
                    continue

                print(f"request line {request_line} from {addr[0]}")

                try:
                    request = HTTPRequest(request_line)
                except InvalidRequest as e:
                    while True:
                        # read and discard header fields
                        line = conn.readline()
                        if line is None:
                            raise OSError(errno.ETIMEDOUT)
                        if line in [b"", b"\r\n"]:
                            break
                    response = HTTPResponse(400, "text/plain", close=True)
                    response.send(conn)
                    conn.write(repr(e).encode("utf-8"))
                    conn.close()
                    continue

                while True:
                    # read header fields and add name / value to dict 'header'
                    line = conn.readline()
                    if line is None:
                        raise OSError(errno.ETIMEDOUT)

                    if line in [b"", b"\r\n"]:
                        break
                    else:
                        if line.find(b":") != 1:
                            name, value = line.split(b':', 1)
                            request.header[name] = value.strip()

                # search function which is connected to (method, path)
                func = self._routes.get((request.method, request.path))
                if func:
                    if func(conn, request) != CONNECTION_KEEP_ALIVE:
                        # close connection unless explicitly kept alive
                        conn.close()
                else:  # no function found for (method, path) combination
                    response = HTTPResponse(404)
                    response.send(conn)
                    conn.close()

            except KeyboardInterrupt:  # will stop the server
                conn.close()
                break
            except Exception as e:
                conn.close()
                if type(e) is OSError and e.errno == errno.ETIMEDOUT:  # communication timeout
                    pass
                elif type(e) is OSError and e.errno == errno.ECONNRESET:  # client reset the connection
                    pass
                else:
                    server.close()
                    raise e

        server.close()
        print("HTTP server stopped")
