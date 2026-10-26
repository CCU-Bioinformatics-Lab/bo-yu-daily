# 計畫：將 longphase-s HP 特徵加入 PhyClone

更新日期：2026-10-21（刪除 L0 與 L1-B：原 §5.7、§5.9、I12、I15、AC16、AC20、AC21。依 2026-10-21 會議決議，只用 long read 模擬資料集，short read 資料集都不用；見 `research/meeting_record/2026_10_21_meeting_summary.md`）。
前一版：2026-10-17（新增 §5.8.8 T-sc scDNA 樹藍圖、I16、AC22）。
狀態：設計文件。尚未完成 C0–C6 實作或效果驗證。

本文件採用 ASD-STE100 的寫作原則：使用短句、主動語態及固定術語。每個步驟只指定一個主要動作。條件先於動作。
本文件保留繁體中文，因此不宣稱符合英文受控詞彙及英文句長規則。寫作依據為 [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) 的程序與說明原則。

證據標記如下：

- **[程式實作／current]**：已核對 PhyClone submodule，commit `2738324`。
- **[資料盤點／current]**：引用 `data_input.md`。執行前仍須核對實體檔案。
- **[實驗室規範／lab-canonical]**：引用實驗室知識庫的定義及驗證規範。
- **[設計提案／inferred]**：本計畫新增的介面、公式、門檻及驗收條件。尚無通過結果。

除非另有標記，以下新增設計皆屬 **[設計提案／inferred]**。「必須」表示必要驗收條件。「選用」表示不影響第一版完成判定。

## 0. 目標與範圍

將 HP 與 PS 資訊轉成兩類觀測。

1. 將單一 SNV 的 haplotype counts 加入 M2 likelihood grid。
2. 將同一 molecule 上的 SNV pair 觀測加入 M5 tree score。

第一類觀測用於限制 genotype 假設及估計 CCF。第二類觀測用於比較 same、ancestor、descendant、branch 四種關係。
兩類觀測都必須保留不確定性。HP tag 不能直接充當 SNV allele 或 clone truth。

第一版的主要資料是完整 HCC1395，只有一個 tumor sample。
第一版的正確率驗證使用獨立模擬真值。HCC1395 用於資料可行性及候選樹相容性分析。

驗證分為三層。每層只支持對應的結論：

| 層 | 資料 | 可支持的結論 | 規格 |
|---|---|---|---|
| L1 | 參數式模擬：直接生成 counts、HP 及 pair | 指定模擬情境下支持改善；dose-response 曲線描述改善隨資訊量的變化 | §5.2、§5.2.1、§5.5 |
| L2 | Read-level 模擬及真實 ONT reads 的 spike-in；樹來自生成器（T-gen）或 scDNA 參考樹（T-sc） | L1 的效果經過真實 read 流程後仍存在；T-sc 只作描述，檢查效果在真實樹結構下的方向 | §5.8、§5.8.8 |
| L3 | 真實 long-read 細胞株，第一版為 HCC1395 | 資料可行性及候選樹相容性；不宣稱真樹準確率 | §1.1、§5.1 |

不使用 short read 資料集（例如 PhyClone 論文 benchmark、SMC-Het）當輸入，也不借用它們的真值樹。這些資料沒有 long-read 觀測。

### 0.1 固定推理設定

- 關閉 outlier／mutation-loss 模型。
- 不啟用 `--outlier-prob`、`--assign-loss-prob` 或 `--user-provided-loss-prob`。
- 固定 `--subtree-update-prob 0`，先使用整棵樹的 Particle Gibbs 更新。
- 固定 baseline 與擴充版的 mutations、clusters、CN、purity、read filters 及推理預算。
- 保留 multiplicity 與 SNV／CNA timing 的邊際化。
- 不計算 multiplicity 正確率，也不要求逐 SNV 的 MAP multiplicity。

**[程式實作／current]** outlier 關閉時，每個 DataPoint 都必須指派到樹內。
因此，mutation loss、subclonal CN 及錯誤 CN 仍可能扭曲結果。HP 特徵不會自動解除這些限制。

### 0.2 三種驗收結果

| 結果 | 判定條件 | 可使用的結論 |
|---|---|---|
| 實作通過 | §5.3 的必要功能檢查全部通過 | 擴充版符合指定輸入及計分契約 |
| 評估完成 | §5.4 的輸出、對照及失敗紀錄完整 | 已量化指定資料下的表現 |
| 支持改善 | §5.5 的預先凍結效果門檻通過 | 在指定模擬情境下支持改善 |

評估完成後，效果可能沒有改善。此結果仍可完成評估，但不能標記為「支持改善」。

## 1. 明確輸入資訊

### 1.1 HCC1395 第一版輸入清單

以下檔案及數量來自 [資料盤點](data_input.md) §1–3。
這些是輸入候選及既有紀錄，不表示本次已重新掃描 BAM 或重算 counts。

| ID | 輸入 | 固定來源或設定 | 用途與必要檢查 |
|---|---|---|---|
| I01 | tagged tumor BAM | `/bip8_disk/boyu114/longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam` | 使用 old tagging 全基因組版及其 `.bai`；核對 sample、header、tagging command 與版本 |
| I02 | baseline SNV 表 | `/bip8_disk/boyu114/phyclone/hcc1395_input/output/hcc1395_phyclone_input.tsv` | 固定 30,368 個 SNV、sample `HCC1395`、既有 CN 與 purity |
| I03 | TP SNV VCF | `/big8_disk/liaoyoyo2001/InterSubMod/data/vcf/HCC1395/pileup/filtered_snv_tp.vcf.gz` | 盤點為 30,490 個 SNV；只取 I02 的位點，並核對 REF／ALT |
| I04 | tagging 使用的 somatic VCF | `/big8_disk/liaoyoyo2001/data/vcf/ClairS_ss/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/pileup/HCC1395_methyl_PASS.vcf` | 盤點為 203,611 筆；只作 tagging provenance，不擴大評估 SNV 集合 |
| I05 | phased normal SNP VCF | `/big8_disk/liaoyoyo2001/data/vcf/HCC1395BL_methyl_phase.vcf.gz` | 使用與 I01 tagging 相同的版本；核對 phased GT、PS、sample 及索引 |
| I06 | ASCAT segments | `/bip8_disk/liaoyoyo2001/ascat_ont_runs/20260610_full/HCC1395/t50_n00/tumor.segments.txt` | 候選 A；既有紀錄 purity 0.99、ploidy 2.97；核對 CN 與來源資料集 |
| I07 | reference FASTA | `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` | 核對 build、contig 名稱、REF allele 及 `.fai` |
| I08 | 固定 cluster 表 | `/bip8_disk/boyu114/phyclone/hcc1395_input/pyclone_vi/hcc1395_clusters.tsv` | 主比較使用既有 5 群；記錄 checksum；小型測試另跑無 cluster 模式 |
| I09 | cellular purity | 主比較固定 `tumour_content=0.99` | 沿用既有 baseline 的 ASCAT 設定；核對估計來源、資料集及定義 |
| I10 | 模擬真值 | 新增生成樹、SNV assignment、mutation-carrier CCF 及生成設定 | 與方法輸入分開保存；評分時才載入真值 |
| I11 | 執行設定 | 新增 `run_manifest.json` | 記錄輸入版本、QC、模型開關、seeds、chains、particles、iterations、硬體及輸出位置 |
| I13 | L2 spike-in 背景 reads | `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395BL.cram` | 與 I05 phased normal VCF 屬同一資料集；核對 sample、header、depth 及 I05 的 phasing 版本 |
| I14 | L2 真值及生成設定 | 新增；生成樹、SNV assignment、SNV haplotype、CN 事件、read→lineage 對應、mutation-carrier CCF | 與方法輸入分開保存；評分及 pipeline 診斷時才載入 |
| I16 | T-sc 藍圖 | 新增；由已發表的 scDNA 參考樹萃取（§5.8.8.1 的來源） | 只用正文、補充表及公開 processed 資料；記錄出處及 checksum；與 I14 分開保存 |

HCC1395 pilot 必須提供 I01–I09 及 I11。I10 在 pilot 標記 `not_applicable`，不得補造真值。
模擬評估必須提供 I10、生成後的觀測與 I11；原始 HCC1395 路徑不適用時，須列出對應模擬輸入。
L2 必須提供 I05、I07、I11、I14；L2-S 另須提供 I13；T-sc 另須提供 I02、I16。
I01 的原 tumor 是完整 HCC1395，並非 `tX_nY` subsample。
不要混用 worktree 中另一份 old-tagging 重跑 BAM，或 new-split BAM。

### 1.2 執行前的輸入閘門

1. 確認必要檔案可讀。
2. 確認 BAM、VCF 及 FASTA 的索引可用。
3. 核對 sample、reference build、contig 及 REF／ALT。
4. 將 variant key 固定為 `(chrom, pos_1based, REF, ALT)`。
5. 將計算使用的座標轉為一致的內部格式。
6. 核對 mutation ID 與 variant key 為一對一。
7. 核對 cluster 表涵蓋固定 SNV 集合。
8. 將檔案識別、checksum、工具版本及過濾設定寫入 manifest。

若識別或 reference 不一致，停止該次實驗。不得靜默改名或刪除不合項目。
大型 BAM 的 checksum 可引用已驗證的來源 receipt。若尚無 checksum，先標記待補，不宣稱可重現性驗收通過。

**CN 來源限制：** I06 來自 `ONT/`，I01 的原始資料來自 `ONT_5khz_simplex_5mCG_5hmCG`。
兩者的資料集來源不同。Pilot 可保留此候選 CN，但必須記錄差異。
未確認 clonal CN 的區域，不得納入 C4 的正式合格集合。

**Purity 定義限制：** longphase-s 的 `0.992164` 是 tumor DNA fraction 估計紀錄。
它不能直接替代 PhyClone 的 cellular purity。兩個數字接近也不能證明定義相同。
若改用此估計值，先提供 ploidy、換算假設及驗證結果。[實驗室規範，來源 S04]

