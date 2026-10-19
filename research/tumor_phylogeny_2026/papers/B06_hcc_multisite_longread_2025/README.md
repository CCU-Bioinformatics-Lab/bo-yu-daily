---
paper_id: B06
category: "C2"
category_label: "long-read 特徵輔助建樹（無 single-cell 真值）"
subtype: "c2_sample_tree_sv"
sc_truth_strength: "none"
title: "Multisite long-read sequencing reveals the early contributions of somatic structural variations to HBV-related hepatocellular carcinoma tumorigenesis"
year: 2025
doc_type: "application"
material: "human_patient"
platform_class: "long_read_feature"
platform_detail: ["ONT WGS ~37x", "Illumina WGS"]
long_read_role: "sample_tree"
long_read_features: ["read-spanned SV breakpoints", "HBV-host chimeric reads", "long-read SV VAF for timing"]
single_cell_truth: "none"
single_cell_tech: []
input_is_single_cell: false
tree_type: ["sample_tree"]
cross_tags: ["structural_variant", "multi_region", "sv_timing"]
keywords_en: ["oxford nanopore", "structural variants", "sniffles2", "jasmine", "hbv integration", "hepatocellular carcinoma", "multi-region sequencing", "neighbor joining", "sample phylogeny", "svclone", "mutationtimer", "facets", "sv timing"]
keywords_zh: ["長讀定序", "結構變異", "B型肝炎病毒嵌入", "肝細胞癌", "多區域採樣", "樣本演化樹"]
summary_zh: "ONT SV 建多區域 sample tree；沒有 single-cell 真值。"
category_index: "../../../PAPER_CATEGORIES.md"
---

# B06 — 多部位肝癌：ONT SV sample tree 與 CN-aware SV timing

