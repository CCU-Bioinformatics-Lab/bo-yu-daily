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
| 2026-10-25 | v0.2 加入 `mistag_rate`、`switch_rate_per_mb`、`base_error`，預設 0 | C4 穩健性測試需要（`research/phyclone_research/C4_ROBUSTNESS_PLAN.md`）。取代上面「不模擬 phasing 誤差」 | 錯誤率 0 時不抽亂數，`input/` 與 v0.1 逐位相同 |
| 2026-10-25 | 錯標以整條 read 為單位；switch 依 read 中點決定 | haplotag 對整條 read 標記；同一 read 上的 SNV 必須同一個 tag | 推論：跨 switch 的 read 在 longphase 是依多數 het SNP 決定，中點是近似 |
| 2026-10-25 | base error 是對稱的 ref↔alt 翻轉 | 計畫定義；只有 ref→alt 方向有實測（HCC1395BL 0.40%） | alt→ref 未量測 |
| 2026-10-26 | v0.3 加入選填 `het_map`：tag 由 longphase-s germline 規則決定（覆蓋 ≥ 1 個 het，且只在一個 PS block） | PPC 顯示固定 tag 機率讓位點間 tag 比例太均勻（SD 0.05 vs 0.25） | 規則取自 `HaplotagStrategy.cpp`，沒有擬合參數；PPC 後 SD 0.248、聚集 0.426 vs 0.428。沒有 map 時輸出不變（`ZeroErrorsMatchV01`） |
| 2026-10-26 | 不模擬 haplotag 的 allele 一致比例 ≥ 0.6 規則 | 模擬的 read 在 het SNP 上沒有鹼基錯誤 | 可能是 tagged alt 太少仍差 0.042 vs 0.057 的原因之一 |
| 2026-10-26 | `het_map` 不設成預設 | 隨機樹 spec 的座標是人工的，套上 map 後 alt read 的 tag 比例中位只有 0.68（20 個 spec：0.58–0.74） | 要預設使用，需先讓隨機樹的 segment 座標落在 callable 區域；由使用者決定 |
| 2026-10-26 | v0.4 主要入口改成參數模式 `longbulksim.generate`，輸入參數照 CONIPHER `tx_simulation` | 使用者指出：使用者不會手寫 clones／segments／edges | 手寫 spec 保留為進階用法；`random_tree` 不變 |
| 2026-10-26 | 參數預設值用 TRACERx 421 單區域中位數（merge 後），depth 用 PCAWG 中位 | 使用者選擇。和藍圖模式同一個來源 | 數值與計算方式見 `param_tree.py` docstring |
| 2026-10-26 | CN 比例相對於基準 ploidy 分類（非 WGD 1:1，WGD 2:2），兩組分開取中位 | 57% TRACERx tumour ploidy ≥ 3；用 1:1 當基準會把 WGD 的 2:2 算成 gain（gain 中位會變成 0.58） | ploidy ≥ 3 當作 WGD 是代理定義 |
| 2026-10-26 | 比例由參數決定，具體 CN 狀態從 TRACERx 同類 segment 重抽 | 只給比例就能得到真實的狀態分布（3:1、2:0 等），不用另設參數 | 可逆 |
| 2026-10-26 | `ccf_alpha` 預設 0.5 | subclone CCF 中位：0.5 → 0.44，1.0 → 0.42；TRACERx 0.45 | alpha 對結果影響小 |
| 2026-10-26 | 不提供 `--prop-mutloss` | 遺失由事件順序產生，和藍圖模式一致；CONIPHER 是直接設定 | 實測中位 0.7%、Q90 2.8% |
| 2026-10-26 | `random_tree` 的排邊程式抽成 `add_cn_items`、`build_edges` 供兩種模式共用 | 避免重複 | 重構前後 30 個 spec 的 sha256 相同 |
| 2026-10-26 | v0.5 加入 `caller`（none／clairs／deepsomatic）：用 P(call \| alt, depth) 抽樣，漏掉的 SNV 移出 `input/` | 原本每個 SNV 都進輸入，即使只有 1 條 alt read；真實 caller 約要 5–10 條 | 曲線來自 CASTLE HCC1395（84×、purity 約 1）vs SEQC2，`lab_report/2026-10-26_caller_detection/`。預設 `none`，舊輸出不變 |
| 2026-10-26 | 曲線用 log(alt) 與 log(depth) 的 logistic | 表格顯示 alt 相同時 depth 越高越難 call，所以 caller 看的是 VAF；兩個變數就能描述 | 抽查與分層表吻合；位點特性（context、MAPQ）未納入 |
| 2026-10-26 | `truth.tsv` 保留漏掉的 SNV，加 `detected` 欄；評分只用 `detected = 1` | 漏掉的 SNV 也是真值，例如可以看出整個 clone 都看不見 | 評分腳本：`tools/eval_hp_truth_phyclone.py`、`tools/eval_random_tree_phyclone.py` |
| 2026-10-26 | 預設 caller 仍是 `none` | 曲線只在 purity 約 1 的樣本上校正，用在低 purity 時可能高估漏抓 | 要改成預設，先在低 purity subsample 上驗證曲線 |