### 1.3 C0 新增輸出的資料契約

| 檔案 | 一列的單位 | 必要內容 |
|---|---|---|
| `INPUT.hp.tsv` | mutation × sample | 原 PhyClone 欄位、F1–F3、PS、CN／phase 狀態及 fallback 原因 |
| `INPUT.total.tsv` | mutation × sample | 將同一次 C0 計數合併為 total counts，供公平 baseline 使用 |
| `PAIRS.tsv` | sample × chromosome × PS × hap × 固定排序的 SNV pair | `mutation_i, mutation_j, sample_id, chrom, ps_block, hap, n11, n10, n01, n00, callable_pair_reads` |
| `pair_candidates.tsv` | 固定候選 pair | 位點距離、各階段 QC、納入狀態及第一個排除原因 |
| `phase_cn_map.tsv` | sample × chromosome × PS × CN segment | HP 對應 CN、支持數、方向信心、clonal CN 證據及狀態 |
| `feature_qc.tsv` | sample 或明確標示的分層 | phased／unphased counts、缺失／衝突原因、count 差異與比例分母 |
| `run_manifest.json` | 一次特徵萃取／推理執行 | I01–I11 的來源、版本、參數、狀態與輸出識別 |

I02 的舊 counts 來自 CRAM pileup。C0 的 counts 來自 I01 BAM。
若二者不同，不得強行保留舊 total counts 再填入新 HP counts。
應輸出差異報告，並以同一次 C0 的 `INPUT.total.tsv` 重跑主比較 baseline。
舊 PhyClone run 僅作歷史參考，不能直接當作新 ablation 的成績。

## 2. 架構與新增內容

### 2.1 改良後的資料流

```text
I01–I09：BAM、VCF、CN、reference、purity、clusters
   │
   ▼
[C0 新增] HP／PS／allele 萃取、CN 對應、pair QC、manifest
   ├── INPUT.total.tsv ──────────────────────────► baseline
   ├── INPUT.hp.tsv
   └── PAIRS.tsv + pair_candidates.tsv
          │
          ▼
M1 輸入驗證 [C1 擴充 schema 與跨檔檢查]
   ├── 單 SNV 觀測 ─► M2 [C2 genotype prior + C3 HP likelihood]
   │                       │ [S × G] grid
   │                       ▼
   │                  M3 cluster 聚合 [C5 診斷]
   │                       │
   │                       ▼
   │                  M4 tree CCF 邊際化 [沿用卷積]
   │                       │
   └── pair 觀測 ─► [C4 新增] 四類 relation score／cluster link table
                           │
                           ▼
                   M5 TreeJointDistribution [加入 link score]
                           │
                           ▼
                   M6 SMC／MCMC [驗證 score、proposal、cache 整合]
                           │ trace + 模型設定
                           ▼
                   M7 MAP／consensus／診斷 [C6 擴充]
                           │
                           ▼
                   [新增] 固定母體評分及 ablation 報告
```

`S` 是 sample 數。`G` 是 CCF grid 大小；第一版沿用 `G=101`。
單 SNV 觀測進入 M2。跨 SNV 的 pair 因子進入 M5。
M4 仍只接收每個 node 的 CCF grid。

### 2.2 原架構與新增責任

| 模組 | 現有責任 [程式實作／current] | 本計畫新增內容 | 交付物 |
|---|---|---|---|
| M1 | 讀取 counts、CN、purity；清理不合格 SNV | HP 欄位、pair schema、ID 對齊、錯誤及 fallback 分類 | 可驗證的輸入物件及 QC 紀錄 |
| M2 | 對 genotype 邊際化，建立單 SNV grid | C2：phase-aware 候選；C3：HP1／HP2／unphased 聯合觀測 | 相同形狀的 `[S × G]` grid |
| M3 | 將同 cluster 的 SNV grid 相加 | pair 端點對應 DataPoint；同 cluster 衝突檢查 | cluster link table 及 cluster QC |
| M4 | 用卷積及累加處理 children CCF 總和限制 | 沿用遞迴與 sum constraint | 原 tree data likelihood |
| M5 | 合併 FS-CRP prior 與 tree data likelihood | C4：依四類 topology relation 加入 link score | 三個一致的 tree score API |
| M6 | PG、DataPoint Gibbs、PruneRegraph、α 更新 | 驗證部分樹、proposal、快取及模型傳遞 | 與指定 target 一致的 sampler |
| M7 | 輸出 MAP／consensus tree、assignment、CCF | C6：HP 診斷、pair 衝突、模型 provenance | 可對齊 SNV 的結果及診斷表 |
| 評分層 | 本計畫尚無評分程式 | 新增固定母體評分器、模擬測試及方法比較 | `evaluation_v1.md` 定義的四類評估檔 |

M4 的數學遞迴預期不變。M6 的演算法種類預期不變。
但 C4 必須完成 M6 整合驗證，才能宣稱 sampler 正確。

## 3. 特徵定義及使用條件

### 3.1 HP 與 PS 的固定語意

| read tag | C0 第一版處理 | 限制 |
|---|---|---|
| `1`、`1-1` | PS 有效且符合位點 block 時，歸入 h1 | REF／ALT 一律讀取位點鹼基 |
| `2`、`2-1` | PS 有效且符合位點 block 時，歸入 h2 | REF／ALT 一律讀取位點鹼基 |
| `3`、`4`、`.`、無 tag | 歸入 unphased，分別記錄原因 | 不推定 LOH、allele 或 clone |
| `1-2`、`2-2` | 第一版保守歸入 unphased，另記 extended tag | 待核對 pinned tagging 版本後，才啟用額外語意 |
| 未識別 tag | 歸入 unphased，記錄原值 | 不得猜測 haplotype |
| PS 缺失或不符 | 歸入 unphased | 不得跨 block 沿用 HP 方向 |

**[實驗室規範／lab-canonical]** HP 的完整詞彙不只原稿所列的五種，見 S04。
各版本實際輸出的 tag 仍須由 BAM 與 pinned code 核對。

HP1／HP2 只在同一 sample、chromosome、PS 內有一致意義。
HP tag 是 read 層級標記。例如 `HP:1-1` 的 read，在待測 SNV 處仍可能是 REF。

### 3.2 F1–F5 特徵表

| 特徵 | 明確定義 | 下游用途 |
|---|---|---|
| F1 | `ref_h1, alt_h1, ref_h2, alt_h2, ref_un, alt_un`；六個不重疊計數 | C3 的三組觀測 |
| F2 | `hap_prob_h1` 及支持數；`π_i(2)=1−π_i(1)` | C2／C3 的 haplotype 假設權重 |
| F3 | `hap1_cn, hap2_cn`、CN orientation 狀態、clonal CN 證據 | C2 multiplicity 候選及 C4 eligibility |
| F4 | `alt_h/(ref_h+alt_h)`；分母為 0 時填 NA | C3 輸入診斷；不當成額外獨立觀測重複計分 |
| F5 | 同一 haplotype、同一 alignment 共覆蓋的 `n11,n10,n01,n00` | C4 topology score 及 C5 cluster QC |

F2 可先用 `Beta(1,1)` 平滑 phased ALT 支持數。
此值是資料衍生的 haplotype 權重，不是經獨立驗證的 phase 正確率。
必須保留支持數，並在模擬中檢查 tagging bias 及重複使用 allele 資訊的影響。

F3 以同一 PS、同一 segment 的 phased germline het SNP depth 推定 HP 對應。
初始定向程序要求至少 5 個合格 het SNP，且至少 30 個去重的 informative molecules。
以兩側支持數及 `Beta(1,1)` prior 估計 HP1 比例 q。
若 `Pr(q>0.5)≥0.9`，將 major CN 對應 HP1；若 `Pr(q<0.5)≥0.9`，對應 HP2。
此為待驗證的定向提案。必須記錄去重、mapping bias 檢查及 posterior 支持數。
若 major CN 等於 minor CN，兩個 HP 的 CN 可直接設成相同值。
若不平衡 CN 無法定向，填 NA，並觸發 fallback。
不得只靠 tumor HP depth 宣稱已證明 CN 正確或 clonal。

### 3.3 第一版參數提案

以下數值是本計畫預設值，不是 ASD-STE100 或文獻提供的效果標準。
先用開發資料檢查可行性，再於正式比較前凍結。不得看測試成績後改門檻。

| 參數 | 初始設定 | 使用位置 |
|---|---|---|
| 最小 MAPQ | 20 | F1、F3、F5 |
| 最小 base quality | 10 | REF／ALT 判定 |
| alignment policy | mapped primary；排除 secondary、supplementary、QC-fail 及已標記 duplicate | 所有 counts；相同 molecule 不重複計數 |
| pair 距離窗 | 同 chromosome，距離 ≤50,000 bp | 固定候選 pair 集合 |
| 最小 pair 共覆蓋 | `callable_pair_reads ≥10` | F5 eligibility |
| 同 haplotype 門檻 | 兩端對同一 h 的 `π_i(h)≥0.9` | C4 eligibility |
| link error `ε` | 0.02；敏感度分析 0.01、0.05 | C4；與單 SNV error 分開 |
| link weight `λ` | 1；另報 0、0.5 的敏感度結果 | 處理複合 score 的證據權重 |
| CCF grid | 101 個 0–1 格點 | 與 baseline 相同 |

F3 定向演算法、支持數門檻及 clonal CN 證據來源必須寫入 manifest。
尚未定義時可完成資料盤點，但不得通過 C2／C4 正式輸入閘門。

## 4. 各項架構改良與驗收

### 4.0 C0–C6 變更總表

以下程式路徑除 `tools/` 外，均相對於 `research/phyclone_research/PhyClone/phyclone/`。
新增檔名是介面提案；實作時可依既有風格調整，但須保留責任及驗收條件。

