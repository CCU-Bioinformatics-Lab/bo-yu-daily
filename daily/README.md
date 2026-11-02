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
| `<YYYY-MM-DD>.html` | 單日日誌（產物，不要手改） |
| `index.html` | 導覽首頁（產物） |
| `README.md` | 本檔（產物，由 `render.py` 產生，不要手改） |
| `figures/<YYYY-MM-DD>/` | 當天的圖 |
| `assets/style.css` | 共用樣式，改這裡會影響所有 HTML 日誌 |

## 日誌

### 2026-10

- **[2026-10-31](2026-10-31.html)** —— diplosim 補了 5 個機制後，在 HCC1395 t50_n00 上 13 項統計的平均相對差距從 0.497 降到 0.061；但旋鈕鎖住、換成較低 purity 的樣本後，差距升到 0.08–0.50，表示 base_error 與 depth φ 只是在 t50_n00 上湊對
- **[2026-10-30](2026-10-30.html)** —— diplosim v1 寫完並 commit：流程照 CONIPHER，只多 2 個 HP 參數；拿真實 HCC1395 long read 比，14 個統計量只有 5 個落在模擬範圍內，tag 比例、定序誤差和 CN 組成是三個缺口
- **[2026-10-29](2026-10-29.html)** —— longbulksim 凍結在 v0.8，改用 Rust 照 CONIPHER 一步一步重寫成 diplosim，參數已逐條定下 13 條；CLAUDE.md 依兩次會議改成「先列方案、一次一步」的流程，並和 report_rule.md 分工
- **[2026-10-28](2026-10-28.html)** —— 真實 ONT 的 allele 計數比 binomial 分散（s≈140），longbulksim v0.8 加入選用 beta-binomial 雜訊；共現能否分兄弟 clone 取決於 truncal 比例，HCC1395 約 75%，模擬每棵分支樹約 4 列兄弟證據
- **[2026-10-27](2026-10-27.html)** —— HG008 的真實 clone 樹上找得到真值樹 ②–⑦ 六類事件；119 顆單細胞支持主幹與兩個共享分枝，但各 clone 的 private 枝無法證實
- **[2026-10-26](2026-10-26.html)** —— 改良版 PhyClone 在模擬資料上選錯樹，是模型的問題，不是模擬器的 bug；三種削弱 pair 證據的修法都失敗，主因是 PhyClone 原本的 FSCRP prior
- **[2026-10-25](2026-10-25.html)** —— HP 真值樹的 7 類事件在 HG008、TRACERx、PCAWG 都找得到實例，但事件密度與突變遺失偏高，所以原樹改當壓力測試，另設計一棵典型樹
- **[2026-10-24](2026-10-24.html)** —— 公開生成器縮到只剩 SISTEM 能直接餵 PhyClone；不給 HP 資訊時，PhyClone 有 99.8% 把遺失的 SNV 併進低 CCF clone，拓樸也分不出來
- **[2026-10-23](2026-10-23.html)** —— CONIPHER 的公開生成程式能逐 byte 重現 PhyClone 用的 300 份資料，所以 10-28 簡報改講它的生成流程，已做成 7 頁
- **[2026-10-21](2026-10-21.html)** —— PhyClone 公開的模擬程式重跑 100 份全部通過規則檢查，但和作者 benchmark 有兩處不同，long read 版生成器要自己寫
- **[2026-10-20](2026-10-20.html)** —— 5 株 cell line 裡有 3 株的 PCDH 區整區高甲基化，甲基化條碼只剩 H1437、HCC1954 還能評估
- **[2026-10-19](2026-10-19.html)** —— 4 個 subagent 分頭搜尋後確認：還沒有已發表方法把長讀的 haplotype／phase set 放進演化樹模型
