# B 類綜整：長讀、長分子與 haplotype 特徵如何真的影響演化推理

查核日期2026-10-15，近期範圍2021–2026。B主選三篇為 **B01、B04、B07**；B03與B05為另外保留的橋接／比較論文。各篇連結通向獨立閱讀筆記及本地PDF。所有「本repo建議」皆屬inferred，不表示已完成模型修改。

## 必須先說的篇數與證據強度

**這三篇不是三個實測ONT/PacBio完整clone-tree方法。** 主選中兩篇使用ONT（B01/B04）、一篇使用population-phased short-read scRNA（B07）。B04的直接貢獻是局部mutation順序與候選樹排除。若條件要求主選都用實測long reads重新估整棵deconvolved clone tree，本次搜尋仍未找到足額證據，不能用上游variant/phasing paper或同論文的preprint補數。

更嚴格的「同一真實病人有獨立single-cell完整參考樹，且long-read獨有特徵用於全樹推理」也尚未閉環。B04最接近，但選擇linear/branched topology的S14與scDNA病例S8/S20不同；B01是小鼠細胞株單細胞衍生培養；B07雖有真病人single-cell，是短讀。此限制是文獻現況與本次證據的界線，不是把single-cell推論樹當成不存在。

## 分層選文與直接入樹證據

| 論文／層級 | 哪一層資料進入演化推理 | 是否重新估topology | single-cell與真值限制 | 最適合本repo的用途 |
|---|---|---|---|---|
| [B01 melanoma 2026](../../papers/B01_melanoma_longread_2026/README.md)，B1實測ONT | 每個single-cell-derived subline的long-read SNV genotype→ScisTree；SV/CNA/DMR後置 | SNV重新建樹；TreeHarmonizer固定輸入樹 | 23小鼠培養subline，非病人／直接scDNA；inbred致germline phase不足 | 分離clone的long-read mixing、mutation loss與placement QC；不適合作HP/PS benchmark首選 |
| [B04 lung 2022](../../papers/B04_lung_longread_phasing_2022/README.md)，B1實測ONT | 同long read的somatic pair partial order；S14據此排除ClonEvol候選 | 有候選topology篩選，不是全基因組聯合HP likelihood | 20病人，S8/S20 scDNA驗證局部關係；不是S14全樹truth | 與現有C4最直接對照、PS範圍、CN影響及held-out pair驗證 |
| [B07 Numbat 2022/2023](../../papers/B07_numbat_2022/README.md)，B3 haplotype/CN可移植方法 | population haplotype、allele counts、expression→CNV posterior→ScisTree | 迭代重新估single-cell tree | 病人scRNA；paired scDNA驗證為NCI-N87細胞株；非long-read實測 | phase uncertainty、soft genotype、cluster/tree迭代與CN-neutral LOH |
| [B05 MEDICC2 2022](../../papers/B05_medicc2_2022/README.md)，B3比較 | haplotype-specific integer CN→LOH/WGD-aware minimum-event distance→NJ | 是；另重建祖先CN | TNBC真病人single cells；short-read CN／推phase；真實樹是reference | 獨立CN tree、parallel LOH/MSAI/WGD simulations，勿拿CN distance當SNV posterior |
| [B03 mutational processes 2022](../../papers/B03_singlecell_mutational_processes_2022/README.md)，橋接 | scDNA/haplotype-specific CN揭露parallel evolution；longread主要作驗證 | 有single-cell phylogeny，但不能宣稱longread linkage入topology | 有真病人與PDX／模型材料，需逐組分開 | 跨資料層驗證與避免把upstream validation冒充tree inference |

B1/B2/B3僅是此調查的技術證據分層，不是各方法官方命名。B01的long-read-derived SNV是直接輸入樹，但不是long-read獨有的co-read feature；B04才直接用單分子關係限制候選。這個區別對本repo聲稱「新增HP/co-read訊號」尤其重要。

## 關鍵詞對應：能解什麼、還缺什麼

- **purity / VAF / CCF / multiplicity**：VAF同時受normal fraction、clone frequency、allele CN與mutant-copy數影響。B04的CCF是模型校正，不是single-cell直接truth；B05的CN distance與B07的haplotype fraction也不能等同SNV CCF。現有`plan.md`C2/C3需保留此區分。
- **haplotype / phasing / phase set**：HP1/HP2是homolog標號，不是clone標號，且跨PS沒有天然一致性。B04提供局部order；B07用phase-switch uncertainty而非確定整染色體phase。C0需以read真正覆蓋與PS/HP資格決定pair。
- **CNV / LOH / copy number / WGD**：total或major/minor CN無法區分AAB與ABB的不同歷史。B05/B07展示allele-CN資訊，但amplified同HP多copy仍破壞「read pattern等於cell genotype」；不能因此解除現行C4的`C_h=1`與clonal-CN限制。
- **single cell**：scDNA直接看到局部DNA；scRNA有dropout與allelic expression；single-cell-derived culture又會受培養擴增選擇影響。三者可互補，但不能用cell barcode／molecule barcode／cultured subline混成同一種真值。

