# Demo program for httpserver
#
# Start this program and use you browser to open the main page ('/').
# The current time will be displayed and updated every second.
# Use an API client like Insomnia or curl to call '/api/date' or
# 'api/stop'.

import _thread
import json
import time

from httpserver import (CONNECTION_KEEP_ALIVE, HTTPResponse, HTTPServer, sendfile)
from httpserver.sse import EventSource

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


@app.route("GET", "/api/time")
def api_time(conn, request):
    """ Set up a server sent event connection to the client updating the time every second """

    def timer_task(conn, eventsource):
        while True:
            time.sleep(1)
            t = time.localtime()
            try:
                eventsource.send(event="time", data=f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}")
            except Exception:  # catch ECONNRESET etc
                conn.close()
                break  # will exit thread

    _thread.start_new_thread(timer_task, (conn, EventSource(conn)))

    return CONNECTION_KEEP_ALIVE


@app.route("GET", "/api/date")
def api_date(conn, request):
    """ Send date as json, then cause an exception """
    response = HTTPResponse(200, "application/json", close=True)
    response.send(conn)
    t = time.localtime()
    sysdate = {
        "day": f"{t[2]:02d}",
        "month": f"{t[1]:02d}",
        "year": f"{t[0]:04d}"
    }
    conn.write(json.dumps(sysdate))
    print(1 / 0)  # will kill the server (but threads stay alive)


@app.route("GET", "/api/stop")
def stop(conn, request):
    response = HTTPResponse(200)
    response.send(conn)
    raise KeyboardInterrupt


if __name__ == "__main__":
    app.start()
