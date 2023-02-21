import usocket
import uasyncio as asyncio
import ujson as json
# an asynchronous version of urequest

class Response:
	def __init__(self, f):
		self.encoding = "utf-8"
		self._cached = f

	def close(self):
		self._cached = None

	@property
	def content(self):
		return self._cached

	@property
	def text(self):
		return str(self.content, self.encoding)

	def json(self):
		return json.loads(self.content)


async def request(
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

	#ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
	#ai = ai[0]

	resp_d = None
	if parse_headers is not False:
		resp_d = {}

	# s = usocket.socket(ai[0], usocket.SOCK_STREAM, ai[2])

	# if timeout is not None:
	#     # Note: settimeout is not supported on all platforms, will raise
	#     # an AttributeError if not available.
	#     s.settimeout(timeout)

	try:
		reader, writer = await asyncio.open_connection(host, port)
		#s.connect(ai[-1])
		#if proto == "https:":
		#    s = ussl.wrap_socket(s, server_hostname=host)
		writer.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
		if not "Host" in headers:
			writer.write(b"Host: %s\r\n" % host)
		# Iterate over keys to avoid tuple alloc
		for k in headers:
			writer.write(k)
			writer.write(b": ")
			writer.write(headers[k])
			writer.write(b"\r\n")
		if json is not None:
			assert data is None
			data = json.dumps(json)
			writer.write(b"Content-Type: application/json\r\n")
		if data:
			if chunked_data:
				writer.write(b"Transfer-Encoding: chunked\r\n")
			else:
				writer.write(b"Content-Length: %d\r\n" % len(data))
		writer.write(b"Connection: close\r\n\r\n")
		if data:
			if chunked_data:
				for chunk in data:
					writer.write(b"%x\r\n" % len(chunk))
					writer.write(chunk)
					writer.write(b"\r\n")
				writer.write("0\r\n\r\n")
			else:
				writer.write(data)
		await writer.drain()

		l = await reader.readline()
		#print(l)
		l = l.split(None, 2)
		if len(l) < 2:
			# Invalid response
			raise ValueError("HTTP error: BadStatusLine:\n%s" % l)
		status = int(l[1])
		reason = ""
		if len(l) > 2:
			reason = l[2].rstrip()
		while True:
			l = await reader.readline()
			#print(l)
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
		writer.close()
		await writer.wait_closed()
		raise

	if redirect:
		writer.close()
		await writer.wait_closed()
		if status in [301, 302, 303]:
			return request("GET", redirect, None, None, headers, stream)
		else:
			return request(method, redirect, data, json, headers, stream)
	else:
		resp = Response(await reader.read())
		resp.status_code = status
		resp.reason = reason
		if resp_d is not None:
			resp.headers = resp_d
		writer.close()
		await writer.wait_closed()
		return resp


async def head(url, **kw):
	return request("HEAD", url, **kw)


async def get(url, **kw):
	return await request("GET", url, **kw)


async def post(url, **kw):
	return await request("POST", url, **kw)


async def put(url, **kw):
	return await request("PUT", url, **kw)


async def patch(url, **kw):
	return await request("PATCH", url, **kw)


async def delete(url, **kw):
	return await request("DELETE", url, **kw)