| 變更 | 新增或修改位置 | 明確新增內容 | 對應驗收 |
|---|---|---|---|
| C0 | 新增 `tools/hp_feature_extract.py` | BAM 萃取、PS 對應、CN 對應、pair 計數、QC、manifest | AC01–AC03 |
| C1 | `data/validator/PhyClone_schema.json`、`data/pyclone.py`；新增 `data/haplotype.py` | 選用 HP schema、HP 觀測物件、pair loader、嚴格欄位驗證 | AC02、AC04 |
| C2 | `data/pyclone.py:get_major_cn_prior` 及新 prior helper | genotype／timing 候選、phase 權重、fallback | AC05 |
| C3 | `utils/math_utils.py`、`data/pyclone.py:to_likelihood_grid` | 給定同一 genotype 的 HP1／HP2／unphased likelihood | AC06–AC07 |
| C4 | 新增 `tree/link.py`；修改 `tree/distributions.py`、`cli.py`、`run.py` | relation score、cluster link table、模型開關、計分及快取識別 | AC08–AC11 |
| C5 | cluster loader／診斷 helper | mutation→DataPoint 對應、cluster 內衝突報告 | AC03、AC12 |
| C6 | `process_trace/` 及 trace metadata | HP 權重、fallback、pair 衝突、link score breakdown、模型 provenance | AC13 |
| 評分 | 新增 `tools/evaluate_hp_phyclone.py` 及模擬／測試 fixtures | AD、V、CCF、四類矩陣、pair 可用率及 NA 規則 | AC14–AC15 |

### 4.1 C0：建立一致的觀測

1. 以 I02 固定位點集合。
2. 從 I03 取得並核對 REF／ALT。
3. 依 §3.3 過濾 alignment 及 base。
4. 依位點鹼基判定 REF、ALT 或 other。
5. 依 HP／PS 分派六組 F1 counts。
6. 保留 other、deletion、ref-skip 及低品質的排除數。
7. 建立 F2 與 F3，並保留支持數及未知狀態。
8. 從固定候選 pair 計算 F5。
9. 輸出 §1.3 的所有檔案。

以 `(sample_id, molecule_id, site)` 去重單點觀測。
以 `(sample_id, molecule_id, mutation_i, mutation_j)` 去重 pair 觀測。
若同一 molecule 出現互相衝突的 primary 記錄，排除該項並記錄原因。

既有 `site_pair_coread_counts.tsv` 不可直接作為 F5。
該表只涵蓋 CNV 區域，且未使用本計畫的 read HP／PS 及 primary 篩選。[資料盤點 §3]

### 4.2 C1：驗證輸入及 fallback

原 PhyClone 必要欄位保持不變：

```text
mutation_id, sample_id, ref_counts, alt_counts,
major_cn, minor_cn, normal_cn
```

HP 擴充欄位如下：

```text
ref_h1, alt_h1, ref_h2, alt_h2, ref_un, alt_un
hap_prob_h1, hap1_cn, hap2_cn, chrom, ps_block
phase_status, cn_orientation_status, clonal_cn_status, fallback_reason
```

- 六組 counts 必須全部提供，且為非負整數。
- `ref_h1 + ref_h2 + ref_un == ref_counts`。
- `alt_h1 + alt_h2 + alt_un == alt_counts`。
- `hap_prob_h1` 必須在 0–1 內；缺失值須有狀態說明。
- 已知 `hap1_cn` 及 `hap2_cn` 時，其總和必須等於 `major_cn+minor_cn`。
- 沒有任何 HP 欄位時，使用原版路徑。
- HP 欄位部分缺失或數值矛盾時，報錯並指出資料列。
- 合法但未知的 phase／CN，使用原模型並記錄 fallback。
- pair 指向未知 mutation／sample、重複 key 或負 counts 時，報錯。

不要把格式錯誤當作正常 fallback。

### 4.3 C2：限制 genotype 候選

**[程式實作／current]** 原模型列舉 multiplicity 及 CN timing 假設，再對其邊際化。
C2 保留此機制，只改候選及權重。

| 條件 | 新行為 |
|---|---|
| SNV 早於 CN 變化，haplotype h 的 CN 已知 | 列舉 `x=1..C_h` |
| SNV 晚於 CN 變化 | 在原本允許的 timing 分支保留 `x=1` |
| haplotype 不確定，但 CN 對應有效 | 以 `π_i(h)` 混合兩側有效假設 |
| phase／CN 對應未知，或 `C_h=0` 與觀測衝突 | 整筆 SNV × sample 退回原模型，記錄原因 |

將 genotype 定義為 `g=(h, x, timing)`。
先固定各 haplotype 內的 timing／multiplicity prior，再乘上 `π_i(h)`。
對全部有效候選重新正規化，確保 `sum_g π_i(g)=1`。

例：CN 為 3:1，且 SNV 明確位於 minor HP。
此 HP 的候選 multiplicity 只能是 1。不得保留 x=2 或 x=3。

C2 仍使用 total counts。它不會單獨建立 haplotype likelihood。
Multiplicity 是潛在變數，不列入第一版正確率指標。

### 4.4 C3：計算 haplotype likelihood

新增 HP 觀測物件，分別保存 h1、h2、unphased counts。
給定同一 `g` 及 CCF `f`，先計算三部分，再做一次 genotype 邊際化：

```text
L_i(f) = Σ_g π_i(g) · L_h1(obs_h1 | f,g)
                        · L_h2(obs_h2 | f,g)
                        · L_un(obs_un | f,g)

log L_i(f) = logsumexp_g[log π_i(g) + log L_h1 + log L_h2 + log L_un]
```

三部分必須共用同一 multiplicity 與 timing。
不得各自呼叫已邊際化的原 likelihood，再把結果相乘。
實作應抽出「給定 genotype」的計算 helper。

對 SNV 所在的 haplotype，使用單一 haplotype 的 copy 加權期望 VAF：

```text
w = (1−t, t(1−f), t·f)
CN 變化前：cn_h = (1, 1, C_h)，mu_h = (ε_base, ε_base, min(1−ε_base,x/C_h))
CN 變化後：cn_h = (1, C_h, C_h)，mu_h = (ε_base, ε_base, min(1−ε_base,1/C_h))
expected_vaf_h = Σ_k w_k·cn_h[k]·mu_h[k] / Σ_k w_k·cn_h[k]
```

另一條 haplotype 的 ALT 先依 error model 計分。
Unphased reads 使用 total CN，但條件在同一 `g`。
支援 binomial／beta-binomial 時，兩條計算路徑都須通過驗收。

第一版的單 haplotype normal CN=1 假設限 autosome、`normal_cn=2`。
其他正常倍數、無法定向的 CN、零 copy 或零分母狀態，依明確規則 fallback。
輸出 grid 仍為 `[S × G]`，M3 仍可直接加總。

**驗證重點：** 完全停用 HP 路徑時，結果必須等同原版。
僅有 balanced CN 或 `π_i(1)=0.5`，不足以要求 HP 模型與 total 模型完全相等。
拆分觀測及 beta-binomial 的 dispersion 可能改變 likelihood。
應用小型解析案例核對新公式，再用模擬評估偏差。

Tagging 可能與 allele 有關。F1 的集合不重疊，不代表其選取機制沒有偏差。
必須檢查 ALT／REF 的 phased rate，並在不同 CN、coverage 及 tagging bias 下報告 CCF 誤差。
若需新增 bias 校正參數，先用開發資料定義，再凍結正式比較設定。

### 4.5 C4：加入 topology link 因子

#### 4.5.1 合格 pair 條件

1. 兩個 SNV 必須位於同一 chromosome、同一 PS。
2. 兩者必須對同一 haplotype 達到 §3.3 的信心門檻。
3. 該 haplotype 在兩端的 tumor CN 必須皆為 1。
4. 兩位點間不得跨越 CN breakpoint。
5. 必須有支持 clonal CN 的證據；unknown 不視為通過。
6. 共覆蓋數必須達到 §3.3 的門檻。

正式 QC 清單保留同 cluster 及跨 cluster pair。
同 cluster pair 用於 C5 診斷；跨 cluster pair 才用於 topology 比較。
將兩個用途分開記錄，避免改變評分母體。

`C_h=1` 的條件用來建立可允許的 allele pattern。
一條 read 仍是一個 molecule 觀測，不是一個獨立細胞樣本。
Pattern 的出現比例仍受 CCF、purity 及取樣影響。

#### 4.5.2 Read 計數條件

- read 的 PS 必須等於兩個 SNV 的 PS。
- read 的 HP 必須符合該 pair 的 haplotype。
- 同一筆 primary alignment 必須同時覆蓋兩個位點。
- 兩端皆須有通過品質門檻的對齊鹼基。
- 不使用 deletion、ref-skip、other allele 或拼接的 supplementary alignment。
- 不以 HP 後綴判定 11、10、01 或 00；只讀取兩端 allele。

其中 1 表示 ALT，0 表示 REF。
因此 `callable_pair_reads=n11+n10+n01+n00`。
沒有可靠 HP／PS 的 read 不進入 F5，但仍可保留於 F1 unphased counts。

#### 4.5.3 四類關係與條件 score

將 pair 依固定 mutation ID 排成 `(i,j)`。
Ancestor／descendant 包含跨多層關係。

| 關係 R | 定義 | 無錯誤時不允許的 pattern |
|---|---|---|
| same | i、j 在同一 node | 10、01 |
| ancestor | i 的 node 是 j 的祖先 | 01 |
| descendant | j 的 node 是 i 的祖先 | 10 |
| branch | 不同 node，且互不為祖先 | 11 |

條件在 `m=n11+n10+n01`，不對 n00 的比例建模。
對允許格子的未知比例，使用 `Beta(1,1)` 積分。
省略對所有 R 相同的 multinomial 係數後：

