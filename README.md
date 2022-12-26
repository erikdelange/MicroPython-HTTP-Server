# MicroPython HTTP Servers

Minimal servers for handling HTTP requests. Includes a asyncio and a single-threaded variant (*ahttpserver* respectively *httpserver*). Intended to be used for simple web-interfaces and to communicate with a microcontroller using HTTP messages.

For every combination of method plus path (like "GET" and "/index") which must be handled by the HTTP server a function must be declared, such as *root* in the example below. By preceding the function definition with decorator @route the function is registered as the handler for the specified method-path combination. In this way the code for the server itself remains hidden and generic; you only need to define the handlers.

Intentionally extremely simple to keep the code as small as possible. HTTP requests are presented as an object to the handlers (see and run *url.py* for the exact content and a demo). Class HTTPResponse (see *response.py*) facilitates creating and sending responses.

``` Python
import uasyncio as asyncio

from ahttpserver import HTTPResponse, HTTPServer, sendfile

app = HTTPServer()


@app.route("GET", "/")
async def root(reader, writer, request):
    response = HTTPResponse(200, "text/html", close=True)
    await response.send(writer)
    await sendfile(writer, "index.html")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
```
To see the async version of the server in action start *ademo.py* via the REPL. Open the main web-page in your browser and/or fire HTTP requests at it via Postman, Insomnia or similar. The demo code includes two divide-by-zero exceptions so you can see how they are handled.

Yes, there are many better and functionally richer examples available on GitHub, but for learning the structure of HTTP requests and responses, and also a bit about uasyncio this code served me well. For a detailed understanding of uasyncio see the excellent GitHub pages of [Peter Hinch](https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md).

### Differences between ahttpserver and httpserver
#### ahttpserver
- Offers assistance for using server-sent events via class *EventSource*.
``` Python
from ahttpserver.sse import EventSource

@app.route("GET", "/api/greeting")
async def api_greeting(reader, writer, request):
    # Say hello every 5 seconds
    eventsource = await EventSource(reader, writer)
    while True:
        asyncio.sleep(5)
        try:
            await eventsource.send(event="greeting", data="hello")
        except Exception as e:  # catch (a.o.) ECONNRESET when the client has disappeared
            break  # close connection#
```
#### httpserver
- Was developed for Pycom's WiPy firmware. Only handles a single request at a time as at the time of writing (2021) Pycom's MicroPython version does not include uasyncio which is required by ahttpserver. I suggest to use ahttpserver whenever possible as it supports cooperative multitasking.
- Can be stopped gracefully by adding the line below in your code. Can come in handy during development.
``` Python
    raise Exception("Stop Server")
```
