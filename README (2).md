# 第9週：網站應用部署至 Cloudflare

## 專案名稱：Campus Kinmen 校務系統

以金門校園生活為情境的全端網站課程專案，使用 **Cloudflare Workers + D1** 部署，包含學生入口與管理後台。非金門大學官方系統，所有教師、課程、成績與校務規則皆為模擬資料。

## 作業目標

本作業將校務網站從本機程式部署到 Cloudflare，讓使用者能透過公開網址操作。Cloudflare Workers 負責接收 API 請求與執行後端邏輯，D1 保存課程、選課、成績與公告資料，靜態資源則提供學生與管理員操作介面。

專案資料夾命名為 `homework_9`；資料夾名稱不影響 Cloudflare 上的 Worker 名稱或既有公開網址。

## 線上展示

- [學生入口](https://campus-kinmen.ryan-campus-2026.workers.dev)
- [管理後台](https://campus-kinmen.ryan-campus-2026.workers.dev/admin.html)

| 身分 | 帳號 | 密碼 |
| --- | --- | --- |
| 示範學生 | student | student123 |
| 第二位示範學生 | student2 | student123 |
| 管理員 | admin | 由網站維護者透過 Cloudflare Secret 設定 |

公開示範帳號共用資料，選課變動會影響使用同一帳號的其他訪客。請勿輸入真實個資；管理員密碼不提供於此儲存庫。

## 功能

| 對象 | 功能 |
| --- | --- |
| 學生 | 登入登出、課程搜尋、加退選、週課表、CSV 匯出、成績與加權平均、公告 |
| 管理員 | 總覽統計、學生資料查詢、課程新增編輯刪除、選課名單、成績登錄、公告管理 |
| 資料檢查 | 重複選課、衝堂、名額上限、25 學分上限、成績範圍 |
| 權限保護 | 管理 API 角色檢查、Session Cookie、CSRF 與來源檢查、參數化 SQL |

已有人選課的課程不能刪除或改時段／學分，容量不能低於現有人數。此版尚未提供註冊、學生帳號新增、密碼重設、成績刪除或管理員代選功能。

## 技術架構

瀏覽器 HTML/CSS/JavaScript → Worker HTTP JSON API → Cloudflare D1。

| 部分 | 技術 |
| --- | --- |
| 前端 | HTML、CSS、原生 JavaScript |
| 後端 | JavaScript / Cloudflare Workers |
| 正式資料庫 | Cloudflare D1 |
| 本機測試資料庫 | Node.js 內建 SQLite，僅記憶體儲存 |
| 單元及 API 測試 | node:test、assert、fetch |
| E2E 測試 | Playwright + Headless Chromium |
| 自動測試 | GitHub Actions |

## 專案檔案

| 路徑 | 用途 |
| --- | --- |
| worker.js | 正式後端、登入、Session、學生 API |
| admin-api.js | 管理後台 API |
| validation.js | 共用後端輸入驗證 |
| static/ | 學生與管理員介面 |
| migrations/ | 資料表、示範資料及資料庫限制 |
| wrangler.jsonc | Cloudflare 部署設定 |
| tests/unit/ | 後端單元測試 |
| tests/api/ | HTTP 系統測試 |
| tests/e2e/ | 無頭瀏覽器操作測試 |
| tests/support/ | 隔離測試伺服器與 SQLite 轉接器 |
| playwright.config.mjs | E2E 啟動、報告與瀏覽器設定 |
| .github/workflows/tests.yml | GitHub 自動測試流程 |
| TESTING.md | 測試設計與執行說明 |

## 本機啟動

需要 Node.js 22.13 以上，建議 Node.js 24。在 package.json 所在資料夾執行：

```bash
npm install
npm run db:local
npm run dev
```

開啟終端機提供的網址，通常為 http://localhost:8787 。請勿直接雙擊 index.html。

本機管理員需要自行建立 `.dev.vars`，內容如下，將示意文字換成至少 12 字元的自訂密碼：

```dotenv
ADMIN_PASSWORD="請換成至少12字元的自訂密碼"
```

此檔已由 .gitignore 排除。Cloudflare 遠端 Secret 與本機 .dev.vars 各自獨立。

## 測試

```bash
npm install
npx playwright install chromium
npm test
```

| 指令 | 用途 |
| --- | --- |
| npm run test:unit | 後端單元測試 |
| npm run test:api | HTTP API 系統測試 |
| npm run test:e2e | Playwright 無頭瀏覽器測試 |
| npm run test:e2e:headed | 顯示瀏覽器執行 E2E |
| npm run test:report | 開啟 E2E HTML 報告 |

2026-11-08 於 Windows / Git Bash 執行 `npm test` 的實測結果：**10 項單元、8 項 API、6 項 E2E，共 24 項通過，0 項失敗**。詳見 [TESTING.md](TESTING.md)。

測試使用隔離的本機 HTTP server 與記憶體 SQLite，呼叫正式 Worker handler，不會變更公開網站資料；不包含 Cloudflare TLS、邊緣網路與遠端 D1 的環境驗證。

## 部署到 Cloudflare

### 原網站更新

設定檔已保留本專案的 Worker 名稱與 D1 ID。原維護者在同一帳號更新時：

```bash
npx wrangler login
npm run db:remote
npm run deploy
```

migration 只套用尚未執行的版本，更新不會清空資料。保持同一 Worker 名稱即可保留既有 Secret。

若尚未設定管理員密碼：

```bash
npx wrangler secret put ADMIN_PASSWORD
```

依提示輸入至少 12 字元密碼。不要把密碼寫入 wrangler.jsonc。

### 其他人部署自己的副本

先執行 `npx wrangler d1 create campus-kinmen-db`，將取得的 ID 填入 wrangler.jsonc 的 database_id，並依需要更改 Worker name。保留 binding 為 DB，再執行 db:remote 與 deploy。設定檔中的 D1 UUID 是識別碼，不提供資料庫存取權；仍需要對應 Cloudflare 帳號授權。

## GitHub Actions

將本專案內容放在儲存庫根目錄，.github/ 與 package.json 同層。push 或 pull request 會自動執行三層測試並保存 Playwright 報告。流程不會自動部署 Cloudflare，也不需要正式環境密碼。

## 部署與除錯紀錄

1. 安裝依賴並登入 Cloudflare。
2. 建立 D1 資料庫，把取得的 UUID 寫入 `wrangler.jsonc`。
3. 執行 `npm run db:remote`，套用 `0001_init.sql` 與 `0002_admin.sql`。
4. 執行 `npm run deploy`，取得公開的 `workers.dev` 網址。
5. 透過 Cloudflare Secret 設定管理員密碼。
6. 執行三層測試，修正公告編輯欄位的 label／textarea 關聯後，全部 24 項測試通過。

過程中曾因 `database_id` 仍為佔位文字而出現 Invalid uuid，填入正確 UUID 後完成資料庫初始化。首次開啟公開網址也曾出現 HTTPS 錯誤，因此部署紀錄、程式測試與瀏覽器實際操作需分別確認。

## 學習重點

- 理解前端畫面、後端 API 與資料庫的分工。
- 使用設定檔將 Worker 綁定到 D1，並以 migration 管理資料庫結構。
- 將學生與管理員權限分開，透過後端驗證限制操作。
- 分別使用單元、API 與 E2E 測試驗證資料規則和使用流程。
- 理解 GitHub 儲存原始碼，Cloudflare 執行公開網站；上傳 GitHub 不等於重新部署網站。

## 作業資料

- 第 9 週主題：網站應用部署至 Cloudflare
- 學校：國立金門大學
- 系級：請填寫
- 學號：請填寫
- 姓名：請填寫
- 製作工具：ChatGPT 協助設計、實作、除錯與測試；此版本未使用 opencode / big pickle。

繳交時附上本儲存庫網址、公開網站網址、包含網址列的操作截圖，以及測試結果截圖。