```text
P(c | same)       = ε^(n10+n01) · (1−2ε)^n11
P(c | ancestor)   = ε^n01 · (1−ε)^(n11+n10) · B(n11+1,n10+1)
P(c | descendant) = ε^n10 · (1−ε)^(n11+n01) · B(n11+1,n01+1)
P(c | branch)     = ε^n11 · (1−ε)^(n10+n01) · B(n10+1,n01+1)
```

必須滿足 `0<ε<0.5`。以 log／log-beta 計算，避免 underflow。
`m=0` 時，四類 score 皆為 0。
多 sample 共用 relation，各 sample 的 nuisance 比例分別積分。

這是 CCF 已被 nuisance prior 取代的 topology 因子提案。
它不等同完整的 read／CCF 聯合生成模型。
有限 counts 只形成軟性支持。例如只有 11，不代表已證明 same；缺少 11 也不代表已證明 branch。

#### 4.5.4 標準化、聚合及相依性

```text
ell_ij(R) = log P(c_ij | R)
            − logsumexp_R'[log P(c_ij | R')] + log(4)

L[a,b,R] = Σ_{i∈a,j∈b} ell_ij(R)
log_p_link(T) = λ · Σ_{a<b, a與b均已在樹內} L[a,b,R_T(a,b)]

log_target(T) = log_FS_CRP(T) + log_data(T) + log_p_link(T)
```

先算每個 SNV pair 的 score，再加總至 cluster pair。
不要先合併不同 SNV pair 的 counts 再算 Beta 積分。
交換 pair 端點時，必須交換 ancestor／descendant。
尚未加入部分樹的端點，不計該 pair。

標準化只扣除 relation 無關常數。
它不會消除 pair 數量的影響，也不會自動校正 outlier 偏好。
第一版不將此設計延伸至 outlier 模型。

同一 molecule 可產生多個 pair。F5 與 F1 也可能重用觀測。
因此整體是帶有相依證據的複合 score，不能宣稱所有項目皆獨立。
必須記錄 molecule 重用數、`λ` 敏感度及負對照結果。
若結果僅在過度加權時出現，不能據此通過效果驗收。

#### 4.5.5 計分及推理整合

新增 `--pairs-file`、`--link-error-rate` 及 `--link-weight`。
以明確的 C2／C3 開關控制 ablation，不以「有欄位」強制啟用所有模型。

必須在三個 API 中加入同一個 link score：

- `TreeJointDistribution.log_p`
- `TreeJointDistribution.log_p_one`
- `TreeJointDistribution.compute_log_p_and_log_p_one`

建構物件時，更新 `__slots__`、模型傳遞及快取識別。
模型識別必須包含 link table、error rate、weight 及相關版本。
不得讓不同 link 設定共用舊 score／proposal 快取。

Score helper 必須支援完整 Tree 及 proposal 使用的 `TreeHolderBuilder`／`BaseTree`。
測試必須包含 TreeHolder 複製、序列化、cache hit／miss 及重新指派 node。

**[程式實作／current]** semi-adapted proposal 的既有 node 部分使用候選 tree 的 `log_p`。
因此加入 link 項可能改變 proposal。不得假定它完全不讀取新 score。
必須共同核對 proposal 機率及 importance weight。

Subtree sampler 現有程式在接回完整樹後會修正權重。
這不表示已驗證新增 link 項的跨邊界計分。
第一版固定 subtree 更新為 0。日後啟用前，另驗證 subtree 內外 pair 的權重修正。

### 4.6 C5：保留 cluster 聚合並新增診斷

M3 繼續加總同 cluster 的 SNV grid。
C2／C3 的 grid 因此直接進入 tree inference。
但固定預分群可能已將不同 clone 的 SNV 合併。PhyClone 不能在 cluster 內拆開 SNV。

新增 `cluster_link_qc.tsv`，列出同 cluster pair 的 n10、n01、有效深度及 same score。
第一版只報告衝突，不自動拆 cluster。
另以小型 SNV 集合比較有 cluster 與無 cluster 模式。
HP-aware 預分群列為第二版工作。

### 4.7 C6：輸出與診斷

| 輸出 | 必要內容 |
|---|---|
| 原 tree／assignment／prevalence 表 | 保留既有功能；CCF 以 mutation ID 及 sample ID 對齊 |
| `haplotype_diagnostics.tsv` | SNV 的輸入 haplotype 權重、支持數、CN 對應、fallback 原因；不得稱為 tree 更新後 posterior |
| `link_conflicts.tsv` | pair、MAP relation、四格 counts、禁止格 counts、有效深度及各 relation score |
| `cluster_link_qc.tsv` | 同 cluster pair 的一致性診斷 |
| `score_components.tsv` | FS-CRP、data、link、total score 及模型識別 |
| trace metadata | 模型開關、link table 識別、參數、輸入及推理版本 |

若 MAP／consensus 後處理會重算 score，必須載入相同 link 模型。
Consensus 本身不必是最高分樹；診斷須標明採用哪棵樹。
若沒有保存 pair 模型，後處理必須明確報錯或標記 score 不可重算。

Multiplicity 候選及權重可作選用診斷。
第一版不要求 multiplicity MAP、正確率或 calibration。

## 5. 驗證指標、驗收標準及執行階段

### 5.1 固定評估契約

採用 [第一版評估規格](evaluation_v1.md) §1–5。
本節補上實作閘門及效果判定提案，不變更已採用的指標與 multiplicity 決定。

| 驗證面向 | 指標／公式 | 單位與分母 | 真值需求及 NA 規則 |
|---|---|---|---|
| 祖先關係 | `AD_F1=2TP/(2TP+FP+FN)` | 固定 SNV 集合的有向、跨多層祖先配對；排除 same | 需已知樹及 assignment；分母 0 為 NA；缺 assignment 為 incomplete_prediction |
| 分群 | `V=2hc/(h+c)`；h 為 homogeneity，c 為 completeness | 相同 SNV 集合的 partition | 需真實群集；空集合為 NA；兩邊皆單群時為 1；其餘零分母依標準定義為 0 |
| CCF | `MAE=Σ abs(pred−truth)/n_scored` | SNV × sample 等權；mutation-carrier CCF，含後代 | 需 CCF 真值；同報 missing／invalid；超出 0–1 不截斷 |
| 局部關係 | 4×4 confusion matrix | 每 sample 的固定合格 pair，每對一次 | row=truth、column=prediction；順序為 same／ancestor／descendant／branch |
| 資訊可用性 | `n_eligible/n_candidate`、`n_informative/n_candidate`、`n_informative/n_eligible` | 方法比較前固定的候選 pair | 無需樹真值；分母 0 為 NA；不是準確率 |
| 實作診斷 | count mismatch、fallback、score 差異、runtime、peak RSS、失敗率、SMC ESS | 各自標明 sample／SNV／pair／iteration／run | 用於功能與成本檢查，不替代生物正確率 |

`informative` 定義為合格 pair 有 `n11+n10+n01>0`。
此定義不表示 pair 能唯一決定 relation。

所有方法使用相同評分母體。不得只挑成功輸出的項目。
樹的 linkage 分層使用各 sample 合格 pair 的聯集，不因 sample 數重複計分。
局部矩陣保留 sample 維度，並保留缺失預測數及四類 support。

分開報告全部、具有合格 linkage、沒有直接 linkage 的 AD。
固定預分群時，V-measure 可能不變。此結果應保留。
CCF MAE 只有完整有效預測時，才標記完整母體結果。

HCC1395 缺少完整獨立 SNV assignment 及 CCF truth。
其 AD、V、CCF MAE 與 relation confusion matrix 應填 `NA: truth_unavailable`。
Golden tree 只作 candidate 相容性參考，不代替完整真值。

### 5.2 比較實驗與獨立性

必要方法為 `baseline`、`+C2`、`+C3`、`+C4`、`+C2+C3`、`+C2+C3+C4`。
`+C3` 保留原 timing／multiplicity prior，再展開 haplotype 觀測；`+C2` 只改 prior。
若原候選在某 haplotype 上不可能成立，例如 `x>C_h`，該分支 likelihood 為 0，不得計算大於 1 的 VAF。
此限制屬 C3 觀測模型的合法範圍，須記錄其影響；不能宣稱 C3 完全不使用 CN 資訊。
只有啟用 C2 時，才使用 §4.3 的 haplotype 內候選正規化規則。
各方法共用 C0／C1 的輸入支援。
Baseline 使用相同原始觀測合成的 total counts。

**模擬分層：** 正確 CN、minor CN ±1、不同 tagging recall、allele bias、低 pair coverage、PS 內 phase switch。
C4 主結果限 clonal `C_h=1`。
Amplified CN、subclonal CN 及 mutation loss 只作範圍外 stress test，分開報告。

**必要對照：** 打亂 pair 對應、PS 內 phase switch、matched-coverage／callability／error 的 short-span 對照。
整個 PS 的 HP1／HP2 連同 CN 及機率一起交換，是不變性檢查。
此交換不是破壞 phase 的負對照。

**獨立性：** 生成樹、assignment 及 CCF truth 不得送進推理器。
不得再用建樹的 F5 當作獨立 relation truth。
若新增 held-out read consistency，須在 tagging 前切分 molecules／相關位點，必要時 retag 或遮罩。
同一 molecule 產生的所有位點與 pairs 必須留在同一側。

`seeds` 是推理重複，不是生物樣本數。
先彙整每個獨立模擬資料集的 seeds，再計算方法的配對差值。
真實多 purity subsample 需先完成 tagging；實測 purity 另行提供。
同一細胞株的 subsample 不視為獨立病人。

#### 5.2.1 Dose-response 曲線

