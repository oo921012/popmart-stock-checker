# Pop Mart 庫存偵測器 🛒

自動偵測 Pop Mart 商品是否有貨，有貨時立即寄 Email 通知你。

**目標商品：** Angry Molly × Crocs "Angry Cheese" Co-branded Figurine

---

## 設定步驟

### 步驟 1 — Fork 這個 Repository

點右上角 **Fork**，把這個 repo 複製到你自己的 GitHub 帳號。

---

### 步驟 2 — 取得 Gmail App 密碼

> 需要使用 App 密碼，不能直接用你的 Gmail 登入密碼。

1. 前往 [Google 帳戶安全性](https://myaccount.google.com/security)
2. 確認已開啟「兩步驟驗證」
3. 搜尋「應用程式密碼」→ 建立新的，名稱填 `popmart`
4. 複製產生的 16 位密碼（格式像 `xxxx xxxx xxxx xxxx`）

---

### 步驟 3 — 在 GitHub 設定 Secrets

在你 fork 的 repo 頁面：

**Settings → Secrets and variables → Actions → New repository secret**

新增以下三個 secret：

| 名稱 | 值 |
|------|-----|
| `GMAIL_USER` | 你的 Gmail 地址（例如 `yourname@gmail.com`） |
| `GMAIL_APP_PASSWORD` | 步驟 2 取得的 16 位應用程式密碼 |
| `NOTIFY_EMAIL` | 要收到通知的 Email（可以和上面一樣） |

---

### 步驟 4 — 啟用 Actions

1. 點 repo 頁面的 **Actions** 分頁
2. 點「I understand my workflows, go ahead and enable them」
3. 完成！GitHub 會每 30 分鐘自動執行一次

---

### 步驟 5 — 手動測試

1. Actions → **Pop Mart 庫存偵測** → **Run workflow**
2. 看執行結果是否正常
3. 如果有貨，你的信箱應該會收到通知信

---

## 常見問題

**Q：多久偵測一次？**
A：預設每 30 分鐘。如要改頻率，修改 `.github/workflows/check_stock.yml` 裡的 `cron` 表達式。

**Q：GitHub Actions 要付費嗎？**
A：免費帳號每月有 2000 分鐘，每次執行約 1 分鐘，30 分鐘偵測一次大概用 1440 分鐘/月，剛好在免費額度內。

**Q：收不到信怎麼辦？**
A：確認 App 密碼正確、Gmail 有開啟兩步驟驗證、Secrets 名稱拼寫正確。

---

## 檔案結構

```
├── check_stock.py                  # 主要偵測腳本
├── .github/
│   └── workflows/
│       └── check_stock.yml         # GitHub Actions 排程設定
└── README.md
```
