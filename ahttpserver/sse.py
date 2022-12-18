# Server-sent event support
#
# Usage:
#
#   import uasyncio as asyncio
#
#   from ahttpserver.sse import EventSource
#
#   @app.route("GET", "/api/greeting")
#   async def api_greeting(reader, writer, request):
#       # Say hello every 5 seconds
#       eventsource = await EventSource.init(reader, writer)
#       while True:
#           asyncio.sleep(5)
#           try:
#               await eventsource.send(event="greeting", data="hello")
#           except Exception as e:  # catch (a.o.) ECONNRESET when the client has disappeared
#               break  # close connection#
#
# Copyright 2022 (c) Erik de Lange
# Released under MIT license

from .response import HTTPResponse


class EventSource:
    """ Helper class for sending server sent events to a client """

    @classmethod
    async def init(cls, reader, writer):
        """ Transform the current connection into an eventsource

        Must use a class method as __init__ is always synchronous.
        """
        response = HTTPResponse(200, "text/event-stream", close=False, header={"Cache-Control": "no-cache"})
        await response.send(writer)
        return cls(reader, writer)

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, data=":", id=None, event=None, retry=None):
        """ Send event to client following the event stream format

        :param str data: event data to send to client. mandatory
        :param int id: optional event id
        :param str event: optional event type, used for dispatching at client
        :param int retry: retry interval in milliseconds
        """
        writer = self.writer
        if id is not None:
            writer.write(f"id: {id}\n")
        if event is not None:
            writer.write(f"event: {event}\n")
        if retry is not None:
            writer.write(f"retry: {retry}\n")
        writer.write(f"data: {data}\n\n")
        await writer.drain()