**目的：** 量化改善幅度如何隨 long-read 資訊量變化。
橫軸為資訊量，縱軸為方法對 baseline 的配對差值。
曲線起點 D1=0、D2=0 表示沒有 phased reads 及 pair。此時 C2 仍可使用 HP 對應的 allele-specific CN（§4.3），因此起點不一定等於 baseline。完全停用 HP 路徑的情況由 AC04 檢查。
此曲線不參與 §5.5 的「支持改善」判定。它支持另外三類描述：改善是否隨資訊量增加、起效點及飽和點、真實資料位置的預期效益。

**設計規則：**

- 一次只改一個因子。其他條件固定在 §5.5 的主要情境。
- 每個格點使用獨立模擬資料集。不同格點不共用資料集。
- 格點、比較及分析規則在 L1 正式執行前寫入 evaluation manifest。看過 L1 測試結果後才新增的格點，標記為 exploratory。
- 橫軸使用可由觀測計算的量（`feature_qc.tsv`、`pair_qc.tsv`），不使用只存在於真值的量。這樣才能把真實資料放到同一橫軸上。例外見因子 D3。

**因子與格點（提案）：**

| 因子 | 生成器控制方式 | 橫軸（觀測量） | 格點 | 主要比較 |
|---|---|---|---|---|
| D1 phased 比例 | 隨機把 phased reads 改為 unphased | SNV 位點上 phased reads／總 reads | 0、0.1、0.2、0.4、0.6、0.8 | `+C2+C3` 對 `+C2`；完整模型對 baseline |
| D2 pair 密度 | 調整 read length 及 SNV 密度 | `n_informative／n_SNV` | 0、0.25、0.5、1、2、4 | `+C4` 對 baseline；完整模型對 `+C2+C3` |
| D3 tagging 正確率 | 調整 HP 錯標率 | 真值 HP 正確率（僅模擬可得） | 0.5、0.8、0.9、0.95、0.99、1.0 | 完整模型對 baseline |

D1 及 D2 的 0 格點代表沒有對應資訊。D2 的生成器設定值須同時記錄，因為同一 pair 密度可由不同 read length 及 SNV 密度組合得到。
D3 的 0.5 代表隨機錯標，作為負對照。D3 的其他格點固定 D1、D2 於主要情境。

**樣本數：** 每個格點至少 10 個獨立資料集，每個資料集至少 4 組 seeds。
與主要情境相同的格點，直接使用 L1 主要情境的資料集及結果，不重複生成。
格點數量多，因此此分析的每點 CI 較寬。結論只用於描述趨勢，不作逐點顯著性宣稱。

**分析規則：**

| 項目 | 計算 | 判讀 |
|---|---|---|
| 零點檢查 | D1=0 且 D2=0 時，完整模型對 `+C2` 及對 baseline 的差值 | 對 `+C2` 預期相同（AC19）；不相同時視為實作錯誤，先修正再分析。對 baseline 的差值是 C2 的 CN 資訊效果，照實報告，不預設為 0 |
| 趨勢 | 以資料集層級差值對橫軸做線性迴歸；在每個格點內重抽資料集，2,000 次 bootstrap 斜率 95% CI | AD／V：斜率 CI 下界 >0；CCF MAE：斜率 CI 上界 <0，記為「改善隨資訊量增加」 |
| 起效點 | 差值 95% CI 首次排除 0 的最小格點 | 只報告格點值，不在格點之間內插門檻 |
| 飽和 | 最高兩個格點的差值之差，及其 95% CI | CI 包含 0 時，記為「在格點範圍內可能飽和」 |
| 高端下降 | 最高格點與峰值格點的差值之差 | CI 排除 0 且方向為變差時，標記為偏差警訊；須以 pipeline 診斷及 §5.2 負對照排查 |
| 負對照 | D3=0.5 的差值 | 不應顯著優於 baseline。若顯著優於 baseline，須先排除替代解釋，才能採用其他 D3 結果 |

線性迴歸只用於檢查趨勢方向。它不代表真實關係是線性。

**真實資料的位置：**

- 以 HCC1395 pilot 的 `feature_qc.tsv` 及 `pair_qc.tsv` 計算 D1、D2 的橫軸值。
- 在曲線上標出該位置。只在相鄰兩格點之間做線性內插，不外推到格點範圍之外。
- 結果稱為「依模擬曲線的預期效益」，不得稱為 HCC1395 的實測改善。
- D3 在真實資料上無法直接觀測。若需要，使用 L2-S 的 tagging 正確率估計值，並註明來源。

**交付物：** `dose_response.tsv`，一列為因子 × 格點 × 方法比較 × 指標，包含資料集數、平均差值、95% CI、生成器設定值及失敗數。另在 `ablation_report.md` 中附曲線圖及上表各項判讀。

### 5.3 實作驗收表

以下全是待執行的必要檢查，不是已通過結果。
數值容許差是本計畫的驗收提案。通過狀態須連結測試輸出或 receipt。

| ID | 驗證案例 | 通過標準 |
|---|---|---|
| AC01 | 輸入來源與版本 | 依 §1.1 的 run type 核對必要輸入；sample／reference／allele 無未解衝突；缺失必要項不得標 PASS |
| AC02 | F1 與 schema | 六組 counts、total counts、pair 四格及 callable counts 逐列守恆；不合資料明確拒絕 |
| AC03 | Read／pair fixtures | PS 不符、跨 HP、重複 molecule、supplementary、deletion、低品質及 other allele 的納入數完全符合手算 |
| AC04 | 無 HP／空 link 回歸 | 與 commit `2738324` 的 grid 及 tree scores 完全相同；若更換數值計算順序，須記錄原因且 `atol≤1e-10, rtol=0` |
| AC05 | C2 prior | 3:1 minor-HP 案例不含 x=2、3；有效 prior 總和為 1；未知 CN／零 copy 衝突的 fallback 可追溯 |
| AC06 | C3 小型解析案例 | 共用 genotype 的聯合 likelihood 與直接列舉一致，`atol≤1e-10`；空觀測項的 log contribution 為 0 |
| AC07 | HP 交換不變性 | 同 PS 的 counts、CN、機率及 pair hap 一起交換後，grid、link score 及 target 在 `atol≤1e-10` 內相同 |
| AC08 | C4 四類 score | 四類公式與手算一致；m=0 為 0；純 11 fixture 支持 same 勝於 branch；強 10 且無 01 fixture 支持 ancestor 勝於 same |
| AC09 | C4 聚合與部分樹 | SNV pair 分別計分後加總等於 link table；端點未加入時為 0；交換端點正確交換 ancestor／descendant |
| AC10 | Score／cache／後處理 | 三個 score API 結果一致；Tree／builder 及 cache hit／miss 一致；改變 link 設定會隔離舊快取；trace 可重算同一 total score |
| AC11 | Sampler target | 小狀態空間可列舉 posterior；proposal 正規化及 importance-weight 公式通過；PG／Gibbs／PruneRegraph 的頻率符合預先固定的 MC 誤差帶 |
| AC12 | Cluster 診斷 | 同 cluster pair 進 QC、不作跨 cluster 重複計分；cluster mapping 與無 cluster fixtures 正確 |
| AC13 | 輸出完整性 | §4.7 的必要檔案齊全；每個 fallback 與 conflict 可回查 SNV／pair；不輸出虛構 multiplicity accuracy |
| AC14 | 評分器已知答案 | 完整完美預測時 AD／V=1、CCF MAE=0、矩陣只含對角線；AD 無有效分母時仍為 NA |
| AC15 | 缺失與失敗 | 空母體、缺 truth、缺 prediction、invalid CCF、失敗 trial 均依規格回報；不靜默刪除或填成完美分數 |
| AC17 | L2 生成器 fixtures | 同一 read 上的所有 spike 位點使用同一 lineage（100%）；各 lineage／haplotype 的 ALT reads 數與生成紀錄完全相符；被跳過的位點與原因可回查 |
| AC18 | L2 觀測獨立性 | 方法輸入不含 I14 欄位；HP 欄位全部可回溯到本次 longphase-s 輸出；tagging 在 spike／模擬後的 reads 上重跑，並記錄版本與參數 |
| AC19 | Dose-response 零點 | D1=0 且 D2=0 的輸入（HP 欄位存在但全部 unphased、pair 表為空）在固定 seed 下，完整模型與 `+C2` 的 grid、tree scores 及 MAP tree 相同；容許差同 AC04 |
| AC22 | T-sc 藍圖萃取 | 每份藍圖的 topology 及 clone prevalence 與來源圖表逐項相符；每個 sample 的 clone 加 normal 比例總和為 1（`atol≤1e-6`）；每個 SNV 都有 `feature_origin`；「僅 scDNA 特徵」母體只含 `feature_origin=scdna` 的 SNV |

AC11 先固定可列舉的狀態空間、chain 長度及至少 4 組獨立 seeds。
初始門檻為 posterior total variation distance ≤0.03。
另要求每個真實機率 ≥0.01 的狀態，頻率差 ≤`max(0.01,4×MCSE)`，且 MCSE ≤0.005。
以獨立 chains 或適當批次估計 MCSE；不得用相依 draws 的原始筆數當獨立樣本數。
若 MCSE 未達門檻，結果為「抽樣精度不足」，不得自行擴大誤差帶。
Subtree sampler 不在第一版啟用範圍。啟用前須新增非零跨邊界 link 的 exact-target 測試。

### 5.4 評估完成的必要交付物

| 檔案 | 完成標準 |
|---|---|
| `evaluation_manifest.json` | 固定 truth／輸入識別、評分母體、方法版本、QC、模型設定、seeds、預算、效果門檻及統計規則 |
| `metrics.tsv` | 每個 trial／seed／方法／分層均有結果或失敗狀態；分母、missing／invalid 及 NA 原因完整 |
| `relation_confusion.tsv` | 每個可評估組合輸出 16 格，包括 0；無 truth 時明確標記 NA |
| `pair_qc.tsv` | candidate／eligible／informative 數、逐階排除數、三個比例及有效深度分布 |
| `ablation_report.md` | 各方法的配對差值、失敗率、runtime／RSS、限制及支持或不支持的結論 |
| `dose_response.tsv` | §5.2.1 的每個因子 × 格點 × 比較 × 指標均有結果或失敗狀態；含資料集數、CI 及生成器設定值 |

