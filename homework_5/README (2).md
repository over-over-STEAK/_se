# Docker 微服務留言展示系統

學校：________　系級：________　學號：________　姓名：________

## 1. 作業目標

學習 Docker 的映像檔、容器、網路、Volume 與 Compose，建立可透過網頁操作的四容器系統。開發環境選用 Node.js 與 Python，沒有使用 Rust。資料庫使用 PostgreSQL。

本文件提供操作說明與學習重點；「個人操作紀錄」請在自己電腦實際執行後填寫，勿將預期結果當成實測結果。

## 2. 系統架構與分工

| 服務 | 技術 | 責任 | 容器內埠 |
|---|---|---|---|
| nginx | nginx:1.28-alpine | 靜態網頁、反向代理 | 80 |
| node-api | Node.js 22、Express、pg | 新增與讀取留言 | 3000 |
| python-api | Python 3.12、FastAPI、psycopg | 統計留言數量 | 8000 |
| db | postgres:16-alpine | 保存留言及建立時間 | 5432 |

對外展示時，訪客開啟 Cloudflare 產生的 HTTPS 公開網址，請求經由本機 cloudflared 轉送到 Nginx。
`/` 提供前端；`/api/node/` 代理至 Node.js；`/api/python/` 代理至 Python。
兩個 API 透過 Compose 網路中的主機名稱 `db` 連線至資料庫。
本機只開放 Nginx 的 8080 埠，綁定 127.0.0.1；資料庫沒有對外開埠。

這是教學用途的服務拆分，兩個 API 共用資料庫，以便展示跨語言讀寫。
系統未包含使用者登入。公開隧道提供訪客端 HTTPS，本機 cloudflared 至 Nginx 使用 HTTP。
cloudflared 在 Windows 主機上執行，不增加 Docker 服務，因此專案仍是四個容器。Quick Tunnel 適合臨時展示，不是長期上線部署。

## 3. 專案檔案

| 路徑 | 用途 |
|---|---|
| docker-compose.yml | 定義四個服務、健康檢查、相依關係、Volume |
| node-api/Dockerfile | 建置 Node.js 執行環境 |
| node-api/server.js | 留言 API 與輸入檢查 |
| node-api/package.json | Node.js 套件版本 |
| python-api/Dockerfile | 建置 Python 執行環境 |
| python-api/app.py | 統計 API |
| python-api/requirements.txt | Python 套件版本 |
| nginx/default.conf | 網頁與反向代理設定 |
| db/init.sql | 建表與一筆初始留言 |
| web/ | HTML、CSS、JavaScript 前端 |
| tests/verify.py | 透過 Nginx 進行 API 整合驗證 |
| .env.example | 可選的本機資料庫密碼設定 |

Dockerfile 放在兩個服務目錄內，Compose 的 `build` 會自動使用各目錄的 Dockerfile。
Nginx 與 PostgreSQL 使用官方映像檔，因此不必另外寫 Dockerfile。

## 4. Windows 啟動步驟

