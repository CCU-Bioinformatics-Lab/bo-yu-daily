# longbulksim 決策紀錄

| 日期 | 決策 | 理由 | 證據／可逆性 |
|---|---|---|---|
| 2026-10-25 | 程式放 repo 根目錄 `longbulksim/`，獨立 package | 使用者選擇。和 `tools/` 一次性腳本分開，可單獨測試 | 可逆 |
| 2026-10-25 | v0.1 只做 molecule 層計數，不產生 BAM | 使用者選擇。PhyClone 與 HP 擴充只需要計數、HP 拆分與 pair 共現 | `plan.md` §5.8.2 規則 4–6 已滿足；L2-R 之後再加 |
| 2026-10-25 | 樹由手寫 YAML spec 提供，用事件重播產生 genome | 使用者選擇。先證明重播等於兩棵已驗證合理性的手寫樹 | `tests/test_model.py` golden test |
| 2026-10-25 | `lost` 定義為「在本 clone 或祖先產生、但本 clone 已不帶」 | 和 `tools/draw_hp_truth_tree.py` 的 `LOST` 一致（C4 也算遺失 s10） | 第一版用「相對 parent」定義，golden test 失敗後改正 |
| 2026-10-25 | read span 用實測分位數，不用參數分布 | 跨越 read 數 vs 間距要對上 HCC1395 實測（取代「每對固定 80 條」） | 預測 48／41／19／1.5／0 對實測 52／44／21／2／0 |
| 2026-10-25 | HP tag 以 read 為單位抽（機率 0.859），不逐位點抽 | 真實 haplotag 對整條 read 標記；同一 read 上兩個 SNV 的 tag 狀態必須一致 | 0.859 = HCC1395 alt read 實測 tagged 比例 |
| 2026-10-25 | `data_hp.tsv` 的 `snv_hp` 用觀測多數決，沒有 tagged alt read 時寫 `.` | 方法輸入不得含真值（`plan.md` §5.8.2 規則 7） | `phyclone_hp.py` 會把 `.` 當 HP2；只影響 alt = 0 的位點 |
| 2026-10-25 | 預設 SNV 密度 12.9／Mb | HCC1395 全基因組實測（37,330 SNV／2.9 Gb）。密度只是 spec 的 segment 長度，可改 | 在此密度下壓力測試樹只有 105 列 pair；要測 pair 特徵需另設高密度情境 |
| 2026-10-25 | 不模擬 phasing 誤差 | 目前目標是真值樹合理性與模擬器本體；phasing 噪音延後 | 未決問題見 memory `hp-extension-open-questions` 第 5 項（germline vs somatic haplotag） |
| 2026-10-25 | 隨機樹直接用 TRACERx 421 單區域樹當藍圖，不用參數式 prior | 每個樹都是真實腫瘤的單區域樹，合理性不需要另外論證 | 只有 NSCLC；可再加其他 cohort |
| 2026-10-25 | CCF 先讓祖先 ≥ 子代總和，再從 root 往下封頂 1 | TRACERx 區域 CCF 常有子代 > 親代；子代 cluster 較大，估計較穩 | 不 merge 時 CCF 中位 0.59（原始 0.58） |
| 2026-10-25 | CCF 與 parent 相差 < 0.05 的 clone 併入 parent | 單一 bulk 樣本分不開；保留會讓評分不公平 | clone 數中位 5 → 3；`merge_gap` 可改 |
| 2026-10-25 | 移除沒有任何 clone 帶的 SNV | 真實資料不會有觀測不到的突變；v1 因此遺失偏高 | 每個 spec 中位移除 1 個 |
| 2026-10-25 | subclonal 事件指派給整個 tumour 樹的隨機 clone，不在區域內就丟掉 | 多區域事件不全屬於這個區域；v2 因此事件過多 | 修正後遺失中位 0、Q90 2.0%（TRACERx 0、1.4%），沒有調參數 |
| 2026-10-25 | CN 目錄改成「每個 segment 的 trunk 狀態 + 最多一個 subclonal 改變」，取代 4 類 ≥ 1 Mb 事件 | 舊目錄沒有 clonal gain 和非 LOH deletion；新表示法一次涵蓋 WGD、clonal cnLOH、3+1 → 2+1 等 | 資料來自 TRACERx `scna_region`；不混用 PCAWG 樣本 |
| 2026-10-25 | trunk 方向：只有一個狀態是 ploidy-neutral 時取它，否則取多數狀態 | PCAWG Battenberg 看不出祖先狀態；TRACERx 有 ploidy 標記 | 65% 用多數規則；遺失率與 ploidy 規則相近（2.7% vs 3.2%） |
| 2026-10-25 | gain／loss 選隨機 copy；SNV 在當下所有 copy 中均勻選一個 | 讓 multiplicity 與遺失由順序決定 | 2:1 early 0.24、2:0 0.42，都在 PCAWG IQR 內 |
| 2026-10-25 | 遺失率高於 TRACERx 下限時不調參數 | TRACERx 是嚴格下限；論文估計更高 | 中位 0.5%、Q90 3.1%；照實記錄 |
