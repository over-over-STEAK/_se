import base64


def build_request(parts, method, headers, data, user=None):
    h = dict(headers)
    default_port = 443 if parts.scheme == "https" else 80
    h.setdefault("Host", parts.host if parts.port == default_port else f"{parts.host}:{parts.port}")
    h.setdefault("Accept", "*/*")
    h.setdefault("Connection", "close")

    credentials = user
    if credentials is None and parts.username is not None:
        credentials = f"{parts.username}:{parts.password or ''}"
    if credentials:
        token = base64.b64encode(credentials.encode()).decode()
        h.setdefault("Authorization", f"Basic {token}")

    body = data or b""
    if body:
        h.setdefault("Content-Length", str(len(body)))
        h.setdefault("Content-Type", "application/x-www-form-urlencoded")

    lines = [f"{method} {parts.path} HTTP/1.1"]
    lines += [f"{k}: {v}" for k, v in h.items()]
    return ("\r\n".join(lines) + "\r\n\r\n").encode("iso-8859-1") + body
