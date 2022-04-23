# Routines for decoding an HTTP request line.
#
# HTTP request line as understood by this package:
#
#   Request line: Method SP Request-URL SP HTTP-Version CRLF
#   Request URL: Path ? Query
#   Query: key=value&key=value
#
# Example: b"GET /page?key1=0.07&key2=0.03&key3=0.13 HTTP/1.1\r\n"
#
#   Method: GET
#   Request URL: /page?key1=0.07&key2=0.03&key3=0.13
#   HTTP version: HTTP/1.1
#   Path: /page
#   Query: key1=0.07&key2=0.03&key3=0.13
#
# See also: https://www.tutorialspoint.com/http/http_requests.htm
#           https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
#
# For MicroPython applications which process HTTP requests.
#
# Copyright 2021 (c) Erik de Lange
# Released under MIT license


class InvalidRequest(Exception):
    pass


def query(request_line):
    """ Place all key-value pairs from a request URL's query string into a dict.

    Example: request b"GET /page?key1=0.07&key2=0.03&key3=0.13 HTTP/1.1\r\n"
    yields dictionary {'key1': '0.07', 'key2': '0.03', 'key3': '0.13'}.

    :param bytes request_line: the complete HTTP request line
    :return dict: dictionary with zero or more entries
    """
    d = dict()
    p = request_line.find(b"?")  # only look in the query part of a request URL
    if p != -1:
        p_space = request_line.find(b" ", p)
        while True:
            n_start = p + 1
            n_end = request_line.find(b"=", n_start)
            if n_end == -1:
                break
            v_start = n_end + 1
            p_and = request_line.find(b"&", v_start)
            v_end = p_space if p_and == -1 else min(p_space, p_and)
            key = request_line[n_start:n_end].decode("utf-8")
            if key not in d:
                d[key] = request_line[v_start:v_end].decode("utf-8")
            p = v_end
            p = request_line.find(b"&", p)
            if p == -1:
                break
    return d


def request(line):
    """ Separate an HTTP request line in its elements and put them into a dict.

    :param bytes line: the complete HTTP request line.
    :return dict: dictionary containing
            method      the request method ("GET", "PUT", ...)
            url         the request URL, including the query string (if any)
            path        the request path from the URL
            query       the query string from the URL (if any, else "")
            version     the HTTP version
            parameters  dictionary with key-value pairs from the query string
            header      placeholder for key-value pairs from request header fields
    :raises InvalidRequest: if line does not contain exactly 3 components separated by spaces
                            if method is not in IETF standardized set
                            aside from these no other checks done here
    """
    d = {key: value for key, value in zip(["method", "url", "version"], line.decode("utf-8").split())}

    if len(d) != 3:
        raise InvalidRequest("Expected 3 elements in {}".format(line))

    if d["method"] not in ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]:
        raise InvalidRequest("Invalid method {} in {}".format(d['method'], line))

    d["parameters"] = query(line)

    question = d["url"].find("?")

    d["path"] = d["url"] if question == -1 else d["url"][0:question]
    d["query"] = "" if question == -1 else d["url"][question + 1:]
    d["header"] = dict()

    return d


if __name__ == "__main__":
    request_lines = [b"GET / HTTP/1.1\r\n",
                     b"GET /page/sub HTTP/1.1\r\n",
                     b"GET /page?key1=0.07&key2=0.03 HTTP/1.1\r\n",
                     b"GET HTTP/1.1\r\n",
                     b"UNKNOWN / HTTP/1.1\r\n"]

    for line in request_lines:
        print("request line", line)
        try:
            print("request:", request(line))
            print("query  :", query(line))
        except Exception as e:
            print("exception", repr(e))
        finally:
            print()
