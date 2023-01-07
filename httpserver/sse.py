# Server-sent event support
#
# Usage:
#
#   import _thread, time
#
#   from httpserver.sse import EventSource
#
#   @app.route("GET", "/api/greeting")
#   def api_greeting(conn, request):
#       """ Say hello every 5 seconds """
#
#       def greeting_task(conn, eventsource):
#           while True:
#               time.sleep(5)
#               try:
#                   eventsource.send(event="greeting", data="hello")
#               except Exception:  # catch (a.o.) ECONNRESET when the client has disappeared
#                   conn.close()
#                   break  # exit thread
#
#       _thread.start_new_thread(greeting_task, (conn, EventSource(conn)))
#
# Copyright 2022 (c) Erik de Lange
# Released under MIT license

from .response import HTTPResponse


class EventSource:
    """ Open and use an event stream connection to the client """

    def __init__(self, conn):
        """ Set up an event stream connection """
        self.conn = conn

        response = HTTPResponse(200, "text/event-stream", close=False, header={"Cache-Control": "no-cache"})
        response.send(self.conn)

    def send(self, data=":", id=None, event=None, retry=None):
        """ Send event to client following the event stream format

        :param str data: event data to send to client. mandatory
        :param int id: optional event id
        :param str event: optional event type, used for dispatching at client
        :param int retry: retry interval in milliseconds
        """
        writer = self.conn
        if id is not None:
            writer.write(f"id: {id}\n")
        if event is not None:
            writer.write(f"event: {event}\n")
        if retry is not None:
            writer.write(f"retry: {retry}\n")
        writer.write(f"data: {data}\n\n")