所有方法必須使用相同 mutations、samples、clusters、CN、purity、filters 及推理預算。
若公平 baseline 需要重算 counts，必須完成重跑。
評分器及評估輸出通過 AC14–AC15 後，才可標記「評估完成」。

### 5.5 支持改善的效果門檻提案

以下是新增的效果判定提案，尚非既有實驗結果。
正式 benchmark 前，將主情境、主指標、樣本數及門檻寫入 evaluation manifest。
若要修改，必須保留版本差異並重新使用未參與調整的測試資料。

建議每個主要情境至少使用 20 個獨立模擬資料集。
每個資料集至少使用 4 組固定推理 seeds。
以資料集為配對單位，對方法差值做 2,000 次 bootstrap，報告 95% CI。
不要以 reads、pairs 或 seeds 擴大獨立樣本數。

| 欲支持的結論 | 預先指定比較及主要條件 | 通過門檻 |
|---|---|---|
| C2／C3 改善 CCF | `+C2`、`+C3` 分別對 baseline；`+C2+C3` 對 `+C2`；主情境為 minor CN 誤差 | `ΔCCF_MAE` 的 95% CI 上界 <0 |
| C4 改善局部關係 | `+C4` 對 baseline；完整模型對 `+C2+C3`；主情境為合格 linkage、clonal CN | linkage 分層 `ΔAD_F1` 的 95% CI 下界 >0，並提供四類矩陣 |
| 完整模型改善整體樹 | `+C2+C3+C4` 對 baseline；主情境為模型範圍內的固定測試集 | 全體 `ΔAD_F1` 的 95% CI 下界 >0 |

以上每項結論，還須同時通過以下退步界線：

- 全體 AD 與 V 的配對差值 CI 下界皆須 ≥−0.01。
- 全體 CCF MAE 的配對差值 CI 上界須 ≤+0.01。
- 主要測試 trials 必須有完整有效結果；若有失敗，先報失敗並處理，不能只在成功子集宣稱通過。
- Pair／phase 負對照及 `λ` 敏感度結果須一併呈現；若出現同等改善，須先排除替代解釋。

0.01 是本計畫提出的絕對差值容許界線，不是相對百分比，也不是文獻既定標準。
若測試集有明顯 ceiling effect 或樣本量不足，填「證據不足」，不得改寫為已通過。
HCC1395 pilot 不使用此表宣稱真樹準確率改善。

### 5.6 執行順序與離開條件

| 階段 | 工作 | 必要產物 | 離開條件 |
|---|---|---|---|
| Phase 0 | 核對 pilot 必要輸入；小區域 C0；量化 counts、phase、CN、pair 可用性及 tagging bias | §1.3 的 pilot 輸出、待補清單、參數版本 | AC01–AC03 通過；分別記錄 C3／C4 的 GO 或 NO_GO |
| Phase 1 | 完成 C1、C2 | HP schema、prior、fallback fixtures | AC04–AC05 通過 |
| Phase 2 | 完成 C3 | HP 觀測物件、聯合 likelihood、模擬偏差檢查 | AC06–AC07 通過；仍保留原版 fallback |
| Phase 3 | 完成 C4 | Link table、三個 score API、cache／sampler 整合 | AC08–AC11 通過；subtree 更新維持 0 |
| Phase 4 | 完成 C5、C6、評分器及正式 ablation；執行 §5.2.1 dose-response | 診斷表、四類評估檔、方法比較報告、`dose_response.tsv` | AC12–AC15、AC19 及 §5.4 通過；另依 §5.5 判定效果 |
| Phase 5 | 執行 L2 | §5.8.7 的交付物 | AC17–AC18 通過；L2 依 §5.8.6 判定；AC22 通過後執行 T-sc，依 §5.8.8.4 描述性報告 |

L2 生成器可與 Phase 2–4 平行開發。L2 的正式測試資料集須在 Phase 4 凍結 L1 參數，並依 §5.8.5.1 決定 `n` 後，才生成或解封。

Phase 0 的最低 GO 條件如下：

- C3：存在通過 QC、CN 可定向且同時有 REF／ALT 支持的 phased SNV。列出實際數量及分母。
- C4：至少存在一對連接不同 DataPoint 的合格 informative pair，且滿足 clonal CN 證據條件。
- 上述最低條件只允許進入實作試驗，不保證統計能力或科學效益。
- 若 C4 合格數為 0 或 clonal CN 證據缺失，記為 `NO_GO_C4`，交付可用性報告；不得放寬條件後沿用原驗收結論。

PhyClone 程式變更應在 submodule 分支中獨立 commit。
本次工作只重寫計畫，不執行以上大型實驗。
後續依變更範圍執行新測試，再執行既有必要檢查：

```bash
cd research/phyclone_research/PhyClone
python -m unittest discover -s phyclone/tests/unit_tests
```

### 5.8 L2：read-level 模擬及 spike-in 驗證

#### 5.8.1 目的與結論範圍

L1 直接依模型假設生成 counts、HP 及 pair。因此 L1 有循環論證的風險。
L2 的觀測必須由 reads 產生，並經過與 HCC1395 pilot 相同的 alignment、tagging 及 C0 流程。
L2 檢查 L1 的效果在真實 read 流程的誤差下是否仍存在。
L2 不代替真實腫瘤的真樹。

L2 分為兩條路線：

| 路線 | Reads 來源 | 主要優點 | 主要限制 |
|---|---|---|---|
| L2-S（spike-in） | I13 真實 ONT normal reads，依已知樹改寫鹼基 | 保留真實覆蓋、read length、錯誤分布及 PS 結構 | 繼承 I05 的 phasing 錯誤；第一版不能模擬 CN gain |
| L2-R（read-level 全模擬） | 由已知 clone genomes 模擬 ONT reads | 真實 haplotype 完全已知；可加入 CN gain 及 germline phasing 錯誤 | 模擬器的錯誤模型與真實 ONT 不同 |

L2-S 是 L2 的主要路線。L2-R 用於 L2-S 無法涵蓋的情境。

#### 5.8.2 共同生成規則

1. 固定生成樹、clone 的 cellular fractions、purity、sample 數、SNV 密度及生成 seed。寫入 I14。生成樹預設來自本計畫的生成器（T-gen）；使用 scDNA 參考樹時，依 §5.8.8（T-sc）。
2. 為每個 SNV 指定 clone、haplotype（HP1／HP2）及位置。CN 事件指定 clone、haplotype 及區段。
3. 依 SNV 與 CN 的時序決定每個 lineage 上的 copy 數。Multiplicity 只作生成紀錄，不作評分答案（`evaluation_v1.md` §2.4）。
4. 每條 read 代表一個 molecule。每條 read 只屬於一個 lineage：normal 或某個 clone。
5. 同一 read 上的所有 SNV，都依該 read 的 lineage 及 haplotype 決定。不得逐位點獨立抽樣。
6. Read 的 lineage 抽樣機率與「lineage 的 cellular fraction × 該位置的 copy 數」成正比。
7. 生成真值（I14）只寫入獨立目錄。方法輸入只能來自 reads 的處理結果。

規則 4–5 是 pair 共現的必要條件。逐位點獨立抽樣會破壞 C4 測試的觀測。

#### 5.8.3 L2-S：spike-in 到真實 ONT reads

**背景 reads：** 使用 I13。I13 與 I05 屬同一資料集，因此 read 的 haplotype 與 I05 phase 一致。

1. 先量測 I13 在候選區域的 depth。
2. 以 read name 的雜湊值，將 reads 不重疊地分成 S 份，每份作為一個 sample。
3. 若每個 sample 的 depth <20×（提案門檻），則減少 S。不得重複使用 reads。

**區域：** 至少使用 3 條 autosome。區域清單寫入 manifest。
排除 C0 過濾條件下不可用的低 mapping quality 區域。

**Read 的真實 haplotype：**

- Read 若帶有 I05 的 germline 等位基因，以 I05 決定 haplotype。
- Read 若沒有可用的 germline SNP，以 0.5 機率隨機指定，並記錄 `haplotype_source=random_untaggable`。這類 read 在觀測端應為 unphased。

**Spike 規則：**

- 只改寫比對鹼基為 REF、且 base quality 符合 C0 門檻的位點。保留原 base quality。
- 若 read 在該位點為 deletion、mismatch 或低品質，不改寫，並記錄原因。
- Spike 位點不得與 I05 的 germline variants 重疊。
- 改寫後重算 MD／NM tags。第一版不重新比對。另取 1 個資料集，轉成 FASTQ 後以 minimap2 重新比對，作敏感度檢查。

**CN：** 第一版只允許下列兩種狀態：

- 雙等位 `C_h=1`。
- 單一 haplotype 的 loss：移除受影響 lineage 在該 haplotype 上的 reads。

CN gain 需要複製 molecule，會產生假的重複 reads。因此 L2-S 不模擬 gain；gain 由 L2-R 處理。

**觀測端處理：** 使用與 I01 相同的 longphase-s 版本及參數，在 spike 後的 reads 上重新 tagging。
germline phasing 使用 I05。之後執行 C0，產生 §1.3 的全部檔案。

#### 5.8.4 L2-R：read-level 全模擬

1. 取 I07 的區域子集。以 I05 的 germline haplotypes 建立兩條 normal haplotype 序列，保留真實 SNP 密度。
2. 依生成樹，為每個 clone 套用 SNV 及 allele-specific CN 事件，產生 clone haplotype 序列。
3. 以 ONT read simulator（PBSIM3 或 Badread，擇一並記錄版本）模擬 tumor 及 matched normal reads。
4. Read length 分布及錯誤模型依 I01 或 I13 的實測值設定，並記錄來源。
5. 以 minimap2 `-ax map-ont` 比對到 I07，記錄版本。
6. 在模擬的 normal reads 上重新做 germline phasing。不得直接使用真實 haplotype 當 phasing 結果。
7. 執行 longphase-s tagging 及 C0。

