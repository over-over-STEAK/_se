import argparse
import requests

parser = argparse.ArgumentParser(description="簡易版 curl 工具")

parser.add_argument("url", help="要連線的網址")
parser.add_argument("-X", "--request", default="GET", help="HTTP 方法")
parser.add_argument("-d", "--data", help="傳送的資料")
parser.add_argument("-H", "--header", action="append", help="HTTP Header")
parser.add_argument("-i", "--include", action="store_true", help="顯示 Response Header")

args = parser.parse_args()

headers = {}

if args.header:
    for item in args.header:
        if ":" in item:
            key, value = item.split(":", 1)
            headers[key.strip()] = value.strip()

try:
    response = requests.request(
        method=args.request.upper(),
        url=args.url,
        headers=headers,
        data=args.data,
        timeout=10
    )

    print("HTTP Status:", response.status_code)

    if args.include:
        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")

    print("\nResponse Body:")
    print(response.text)

except requests.exceptions.Timeout:
    print("錯誤：連線逾時")

except requests.exceptions.ConnectionError:
    print("錯誤：無法連線到伺服器")

except requests.exceptions.RequestException as e:
    print("發生錯誤：", e)