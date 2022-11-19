import time

import uasyncio as asyncio

from ahttpserver import Server, sendfile

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
        print("exception in function root():", e)  # exception handled locally, does not stop server


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
    print(1/0)  # will be caught by global exception handler, stops server (and the rest)


@app.route("GET", "/api/stop")
async def stop(reader, writer, request):
    """ Force asyncio scheduler to stop, just like ctrl-c on the repl """
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Connection: close\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    raise (KeyboardInterrupt)


async def hello():
    """ Show system is still alive """
    count = 0
    while True:
        print("hello", count)
        count += 1
        await asyncio.sleep(60)


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

        loop.create_task(hello())
        loop.create_task(app.start())

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(app.stop())
        asyncio.new_event_loop()