L2-R 可加入 `C_h≥2` 的 CN gain。依 §5.2，這類情境屬範圍外 stress test，分開報告。

目前環境有 minimap2 及 samtools，沒有 PBSIM3 或 Badread。安裝後須把版本寫入 manifest。

#### 5.8.5 輸入模式及情境

| 模式 | SNV 位點 | CN | 用途 |
|---|---|---|---|
| truth-site | 真實 SNV 的位置及 REF／ALT；不含 clone 或 haplotype | 真實 allele-specific CN | 隔離 read 及 tagging 的誤差 |
| called | 與 HCC1395 pilot 相同的 somatic caller 及版本 | CN caller 輸出 | 端到端誤差 |

主要情境使用 truth-site 模式。called 模式作端到端檢查，分開報告。
truth-site 模式另依 §5.2 加入 minor CN ±1 的 CN 擾動分層。

**SNV 密度：**

- 主要分層：與 HCC1395 pilot 相同區域的實測 somatic SNV 密度。
- 高密度分層：主要密度 ×10，檢查 pair 充足時的上限。結果分開報告，不混入主要結論。
- Dose-response 抽點：D1 取 0.2、0.4 及主要情境值（以隨機遮蔽 HP tag 降低 phased 比例）；D2 取主要密度、×3、×10。每點至少 5 個資料集，只檢查曲線方向是否與 §5.2.1 的 L1 曲線一致，不作判定。

Purity、sample 數及 depth 的格點在正式執行前寫入 manifest。
L2-S 的 depth 受 I13 限制，須依 §5.8.3 的實測 depth 決定。

**開發／測試分離：** 先生成獨立的開發資料集，用於除錯、QC 參數檢查及 §5.8.5.1 的變異估計。
每條路線至少 5 個開發資料集。開發資料集不計入正式判定。
正式測試資料集在 L1 參數凍結後才生成或解封，且不得用於調整參數。

##### 5.8.5.1 L2 樣本數規則

L2 的資料集數 `n` 在 L1 完成後決定。每個資料集至少使用 4 組 seeds。
`n` 的下限為 10。L2-S 與 L2-R 分別計算 `n`。

**步驟：**

1. 列出 L1 依 §5.5 已通過的結論。每項結論使用 §5.5 的主要比較及主要指標。
2. 對每項結論，取 L1 配對差值的 95% CI 中靠近 0 的端點，取絕對值，記為 `d_plan`。這是保守的效果大小。
3. 對每項結論，計算資料集間差值的標準差。取 L1 的值及 L2 開發資料集的值中較大者，記為 `s_plan`。
4. 以單側 α=0.025、power=0.80 計算所需數量：

```text
n_req = ceil( ((1.96 + 0.84) * s_plan / d_plan)^2 )
```

5. 同一路線取各結論 `n_req` 的最大值，記為 `n_req_max`。
6. 以開發資料集量測每個資料集的運算時間，並依可用資源估計可執行的上限 `n_max`。
7. 決定 `n`：

| 條件 | `n` | 報告要求 |
|---|---|---|
| `n_req_max ≤ n_max` | `max(10, n_req_max)` | 記錄 `d_plan`、`s_plan`、`n_req` |
| `n_req_max > n_max` | `max(10, n_max)` | 記錄 `n_req`，並報告此 `n` 下的預期 power；標記「未達 80% power」 |
| L1 沒有通過任何結論 | 10 | L2 只作描述性報告，不作 §5.8.6 判定 |

此 `n` 下的預期 power 以常態近似計算：

```text
power ≈ Φ( sqrt(n) * d_plan / s_plan − 1.96 )
```

**限制：**

- 公式使用常態近似。它只用於規劃 `n`。正式判定仍使用 §5.8.6 的 bootstrap CI。
- L2 的真實效果可能小於 L1，因為 read 流程會加入誤差。`d_plan` 使用 CI 端點，以降低高估的風險。
- `n` 在生成正式測試資料集前寫入 `l2_manifest.json`。看到測試結果後，不得增加或減少資料集。
- 若需要更多資料集，須生成新的獨立測試批次，並在報告中分開標示批次。

#### 5.8.6 方法、指標及判定規則

方法沿用 §5.2 的六種。Baseline 使用同一次 C0 的 `INPUT.total.tsv`。
指標沿用 §5.1 及 `evaluation_v1.md`。另加入下列 pipeline 診斷，這些診斷使用 I14，只在評分時計算：

| 診斷 | 定義 | 用途 |
|---|---|---|
| Tagging recall／accuracy | 依真實 haplotype，分 REF／ALT 計算 tagged 比例及 HP 正確率 | 量化 allele-dependent tagging bias |
| Pair 漏斗 | 真實共覆蓋 pair → candidate → eligible → informative 的數量 | 找出 pair 資訊在哪一步流失 |
| QC 誤納率 | Eligible pair 中，真實 `C_h≠1` 或跨 CN breakpoint 的比例 | 檢查 C4 合格條件 |
| Caller 準確度（僅 called 模式） | SNV recall／precision；CN 區段的一致比例 | 區分上游錯誤與模型錯誤 |

**判定規則：** 只檢查 L1 已依 §5.5 通過的結論。主要情境使用相同比較及相同指標。

| L2 結果 | 條件 | 記錄 |
|---|---|---|
| 重現 | 差值 95% CI 達到 §5.5 門檻，且退步界線通過 | 「L2 支持此結論」 |
| 方向一致 | 點估計方向相同，但 CI 跨越 0 | 「方向一致，證據不足」 |
| 不支持 | CI 排除 0，且方向相反；或退步界線未通過 | 「L2 不支持」；必須以 pipeline 診斷分析原因 |

L2-S 與 L2-R 分開判定。兩者結果不一致時，兩者都要報告，不得只挑一條。
L2 結論不能改寫 L1 的判定。L2 不支持時，L1 的結論範圍須限定為參數式模擬。

#### 5.8.7 L2 交付物

| 檔案 | 完成標準 |
|---|---|
| `l2_manifest.json` | 路線、模式、區域、情境格點、生成 seeds、工具版本、開發／測試分割、§5.8.5.1 的 `d_plan`／`s_plan`／`n_req`／`n_max`／`n` 及判定規則 |
| `l2_truth/`（I14） | 與方法輸入不同目錄；包含 read→lineage 對應及 spike 跳過紀錄 |
| §5.4 的評估檔 | 加上路線、模式及密度分層欄位 |
| `l2_pipeline_qc.tsv` | §5.8.6 的 pipeline 診斷，含分母 |
| `l2_report.md` | 各結論的 L2 判定、與 L1 的差異、pipeline 診斷及限制 |

#### 5.8.8 樹來源 T-sc：以 scDNA 參考樹為生成藍圖

**目的：** §5.8.2 預設使用本計畫生成器產生的樹，記為 T-gen。T-sc 改用已發表的 scDNA 參考樹。
T-sc 讓 L2 的樹結構、clone 數、prevalence 及 CN 更接近真實腫瘤。
T-sc 是樹的來源，不是新路線。T-sc 的資料集仍走 L2-S 或 L2-R。

**結論範圍：** 「在 k 棵 scDNA 參考樹的結構下，L2 的效果仍存在或不存在」。
T-sc 不支持「在該病人身上有改善」。原病人資料沒有 long reads。
scDNA 樹本身也是推論結果，而且只涵蓋部分細胞及部分特徵。因此，文件中稱它為「參考樹」，不稱為「真樹」。

##### 5.8.8.1 候選來源

**[資料盤點／current]** 依 `research/literature/surveys/patient_sc_longread_2026/A_SUMMARY.md` 及各篇 README。本計畫尚未下載任何補充資料。

| 優先序 | 來源 | 樹及特徵 | 可取得的資料 | 限制 |
|---|---|---|---|---|
| 1 | A03 PA04（胰臟，Tapestri） | 7 群；25 SNV＋8 SMAD4 deletion features；3 samples | 公開 Supplementary Data 的 PA04-SCG_input | 只有 panel 特徵；沒有全基因組 CN |
| 2 | A05（MPAL，DAb-seq） | 每位病人一棵 SCITE mutation tree；9 位病人可作多步分析 | GEO GSE232074 及 Source Data | Targeted panel；沒有 allele-specific CN |
| 3 | A01（卵巢，DLP+ scWGS） | MEDICC2 樹加人工 clade；有 haplotype-specific CN | Synapse syn66399325（processed）；補充表的 clone frequencies | 須確認 processed 資料的取得條件；clade 切法為人工決定 |
| 4 | A04（CK-AML，Strand-seq） | 人工 curated clone trees；homolog-specific SV | 補充表的 subclone 註解 | 主要是 SV；不是 scDNA 的 SNV 樹 |

- 只使用論文正文、補充表及公開 processed 資料。不申請也不使用受控 raw reads。
- HGSOC 的 reference tree 來源未確認。確認是 scDNA 參考樹之前，不納入 T-sc。
- 每個來源的實際檔案、版本及 checksum，在使用前寫入 manifest。

##### 5.8.8.2 藍圖萃取

每棵參考樹萃取成一份藍圖，存成 I16。藍圖只包含以下欄位：

| 欄位 | 內容 | 缺少時的處理 |
|---|---|---|
| Topology | Clone 之間的父子關係 | 不可缺；缺少時不使用該樹 |
| Clone prevalence | 每個 sample 中各 clone 的細胞比例 | 只有單一 sample 時，S=1 |
| Clone 特徵 | 每條邊上的 SNV 及 CN 事件 | 見 §5.8.8.3 |
| Allele-specific CN | 各 clone 在每個區段的 `C_A`、`C_B` | 沒有時，全部設為 1:1 |
| 出處 | 論文、圖表或檔案、版本、萃取日期 | 不可缺 |

