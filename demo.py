from httpserver import sendfile, Server

app = Server(timeout=10)


@app.route("GET", "/")
def root(conn, request):
    conn.write(b"HTTP/1.1 200 OK\r\n")
    conn.write(b"Connection: close\r\n")
    conn.write(b"Content-Type: text/html\r\n")
    conn.write(b"\r\n")
    sendfile(conn, "index.html")


@app.route("GET", "/favicon.ico")
def favicon(conn, request):
    conn.write(b"HTTP/1.1 200 OK\r\n")
    conn.write(b"Connection: close\r\n")
    conn.write(b"Content-Type: image/x-icon\r\n")
    conn.write(b"\r\n")
    sendfile(conn, "favicon.ico")


@app.route("GET", "/api/stop")
def stop(conn, request):
    conn.write(b"HTTP/1.1 200 OK\r\n")
    conn.write(b"Connection: close\r\n")
    conn.write(b"\r\n")
    raise Exception("Stop Server")


if __name__ == "__main__":
    app.start()
