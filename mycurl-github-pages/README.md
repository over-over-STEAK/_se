# mycurl 作業展示頁

此資料夾可直接部署到 GitHub Pages。`index.html` 是靜態展示網站，`src/mycurl.py` 是可在電腦執行的 HTTP 客戶端，`tests/test_mycurl.py` 是本機測試。

## 在電腦執行

```bash
python src/mycurl.py --help
python src/mycurl.py https://example.com
python -m unittest discover -s tests -v
```

## 放到 GitHub Pages

1. 在 GitHub 建立新的公開 repository，例如 `se-hw1-curl`。
2. 將本資料夾的 `index.html`、`src`、`tests` 和 `README.md` 上傳到 repository **根目錄**。
3. 進入 repository 的 Settings → Pages → Build and deployment，Source 選 Deploy from a branch，Branch 選 main、資料夾選 /(root)，再按 Save。
4. 等待 GitHub Pages 完成部署，網站網址通常是 `https://你的帳號.github.io/se-hw1-curl/`。

GitHub Pages 上的頁面用來展示程式及下載原始碼；真正的 HTTP 請求由 Python 命令列程式在你的電腦上執行。
