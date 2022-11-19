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


CRLF = b"\r\n"


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


class CacheControl:
    NO_CACHE = b"Cache-Control: no-cache\r\n"
