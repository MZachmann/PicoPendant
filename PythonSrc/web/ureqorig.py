import usocket
# urequest with print statements for debugging


class Response:
    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson

        return ujson.loads(self.content)

def uss(s, txt) :
    print('s+%s' % txt)
    s.write(txt)
    print('s1+%s' % txt)

def sread(s) :
    u = s.readline()
    print(u)
    return u

def request(
    method,
    url,
    data=None,
    json=None,
    headers={},
    stream=None,
    auth=None,
    timeout=None,
    parse_headers=True,
):
    redirect = None  # redirection url, None means no redirection
    chunked_data = data and getattr(data, "__iter__", None) and not getattr(data, "__len__", None)

    if auth is not None:
        import ubinascii

        username, password = auth
        formated = b"{}:{}".format(username, password)
        formated = str(ubinascii.b2a_base64(formated)[:-1], "ascii")
        headers["Authorization"] = "Basic {}".format(formated)

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl

        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]
    print(ai)

    resp_d = None
    if parse_headers is not False:
        resp_d = {}

    s = usocket.socket(ai[0], usocket.SOCK_STREAM, ai[2])
    print('socket built')

    if timeout is not None:
        # Note: settimeout is not supported on all platforms, will raise
        # an AttributeError if not available.
        print('set timeout %d' % int(timeout))
        s.settimeout(timeout)
        print('did set timeout %d' % int(timeout))

    try:
        print('try socket connect ')
        print(ai[-1])
        s.connect(ai[-1])
        print('socket connected')
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        uss(s,b"%s /%s HTTP/1.0\r\n" % (method, path))
        if not "Host" in headers:
            uss(s,b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            uss(s,k)
            uss(s,b": ")
            uss(s,headers[k])
            uss(s,b"\r\n")
        if json is not None:
            assert data is None
            import ujson

            data = ujson.dumps(json)
            uss(s,b"Content-Type: application/json\r\n")
        if data:
            if chunked_data:
                uss(s,b"Transfer-Encoding: chunked\r\n")
            else:
                uss(s,b"Content-Length: %d\r\n" % len(data))
        uss(s,b"Connection: close\r\n\r\n")
        if data:
            if chunked_data:
                for chunk in data:
                    uss(s,b"%x\r\n" % len(chunk))
                    uss(s,chunk)
                    uss(s,b"\r\n")
                uss(s,"0\r\n\r\n")
            else:
                uss(s,data)

        l = sread(s)
        # print(l)
        l = l.split(None, 2)
        if len(l) < 2:
            # Invalid response
            raise ValueError("HTTP error: BadStatusLine:\n%s" % l)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = sread(s)
            if not l or l == b"\r\n":
                break
            # print(l)
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + str(l, "utf-8"))
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                if status in [301, 302, 303, 307, 308]:
                    redirect = str(l[10:-2], "utf-8")
                else:
                    raise NotImplementedError("Redirect %d not yet supported" % status)
            if parse_headers is False:
                pass
            elif parse_headers is True:
                l = str(l, "utf-8")
                k, v = l.split(":", 1)
                resp_d[k] = v.strip()
            else:
                parse_headers(l, resp_d)
    except OSError:
        s.close()
        raise

    if redirect:
        s.close()
        if status in [301, 302, 303]:
            return request("GET", redirect, None, None, headers, stream)
        else:
            return request(method, redirect, data, json, headers, stream)
    else:
        resp = Response(s)
        resp.status_code = status
        resp.reason = reason
        if resp_d is not None:
            resp.headers = resp_d
        return resp


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)