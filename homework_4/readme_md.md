# Git & GitHub 分支、合併與 Fork / Pull Request 操作說明書

本文件說明如何透過 Git 指令與 GitHub 操作，完成**分支建立**、**分支合併**、**Fork 專案**以及**跨專案提交 Pull Request (PR)** 的完整過程。

此流程為軟體開發中最常見的 **Forking Workflow（Fork 工作流 / 跨團隊協作流程）**，並結合了 **Git Flow** 中的分支命名策略（如 `main` 與 `develop`）。

---

## 網址與專案關係說明

| 項目 | 連結 |
| :--- | :--- |
| **母專案（Upstream）** | https://github.com/over-over-STEAK/parent-project |
| **母專案的分支** | https://github.com/over-over-STEAK/parent-project/tree/developGitBranch |
| **別人 fork 的分支** | https://github.com/over-over-STEAK/git-examples |

*註：若開啟鏈結顯示 404 或「沒東西」，代表該分支（例如 `developGitBranch`）尚未建立並推送到遠端，請先照下方步驟 2 執行推送即可！*

---

## 操作步驟解說

### 1. Fork 母專案（建立子專案）
**動作目標**：將母專案複製一份到自己的 GitHub 帳號下（成為子專案）。

* **GitHub 介面操作**：
  1. 開啟母專案網址 `https://github.com/over-over-STEAK/parent-project`。
  2. 點選頁面右上角的 **`Fork`** 按鈕。
  3. 選擇你的目標帳號進行複製，完成後即生成個人專案。

* **本地端 Git 設定**：
  ```bash
  # 將你的 Fork 子專案 Clone 到本地電腦
  git clone https://github.com/over-over-STEAK/git-examples.git
  cd git-examples

  # 設定母專案為遠端上游 (upstream)，方便日後同步最新程式碼
  git remote add upstream https://github.com/over-over-STEAK/parent-project.git
  ```

---

### 2. 建立分支 (Branching)
**動作目標**：在本地建立並切換至新分支 `developGitBranch`，並推送到遠端倉庫。

* **Git 本地指令操作**：
  ```bash
  # 建立並切換到新分支 developGitBranch
  git checkout -b developGitBranch

  # 在該分支上進行檔案修改或開發工作
  echo "Add new feature" >> README.md
  git add README.md
  git commit -m "feat: 新增開發功能與說明"

  # 將新分支推送到你的遠端專案 (origin)
  git push -u origin developGitBranch
  ```

---

### 3. 提出 Pull Request (PR)
**動作目標**：請求將子專案的 `developGitBranch` 分支變更，合併回母專案的 `main` 或開發分支。

* **GitHub 介面操作**：
  1. 進入你的 Fork 子專案。
  2. 切換分支至 `developGitBranch`，點擊 **Compare & pull request**。
  3. 設定比較方向：
     * **base repository**: `over-over-STEAK/parent-project` (base: `main`)
     * **head repository**: `over-over-STEAK/git-examples` (compare: `developGitBranch`)
  4. 填寫 PR 的標題與變更說明後，點選 **Create pull request** 提交。

---

### 4. 合併分支 (Merging)
**動作目標**：母專案管理者審核通過後，將 PR 合併進母專案的主分支。

* **GitHub 介面操作（母專案管理者）**：
  1. 開啟母專案的 **Pull requests** 頁面並點入該 PR。
  2. 確認 Code Review 無誤後，點擊 **Merge pull request**（或選擇 **Squash and merge** / **Rebase and merge**）。
  3. 點選 **Confirm merge** 完成合併。

* **（選用）本地端指令合併流程**：
  ```bash
  # 切換到主分支
  git checkout main

  # 將開發分支合併進 main 分支
  git merge developGitBranch

  # 推送更新後的 main 到遠端倉庫
  git push origin main
  ```

---

## 工作流說明 (Git Workflow)

1. **Forking Workflow**：
   * **適用場景**：開源專案（Open Source）或跨團隊/外部廠商協作。
   * **核心特點**：開發者不需要母專案的直接寫入權限 (Write Access)。每位開發者擁有獨立的 Fork 子專案，在自己的倉庫完成開發後，統一以 Pull Request 形式請求母專案管理者審核併入。

2. **Git Flow (分支管理概念)**：
   * 使用特定的分支名稱（如 `developGitBranch`）專門進行新功能開發，避免直接修改穩定運作的 `main` 主分支，實現功能隔離與安全發布。