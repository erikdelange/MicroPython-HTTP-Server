# Components of HTTP/1.1 responses
#
# Use when manually composing an HTTP response
# Expand as required for your use
#
# For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt
# For MIME types see: https://www.iana.org/assignments/media-types/media-types.xhtml
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license

CRLF = b"\r\n"  # empty line: end of header, start of optional payload


class StatusLine:
    OK_200 = b"HTTP/1.1 200 OK\r\n"
    BAD_REQUEST_400 = b"HTTP/1.1 400 Bad Request\r\n"
    NOT_FOUND_404 = b"HTTP/1.1 404 Not Found\r\n"


class ResponseHeader:
    CONNECTION_CLOSE = b"Connection: close\r\n"
    CONNECTION_KEEP_ALIVE = b"Connection: keep-alive\r\n"


class MimeType:
    TEXT_HTML = b"Content-Type: text/html\r\n"
    TEXT_EVENT_STREAM = b"Content-Type: text/event-stream\r\n"
    IMAGE_X_ICON = b"Content-Type: image/x-icon\r\n"
    APPLICATION_JSON = b"Content-Type: application/json\r\n"


reason = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found"
}


class HTTPResponse:

    def __init__(self, status, mimetype=None, close=True, header=None):
        """ Create a response object

        :param int status: HTTP status code
        :param str mimetype: HTTP mime type
        :param bool close: if true close connection else keep alive
        :param dict header: key,value pairs for HTTP response header fields
        """
        self.status = status
        self.mimetype = mimetype
        self.close = close
        if header is None:
            self.header = {}
        else:
            self.header = header

    def send(self, writer):
        """ Send response to stream writer """
        writer.write(f"HTTP/1.1 {self.status} {reason.get(self.status, 'NA')}\n")
        if self.mimetype is not None:
            writer.write(f"Content-Type: {self.mimetype}\n")
        if self.close:
            writer.write("Connection: close\n")
        else:
            writer.write("Connection: keep-alive\n")
        if len(self.header) > 0:
            for key, value in self.header.items():
                writer.write(f"{key}: {value}\n")
        writer.write("\n")
