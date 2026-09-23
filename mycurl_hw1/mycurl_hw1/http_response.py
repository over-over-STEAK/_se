from dataclasses import dataclass


@dataclass
class HTTPResponse:
    http_version: str
    status_code: int
    reason: str
    headers: dict
    body: bytes


def _decode_chunked(data):
    out = bytearray()
    pos = 0
    while True:
        end = data.find(b"\r\n", pos)
        if end < 0:
            break
        size_text = data[pos:end].split(b";", 1)[0]
        size = int(size_text, 16)
        pos = end + 2
        if size == 0:
            break
        out.extend(data[pos:pos + size])
        pos += size + 2
    return bytes(out)


def parse_response(raw, method="GET"):
    head, sep, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    version, code, *reason = lines[0].split(" ")
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    status = int(code)
    if method == "HEAD" or status in (204, 304) or 100 <= status < 200:
        body = b""
    elif "chunked" in headers.get("transfer-encoding", "").lower():
        body = _decode_chunked(body)
    elif "content-length" in headers:
        body = body[:int(headers["content-length"])]

    return HTTPResponse(version.replace("HTTP/", ""), status, " ".join(reason), headers, body)
