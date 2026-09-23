import argparse
import sys

from url_parser import parse_url
from http_request import build_request
from socket_client import perform_request
from utils import CurlError, read_data_arg, parse_header_args, print_verbose_request, print_verbose_response


def create_parser():
    p = argparse.ArgumentParser(prog="mycurl", description="curl-like HTTP client using only Python standard library")
    p.add_argument("urls", nargs="+", help="URL(s) to request")
    p.add_argument("-X", "--request", default=None, help="HTTP method")
    p.add_argument("-H", "--header", action="append", default=[], help="Custom header: NAME: VALUE")
    p.add_argument("-d", "--data", help="Request body or @filename")
    p.add_argument("-o", "--output", help="Write response body to file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show request/response details")
    p.add_argument("-L", "--location", action="store_true", help="Follow redirects")
    p.add_argument("-m", "--max-time", type=float, default=30.0, help="Timeout in seconds")
    p.add_argument("--user", help="Basic auth user:password")
    p.add_argument("--json", help="Send JSON body")
    p.add_argument("--cookie", help="Cookie header value")
    p.add_argument("--user-agent", default="mycurl/1.0", help="User-Agent value")
    p.add_argument("-I", "--head", action="store_true", help="HEAD request / headers only")
    p.add_argument("--no-progress", action="store_true", help="Disable file download progress")
    return p


def one_request(url, args):
    headers = parse_header_args(args.header)
    headers.setdefault("User-Agent", args.user_agent)

    if args.cookie:
        headers["Cookie"] = args.cookie

    data = read_data_arg(args.data) if args.data is not None else None
    if args.json is not None:
        data = args.json.encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    method = args.request.upper() if args.request else ("POST" if data is not None else "GET")
    if args.head:
        method = "HEAD"

    current_url = url
    redirects = 0

    while True:
        parts = parse_url(current_url)
        request = build_request(parts, method, headers, data, args.user)

        if args.verbose:
            print_verbose_request(parts, request)

        response = perform_request(parts, request, args.max_time, method)

        if args.verbose:
            print_verbose_response(response)

        if args.location and response.status_code in (301, 302, 303, 307, 308) and "location" in response.headers:
            redirects += 1
            if redirects > 10:
                raise CurlError(3, "too many redirects")
            current_url = response.headers["location"]
            if current_url.startswith("/"):
                current_url = f"{parts.scheme}://{parts.host}:{parts.port}{current_url}"
            if response.status_code in (301, 302, 303) and method not in ("GET", "HEAD"):
                method, data = "GET", None
            continue
        break

    if args.head:
        print(f"HTTP/{response.http_version} {response.status_code} {response.reason}")
        for k, v in response.headers.items():
            print(f"{k}: {v}")
        return

    if args.output:
        with open(args.output, "wb") as f:
            total = len(response.body)
            chunk = max(1, total // 20)
            written = 0
            for i in range(0, total, chunk):
                piece = response.body[i:i + chunk]
                f.write(piece)
                written += len(piece)
                if not args.no_progress:
                    pct = 100 if total == 0 else int(written * 100 / total)
                    print(f"\rDownloading: {pct:3d}% ({written}/{total} bytes)", end="", file=sys.stderr)
            if not args.no_progress:
                print(file=sys.stderr)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        try:
            sys.stdout.write(response.body.decode("utf-8"))
            if response.body and not response.body.endswith(b"\n"):
                print()
        except UnicodeDecodeError:
            sys.stdout.buffer.write(response.body)


def main():
    args = create_parser().parse_args()
    try:
        for i, url in enumerate(args.urls):
            if len(args.urls) > 1:
                print(f"==> {url} <==", file=sys.stderr)
            one_request(url, args)
        return 0
    except CurlError as e:
        print(f"mycurl: ({e.code}) {e}", file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        print("\nmycurl: cancelled", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
