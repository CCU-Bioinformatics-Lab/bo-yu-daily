# 第一類 A：真正病人 single-cell DNA 支撐的演化參考樹（5 篇）

搜尋與下載核驗日：2026-10-15。這五篇均有病人 genomic DNA 資料與 genetic tree；不是以 RNA expression dendrogram、UMAP 或純 CNV-from-RNA 當病人 lineage 真值。單細胞資料可較直接觀測 mutations/CN/SV 的共存，**樹仍是推論所得**，沒有一篇提供每個祖先分裂均由直接實驗追蹤確認的完整病人真樹。

## 核心索引與優先順序

| ID | 論文／年份 | 真病人與樹範圍 | 推樹輸入與方法 | 長讀／phase 的實際角色 | 最值得本 repo 使用的內容 |
|---|---|---|---|---|---|
| [A01](papers/A01_ovarian_cfDNA_2025/README.md) | [Tracking clonal evolution during treatment in ovarian cancer using cell-free DNA](https://doi.org/10.1038/s41586-025-09580-0), 2025 | 24 HGSOC 病人有 scWGS；18 為多年追蹤分析；21,916 cells | SIGNALS allele-specific CN → MEDICC2 → 人工挑 clades；SV markers 追 cfDNA | 無 ONT/PacBio；haplotype-specific CN 實際進樹 | CN-aware CCF、WGD、pseudobulk benchmark |
| [A02](papers/A02_sprinter_2025/README.md) | [SPRINTER](https://doi.org/10.1038/s41588-024-01989-z), 2024 online／2025 卷期 | 1 NSCLC 病人、10 部位、14,994 cells；另分析既有 breast/ovarian datasets | clone-pseudobulk SNV frequency → HUNTRESS topology → MEDICC2 固定該 topology → MACHINA | 無 long reads；不是 HP/PS likelihood 方法 | S-phase/CN 假訊號、clone 內 subclonal SNVs、分部位驗證 |
| [A03](papers/A03_pancreatic_snDNA_2023/README.md) | [Application of high-throughput single-nucleus DNA sequencing in pancreatic cancer](https://doi.org/10.1038/s41467-023-36344-z), 2023 | 16 PDAC 病人；主要 Fig.6 樹來自 PA04 一人、3 samples、8,061 nuclei | 25 SNV＋8 SMAD4 deletion features → SCG 分群 → clone/event hierarchy | 無 long reads；HaplotypeCaller 名稱不代表 phasing | 正常細胞混入、ADO/doublets、CN 導致 mutation loss |
| [A04](papers/A04_aml_strandseq_2024/README.md) | [Single-cell multiomics analysis… CK-AML](https://doi.org/10.1038/s41588-024-01999-x), 2024 | 8 primary 病人；542 初始 cells；加 PDX/縱向為855 genomes | Strand-seq chromosome-length haplotype＋depth＋orientation → scTRIP SV → 人工 clone trees | **75-bp Illumina Strand-seq**；OGM 為光學圖譜，均非 long-read sequencing | total CN 相同但 homolog/SV 不同的克隆；C2/C5/C6 |
| [A05](papers/A05_mpal_multiome_2024/README.md) | [Multiomic single cell sequencing identifies stemlike nature of mixed phenotype acute leukemia](https://doi.org/10.1038/s41467-024-52317-2), 2024 | 14 MPAL 病人、58,807 DAb-seq cells；9 人可作多步 mutation/phenotype 分析 | targeted DNA genotypes → SCITE mutation tree | 無 long reads／genome-wide CN／PS | 少量公開 genotype 起步、FP/FN 與 rare-clone 敏感性 |

建議起步資料順序：**A03 PA04 的公開 SCG_input → A05 genotype/source data → A01 clone CN/CCF → A02/A04 較複雜資料**。這是取得資料與驗證成本的排序，不代表論文品質排序；EGA/dbGaP raw data 大多仍需 DAC。

## 與本 repo 設計 C0–C6 的對應

依目前 `plan.md:194–200` 命名；以下是研究建議，不是已實作功能。

| 模組 | 可具體改進 | 對應證據 | 最小驗證 |
|---|---|---|---|
| C0 BAM/CRAM＋SNV＋CN extractor | 不把 no-call 當 REF；保留 coverage、CN resolution、sample/assay、PS/orientation 及 CN confidence | A03 的 ADO/doublet；A02 的 replication artifact；A04 homolog-specific SV | held-out 細胞聚合成 pseudobulk，再加 missingness/CN uncertainty |
| C1 optional schema | 分開 cellular purity、tumor DNA fraction、mutation CCF、clone proportion；記錄參考樹建法和 error model | A01 CCFtree；A03 area vs nuclei；A05 cellular clone posterior | 檢查不同 estimand 不會混入同一欄位；無新欄位維持 baseline |
| C2 multiplicity prior cap `C_h` | 對 allele-specific CN/WGD 建 prior；CN-mediated mutation loss 不應當成絕對互斥 | A01 haplotype CN；A03 SMAD4 deletion；A04 homolog events | total CN vs allele-specific CN；以真細胞 carrier fraction 評估 |
| C3 HP split per-SNV likelihood | 驗證 phased/unphased likelihood 能否改善 CCF；考慮 phase/CN uncertainty | A01 有 CN/CCF 校正可借鑑，五篇皆無本 repo 的 HP-split likelihood 實測對照 | 相同 pseudobulk counts 比較 baseline/C2/C2+C3；無長讀時只能部分驗證 |
| C4 read-pair topology factor | 首版同 PS、同 HP、clonal CN、`C_h=1`；same-cell 共存不可直接填成 same-molecule pair counts | A03/A05 只提供 cell co-occurrence；A04 是 homolog inference | 需要 matched long-read molecules；無則明標 genotype-conditioned simulation |
| C5 clustering | 比較 SNV-only、加 CN、加 homolog/SV；允許 CNA clone 內仍有 subclonal SNVs | A03 7-cluster；A02 clone 內 SNVs；A04 total-CN ambiguity | clone recovery、錯併率、held-out variant relation |
| C6 posterior/conflicts/trace | 輸出 edge uncertainty、rare-clone cutoff、HP/CN conflicts、reference-tree provenance | A01 人工 clades；A04 curated trees；A05 FP/FN 假設 | cell/variant bootstrap、error-rate/phase-flip 敏感性與衝突表 |

不能只看 RF/tree edit distance：不同研究的 leaves 可能是 cells、clones 或 mutations。跨方法比較時先轉成共同 SNV 的 ancestor/descendant/mutually-exclusive 關係，再報 clone recovery 與 carrier-fraction error。對未取樣或 panel 外事件不計答案；有多個 equally plausible trees 時報相容區間，不硬選一棵當絕對真值。

## 必須保留的四個證據限制

1. A02 的 cell-cycle **ground truth 是實驗週期標籤**，不是病人演化樹真值；SNV topology 與 CNA reconstruction 也不是獨立兩棵樹。
2. A01 `CCFtree/VAFpseudobulk` 校正本身依賴同一樹，不能回頭當獨立 topology validation。24/18 名病人是不同分析 denominator。
3. A04 primary、PDX、relapse 的 cell fractions 不可混合；Strand-seq 的 chromosome-length phasing 不等於 long-read sequencing。
4. 五篇皆未同時提供本 repo 所需的 matched `HP/PS` long-read pair counts 與獨立病人 lineage truth，故它們完成第一方向五篇，**不能重複計成第二方向五篇長讀建樹**。

## PDF 下載與閱讀 manifest

全部為 Nature 官方 final journal PDFs；每個目錄包含 `paper.pdf`、以 `pdftotext -layout` 產生的 `paper.txt`、已讀 Methods/Fig/Data availability 的繁中 README。已用 `file` 確認 PDF、`pdfinfo` 確認 metadata/physical pages 並成功抽全文。部分 PDF 的 `file` heuristic 頁數與 `pdfinfo` 不同，以下採解析 PDF page tree 的 **pdfinfo 實體頁數**；精讀頁碼也採此口徑。

| ID | 官方下載 URL | pdfinfo 頁數 | SHA-256 |
|---|---|---:|---|
| A01 | https://www.nature.com/articles/s41586-025-09580-0.pdf | 30 | `6f610ce0e553751e56036830923d0bb8becf8a759cd333f043f6113263bc4b13` |
| A02 | https://www.nature.com/articles/s41588-024-01989-z.pdf | 34 | `8bf2a203efc1375eb22f25ab8d4bc4beaa52cff711700119a16cb51e93dea152` |
| A03 | https://www.nature.com/articles/s41467-023-36344-z.pdf | 14 | `1607997a06a29b67e8be78c93e18838b24d367082a0b17abaa8217ddbca19f0c` |
| A04 | https://www.nature.com/articles/s41588-024-01999-x.pdf | 39 | `9a040a76357a1e0b573dc9c2e4fdc96659cc45336884bccb001a9f04178508bc` |
| A05 | https://www.nature.com/articles/s41467-024-52317-2.pdf | 17 | `77786c0dc2f63a13ae97eb66695781047840207adaa70f40dd60ea9439016fd4` |

未下載 raw FASTQ/BAM 或需授權的 patient data；accession、可取得程度與使用限制均在個別 README。A03/A05 的獨立 Supplementary Methods/Figures 尚未下載，筆記沒有把它們標作已精讀。各 PDF 本身包含的 Extended Data 已可在保存檔中閱讀。
