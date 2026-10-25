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
