# Long-read 特徵（HP／PS／同 read 共現）建演化樹：多 agent 搜尋總結

日期：2026-10-19。4 個 subagent 平行搜尋。原始報告在 `raw/`：

| 檔案 | 搜尋角度 |
|---|---|
| `raw/search_A_cooccurrence.md` | 同 read SNV 共現、read phasing、PS／HP tag、mutation pair 排序 |
| `raw/search_B_haplotype_cn.md` | phased long read 的 haplotype-specific CN、CNV／WGD timing |
| `raw/search_C_singlecell_methyl_sv.md` | single-cell long read、methylation lineage、SV phylogeny |
| `raw/search_D_repos_preprints.md` | GitHub、2023–2026 preprint、各 lab 專案 |

納入規則：一定要有建樹或排序步驟。只做 VAF clustering、Fishplot 或人工樹都不算。已排除 M03、B06、B08、B02，不列入。

## 1. 結論

- **沒有任何已發表的腫瘤 clone tree 方法把 long-read HP／PS 或同 read 共現放進 tree likelihood 或 prior。** 4 個 agent 各自得到這個結論。
- 現有工具只做到「產生 phased feature」或「把變異放到外部給定的樹上」，沒有用 phasing 約束 topology。
- longphase-s 的 HP1-1／HP2-1 標籤加上 Wakhan 的 subclonal hp1/hp2 CN，已經是現成的輸入。缺的是把它們接進 PhyClone 的模型。這是本研究可以佔的新穎點（分析推論）。

## 2. 有建樹或排序步驟，且 long read 有角色

| 項目 | 狀態 | long-read 特徵 | 角色 | 建樹方法 | 真值 |
|---|---|---|---|---|---|
| B04 Sakamoto 2022 肺癌 | 已收錄 | 同 read SNV pair order（WhatsHap） | topology_constraint（只在 S14） | PyClone-VI → ClonEvol 候選，long read 選 linear model | scDNA 局部（S8、S20） |
| B01 Liu … Kolmogorov 2026 melanoma sublines | 已收錄 | ONT SNV；phased SV、Wakhan CN 只在建樹後放置 | tree_input（只有 SNV genotype） | ScisTree；TreeHarmonizer 把變異放到 MRCA | 無 |
| **Hackett … Blundell 2026**（bioRxiv `10.64898/2026.02.23.707349`） | 已收錄為 [B09](../../papers/B09_pcdh_methylation_barcode_2026/README.md)（2026-10-20） | WhatsHap／LongPhase 把 read 分 HP；每條 read 的 PCDH CpG 5mC | **tree_input** | read × CpG 矩陣 → kNN 補值 → Hamming 距離 UPGMA | scWGS 樹；topology 相近，branch length 不符 |
| BitPhylogeny（Yuan … Beerenwinkel, Genome Biol 2015） | 已收錄為 [M08](../../papers/M08_bitphylogeny_2015/README.md)（2026-10-19） | 每條 read 的多位點 methylation pattern | transferable_only | read 當成 TSSB mixture tree 的一次抽樣 | 模擬＋病人 |
| TreeClone M02（2019） | 已收錄 | 短讀 SNV pair | transferable_only | pair likelihood＋tree prior，MCMC；只限 CN-neutral | 模擬 |

註：

- Hackett 的材料是 MPN 病人與健康人的血液，不是實體腫瘤。論文沒有公開 code。2026-10-20 已讀全文與補充資料，見 B09 README。
- Agent A 把 B04 標成 validation_only。這是漏看補充資料：Fig. S9c–d 顯示 long read 讓 S14 選 linear model。repo 保留 `topology_constraint`。
- bioRxiv 從 2025-12-01 起改用 `10.64898` 前綴（openRxiv 公告），所以這個 DOI 格式正確。

## 3. 邊緣或不納入

| 項目 | 不納入原因 |
|---|---|
| Wong … Wei 2025 ecLego3（GBM ecDNA，ONT） | 畫了 ecDNA phylogeny，但沒寫演算法，視為人工樹 |
| SVCFit（Karchin lab, bioRxiv 2025） | 用 SV CCF 建樹，但用短讀。long read 只出現在 Discussion |
| PairClone 2019 | TreeClone 前身，不建樹 |
| Foltz … Ding 2024 myeloma（10x linked read, SomaticHaplotype） | phased pair 只用來解讀資料，不建樹。這篇和已排除的 B02（Liu 2021）不同 |
| Espejo Valle-Inclan 2025 osteosarcoma、ecSingle 2026 | long read 只做驗證 |
| SMOOTH-seq、Hård 2023、scNanoGPS、nanoranger、LongSom | 只做 genotyping／clustering，不建樹 |
| CNVeil 2026、Refphase 2023 | haplotype-specific CN，但不用 long read |
| Yuelin Liu 2025 UMD 博士論文、NCM 2023 talk | 用 phased CpG 建 sublines 樹，但沒找到 code 或論文版本 |

