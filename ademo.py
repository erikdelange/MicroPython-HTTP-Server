import sys
import time
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
    try:
        print(1/0)
    except Exception as e:
        print("exception in function root():", e)  # exception handled locally


# @app.route("GET", "/")  # if uncommented raises route already declared exception
# async def also_root(reader, writer, request):
#     return


@app.route("GET", "/favicon.ico")
async def favicon(reader, writer, request):
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Connection: close\r\n")
    writer.write(b"Content-Type: image/x-icon\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    await sendfile(writer, "favicon.ico")


@app.route("GET", "/api/time")
async def get_time(reader, writer, request):
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Connection: close\r\n")
    writer.write(b"Content-Type: text/html\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    t = time.localtime()
    writer.write(f"{t[2]:02d}-{t[1]:02d}-{t[0]:04d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}")
    print(1/0)  # will be caught by global exception handler


@app.route("GET", "/api/stop")
async def stop(reader, writer, request):
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Connection: close\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    raise(KeyboardInterrupt)


async def hello():
    """ For demo purposes show system is still alive """
    count = 0
    while True:
        print("hello", count)
        count += 1
        await asyncio.sleep(60)


def set_global_exception_handler():
    def handle_exception(loop, context):
        # uncaught exceptions raised in route handlers end up here
        print("global exception handler:", context)
        sys.print_exception(context["exception"])

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


if __name__ == "__main__":
    try:
        set_global_exception_handler()

        asyncio.create_task(hello())
        asyncio.run(app.start())  # must be last, does not return
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(app.stop())
        asyncio.new_event_loop()