## 暫未列入核心的候選與原因

下列是已追到primary sources的搜尋線索。**這些項目未建立完整PDF閱讀包，不計入已完成論文數**。

| 候選 | Primary source與判斷 |
|---|---|
| SomaticHaplotype 2024 | [bioRxiv 10.1101/2024.08.09.607342](https://doi.org/10.1101/2024.08.09.607342)，14 MM病人23 samples，linked-read phase/PS extension與NRAS局部關係；不是完整tree sampler。 |
| HATCHet2 2024 | [10.1186/s13059-024-03267-x](https://doi.org/10.1186/s13059-024-03267-x)，clone/haplotype CN inference與mirrored subclonal CNA，主要產物是CN與clone mixture；不能把clone deconvolution自動等同clone phylogeny。C0/F3上游值得另讀。 |
| ALPACA 2025 | [Clone copy number diversity is linked to survival in lung cancer，10.1038/s41586-025-09398-w](https://doi.org/10.1038/s41586-025-09398-w)，以SNV tree、clone proportions、allele fractional CN為輸入，解CN evolutionary history，**固定輸入topology**。對subclonal CN、LOH、SNV/CNA timing有用，但不是long-read建樹驗證。 |
| Weaver 2016／RCK 2020 | [Weaver](https://pmc.ncbi.nlm.nih.gov/articles/PMC4965314/)為allele-specific SV/CN量化；[RCK](https://pmc.ncbi.nlm.nih.gov/articles/PMC7545144/)重建clone/haplotype cancer karyotypes並支援long-range adjacency，但不宜以karyotype重建替代clone-tree inference，且不在2021+。 |
| Haploflow | [原研究，10.1186/s13059-021-02426-8](https://doi.org/10.1186/s13059-021-02426-8)主要是混合viral haplotype assembly，不是腫瘤phylogeny。名稱相似不是收錄理由。 |
| EVOFLUx 2025 | [10.1038/s41586-025-09374-4](https://doi.org/10.1038/s41586-025-09374-4)，ONT methyl haplotypes與single-cell RRBS支持methylation機制，longitudinal phylogeny以PISCA/BEAST分析fCpG；需確認ONT是否直接入該樹，不能僅因同篇有ONT就算嚴格命中。 |

## 可重現搜尋方向與檢索字串

本worker做過本地current repo查核與primary-source web搜尋，主搜尋語句如下（可再加2021–2026篩選）：

```text
"long read" "tumor" "phylogeny" haplotype
"long-read" "clonal evolution" phylogeny single cell
"somatic phasing" "phylogenetic" reconstruction
"tumor phylogeny" "read phasing"
"tumor" "haplotype" "phylogeny" "linked-read"
"long-read" "clonal phylogeny" cancer
"long-read" "phylogenetic reconstruction" leukemia cancer
"haplotype" "tumor phylogenies" reconstruction phase reads
"MEDICC2" haplotype patients 2022 pdf
"HATCHet2" haplotype tumor phylogeny
"ALPACA" "copy number" phylogenetic evolution
"SCONCE2" allele specific copy number phylogeny
"SPRINTER" single cell allele haplotype phylogeny copy number
"long-read" "cancer" "phylogenetic" "methylation"
```

搜得upstream SV/phasing、分群或clonality文章後，必須回Methods檢查實際tree target。搜尋引擎結果中有2025preprint與2026正式版melanoma、Numbat2022online與2023issue、2021MM與2024衍生preprint，均依同一研究去重。精確來源與實讀定位見各篇README；B05已渲染核對PDF p.11 Fig.5，B07已渲染核對preprint p.24 Fig.3。B07的PDF版本與正式版HTML差異已顯著標註。

## 對repo的優先結論

最有直接證據的第一步是 **C0先量化同PS、同HP、`C_h=1`的informative pair**，再用B04的partial-order範式評估C4。其後以B07的soft phase/genotype思想改善C2/C3，以B05另建CN-tree／LOH-WGD模擬做外部比較。現有HCC1395是細胞株、candidate tree缺完整SNV assignment，不足以證明病人級tree準確率；需另有病人scDNA reference或實驗已知mixture truth。這些是根據`plan.md:194–200,313–425,466,481`與`data_input.md:82–103`提出的下一步，非聲稱已改善PhyClone。
