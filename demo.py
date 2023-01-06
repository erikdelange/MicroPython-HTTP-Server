from httpserver import HTTPResponse, HTTPServer, sendfile

app = HTTPServer(timeout=10)


@app.route("GET", "/")
def root(conn, request):
    response = HTTPResponse(200, "text/html")
    response.send(conn)
    sendfile(conn, "index.html")


@app.route("GET", "/favicon.ico")
def favicon(conn, request):
    response = HTTPResponse(200, "image/x-icon")
    response.send(conn)
    sendfile(conn, "favicon.ico")


@app.route("GET", "/api/stop")
def stop(conn, request):
    response = HTTPResponse(200)
    response.send(conn)
    raise KeyboardInterrupt


if __name__ == "__main__":
    app.start()
