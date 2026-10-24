---
paper_id: B04
category: "C3b"
category_label: "single-cell 真值樹 × long-read 特徵"
subtype: "c3b_topology_constraint_sc_partial"
sc_truth_strength: "partial"
title: "Phasing analysis of lung cancer genomes using a long read sequencer"
year: 2022
doc_type: "application"
material: "human_patient"
platform_class: "long_read_feature"
platform_detail: ["ONT PromethION bulk WGS (pair order)", "Illumina WGS (VAF, FACETS -> PyClone-VI -> ClonEvol)"]
long_read_role: "topology_constraint"
long_read_features: ["same-read somatic SNV co-occurrence (pair order)", "WhatsHap germline phasing/haplotag", "long-read SV", "methylation", "RNA"]
single_cell_truth: "sc_partial_validation"
single_cell_tech: ["10x Chromium scDNA-seq (NovaSeq 150bp PE), cases S8/S20"]
input_is_single_cell: false
tree_type: ["clone_tree", "local_order"]
cross_tags: ["read_cooccurrence_model", "haplotag", "topology_selection", "priority_intersection"]
keywords_en: ["nsclc", "lung cancer", "oxford nanopore", "promethion", "whatshap", "haplotype phasing", "mutation pair order", "read co-occurrence", "clonevol", "pyclone-vi", "facets", "scdna-seq", "10x chromium", "topology selection"]
keywords_zh: ["肺癌", "長讀定序", "單倍型定相", "突變先後順序", "單細胞DNA驗證", "拓樸篩選"]
summary_zh: "long read 同 read 排序選出 S14 線性樹；scDNA 局部驗證。"
category_index: "../../PAPER_CATEGORIES.md"
---

# B04｜真實肺癌病人：long-read mutation partial order、候選 topology 篩選與 scDNA 驗證

## 論文與分類結論