Zeng T, Liao H, Xia L, et al. **Multisite long-read sequencing reveals the early contributions of somatic structural variations to HBV-related hepatocellular carcinoma tumorigenesis.** *Genome Research* 35(4), 671–685 (2025)，2025-03-04 online。DOI：[10.1101/gr.279617.124](https://doi.org/10.1101/gr.279617.124)。

[期刊入口](https://genome.cshlp.org/content/35/4/671) · [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12047258/) · [本地正式 PDF](paper.pdf) · [全文文字](paper.txt) · [補充圖 PDF](supplement.pdf) · [補充文字](supplement.txt)。主文 15 個實體頁，p1 對應期刊671；補充圖23頁，各自從1計。

## 收錄理由與材料範圍

這是一篇真正把 **long-read-derived SV 訊號送進 phylogeny** 的病人研究，而不是只有在 discussion 提到長讀。5 位 HBV-positive HCC 病人，共42個樣本：27個 tumor regions、10個相鄰非腫瘤肝組織、5個 matched blood。37個組織樣本的 ONT 平均 depth 約36.72×、read N50平均22.41kb；另有 Illumina WGS偵測 SNV，部分樣本有 ONT RNA-seq。[主文p1–2、Fig.1 p3]

**本研究沒有 single-cell sequencing；樹的葉是採樣區域，不是細胞或解混後的 clone。** 組織仍可能 polyclonal，不能把鄰近組織與腫瘤的共同 branch 直接翻成某兩個純 clone 的 ancestry。血液才是主要 constitutional normal；鄰近纖維化肝臟存在 somatic mosaicism，不能一律當 germline normal。

## 特徵如何進入樹與 timing

流程分成兩個問題，不能混為一個 joint generative model。

**Sample tree。** ONT對 GRCh38＋21個HBV genomes比對，Sniffles2抓 breakpoint與supporting reads；候選somatic SV須有至少3條支持、≥50bp，matched blood無支持，再經PON、mapping/VAF filters與人工檢查。Jasmine跨樣本合併SV identity。將genome切500-bp bins，按SV breakpoints與SNVs各自建立binary presence/absence matrix，分別以neighbor joining建sample phylogeny。[p11–12，Methods「Identification of somatic SVs」「VCF merging」「Phylogenetic tree construction」]

**SV CCF與相對CN timing。** 作者改造SVclone，使用long-read split/spanning support與跨breakpoint的reference reads估VAF，並在其long-read適配中省略原本normal-read gain adjustment；再結合somatic SNV、FACETS CN、purity/ploidy做coclustering。MutationTimeR將SV歸為early clonal、clonal unspecified、late clonal或subclonal。[p12–13，Methods「Timing of somatic SVs」；Fig.5C p8、結果p9]

這裡的「省略調整」是作者針對SVclone計數單位的修改，**不能推廣成 long-read VAF 在 CNA 區域不需要 CN correction**。本文後續仍整合CN、purity與ploidy。該模型沒有本repo所設計的PS/HP-specific SNV likelihood，也沒有用同read `n11/n10/n01/n00`聯合抽樣整棵clone tree。

## 實際讀到的演化證據

主文p4–5與 **supplement p14 Fig.S7** 顯示每個病人各一組SV-based和SNV-based樹。已渲染核對此頁：五名病人的組織tips與germline root清楚可見；SV樹有灰色共同branches連結tumor與adjacent nontumor，SNV樹呈現不同分離模式。這支持不同variant類型捕捉不同演化層次，並非已知祖先細胞的直接觀察。

主文Fig.5C展示HBV integration／SV被推為copy gain以前的early clonal事件。對本repo而言，重要的是同時保留 **mutation identity、CN background、VAF、CCF與event timing**，而不是只將位點按VAF排序。樹推斷與timing彼此相關，但sample distance tree本身沒有替所有SV提供唯一發生時間。

作者對早期SV與HCC發生的關係提出生物學解釋；本筆記只把共享SV與推定timing當作證據，不將鄰近組織的橫斷取樣等同前瞻追蹤或確定因果。主文Discussion p9–11也保留額外validation、sample size與depth限制。

## purity、VAF、CCF、CNV/LOH、phase 的邊界

FACETS從short-read tumor-normal資料估purity、ploidy與allele-specific CN；CNV事件分析排除小於100kb的變化。SV VAF的分母則是有效覆蓋breakpoint的molecules，不能直接跟SNV單鹼基pileup分母合併。SV支持門檻、normal depth、repeats與Jasmine合併規則都會影響presence matrix，absence不必然等於未繼承。

本文重點不是germline phasing、phase set或haplotype-resolved clone inference；不要因native long reads能跨多段就補寫HP/PS模型。LOH對CN與timing當然相關，但本文不提供獨立LOH真值，也沒有處理所有subclonal CNA ambiguity。對單一sample的clone mixtures而言，binary sample tree不足以取代PhyClone的CCF sum constraints。

## 對本 repo C0–C6 的用途與最小比較

以下為 **inferred** 建議，尚未在repo實作：

- **C0/C1**：未來增加SV時，另存breakpoint pair、orientation、callability、split/spanning molecule IDs、SV merger版本；不能把SV支持reads直接當作SNV counts。GRCh38＋HBV reference與既有CRAM reference的差異要保存。
- **C2/C3**：設計SV multiplicity／copy-gain timing的獨立觀測模組，保留purity/ploidy來源與uncertainty；不要將已估CCF再當無誤差observed CCF輸入同模型。
- **C4**：SV-based sample tree可作另一類證據對照，不直接充當bulk clone tree truth。跨junction的long read若用於SNV linkage，須另建能處理rearranged coordinates的模型，不能直接解除現有single-primary、同PS、`C_h=1`條件。
- **C5/C6**：比較SNV與SV推得關係的衝突，輸出CN/coverage/normal來源是否能解釋差異；保留sample tree與clone tree兩種輸出語義。

最小benchmark：從公開processed mutation matrices重現Fig.S7，以matched callability篩選後比較SNV-only與SV-only sample relations；再在同病人多區域資料做leave-one-region-out，檢查shared-SV與timing的穩健性。若以已知clone genomes模擬多區域bulk，再比較PhyClone與新增SV evidence，必須另給生成clone tree。對真實本文資料只報published-tree reproducibility、held-out breakpoint consistency與timing sensitivity，不報「已知病人完整樹accuracy」。

## 資料與 PDF 來源

Data access在主文p13：GSA-Human **HRA007177**；[作者程式 ONT_SV](https://github.com/tianfuzeng/ONT_SV)。patient raw reads依GSA-Human正式申請規則取得，本次未下載。不是把BioProject／project ID猜成可直接下載的病人資料。

正式PDF經NCBI新版官方公開AWS資料集取得，metadata標記`is_manuscript=false`。詳見 [PDF_PROVENANCE.md](PDF_PROVENANCE.md) 與保存的 [oa_metadata.json](oa_metadata.json)。

| 檔案 | 官方實際下載來源 | SHA-256 |
|---|---|---|
| paper.pdf，15頁 | [PMC12047258.1.pdf](https://pmc-oa-opendata.s3.amazonaws.com/PMC12047258.1/PMC12047258.1.pdf) | `5e69c92f8dfa6db09d8a0911b8e8d7ed58242017feefeb6f1f9eaa8b815d513a` |
| supplement.pdf，23頁 | [Supplemental_Figures.pdf](https://pmc-oa-opendata.s3.amazonaws.com/PMC12047258.1/Supplemental_Figures.pdf) | `923c7a6752579c1dc3fdf4cfc1a39d57d28122983068fac562800ca48e17132b` |

兩檔均通過PDF magic、`file`、`pdfinfo`與官方MD5核對；已實讀Methods、Fig.S7與timing相關段落。下載失敗的HTML另名保存，不列作PDF。