1. 安裝 Docker Desktop：[https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
2. 依安裝提示啟用 WSL 2 等需求，必要時重新開機。啟動 Docker Desktop，使用 Linux containers。
3. 解壓縮專案，以 VS Code 開啟 `docker-microservices` 資料夾。
4. 開啟終端機，確認目前目錄內有 `docker-compose.yml`。

```powershell
docker --version
docker compose version
docker info
docker compose config
docker compose up -d --build --wait
docker compose ps
```

第一次需要下載映像檔與套件，請保持網路連線。`--wait` 會等待服務啟動且健康。
若 Compose 不支援 `--wait`，請更新 Docker Desktop，或執行 `docker compose up -d --build` 後用 `docker compose ps` 確認狀態。

先在自己的瀏覽器開啟 [http://localhost:8080](http://localhost:8080)，確認本機系統正常，再依下一節產生公開網址。

正常情況下可以看到初始留言、Node.js 與 Python 健康狀態，以及留言總數。
輸入新留言後，留言清單與統計數量應一起更新。

預設示範密碼為 `demo_local_only`。如需自訂，第一次啟動前將 `.env.example` 複製為 `.env`，修改 `DB_PASSWORD`。已有 Volume 時，單純修改環境變數不會修改資料庫內既有密碼。

## 5. 公開網站：Cloudflare Quick Tunnel

本機服務啟動後，使用 Cloudflare Quick Tunnel 取得公開 HTTPS 網址。此方式不需 Cloudflare 帳號或自備網域。

### 5.1 下載工具

開啟 [Cloudflare 官方下載頁](https://developers.cloudflare.com/tunnel/downloads/)，下載符合 Windows 架構的執行檔。一般 Intel / AMD 64 位元電腦選擇 Windows amd64 版本。

將執行檔重新命名為 `cloudflared.exe`，放在包含 `docker-compose.yml` 的專案資料夾。請確認不是 `cloudflared.exe.exe`。

### 5.2 建立公開隧道

在該資料夾開啟 PowerShell，執行：

```powershell
.\cloudflared.exe --version
.\cloudflared.exe tunnel --url http://localhost:8080
```

終端機會輸出一個以 `https://` 開頭、以 `.trycloudflare.com` 結尾的網址。請複製終端機實際產生的網址，分享給老師。

//**本次公開展示網址：待啟動隧道後貼上**

公開網址會把網頁及 `/api/node/`、`/api/python/` 請求一起轉送到 Nginx。前端使用相對 API 路徑，不需要把程式內的 URL 改成公開網域，也不需修改 Compose 的 `127.0.0.1:8080:80`。

### 5.3 外部連線測試與停止方式

1. 保持電腦開機、連網，且不要進入休眠。
2. 保持 Docker Desktop 與執行 cloudflared 的終端機運行。
3. 手機關閉 Wi-Fi，使用行動網路開啟實際公開網址。
4. 測試新增留言，確認清單與統計數量更新。
5. 截圖公開網址與操作結果，記錄測試時間。

任何拿到公開網址的人都可以讀取及新增留言。展示時請使用測試資料。

在隧道終端機按 `Ctrl+C` 可停止公開存取；Docker 容器仍會運行。重新建立 Quick Tunnel 時，網址會改變，舊網址不能繼續使用。老師若稍後才查看，必須保持隧道運行，並提供仍有效的網址。Quick Tunnel 沒有上線時間保證。

## 6. Docker 學習重點

| 名詞 | 我的理解 |
|---|---|
| Image（映像檔） | 應用程式與執行環境的模板；Dockerfile 用來描述建置方式 |
| Container（容器） | 由映像檔啟動的執行個體，可以停止、刪除及重建 |
| Dockerfile | FROM 選基底，WORKDIR 設目錄，COPY 複製，RUN 安裝，CMD 指定啟動命令 |
| Compose | 使用 YAML 一次定義及管理多個服務 |
| Port mapping | 127.0.0.1:8080:80 將本機 8080 連到 Nginx 容器 80 |
| Volume | 將資料獨立於容器保存，重建容器仍保留資料 |
| Bind mount | 把本機網頁、設定、初始化 SQL 掛入容器，本專案使用唯讀掛載 |
| Service DNS | 容器用服務名稱找彼此，不能把 localhost 當作另一個容器 |
| Healthcheck | 執行檢查來判定服務是否可用，而非只看程序是否啟動 |
| Reverse proxy | 瀏覽器只存取 Nginx，由它將不同 URL 轉交給不同後端 |

`EXPOSE` 只是描述容器使用的埠；真正對主機開放埠的是 Compose 的 `ports`。
Compose 自動建立本專案的預設網路。API 等待資料庫健康，Nginx 等待兩個 API 健康。
這個啟動順序不代表執行期間會自動修復所有故障；資料庫斷線時 API 會回應 503。

Nginx 的 `proxy_pass http://node-api:3000/;` 有結尾斜線，會將 `/api/node/` 前綴替換為 `/`，因此外部 `/api/node/messages` 會到後端 `/messages`。

## 7. 常用操作記錄

```powershell
# 查看服務狀態
docker compose ps
# 查看最近 100 行日誌
docker compose logs --tail=100
# 持續查看 Node.js 日誌；Ctrl+C 只結束日誌追蹤
docker compose logs -f node-api
# 修改程式後重新建置及啟動
docker compose up -d --build --wait
# 暫停與恢復
docker compose stop
docker compose start
# 停止並移除容器及專案網路，保留資料 Volume
docker compose down
# 檢視 Volume（實際名稱通常包含專案目錄前綴）
docker volume ls
# 直接查詢資料庫
docker compose exec db psql -U demo -d demo -c "SELECT * FROM messages ORDER BY id DESC;"
```

## 8. API 驗證

| 方法 | 路徑 | 預期結果 |
|---|---|---|
| GET | /api/node/health | Node.js 與資料庫健康 JSON |
| GET | /api/node/messages | 最新 100 筆留言陣列 |
| POST | /api/node/messages | 新增留言，HTTP 201 |
| GET | /api/python/health | Python 與資料庫健康 JSON |
| GET | /api/python/stats | total_messages 與 latest_message_at |

以下為本機 PowerShell 驗證範例（程式碼區塊內使用純網址，不要加入 Markdown 連結語法）：

```powershell
Invoke-RestMethod http://localhost:8080/api/node/health
Invoke-RestMethod http://localhost:8080/api/python/health
Invoke-RestMethod http://localhost:8080/api/node/messages -Method Post -ContentType 'application/json' -Body '{"content":"Docker test message"}'
Invoke-RestMethod http://localhost:8080/api/node/messages
Invoke-RestMethod http://localhost:8080/api/python/stats
```

若電腦已安裝 Python，執行完整驗證：

```powershell
py tests/verify.py
```

macOS / Linux 可使用 `python3 tests/verify.py`。若主機沒有 Python，可使用現成的 Python 容器執行：

```powershell
docker compose cp tests/verify.py python-api:/tmp/verify.py
docker compose exec python-api python /tmp/verify.py http://nginx
```

驗證會檢查網頁、健康狀態、新增與讀取留言、跨服務統計，以及空白、超長、錯誤型別輸入。
測試會保留一筆帶有 `Docker verification` 前綴的留言，方便查核；每次執行會再新增一筆。
請避免在測試同時大量新增留言，因為清單僅保留顯示最新 100 筆。

### 從公開網址驗證 API

將下列字串改成終端機實際產生的網址，再執行；不要使用範例網域直接測試。

```powershell
$publicUrl = "https://YOUR-ACTUAL-HOST.trycloudflare.com"
Invoke-RestMethod "$publicUrl/api/node/health"
Invoke-RestMethod "$publicUrl/api/python/health"
Invoke-RestMethod "$publicUrl/api/node/messages"
Invoke-RestMethod "$publicUrl/api/python/stats"
py tests/verify.py $publicUrl
```

最後一行需要主機安裝 Python，會新增一筆測試留言；前四行只讀取狀態及資料。

## 9. 資料持久化測試

1. 在網頁新增獨特留言，例如「持久化測試 2026-10-16」。
2. 記錄其 ID，執行 `docker compose down`。
3. 執行 `docker compose up -d --wait`。
4. 回到網頁，確認相同 ID 與留言仍存在，截圖。

`pg_data` 掛載至 PostgreSQL 16 的 `/var/lib/postgresql/data`。
`init.sql` 只會在空資料目錄初始化時執行；修改 SQL 後重啟不會自動重新執行。

只有要清空所有示範資料、重新初始化時才使用以下指令：

```powershell
# 注意：-v 會永久刪除本專案資料庫 Volume 和所有留言！
docker compose down -v
docker compose up -d --build --wait
```

## 10. 常見問題與處理

| 問題 | 處理方式 |
|---|---|
| 找不到 docker 指令 | 安裝 Docker Desktop，重新開啟終端機 |
| 無法連線 Docker daemon | 啟動 Docker Desktop，等待引擎完成啟動 |
| no configuration file provided | 切換到包含 docker-compose.yml 的目錄 |
| 8080 已被使用 | 將 ports 改成 127.0.0.1:8081:80，重啟並改用 8081 網址；驗證腳本也指定新網址 |
| 找不到 cloudflared.exe | 確認檔案放在目前目錄，PowerShell 指令以 `.\cloudflared.exe` 開頭 |
| 公開網址無法連線 | 先確認本機 8080 可開啟，再檢查隧道是否仍運行、電腦是否休眠、網址是否為最新產生的網址 |
| 網頁回應 502 | 檢查 `docker compose ps` 和 API 日誌；API 重建導致位址改變時可 `docker compose restart nginx` |
| API 回應 503 | 查看 db 與 API 日誌、健康狀態、環境變數與資料庫密碼 |
| 改了 init.sql 沒生效 | 既有 Volume 不會再初始化；要保留資料時使用 SQL 更新，不要直接刪 Volume |
| 修改 Python / Node 程式未生效 | API 程式複製在映像檔中，需要 `docker compose up -d --build --wait` |
| 網頁沒有更新 | 重新整理或強制重新整理；web 目錄使用掛載，不需重建 API |
| 映像檔或套件下載失敗 | 檢查網路、代理設定及錯誤訊息，再執行建置 |

## 11. 檢查狀態與個人操作紀錄

專案製作環境未安裝 Docker，無法執行映像檔建置、Compose config、容器啟動與真實 API 整合驗證。
已進行 Python / JavaScript 語法檢查、YAML 解析及服務結構檢查；這些靜態檢查不能取代實際 Docker 執行。
公開隧道尚未在使用者電腦啟動，公開網址與外部存取也尚未實測。
套件直接版本有固定，但未提供完整的傳遞套件鎖檔，也未固定基底映像 digest。

以下由本人操作後填寫：

| 項目 | 日期／實際結果／截圖檔名 |
|---|---|
| 作業系統與 Docker / Compose 版本 | 待填 |
| docker compose config 成功 | 待實測 |
| 建置映像及四個服務 healthy | 待實測 |
| 網頁新增與讀取留言 | 待實測 |
| Python 統計隨新增而更新 | 待實測 |
| tests/verify.py 全部 PASS | 待實測 |
| 移除容器再啟動後資料仍存在 | 待實測 |
| Cloudflare 公開網址與測試時間 | 待填 |
| 手機行動網路開啟網站及新增留言 | 待實測 |
| 公開網址 API 驗證 | 待實測 |
| 遇到的問題與修正方法 | 待填 |

學習心得建議自行回答：Dockerfile 與 Compose 有什麼差別？為什麼容器內資料庫主機寫 `db`？如果不使用 Volume 會怎樣？Nginx 如何將 URL 分派給不同服務？

## 12. 繳交清單

- 完整專案資料夾（包含兩個 Dockerfile 與 docker-compose.yml）。
- README.md：補上個人資料、真實操作紀錄與心得。
- 四容器健康狀態截圖：`docker compose ps`。
- 網頁新增留言與統計結果截圖。
- API 驗證通過截圖及資料持久化前後截圖。
- 實際公開網址、外部存取測試截圖與可供查看的時間。

## 13. 官方參考資料

- Docker Desktop 安裝：[https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
- Dockerfile：[https://docs.docker.com/reference/dockerfile/](https://docs.docker.com/reference/dockerfile/)
- Compose 啟動順序與健康檢查：[https://docs.docker.com/compose/how-tos/startup-order/](https://docs.docker.com/compose/how-tos/startup-order/)
- PostgreSQL 官方映像與初始化：[https://hub.docker.com/_/postgres](https://hub.docker.com/_/postgres)
- Nginx proxy_pass：[https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)

- Cloudflare 下載：[https://developers.cloudflare.com/tunnel/downloads/](https://developers.cloudflare.com/tunnel/downloads/)
- Cloudflare Quick Tunnel：[https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
