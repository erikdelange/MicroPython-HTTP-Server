# Demo program for ahttpserver
#
# Start this program and use you browser to open the main page ('/').
# The current time will be displayed and updated every second.
# Use an API client like Insomnia or Postman to call '/api/date' or
# 'api/stop'.

import gc
import json
import time

import uasyncio as asyncio

from ahttpserver import HTTPResponse, HTTPServer, sendfile
from ahttpserver.sse import EventSource

app = HTTPServer()


@app.route("GET", "/")
async def root(reader, writer, request):
    response = HTTPResponse(200, "text/html", close=True)
    await response.send(writer)
    await sendfile(writer, "index.html")
    await writer.drain()
    try:
        print(1/0)
    except Exception as e:
        print("exception in function root():", e)  # exception handled locally, does not stop server


# @app.route("GET", "/")  # if uncommented raises route already declared exception
# async def also_root(reader, writer, request):
#     return


@app.route("GET", "/favicon.ico")
async def favicon(reader, writer, request):
    response = HTTPResponse(200, "image/x-icon", close=True)
    await response.send(writer)
    await writer.drain()
    await sendfile(writer, "favicon.ico")


@app.route("GET", "/api/time")
async def api_time(reader, writer, request):
    """ Setup a server sent event connection to the client updating the time every second """
    eventsource = await EventSource(reader, writer)
    while True:
        await asyncio.sleep(1)
        t = time.localtime()
        try:
            await eventsource.send(event="time", data=f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}")
        except Exception:
            break  # close connection


@app.route("GET", "/api/date")
async def api_date(reader, writer, request):
    """ Send date as json, then cause an exception """
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    await writer.drain()
    t = time.localtime()
    sysdate = {
        "day": f"{t[2]:02d}",
        "month": f"{t[1]:02d}",
        "year": f"{t[0]:04d}"
    }
    writer.write(json.dumps(sysdate))
    await writer.drain()
    print(1/0)  # will be caught by global exception handler, stops server (and the rest)


@app.route("GET", "/api/stop")
async def api_stop(reader, writer, request):
    """ Force asyncio scheduler to stop, just like ctrl-c on the repl """
    response = HTTPResponse(200, "text/plain", close=True)
    await response.send(writer)
    writer.write("stopping server")
    await writer.drain()
    raise (KeyboardInterrupt)


async def say_hello_task():
    """ Show system is still alive """
    count = 0
    while True:
        print("hello", count)
        count += 1
        await asyncio.sleep(60)


async def free_memory_task():
    """ Avoid memory fragmentation """
    while True:
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        def handle_exception(loop, context):
            # uncaught exceptions end up here
            import sys
            print("global exception handler:", context)
            sys.print_exception(context["exception"])
            sys.exit()

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_exception)

        loop.create_task(say_hello_task())
        loop.create_task(free_memory_task())
        loop.create_task(app.start())

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(app.stop())
        asyncio.new_event_loop()
