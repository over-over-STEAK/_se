# mycurl

`mycurl` 是使用 Python **純標準函式庫**製作的 curl 風格 HTTP Client，不使用 `requests` 等第三方 HTTP 套件。

## 功能

- HTTP / HTTPS (`socket` + `ssl`)
- GET / POST / PUT / DELETE / PATCH / HEAD
- `-H` 自訂 Header
- `-d` 傳送 Body，亦支援 `@filename`
- `--json` JSON Body
- `--cookie` Cookie
- `--user-agent` User-Agent
- `--user user:password` Basic Authentication
- URL 內嵌 `user:pass@host`
- `-L` Redirect
- `-o` 儲存 Response Body
- `-I` 只取得 Header
- `-v` Verbose
- `-m` Timeout
- Content-Length / Chunked Transfer-Encoding
- 多 URL
- 下載進度顯示
- Exit Code 錯誤回報

## 檔案結構

| 檔案 | 說明 |
| --- | --- |
| `main.py` | 命令列參數與主流程 |
| `url_parser.py` | URL 解析 |
| `http_request.py` | 建構 HTTP Request |
| `http_response.py` | 解析 HTTP Response |
| `socket_client.py` | TCP Socket 與 TLS/SSL |
| `utils.py` | 錯誤、Header、Verbose 等工具 |
| `README.md` | 專案說明 |
| `README-testing.md` | 測試方式 |

## 執行

不需安裝第三方套件：

```bash
python main.py https://httpbin.org/get
```

### GET

```bash
python main.py https://httpbin.org/get
```

### Verbose

```bash
python main.py -v https://httpbin.org/get
```

### POST

```bash
python main.py -d "name=alice&age=20" https://httpbin.org/post
```

### JSON

```bash
python main.py --json "{\"name\":\"Lin\",\"age\":20}" https://httpbin.org/post
```

### 自訂 Header

```bash
python main.py -H "Accept: application/json" https://httpbin.org/headers
```

### Redirect

```bash
python main.py -L https://httpbin.org/redirect/3
```

### Basic Auth

```bash
python main.py --user admin:secret https://httpbin.org/basic-auth/admin/secret
```

### 儲存檔案

```bash
python main.py -o result.html https://httpbin.org/html
```

### HEAD

```bash
python main.py -I https://example.com
```

### Timeout

```bash
python main.py -m 5 https://httpbin.org/delay/3
```

## Exit Code

| Code | 意義 |
| ---: | --- |
| 0 | 成功 |
| 3 | URL / Redirect 錯誤 |
| 6 | Header / Body 檔案錯誤 |
| 7 | DNS / TCP / TLS 連線錯誤 |
| 28 | Timeout |

## 專案重點

本專案沒有使用高階 HTTP 第三方套件，而是從 TCP Socket 開始建立連線。HTTPS 使用 `ssl` 建立 TLS 加密連線，HTTP Request Header 與 Body 由程式自行組合，Response 也由程式自行解析。

透過實作可以理解 URL、DNS、TCP、TLS、HTTP Method、Header、Body、Status Code、Redirect、Content-Length、Chunked Transfer-Encoding 與 Basic Authentication 的基本運作方式。
