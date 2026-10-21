# GIT 分支專案

| 項目 | 連結 |
| :--- | :--- |
| **母專案** | https://github.com/over-over-STEAK/parent-project |
| **母專案的分支** | https://github.com/over-over-STEAK/parent-project/tree/developGitBranch |
| **別人 fork 的分支** | https://github.com/over-over-STEAK/git-examples |

---

## 📌 要點一：母專案用 `git checkout -b` 開分支後 merge

在母專案的本地副本（clone 下來的資料夾）操作：

### 1. 複製專案並進入資料夾
```bash
git clone https://github.com/over-over-STEAK/parent-project.git
cd parent-project
```

### 2. 建立並切換至新功能分支
```bash
# 建立名為 developGitBranch 的分支並立刻切換過去
git checkout -b developGitBranch
```

### 3. 修改內容並提交變更
```bash
# 將變更加入暫存區
git add .

# 提交變更並附帶說明訊息
git commit -m "feat: 新增分支功能與說明文件"
```

### 4. 將分支推送到遠端 GitHub
```bash
git push -u origin developGitBranch
```

### 5. 合併分支回主分支 (Merge)
當分支上的功能開發完成後，切換回主分支並完成合併：
```bash
# 切換回主分支
git checkout main

# 將 developGitBranch 的內容合併進 main
git merge developGitBranch

# 將更新後的 main 推送到 GitHub
git push origin main
```

---

## 📌 要點二：Fork 專案與提交 Pull Request (PR)

當你想參與別人的專案開發或寫練習作業時：

1. **Fork 母專案**：在 GitHub 上點選母專案右上角的 **Fork** 按鈕，複製一份到自己的帳號。
2. **Clone 到本地**：複製你個人帳號底下的專案網址並進行修改。
3. **發送 Pull Request**：修改並推送回個人遠端儲存庫後，回到 GitHub 點擊 **New Pull Request** 請求母專案管理員採納你的變更。