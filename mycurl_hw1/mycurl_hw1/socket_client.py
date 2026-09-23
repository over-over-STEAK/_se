import socket
import ssl

from http_response import parse_response
from utils import CurlError


def perform_request(parts, request, timeout, method="GET"):
    try:
        sock = socket.create_connection((parts.host, parts.port), timeout=timeout)
    except socket.gaierror as e:
        raise CurlError(7, f"DNS lookup failed: {e}")
    except socket.timeout:
        raise CurlError(28, "connection timed out")
    except OSError as e:
        raise CurlError(7, f"connection failed: {e}")

    try:
        if parts.scheme == "https":
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=parts.host)
            sock.settimeout(timeout)

        sock.sendall(request)
        chunks = []
        while True:
            try:
                data = sock.recv(65536)
            except socket.timeout:
                raise CurlError(28, "receive timed out")
            if not data:
                break
            chunks.append(data)
        return parse_response(b"".join(chunks), method)
    except ssl.SSLError as e:
        raise CurlError(7, f"TLS/SSL error: {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass
