# mycurl

使用 Python 標準函式庫製作的 curl 風格命令列 HTTP 客戶端，支援 HTTP/HTTPS，不需安裝套件。需要 Python 3.9 以上。

## 執行

```bash
python mycurl.py https://example.com
python mycurl.py -I https://example.com
python mycurl.py -L -i https://example.com
python mycurl.py -H 'Accept: application/json' -u 'user:password' https://example.com/api
python mycurl.py -d 'name=Alice' -d 'age=20' https://example.com/form
python mycurl.py -X PUT --data-binary photo.jpg https://example.com/upload
python mycurl.py -o result.html --progress --max-time 10 https://example.com
```

使用 `python mycurl.py --help` 查看參數。`-d` 會以 `&` 串接各段輸入；需要 URL 編碼時請自行編碼。`--data-binary -` 從標準輸入讀取。`-L` 依 HTTP 重新導向規則追蹤；未指定時 3xx 回應直接輸出。`-k` 會停用憑證驗證，僅供測試。

結束碼：`0` 表示成功取得 HTTP 回應（包括 4xx/5xx）；`7` 表示連線、逾時或輸出錯誤；`26` 表示讀取上傳檔案失敗；`2` 表示參數錯誤。

## 專案結構

- `mycurl.py`：命令列程式
- `tests/test_mycurl.py`：本機 HTTP 測試

執行測試：`python -m unittest discover -s tests -v`。