## 4. 產生 phased feature 的工具（都不建樹）

| 工具 | 輸出 | 對 PhyClone 的用途 |
|---|---|---|
| longphase-s（bioRxiv 2025-11） | somatic haplotag HP1-1／HP2-1、phase-aware purity | SNV 所在的 parental haplotype。原文把 subclonality 聯合模型列為未來工作 |
| LongPhase-TO（bioRxiv 2026-09） | tumor-only germline＋somatic 聯合 phasing、LOH、tumor DNA fraction | 一層 lineage（HP1 → HP1-1）。tumor DNA fraction 不等於 cellular purity |
| Wakhan | haplotype-specific CN；`--copynumbers-subclonal-enable` 輸出 subclonal hp1/hp2 CN | 取代 PhyClone 的 major/minor CN，保留 HP 對應。論文說它不建模 clone 混合 |
| Severus、SAVANA | phased somatic SV；SAVANA 另給 allele-specific CN、purity | CN breakpoint 與 SV 事件 |
| PRCGAP（Sakamoto … Shiraishi, bioRxiv 2026） | 把 SNV／SV／CN／methylation 指派到 haplotype | 資料含 HCC1954，和本研究重疊 |
| TreeHarmonizer | 把變異放到既有樹的 MRCA | 可當 baseline：「先建樹再放 HP」 |

## 5. 新穎點提案：HP-aware PhyClone（分析推論，尚未實作）

下面 3 個元件可以分開做，也可以組合。都以 PhyClone 為基線。PhyClone 的 prior 是 FS-CRP，不是 TSSB。

1. **HP-specific multiplicity emission**
   - 現況：PhyClone 用 major/minor CN 列舉 genotype，不知道 SNV 在哪個 allele。
   - 改法：用 longphase-s 給的 HP 和 Wakhan 的 `C_h`，把 multiplicity 限制在 `1 ≤ m ≤ C_h`。只用該 HP 的 read 算 VAF：`VAF_h ≈ m / C_h × (tumor fraction on h)`。
   - 效果：減少 genotype 歧義，並能判斷 mutation 發生在 CN gain 之前或之後（timing）。
2. **同 read 共現的 pairwise likelihood（TreeClone 式）**
   - 對同一 PS、同一 HP 的 SNV pair，計算 4 類 read 數：11、10、01、00。
   - 如果 i 是 j 的祖先，01（有 j 沒 i）只能來自錯誤。如果 i、j 是兄弟，11 只能來自錯誤。
   - 把這一項乘進 PhyClone 的 tree likelihood。在 SMC／PG 加入節點時更新。PhyClone 以 cluster 為單位，所以要在 cluster pair 層級加總。
   - 只用 `C_h = 1` 且沒有 CN breakpoint 的區段（見 B04 README 的 C4）。沒有 11 read 的稀疏 pair 不要硬判 branching。
3. **read 當成抽樣單位（BitPhylogeny 式，進階）**：每條 phased read 帶一組 SNV pattern，直接指派到 clone。這比 pair 計數用到更多資訊，但計算量大。

驗證方式：

- 用模擬資料測試。
- 用 PhyClone benchmarking 資料集比對。
- 在 HCC1395 的多個 `tX_nY` subsample 上檢查樹是否穩定。
- `tX_nY` 是 nominal purity，不是實測值。與 H01 golden tree 比對時，只能當部分佐證。

## 6. 未驗證與後續

- AACR 2025 Abstract 5049（Wakhan，提到 H1437 subclonal CN）回傳 403，內容只來自搜尋摘要。
- SPLONGGET 摘要提到 "clonal dynamics"，但不確定有沒有建樹。需要讀全文。
- Nature Communications 版本的 B01 需要登入，沒有抓到。
- PoreMeth2、Decoil、ULI-HiFi 抓取失敗。
- 是否把 Hackett 2026 加進 `paper_categories.tsv`：它有 long-read phasing 當 tree input，也有 scWGS 真值樹，形式上可歸 C3b。這需要使用者決定。
