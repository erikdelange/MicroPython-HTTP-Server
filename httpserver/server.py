# Minimal HTTP server
#
# Usage:
#
#   from httpserver import senffile, Server, CONNECTION_CLOSE
#
#   app = Server()

#   @app.route("GET", "/")
#   def root(conn, request):
#       conn.write(b"HTTP/1.1 200 OK\r\n")
#       conn.write(b"Connection: close\r\n")
#       conn.write(b"Content-Type: text/html\r\n")
#       conn.write(b"\r\n")
#       sendfile(conn, "index.html")
#       return CONNECTION_CLOSE
#
#   app.run()
#
# Handlers for the (method, path) combinations must be decrorated with
# @route, and declared before the server is started (via a call to run).
# Every handler receives the connection socket and a dict with all the
# details from the request (see url.py for exact content).
# When leaving the handler the connection is expected to be closed,
# unless the return code of the handler is CONNECTION_KEEP_ALIVE.
# Any combination of (method, path) which has not been declared using
# @route will, when received by the server, result in a 404 HTTP error.
# The server cannot be stopped unless an alert is raised. If a Handler
# wants to stop the server it should use 'raise Exception("Stop Server")'.
# Only this exception will cause a reasonably graceful exit.
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

import socket
import errno

import httpserver.url as url


CONNECTION_CLOSE = const(0)
CONNECTION_KEEP_ALIVE = const(1)


class HTTPServerError(Exception):
    pass


class Server:

    def __init__(self, host="0.0.0.0", port=80, backlog=5, timeout=30):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.timeout = timeout
        self._routes = dict()  # stores link between (method, path) and function to execute

    def route(self, method="GET", path="/"):
        """ Decorator which connects method and path to the decorated function. """

        if (method, path) in self._routes:
            raise HTTPServerError("route{} already registered".format((method, path)))

        def wrapper(function):
            self._routes[(method, path)] = function

        return wrapper

    def start(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        serversocket.bind((self.host, self.port))
        serversocket.listen(self.backlog)

        print("HTTP server started on {}:{}".format(self.host, self.port))

        while True:
            try:
                conn, addr = serversocket.accept()
                conn.settimeout(self.timeout)

                request_line = conn.readline()
                if request_line is None:
                    raise OSError(errno.ETIMEDOUT)

                if request_line in [b"", b"\r\n"]:
                    print("empty request line from", addr[0])
                    conn.close()
                    continue

                print("request line", request_line, "from", addr[0])

                header = dict()

                while True:
                    # read header fields and add name / value to dict 'header'
                    line = conn.readline()
                    if request_line is None:
                        raise OSError(errno.ETIMEDOUT)

                    if line in [b"", b"\r\n"]:
                        break
                    else:
                        semicolon = line.find(b":")
                        if semicolon != -1:
                            name = line[0:semicolon].decode("utf-8")
                            value = line[semicolon + 1:-2].lstrip().decode("utf-8")
                            header[name] = value

                try:
                    request = url.request(request_line)
                except url.InvalidRequest as e:
                    conn.write(b"HTTP/1.1 400 Bad Request\r\n")
                    conn.write(b"Connection: close\r\n")
                    conn.write("Content-Type: text/html\r\n")
                    conn.write(b"\r\n")
                    conn.write(bytes(repr(e), "utf-8"))
                    conn.close()
                    continue

                request["header"] = header

                # search function which is connected to (method, path)
                func = self._routes.get((request["method"], request["path"]))
                if func:
                    if func(conn, request) != CONNECTION_KEEP_ALIVE:
                        # close connection unless explicitly kept alive
                        conn.close()
                else:  # no function found for (method, path) combination
                    conn.write(b"HTTP/1.1 404 Not Found\r\n")
                    conn.write(b"Connection: close\r\n")
                    conn.write(b"\r\n")
                    conn.close()

            except Exception as e:
                conn.close()
                if e.args[0] == errno.ETIMEDOUT:  # communication timeout
                    pass
                elif e.args[0] == errno.ECONNRESET:  # client reset the connection
                    pass
                elif e.args[0] == "Stop Server":  # magic exception to stop server
                    break
                else:
                    serversocket.close()
                    serversocket = None
                    raise e

        serversocket.close()
        serversocket = None
        print("HTTP server stopped")
