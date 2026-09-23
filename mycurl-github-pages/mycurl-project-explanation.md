# 習題 1：mycurl — 類似 curl 的 HTTP 客戶端

## 一、專案目的

本專案使用 **Python 標準函式庫**實作一個簡易的 curl 風格命令列程式。使用者在終端機輸入網址與選項後，程式會發送 HTTP 請求，取得伺服器回應，並將內容顯示在終端機或儲存成檔案。透過實作與測試，可認識 URL、HTTP 方法、Header、狀態碼、重新導向及資料傳輸流程。

另外製作了靜態展示網站，介紹功能、運作原理、使用範例及原始碼。**展示網站不會代替 Python 程式發送任意 HTTP 請求**；真正的請求在使用者電腦執行 `mycurl.py` 時發生。

## 二、專案檔案

```text
mycurl-github-pages/
├── index.html               # GitHub Pages 展示頁面
├── README.md                # 簡易操作與部署說明
├── src/
│   └── mycurl.py            # HTTP 客戶端主程式
└── tests/
    └── test_mycurl.py      # 使用本機 HTTP 伺服器的測試
```

## 三、主要功能

| 選項 | 功能 | 範例 |
|---|---|---|
| `-X` | 指定 HTTP 方法 | `-X PUT` |
| `-H` | 加入自訂請求標頭，可重複使用 | `-H 'Accept: application/json'` |
| `-d` | 傳送表單文字，預設使用 POST | `-d 'name=Alice'` |
| `--data-binary` | 以檔案或標準輸入內容作為請求本文 | `--data-binary data.json` |
| `-u` | 加入 Basic Auth 認證標頭 | `-u 'user:password'` |
| `-L` | 追蹤 HTTP 重新導向 | `-L` |
| `-I` | 發送 HEAD 請求，只顯示回應標頭 | `-I` |
| `-i` | 同時顯示回應標頭和本文 | `-i` |
| `-o` | 將回應本文寫入檔案 | `-o page.html` |
| `--progress` | 顯示已下載位元組數 | `--progress` |
| `--max-time` | 設定連線逾時秒數 | `--max-time 10` |
| `-k` | 測試時略過 HTTPS 憑證驗證 | `-k` |

程式支援 `http://` 與 `https://`。預設會驗證 HTTPS 憑證；若沒有指定 `-L`，伺服器回傳 3xx 時會直接顯示該回應。HTTP 4xx 或 5xx 仍屬於「已取得 HTTP 回應」，程式會輸出其內容。

## 四、程式運作流程

1. 使用 `argparse` 解析網址與命令列參數，檢查網址、標頭格式及衝突的選項。
2. 依照使用者的輸入決定 HTTP 方法：沒有資料時預設 GET，有 `-d` 或 `--data-binary` 時預設 POST；也可由 `-X` 明確指定。
3. 將文字資料轉成 UTF-8 位元組；若有 `-u`，將帳號與密碼編碼成 HTTP Basic Auth 標頭。
4. 透過 `urllib.request.Request` 建立請求，由 `urllib.request` 發送；HTTPS 使用 `ssl` 建立加密連線。
5. 取得狀態碼、Header 與回應本文。本文分段讀取，以便下載較大的內容並顯示進度。
6. 依選項將結果輸出到終端機或檔案；若發生連線或檔案錯誤，顯示錯誤並回傳非零結束碼。

一筆 HTTP 交換可以簡化為：

```text
終端機輸入 → 解析 URL 與選項 → 建立 HTTP Request → 伺服器處理
                                            ↓
終端機或檔案 ← 輸出回應內容 ← 讀取 HTTP Response
```

## 五、安裝與執行

需要 Python 3.9 以上，**不需安裝第三方套件**。在包含 `index.html`、`src` 和 `tests` 的資料夾開啟終端機：

```bash
python src/mycurl.py --help
python src/mycurl.py https://example.com
python src/mycurl.py -I https://example.com
python src/mycurl.py -o example.html https://example.com
```

在 Windows 上，如果 `python` 指令無法執行，可改用 `py`。執行 `-o example.html` 後，可在目前資料夾找到下載的檔案。

### 展示網站的本機預覽

在同一個資料夾啟動靜態網站：

```bash
python -m http.server 8000
```

然後在瀏覽器打開 `http://localhost:8000/`。終端機需保持開啟；要停止網站時按 `Ctrl + C`。若直接雙擊 `index.html`，部分瀏覽器可能因本機檔案限制而無法載入原始碼預覽，因此建議使用上述方式。

### 發布到 GitHub Pages

將 `index.html`、`README.md`、`src`、`tests` 上傳到 GitHub repository **根目錄**。在該 repository 的 **Settings → Pages** 選擇 `Deploy from a branch`、`main` 與 `/(root)`。部署完成後，網址通常為 `https://你的帳號.github.io/儲存庫名稱/`。

## 六、測試與結果

在專案根目錄執行：

```bash
python -m unittest discover -s tests -v
```

測試程式會在本機啟動 HTTP 伺服器，不依賴外部網站，檢查：

- GET 請求及 HTTP 錯誤回應。
- `-L` 重新導向與 `-I` HEAD 標頭。
- POST 資料、Basic Auth 與 `-o` 檔案輸出。

本專案的三項測試已執行並通過，終端機顯示 `Ran 3 tests` 與 `OK`。我也使用 `https://example.com` 實際執行 GET、HEAD 與檔案下載指令，分別取得 HTML 內容、`200 OK` 回應標頭，以及下載檔案。

## 七、學習心得

這次實作讓我理解 curl 不只是「下載網頁」：一個 HTTP 客戶端還需要處理不同方法、標頭、請求本文、憑證、重新導向、逾時及輸出方式。以命令列實際觀察回應標頭與狀態碼，比只在瀏覽器開啟網頁更容易看出 HTTP 請求與回應的結構。展示網站則將專案的功能與使用方式整理成易於閱讀的頁面；網站與命令列工具各有不同用途。
