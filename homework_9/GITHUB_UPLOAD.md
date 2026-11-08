# 重新上傳 GitHub

此壓縮檔解壓縮後，README.md、package.json、worker.js 與 .github/ 應在同一層。

## 更新原本的 homework_7
1. 先備份原資料夾。
2. 將本包內容複製到原 homework_7，覆蓋同名檔案，保留原本 .git 資料夾。
3. 不要覆蓋自己的 .dev.vars 或 .env；本包沒有這些檔案。
4. 在 homework_7 根目錄開啟終端機，執行：

```bash
git remote -v
git status --short
```

確認 origin 指向你要更新的儲存庫，再執行：

```bash
git add .
git diff --cached --stat
git diff --cached --name-only
```

檢查待提交清單不含 node_modules、.wrangler、.env、.dev.vars、資料庫或個人密碼。若它們之前已被追蹤，.gitignore 不會自動取消追蹤，需先移出 Git 索引再提交，請先確認清單。

```bash
git commit -m "整理校務系統與三層自動測試"
git push
```

若沒有 origin、沒有 upstream 或發生衝突，先查看訊息，不要使用 force push。

## 使用 GitHub 網頁上傳

進入目標儲存庫 → Add file → Upload files。上傳解壓縮後的原始碼與資料夾，不要只上傳 ZIP，也不要再多包一層 campus-portal。相同路徑檔案會更新；舊版多餘檔案不會自動刪除。請確認 .github/workflows/tests.yml 和 .gitignore 有上傳（隱藏檔可能未被拖入）。較建議使用前面的 Git 指令，能保留資料夾結構。

上傳後檢查首頁顯示 README，點 Actions 查看測試結果。GitHub push 本身不會更新 Cloudflare 網站；網站更新另執行 npm run deploy。
