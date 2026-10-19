<!-- daily-log:generated — 這個檔由 render.py 產生，手改會被覆蓋 -->
# 每日工作日誌

## 怎麼看

日誌是 **HTML**（排版完整，含配色、圖表、折疊區）。
⚠️ **GitHub 網頁點 `.html` 只會顯示原始碼**，要先把檔案取下來：

```bash
git clone https://github.com/CCU-Bioinformatics-Lab/bo-yu-daily.git
cd bo-yu-daily && xdg-open index.html      # macOS 用 open，Windows 用 start
```

或按 **Code → Download ZIP**，解壓後點 `index.html`。

下面的索引供快速定位哪一天發生什麼；點進去要用上面的方式開。

> **給 agent**：要跨日彙整（「掃過這個月的紀錄，整理出進度」）請直接讀
> `.data/<日期>.json` —— 那是事實來源，欄位有語意、不必剖 HTML。

## 檔案結構

| 路徑 | 說明 |
|---|---|
| `.data/<YYYY-MM-DD>.json` | **事實來源**。要改內容改這裡再重新渲染 |
| `daily/<YYYY-MM-DD>.html` | 單日日誌（產物，不要手改） |
| `index.html` | 導覽首頁（產物） |
| `README.md` | 本檔（產物，由 `render.py` 產生，不要手改） |
| `daily/figures/<YYYY-MM-DD>/` | 當天的圖 |
| `assets/style.css` | 共用樣式，改這裡會影響所有 HTML 日誌 |

## 日誌

### 2026-10

- **[2026-10-19](daily/2026-10-19.html)** —— 10/21 簡報從 13 頁的盤點式報告改成 10 頁、只有一個主問題；大綱過了兩方三輪審查才動手重做，已發布成 Version 9