**萃取規則：**

1. 依來源的 clone 定義使用 clone。不自行拆分或合併 clone。
2. 正常細胞比例設為 normal lineage。各 sample 的 clone 比例加上 normal 比例須等於 1。
3. 來源有多棵等可能的樹時，每棵都萃取成獨立藍圖，並標記為同一來源。
4. 來源的 doublet、allelic dropout 及低品質細胞不重新生成。這些是 scDNA 的測量誤差，不是腫瘤結構。

##### 5.8.8.3 補足特徵

scDNA 參考樹的特徵很少。例如 A03 PA04 只有 25 個 SNV。這些特徵不足以產生 pair 觀測。因此，生成器須補上合成 SNV。

1. **原始特徵：** 保留來源的 SNV 及 CN 事件，標記 `feature_origin=scdna`。
2. **合成 SNV：** 在每條邊上加入合成 SNV，標記 `feature_origin=synthetic`。
   - 每條邊的 SNV 數量依 HCC1395 pilot 的實測 somatic SNV 密度設定。數量規則寫入 manifest。
   - 位置從 I02 不放回地抽取。來源 SNV 有真實座標時，保留原座標。
3. **CN：** 來源有 allele-specific CN 時，使用來源的值。沒有時，全部設為 1:1。不得借用 HCC1395 的 CN profile。
4. **SNV haplotype 及 HP 對應：**
   - 每個 CN segment 以 0.5 機率把兩個 allele 對應到 HP1／HP2，並記錄結果。
   - 突變 copy 數使用來源的值；來源沒有時設為 1。
   - 只有一條 haplotype 的 copy 數 `C_h ≥` 突變 copy 數時，指定該 haplotype。兩條都滿足時，依 `C_h` 的比例抽樣。兩條都不滿足時，記錄 `haplotype_conflict`，該 SNV 的 reads 全部為 unphased。
5. **Sample 數：** 使用 `min(來源的 sample 數, §5.8.3 可行的 S)`。減少 sample 時，記錄被省略的 sample。

補足後的完整真值寫入 I14。藍圖（I16）與 I14 分開保存，以便追溯哪些部分來自 scDNA。

##### 5.8.8.4 生成、評分及判定

**生成：** 依 §5.8.2 的共同生成規則，以藍圖取代規則 1 的生成樹。之後依 L2-S 或 L2-R 處理。
CN gain 只在 L2-R 生成，限制同 §5.8.3。
每份藍圖至少生成 5 個資料集。各資料集使用不同的合成 SNV 位置及 read 抽樣 seed。

**評分：** 每個資料集報兩種評分母體。

| 評分母體 | 內容 | 用途 |
|---|---|---|
| 全部 SNV（主要） | 原始特徵及合成 SNV | 使用 I14 的完整真值 |
| 僅 scDNA 特徵 | 只保留 `feature_origin=scdna` 的 SNV；樹修剪至這些 SNV，並折疊變空的節點 | 模擬真實論文的驗證方式（同 PhyClone 論文的 HGSOC 修剪及折疊規則，見 S06 E6） |

**判定：** 同一份藍圖的資料集不是獨立病人。藍圖數量也少於 §5.8.5.1 的下限 10。

- T-sc 只作描述性報告。T-sc 不參與 §5.8.6 的 L2 判定。
- 先彙整每份藍圖的資料集，再逐份藍圖報告差值及 95% CI。
- 不把不同藍圖的資料集合併成一個 CI。最後報告「k 份藍圖中，有幾份與 T-gen 的方向一致」。
- T-sc 與 T-gen 方向不一致時，兩者都要報告，並以 §5.8.6 的 pipeline 診斷分析原因。

##### 5.8.8.5 T-sc 交付物

| 檔案 | 完成標準 |
|---|---|
| `tsc_blueprints/`（I16） | 每份藍圖一個檔案；包含 §5.8.8.2 的欄位、出處及萃取規則版本 |
| `tsc_manifest.json` | 來源檔案及 checksum、合成 SNV 數量規則、每份藍圖的資料集數、seeds、路線（L2-S／L2-R） |
| §5.4 的評估檔 | 加上藍圖 ID、評分母體及 `feature_origin` 分層欄位 |
| `tsc_report.md` | 逐份藍圖的結果、與 T-gen 的方向比較、兩種評分母體的差異及限制 |

## 6. 剩餘工作與停止條件

| 未解項目 | 第一版處理 | 後續會新增什麼 |
|---|---|---|
| CN 定向／clonality 證據不足 | F3 標 unknown；相關模型 fallback；C4 不納入 | 可驗證的 orientation 模型及正交 CN／clonality 證據 |
| Allele-dependent tagging | 報 phased rate／VAF 偏差；以模擬及開發資料檢查 | 必要時新增 tagging selection 校正及獨立測試 |
| 共享 molecules／pair 重複證據 | 記錄相依性及 `λ` 敏感度 | molecule-level 生成模型或互斥觀測分組 |
| `C_h≥2`、subclonal CN | 主 C4 排除，另作 stress test | copy／timing-aware linkage 模型 |
| 固定預分群錯誤 | C5 報衝突，不自動拆群 | HP-aware 預分群或可拆分的 assignment 設計 |
| Mutation loss／outlier | 關閉，報衝突及模型範圍限制 | 重新定義 outlier-link target 及完整驗收 |
| Subtree 更新 | 第一版固定為 0 | 跨邊界 pair 的條件 target／權重修正測試 |
| HP3 或其他 ambiguous tags 偏多 | 保留 unphased 並報原因 | 版本及局部 phasing 診斷；不直接解讀為 LOH |
| 多 purity 評估 | 現有完整 HCC1395 僅作單 sample pilot | 各 subsample 的 tagging、實測 cellular purity 及共同變異驗證 |
| 純 normal `t00_n25` | 僅作 error／tagging bias 對照，不進 tree inference | 完成相同 filters 的對照資料及萃取 |
| L2-S 不能模擬 CN gain | gain 只在 L2-R 測試 | 不產生假重複 molecule 的 gain spike-in 方法 |
| L2-S 繼承 I05 的 phasing 錯誤 | Germline phasing 錯誤只由 L2-R 評估 | 另一個具獨立 phasing 真值的背景資料 |
| L2 只有單一背景細胞株 | 結論限於 I13 的資料特性 | 其他細胞株或 chemistry 的背景 reads |
| 單細胞驗證的真實資料只有 short reads | scDNA 樹只作 L2 的生成藍圖（§5.8.8 T-sc），結果只作描述 | 同時有 long-read bulk 及 scDNA 的資料集 |
| T-sc 藍圖數量少、特徵少 | 補合成 SNV；逐份藍圖報告，不作 L2 判定 | 更多公開 scDNA 參考樹；可取得 processed 資料的來源 |

若真值、分母或必要輸入無法確定，停止相應正確率 claim。
仍可交付清楚標記的資料盤點、可用性統計及失敗原因。
所有 C2–C6 效益都須經驗收後才能描述為「已改善」。

## 7. 來源與可追溯性

| ID | Status | Source | Locator／支持範圍 |
|---|---|---|---|
| S01 | current | [data_input.md](data_input.md) | §1–3：BAM 選擇、單 sample、VCF、baseline counts、CN 來源及舊 pair 限制；本次未重驗原始 BAM |
| S02 | current | [evaluation_v1.md](evaluation_v1.md) | §1–5：已採用指標、固定母體、NA、ablation、獨立性及必要輸出 |
| S03 | current | [PhyClone source](research/phyclone_research/PhyClone/phyclone/)；commit `2738324` | `data/pyclone.py:get_major_cn_prior,PyCloneDataPoint.to_likelihood_grid`；`tree/distributions.py:TreeJointDistribution`；`smc/swarm/tree_holder.py:TreeHolder.tree`；`smc/kernels/base.py:_set_log_p_dist`；`mcmc/particle_gibbs.py:_correct_weights` |
| S04 | lab-canonical | [LongPhase-S 定義](/big8_disk/liaoyoyo2001/Knowledge/05_tools/longphase-s.md) | L40–41：DNA fraction；L199–219：完整 HP 詞彙及判讀邊界；L296–302：限制 |
| S05 | lab-canonical | [依輸出類型驗證](/big8_disk/liaoyoyo2001/Knowledge/06_workflows/validation-by-output-type.md) | §1、§4.2、§6–8：輸出契約、分母、HP、CN／purity、獨立性及驗收分級 |
| S06 | current | [PhyClone 實驗與指標](research/phyclone_research/notes/zh-TW/03_EXPERIMENTS_RESULTS.md) | 「指標與統計方法」：AD／V 原始定義的本地整理；開頭段落：論文推理設定（PhyClone 0.7.0、4 chains 等）；E6：HGSOC 的修剪及折疊評分規則 |
| S07 | current | [HCC1395 golden-tree 研究](research/hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/02_tree_reconstruction.md) | §2：候選樹及缺乏完整 SNV assignment 的限制 |
| S08 | inferred | 本文件 §3.3、§4、§5.3–5.8 | 新介面、模型修正、QC 預設值、功能驗收、效果門檻及 L2 規格；均未產生通過結果 |
| S09 | current | [tumor_sample.md](tumor_sample.md) | HCC1395 CRAM 路徑 |
| S11 | current | [A 類 scDNA 文獻整理](research/literature/surveys/patient_sc_longread_2026/A_SUMMARY.md) 及 `research/literature/papers/A0*/README.md` | 各篇的樹範圍、特徵、資料取得方式及限制；支持 §5.8.8.1 表格；補充資料尚未下載 |

本次已查閱實驗室規範及目前 repository。
歷史知識庫 `/bip8_disk/boyu114/bip8_disk_boyu_database` 不存在，狀態為 `not-found`。
本次未以歷史資料補造實驗結果，也未將未追蹤的設計文件視為已完成實作。
