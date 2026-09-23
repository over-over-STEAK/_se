# mycurl 測試說明

在 VS Code 終端機進入專案資料夾：

```bash
cd mycurl_hw1
```

確認 Python：

```bash
python --version
```

## 1. GET

```bash
python main.py https://httpbin.org/get
```

預期：回傳 JSON，程式 Exit Code 為 0。

## 2. Verbose

```bash
python main.py -v https://httpbin.org/get
```

預期：終端機可看到 `>` Request Header 與 `<` Response Header。

## 3. POST

```bash
python main.py -d "name=alice&age=20" https://httpbin.org/post
```

預期：回傳資料包含 `name=alice&age=20`。

## 4. JSON

Windows PowerShell：

```powershell
python main.py --json '{"name":"Lin","age":20}' https://httpbin.org/post
```

## 5. Redirect

```bash
python main.py -L https://httpbin.org/redirect/3
```

預期：自動追蹤至最後頁面。

## 6. Basic Auth

```bash
python main.py --user admin:secret https://httpbin.org/basic-auth/admin/secret
```

預期：authenticated 為 true。

## 7. 下載檔案

```bash
python main.py -o result.html https://httpbin.org/html
```

預期：專案資料夾產生 `result.html`。

## 8. HEAD

```bash
python main.py -I https://example.com
```

預期：只顯示 HTTP 狀態與 Headers。

## 9. 自訂方法

```bash
python main.py -X DELETE https://httpbin.org/delete
```

## 10. 查看 Exit Code

PowerShell：

```powershell
python main.py https://httpbin.org/get
$LASTEXITCODE
```

成功應為 `0`。
