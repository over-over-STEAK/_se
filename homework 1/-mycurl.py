import argparse
import sys
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description="簡易版 curl HTTP 客戶端")
    parser.add_argument("url", help="要請求的網址")
    parser.add_argument("-X", "--request", help="HTTP 方法，例如 GET、POST、PUT")
    parser.add_argument("-H", "--header", action="append", default=[],
                        help="自訂標頭，例如 'Accept: application/json'")
    parser.add_argument("-d", "--data", help="要送出的資料")
    parser.add_argument("-L", "--location", action="store_true",
                        help="追蹤重新導向")
    parser.add_argument("-I", "--head", action="store_true",
                        help="只取得回應標頭")
    parser.add_argument("-i", "--include", action="store_true",
                        help="同時顯示回應標頭")
    parser.add_argument("-o", "--output", help="將回應內容存成檔案")
    parser.add_argument("--timeout", type=float, default=10,
                        help="逾時秒數，預設 10 秒")
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        parser.error("網址必須以 http:// 或 https:// 開頭")

    headers = {}
    for item in args.header:
        if ":" not in item:
            parser.error("-H 格式必須為「名稱: 值」")
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()

    data = args.data.encode("utf-8") if args.data is not None else None
    method = args.request or ("HEAD" if args.head else
                              "POST" if data is not None else "GET")

    request = urllib.request.Request(
        args.url,
        data=data,
        headers=headers,
        method=method.upper()
    )

    handlers = []
    if not args.location:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, request, fp, code, msg, headers, newurl):
                return None

        handlers.append(NoRedirect())

    opener = urllib.request.build_opener(*handlers)

    try:
        try:
            response = opener.open(request, timeout=args.timeout)
        except urllib.error.HTTPError as error:
            response = error

        with response:
            if args.head or args.include:
                print(f"HTTP {response.status} {response.reason}")
                for name, value in response.headers.items():
                    print(f"{name}: {value}")
                print()

            if not args.head:
                content = response.read()
                if args.output:
                    with open(args.output, "wb") as file:
                        file.write(content)
                    print(f"已儲存至 {args.output}", file=sys.stderr)
                else:
                    sys.stdout.buffer.write(content)

    except urllib.error.URLError as error:
        print(f"連線失敗：{error.reason}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"檔案或網路錯誤：{error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())