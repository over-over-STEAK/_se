#!/usr/bin/env python3
"""A small curl-like HTTP client using only Python's standard library."""
import argparse
import base64
import http.client
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def header(value):
    name, separator, content = value.partition(':')
    if not separator or not name.strip():
        raise argparse.ArgumentTypeError('header 格式須為「名稱: 值」')
    return name.strip(), content.strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description='純標準函式庫的 curl 風格 HTTP 客戶端')
    parser.add_argument('url', help='http:// 或 https:// 網址')
    parser.add_argument('-X', '--request', metavar='METHOD', help='HTTP 方法')
    parser.add_argument('-H', '--header', action='append', type=header, default=[], help='自訂標頭，可重複')
    parser.add_argument('-d', '--data', action='append', help='送出文字資料，可重複')
    parser.add_argument('--data-binary', metavar='FILE', help='讀取檔案內容送出；- 表示 stdin')
    parser.add_argument('-u', '--user', metavar='USER:PASS', help='HTTP Basic Auth')
    parser.add_argument('-L', '--location', action='store_true', help='追蹤重新導向')
    parser.add_argument('-I', '--head', action='store_true', help='只取得回應標頭')
    parser.add_argument('-i', '--include', action='store_true', help='輸出回應標頭及本文')
    parser.add_argument('-o', '--output', metavar='FILE', help='將本文寫入檔案')
    parser.add_argument('-s', '--silent', action='store_true', help='不顯示進度及錯誤')
    parser.add_argument('--progress', action='store_true', help='顯示下載進度')
    parser.add_argument('--max-time', type=float, default=30, metavar='SECONDS', help='逾時秒數（預設 30）')
    parser.add_argument('-k', '--insecure', action='store_true', help='略過 HTTPS 憑證驗證')
    args = parser.parse_args(argv)
    parsed = urllib.parse.urlsplit(args.url)
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.netloc:
        parser.error('URL 須為有效的 http:// 或 https:// 網址')
    if args.max_time <= 0:
        parser.error('--max-time 必須大於 0')
    if args.data is not None and args.data_binary is not None:
        parser.error('-d 與 --data-binary 不可同時使用')
    if args.head and (args.data is not None or args.data_binary is not None):
        parser.error('-I 不可與資料上傳同時使用')
    if args.head and args.request and args.request.upper() != 'HEAD':
        parser.error('-I 不可與非 HEAD 的 -X 同時使用')
    if args.output == '-' and args.include:
        parser.error('-o - 與 -i 不可同時使用')

    headers = dict(args.header)
    if args.user is not None:
        if ':' not in args.user:
            parser.error('-u 格式須為「帳號:密碼」')
        headers['Authorization'] = 'Basic ' + base64.b64encode(args.user.encode()).decode('ascii')
    body = None
    if args.data is not None:
        body = '&'.join(args.data).encode('utf-8')
        if not any(k.lower() == 'content-type' for k in headers):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif args.data_binary is not None:
        try:
            body = sys.stdin.buffer.read() if args.data_binary == '-' else open(args.data_binary, 'rb').read()
        except OSError as exc:
            if not args.silent:
                print(f'mycurl: {exc}', file=sys.stderr)
            return 26
    method = (args.request or ('HEAD' if args.head else 'POST' if body is not None else 'GET')).upper()
    if not method.isascii() or not method or any(c not in "!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in method):
        parser.error('無效的 HTTP 方法')
    request = urllib.request.Request(args.url, data=body, headers=headers, method=method)
    context = ssl._create_unverified_context() if args.insecure else ssl.create_default_context()
    handlers = [urllib.request.HTTPSHandler(context=context)]
    if not args.location:
        handlers.append(NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    try:
        try:
            response = opener.open(request, timeout=args.max_time)
        except urllib.error.HTTPError as exc:
            response = exc  # HTTP 4xx/5xx still has a response body.
        with response:
            status = response.status
            if args.include or args.head:
                line = f'HTTP/1.1 {status} {http.client.responses.get(status, "")}\r\n'
                line += ''.join(f'{k}: {v}\r\n' for k, v in response.headers.items()) + '\r\n'
                sys.stdout.buffer.write(line.encode('iso-8859-1', errors='replace'))
            if method != 'HEAD':
                target = sys.stdout.buffer if args.output is None or args.output == '-' else open(args.output, 'wb')
                try:
                    total = response.headers.get('Content-Length')
                    total = int(total) if total and total.isdigit() else None
                    count = 0
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        target.write(chunk)
                        count += len(chunk)
                        if args.progress and not args.silent:
                            progress = f'{count}/{total} bytes ({count / total:.0%})' if total else f'{count} bytes'
                            print('\r' + progress, end='', file=sys.stderr, flush=True)
                    if args.progress and not args.silent:
                        print(file=sys.stderr)
                finally:
                    if target is not sys.stdout.buffer:
                        target.close()
            return 0
    except (OSError, urllib.error.URLError, ValueError) as exc:
        if not args.silent:
            print(f'mycurl: {exc}', file=sys.stderr)
        return 7


if __name__ == '__main__':
    sys.exit(main())
