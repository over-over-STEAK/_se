import sys


class CurlError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def read_data_arg(value):
    if value.startswith("@"):
        try:
            with open(value[1:], "rb") as f:
                return f.read()
        except OSError as e:
            raise CurlError(6, f"cannot read body file: {e}")
    return value.encode("utf-8")


def parse_header_args(items):
    result = {}
    for item in items:
        if ":" not in item:
            raise CurlError(6, f"invalid header: {item}")
        k, v = item.split(":", 1)
        if not k.strip():
            raise CurlError(6, f"invalid header: {item}")
        result[k.strip()] = v.strip()
    return result


def print_verbose_request(parts, request):
    first, _, rest = request.partition(b"\r\n")
    print(f"* Connected target: {parts.host}:{parts.port} ({parts.scheme})", file=sys.stderr)
    print("> " + first.decode("iso-8859-1"), file=sys.stderr)
    for line in rest.split(b"\r\n"):
        if not line:
            break
        print("> " + line.decode("iso-8859-1"), file=sys.stderr)
    print(">", file=sys.stderr)


def print_verbose_response(response):
    print(f"< HTTP/{response.http_version} {response.status_code} {response.reason}", file=sys.stderr)
    for k, v in response.headers.items():
        print(f"< {k}: {v}", file=sys.stderr)
    print("<", file=sys.stderr)
