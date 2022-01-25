# Memory efficient file transfer
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

_buffer = bytearray(512)  # adjust size to your systems available memory
_bmview = memoryview(_buffer)  # reuse pre-allocated _buffer


async def sendfile(conn, filename):
    """ Send a file to a connection in chunks - lowering memory usage.

    :param socket conn: connection to send the file content to
    :param str filename: name of file to send
    """
    with open(filename, "rb") as fp:
        while True:
            n = fp.readinto(_buffer)
            if n == 0:
                break
            conn.write(_bmview[:n])
            await conn.drain()