Sakamoto Y, Miyake S, Oka M, et al. **Phasing analysis of lung cancer genomes using a long read sequencer.** *Nature Communications* 13, 3464 (2022). DOI：[10.1038/s41467-022-31133-6](https://doi.org/10.1038/s41467-022-31133-6)。本地為正式出版版，17 頁；另保存 58 頁官方 Supplementary Information。查核日期：2026-10-15。

**這是目前本批交集搜尋最接近目標的研究：同一篇有真實病人 ONT long reads、同病人 scDNA-seq，而且 long-read pair order 真的協助排除演化樹候選。** 但必須分開兩個事實：有直接 topology 篩選示例的病人是 S14；做 scDNA 驗證的病人只有 S8、S20。不能把它寫成「以 scDNA 完整標準答案驗證 long-read 全樹重建」。scDNA 提供的是 mutation、SV 與 CN 子群的局部佐證；全樹仍由 bulk clustering、ClonEvol 候選與 long-read 局部順序組合推論。

| 查核軸 | 結果 |
|---|---|
| 樣本 | 20 名日本 NSCLC 真實病人，手術冷凍腫瘤與 matched-normal；不是 cell line／PDX |
| long features | ONT PromethION bulk WGS、實際跨兩個 somatic SNV 的單分子 reads、germline haplotype blocks；另有 long-read RNA／methylation |
| single cell | S8、S20 的 10x Chromium scDNA-seq，由 NovaSeq 150-bp paired-end 讀出；不是 scRNA 替代 DNA |
| 樹的輸入 | short-read somatic SNV VAF、FACETS CN／purity → PyClone-VI clusters → ClonEvol；long-read partial orders 篩選部分候選 |
| ground truth 強度 | 真實病人、同病例 scDNA 支持；沒有獨立且完整的已知 lineage tree |
| 建議定位 | 優先交集／橋接文獻；不能當完整 long-read-tree benchmark truth |

## 實際讀到的方法與證據

主文 p2–4 Fig. 1：matched-normal short-read WGS 先用 GATK 建 germline heterozygous SNP；tumor／normal ONT 各自以 WhatsHap 1.0 建雙 haplotype blocks，然後 haplotag，再將 somatic mutations 指派到背景 haplotype。這是 germline homolog phasing，尚未等於跨整個 block 的 somatic clone phasing。主文 p6 甚至明講沒有分析距離大於 read 長度的 somatic mutation 關係。p15 也說不同 block 的 allele 數字不具共同意義，正是本 repo 必須保留 `PS` 的理由。

主文 p6、p7 Fig. 3f：單條 read 同時覆蓋 NKAIN4 3′UTR 與 BIRC7 exon mutation，觀察 single-mutant／double-mutant 型態，推定先後。20 個病例每例平均 69 對可排序 mutation pairs，範圍 0–649。bulk 分析有 44 對被分到不同 clones，並非所有 pair 都能用 bulk VAF 分開。Fig. 3d 的 EGFR 雙突變主要只看到 wild type／double mutant，作者保留同時發生或 single-mutant clone 已消失的多種可能；**只有 `11` 不足以確認兩個 mutation 同時發生，也不提供唯一順序。**

最關鍵證據在 **supplement p19–20 Fig. S9c–d 與 Note**：S14 的 ClonEvol 同時存在 branched、linear model，作者因 long reads 直接支持 C2→C3 而選擇 linear。這比「long reads 只做 upstream variant calling」更直接，但只對局部 mutation／cluster 關係施加約束。S20 的 Fig. S9e–f 展示 PDGFD intron 4.9-kb pair；C1 的 CCF=1、C2=0.323，其順序與 long reads 一致。

主文 p14–15 與 **supplement p21–26 Fig. S10**：scDNA 的目標回收設定各 500 cells；實際 Table S7（p48）列 S8 原始 178、QC 後 138，S20 原始 420、QC 後 376。CNV estimated resolution 約 0.40、0.43 Mb，分析抽取 20-kb windows，用 Manhattan distance＋complete linkage 分群。SNV read 萃取使用 baseQ≥20、MAPQ≥60，排除 secondary／supplementary／duplicate reads；SV 則另從 junction reads 與 cell barcode 回推 mutant cells。

**資料內部 conflict：** Fig. S10a caption（p25）將 138／376 對應的 S8／S20 寫反。本筆記採 **圖 p21 的清楚標籤與 Table S7 p48**：S8=138、S20=376，兩者相互一致。沒有自行把表格數字換掉。

supplement p26 Note 說明：可由 scDNA 覆蓋的 long-read-order pairs 在 S8、S20 各只有 **2、13 對**，展示其中兩例。minor mutation 並非每個細胞都看得到，作者明示低 coverage／allele dropout，需彙整多細胞。S10e 顯示 minor mutation 只在一個細胞子群；S10f 顯示 minor mutation 分布在多個 CN 子群，故它可能早於造成 CN 子群差異的事件。這是有價值的 partial-order validation，不能把缺少 alt 的細胞直接標成真陰性，也不能將 CN dendrogram 直接當 SNV evolution tree。

## purity、VAF、CCF、CNV／LOH、HP／PS 的關係

主文 p15 用 FACETS 估 CN／purity，作 PyClone-VI 的輸入，然後 ClonEvol 建候選；這些 CCF 來自模型，並非 scDNA 的直接計數 truth。主文的 purity fallback 原句寫「half of the average of VAFs」，本筆記保留為方法描述疑點，不將此規則推薦給本 repo。

SNV 指派 haplotype 的門檻為某一 HP 至少 3 條 mutant reads、另一 HP 至多 1 條（p15）。低 VAF 病例的可 phasing 比例下降，VAF≥0.2 後比例改善；因此只分析可 phased variants 會富集較高 CCF／purity 的事件，必須報告 missingness。S14 的 PTEN deletion／LOH（p6、Fig. 3e）也直接說明：local HP2 可跨 SV 連到另一 block 的 HP1，數字翻轉不是 biological parental switch。amplification、多重同源 copy 或 mutation loss 又可能破壞由 molecule pattern 推 cell lineage 的簡單對應。

## 對本 repo 的具體用途與最小實驗

以下是**本筆記分析推論**，不是論文已實作的 PhyClone 改動。依據 repo `plan.md` §4.1–4.7：

- **C0／C1**：輸出每 pair 的 read IDs、`PS`、HP、兩位點實際 allele、`n11/n10/n01/n00` 與 CN eligibility；另報每 sample 可排序 pairs／全部 pairs，避免只報成功案例。
- **C2／C3**：借用 phased-mutation success versus VAF／purity 分層圖做 feasibility；本論文沒有驗證 HP-specific likelihood 可以解 multiplicity／CCF 歧義。不可把 >99% germline concordance 當成 somatic HP assignment accuracy。
- **C4**：S14 的 branched-versus-linear 例子是最直接的生物學動機。先在同 `PS`、同 HP 且該 HP 的 `C_h=1`、無 CN breakpoint 的 pair 使用軟 likelihood；對無 `11` 的稀疏資料避免硬判 branching。
- **C5**：保留未被 bulk 分開的 pair，以檢查固定預分群是否把具有順序訊號的兩個變異壓在同 cluster。
- **C6**：輸出每個支持／衝突 pair 對應的 posterior ancestral probability，附 CN／coverage／PS 限制，不能只輸出一棵無不確定性的樹。

最小 ablation：固定 SNV set、clusters、CN、purity、seeds，比較 baseline、`+C4 真實 pair`、`+C4 打亂 pair 對應`，並分 `C_h=1` 與放寬 CN 的敏感度組。先看 held-out scDNA-supported pair 的 ancestral direction、credible-set coverage 與不合法 link 比例；不能把這篇資料硬轉成完整 tree edit distance truth。若取不到受控 raw data，先重畫 Fig. S9／S10 提供的 published constraints，做規格 fixture，不宣稱完成獨立實驗。

## 資料、檔案與重現定位

新產生的 clinical long WGS／scDNA／RNA 在 **JGAS000349**，需要 JGA 受控申請；沿用資料 **JGAS000065**（JGAD000252、JGAD000253）亦受控。HG002 QC 為公開 **DRA012759**。來源：主文 p16 Data availability。

| 本地檔 | 來源／頁數 | SHA256 |
|---|---|---|
| [paper.pdf](paper.pdf) | [官方 PDF](https://www.nature.com/articles/s41467-022-31133-6.pdf)，17 頁 | `e13aa7957455432171cf39edd4fee9c09ad257d4f53328d9b48e58fddcd12e21` |
| [supplement.pdf](supplement.pdf) | [官方 MOESM1](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-022-31133-6/MediaObjects/41467_2022_31133_MOESM1_ESM.pdf)，58 頁 | `d30f94ed901c5f886dd89d50ea264866c5b221498610c43effa51dc807e053de` |

[paper.txt](paper.txt)、[supplement.txt](supplement.txt) 均以 `pdftotext -layout` 產生，保留 form-feed page breaks。已用 `file`／`pdfinfo` 驗真，並實際渲染核對 Fig. S9 p19、Fig. S10 p21。上述頁碼均為 PDF physical page，從 1 起算。
