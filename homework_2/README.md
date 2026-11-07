# Campus Kinmen｜Cloudflare 精簡版

非官方校務系統教學作品；使用模擬資料。保留登入、選課、課表匯出、成績與公告管理。

## 公開部署
需 Node.js 22 以上及 Cloudflare 帳號。在此資料夾開啟終端機，依序執行：

```powershell
npm install
npx wrangler login
npx wrangler d1 create campus-kinmen-db
```

開啟 wrangler.jsonc，把 REPLACE_WITH_YOUR_DATABASE_ID 換成建立資料庫時取得的 UUID。保留 binding 為 DB。若自動設定提示出現，選 No 並手動填寫；使用專用空白資料庫，不要混用其他作業的資料庫。

```powershell
npm run db:remote
npm run deploy
npx wrangler secret put ADMIN_PASSWORD
```

初始化詢問時輸入 y。deploy 完成後顯示的 workers.dev 網址即為公開網址。ADMIN_PASSWORD 請設定至少 12 字元；不要使用 admin123。設定 secret 後會發布更新。

| 身分 | 帳號 | 密碼 |
| --- | --- | --- |
| 示範學生 | student | student123 |
| 第二位學生 | student2 | student123 |
| 管理員 | admin | 自訂 ADMIN_PASSWORD |

公開學生帳號共用資料，訪客的選課變動會互相影響。請勿放真實個資。

## 本機與更新
執行 npm run db:local，再執行 npm run dev。本機與雲端資料不同。測試本機管理員可建立 .dev.vars，寫入 ADMIN_PASSWORD="至少12字元的自訂密碼"。
修改網站後執行 npm run deploy，原 D1 資料保留。migration 只執行一次，不要修改已套用的 SQL。

## 檔案
worker.js 為後端；static/ 為網頁；migrations/ 為資料庫；wrangler.jsonc 為部署設定。
本精簡版移除舊 Python 程式、舊測試、冗長說明及套件鎖定檔。Wrangler 固定為 4.158.0，npm install 會重新產生 package-lock.json。網站功能檔案與資料庫 SQL 保持原樣。

執行 npm run check 可檢查 JavaScript 語法。原版已通過資料庫限制測試、Wrangler dry-run 及本機 D1 初始化；尚未完成瀏覽器與遠端部署驗證。

作業請補上學號、姓名、系級、GitHub、公開網址及操作截圖。由 ChatGPT 協助實作。
