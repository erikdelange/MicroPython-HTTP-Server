# MicroPython HTTP Servers

Minimal servers for handling HTTP requests. Included are a single-threaded and an uasyncio variant (*httpserver* respectively *ahttpserver*). Intended to be used for simple web-interfaces and to communicate with the microcontroller using HTTP messages.

For every combination of method plus path (like "GET" and "/index") which must be handled by the HTTP server a function must be declared, such as *root* in the example below. By preceding the function definition with decorator @route the function is registered as the handler for the specified method-path combination. In this way the code for the server itself remains hidden and generic; you only need to define the handlers.

Intentionally extremely simple to keep the code as small as possible. HTTP requests are presented as a dict to the handlers (see and run *url.py* for the exact content and a demo), but HTTP responses must be crafted line by line (or by using predefined ones from *response.py*).

``` Python
import uasyncio as asyncio

from ahttpserver import sendfile, Server

app = Server()


@app.route("GET", "/")
async def root(reader, writer, request):
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Connection: close\r\n")
    writer.write(b"Content-Type: text/html\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    await sendfile(writer, "index.html")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
```
To see the async version of the server working start *ademo.py* via the REPL and fire HTTP requests at it via Postman, Insomnia or similar. The demo code includes two divide-by-zero exceptions so you can see how they are handled.

Yes, there are many better and functionally richer examples available on GitHub, but for learning the structure of HTTP requests and also a bit about uasyncio this code served me well. For a detailled understanding of uasyncio see the excellent GitHub pages of [Peter Hinch](https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md).

### Differences between httpserver and ahttpserver
httpserver
- Is single threaded. Is suggest to use ahttpserver whenever possible as it supports cooperative multitasking.
- Also works on Pycom's WiPy's. At the time of writing (2021) Pycom's MicroPython version is lagging behind and does not has asyncio and f-strings included which are required by ahttpserver.
- Can be stopped gracefully by adding the line below in your code. Can come in handy during development.
``` Python
    raise Exception("Stop Server")
```
- Can be used with Keep-Alive connections. See [Wipy 2.0 Web-Interface using JavaScript](https://github.com/erikdelange/WiPy-2.0-Web-Interface-using-JavaScript) for an example.
