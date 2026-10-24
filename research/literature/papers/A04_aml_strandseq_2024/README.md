---
paper_id: A04
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_patient_sc_reference"
sc_truth_strength: "reference_tree"
title: "Single-cell multiomics analysis reveals dynamic clonal evolution and targetable phenotypes in acute myeloid leukemia with complex karyotype"
year: 2024
doc_type: "application"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["Strand-seq scTRIP (Illumina NextSeq)", "OGM validation"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "patient_scdna_reference_tree"
single_cell_tech: ["Strand-seq scTRIP", "CITE-seq"]
input_is_single_cell: true
tree_type: ["clone_tree", "cn_event_tree"]
cross_tags: ["haplotype_specific_cn", "structural_variant", "strand_seq_phasing", "pdx"]
keywords_en: ["ck-aml", "acute myeloid leukemia", "strand-seq", "sctrip", "chromosome-length haplotype", "structural variants", "chromothripsis", "bfb", "optical genome mapping", "pdx", "haplotype-aware copy number"]
keywords_zh: ["急性骨髓性白血病", "複雜核型", "單細胞結構變異", "染色體長度單倍型", "染色體碎裂", "人工整理樹"]
summary_zh: "Strand-seq 單細胞 SV+單倍型建 CK-AML 人工 clone 樹。"
category_index: "../../PAPER_CATEGORIES.md"
---

# A04 — CK-AML 的 chromosome-length haplotype 與單細胞 SV 樹

Leppä, A.-M., Grimes, K., Jeong, H. et al. **Single-cell multiomics analysis reveals dynamic clonal evolution and targetable phenotypes in acute myeloid leukemia with complex karyotype.** *Nature Genetics* **56**, 2790–2803 (2024). DOI: [10.1038/s41588-024-01999-x](https://doi.org/10.1038/s41588-024-01999-x)。2024-11-25 online；保存正式期刊版。

[官方正文](https://www.nature.com/articles/s41588-024-01999-x) · [官方 PDF](https://www.nature.com/articles/s41588-024-01999-x.pdf) · [本機 PDF](paper.pdf) · [完整文字](paper.txt)

## 為何重要；分類邊界

第一類 A，而且是與本 repo 的 **haplotype-aware CN/SV** 最直接相關的病人研究之一。8 名 primary CK-AML 病人的初始/救援治療樣本有 542 個 single-cell genomes；加入 5 個 matched PDX 和 2 個 relapse/refractory samples，總計 855 genomes。直接病人、PDX 和縱向樣本必須分層，不把 855 都算初始病人細胞。

關鍵是 **Strand-seq 並非 long-read sequencing**。Methods 明寫 Illumina NextSeq 500、75-bp paired-end；染色體長度的 haplotype 由 template-strand inheritance 跨細胞解出。OGM 量測 ultra-long DNA molecules，也不是 ONT/PacBio sequence reads。故它符合 A，作為 B 的相鄰技術/方法啟發討論，不能充作一篇長讀推樹論文。

PDF 實體頁從 1 起算：p.1–2 cohort 與 Fig.1；p.3 Fig.2 樹圖、p.4（印刷 2793）圖說「Manually curated clonal trees」與解讀；p.15 Methods「Strand-seq-based structural variant discovery」和 library protocol；p.17 Data/Code availability。Extended Data Fig.1/5 補 homolog-specific rearrangements 與 amplification；本文並未展示以 `HP`/`PS` 欄位直接當 clonal labels。

## 從 phasing 到 clonal tree

scTRIP 結合 100-kb bins 的 read depth、Watson/Crick strand orientation、chromosome-length haplotype，以 Bayesian segment genotype likelihood 判斷 SV，後續人工檢查。細胞依共享 SV 分群；通常至少 3 個 cells 共享一組 SV 才定 clone，但對清楚的 progeny 可接受更少 cells。Fig.2 的 clone hierarchy 是**人工整理的樹**，不是一個經外部真值驗證的自動推樹器。

8 個初始病人中 2 例 monoclonal、3 例 linear、3 例 branched；75% 有多個 subclones。克隆共享與額外取得的 deletions、duplications、inversions、translocations 可推其祖先順序。haplotype 提供重要辨識力：例如同一 homolog 上的 clustered rearrangements 支持 chromothripsis，inverted duplication＋terminal deletion 支持 BFB。總 CN 相同仍可有平衡 SV 或不同 homolog 事件，僅靠 total-CN distance 會丟失這些關係。

## 能當什麼樣的真值

Strand-seq genomic evidence、部分 OGM/M-FISH 正交驗證及真正縱向樣本，使其比 RNA-derived CN tree 更接近 user 所需的病人答案；但原始病人細胞經一次細胞分裂的 BrdU culture（約 52–62 h）後選取，可能偏向可存活/可增殖細胞。PDX engraftment 的選擇壓力也會改變 clonal composition，不能把 PDX 頻率當病人原位頻率。樹的人工選擇、SV resolution 和 rare-clone 門檻仍是 uncertainty。

本篇重點是 haplotype/CN/SV，不是 bulk purity 或 VAF→CCF 的完整校正研究；Fig.2 的 CF 是取樣細胞中 clone fraction。CN loss 及 TP53 等背景可與 LOH 相關，但本文不是獨立 LOH accuracy benchmark。H1/H2 是 homolog 座標，沒有 parental orientation 就不可直接叫父母源；亦不能把它等同本 repo 每個 phase set 的 HP1/HP2。

## 資料與重現入口

Strand-seq/CITE-seq：EGA **EGAS00001007436**（受控）；bulk RNA：ArrayExpress **E-MTAB-14420**。[EGA study](https://ega-archive.org/studies/EGAS00001007436) · [scNOVA](https://github.com/jeongdo801/scNOVA) · [Mosaicatcher](https://github.com/friendsofstrandseq/mosaicatcher-pipeline) · [StrandPhaseR](https://github.com/daewoooo/StrandPhaseR) · [PloidyAssignR](https://github.com/lysfyg/PloidyAssignR)。supplementary tables 提供病人、SV 與 subclone 註解；本次只取得論文 PDF。

## 對 C0–C6 的改進與最小實驗（尚未實作）

C0 可加入 homolog-specific SV/CN feature 的來源、resolution、confidence，與 LongPhase read tags 分開。C1 schema 應包含 phase-block orientation 與 event identity，避免不同 PS 的 HP1 被當同一 homolog。C2 用 `C_h` 限 multiplicity 的動機很強，但平衡 rearrangements 也能定 clone；C3 的 likelihood 不應因 total CN 相同就假定同一 clone。C4 首版限制同 PS/同 HP/`C_h=1`，不能直接跨染色體延伸。C5 可測 total CN、allele-specific CN、再加 SV 的分群差異。C6 應輸出「同 total CN 不同 homolog/SV」的衝突，讓人工 curate 能回溯。

最小 benchmark：先挑 Fig.2 一個 linear case 與一個 branched case，以 curated SV clone matrix 作外部參考，分別隱藏 homolog、只保留 total CN、再還原 homolog/SV。評估錯併 clone、ancestor-pair recovery 和 rare-clone sensitivity，並按 primary/PDX/relapse 分開報告。若以此矩陣模擬 ONT 分子測 C4，必須標為 patient-derived genotype simulation；Strand-seq 自身並不提供 long-read pair-count 的實測增益。
