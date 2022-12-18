# Basic HTTP/1.1 response
#
# For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt
# For MIME types see: https://www.iana.org/assignments/media-types/media-types.xhtml
#
# Copyright 2022 (c) Erik de Lange
# Released under MIT license


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
            self.header={}
        else:
            self.header=header

    async def send(self, writer):
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
        await writer.drain()
