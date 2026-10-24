---
paper_id: B05
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_sc_partial"
sc_truth_strength: "partial"
title: "MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution"
year: 2022
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["bulk Illumina WGS (PCAWG)", "short-read scDNA (Minussi TNBC)", "simulated"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "sc_partial_validation"
single_cell_tech: ["scDNA-seq (Minussi TNBC, ~1000 cells/patient)"]
input_is_single_cell: true
tree_type: ["sample_tree", "cell_tree", "cn_event_tree"]
cross_tags: ["haplotype_specific_cn", "wgd", "single_cell_input"]
keywords_en: ["medicc2", "haplotype-specific copy number", "minimum event distance", "whole-genome doubling", "loh", "mirrored subclonal allelic imbalance", "neighbor joining", "copy-number phylogeny", "pcawg", "prostate cancer", "triple-negative breast cancer", "single-cell dna"]
keywords_zh: ["單倍型特異拷貝數", "全基因組加倍", "最小事件距離", "拷貝數演化樹", "單細胞DNA"]
summary_zh: "haplotype CN+WGD 改變 topology；單細胞樹仍是推論。"
category_index: "../../PAPER_CATEGORIES.md"
---

# B05 — MEDICC2：把 haplotype-specific CN、LOH 與 WGD 直接用於樹重建

## 書目、檔案與分類

- Kaufmann TL, Petkovic M, Watkins TBK et al. **MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution**. *Genome Biology* 23, 241 (2022)。DOI：[10.1186/s13059-022-02794-9](https://doi.org/10.1186/s13059-022-02794-9)。本地 PDF 是註記「corrected publication 2023」的修正版，不是另一篇研究。
- 已下載並閱讀：[paper.pdf](paper.pdf)，27 個實體頁；可搜尋逐頁文字：[paper.txt](paper.txt)。來源：[出版社 PDF](https://genomebiology.biomedcentral.com/counter/pdf/10.1186/s13059-022-02794-9)；[PMC 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9661799/)。本文的 p. 指 PDF 實體頁，與其頁首 Page x of 27 一致。
- 收錄層級 **B3：可移植到 long-read 的 haplotype/CN 特徵方法**。它真正重新估計 topology，也有真實病人 single-cell 資料，但本研究沒有以 ONT/PacBio long reads 或 read-backed phase set 作主要實驗；不可計入「實測 long-read 入樹」篇數。
- 真值層級：模擬有已知生成樹；真實病人的 single-cell 樹是模型推論，原研究 clone 結構、SNV 樹及 SV 為比較／支持證據，不是完整生物學真值。
- PDF已以`pdfinfo`驗證27頁，並實際渲染核對p.11 Fig.5。SHA-256：`1dc022bbb36f2050f50ddbdd89bcf2464f32063079385890ae80cbe1b1ab9089`。

## 問題與方法：major/minor CN 相同，演化卻可能不同

一般 major/minor CN 會把 AAB 與 ABB 都寫成 2:1，因此兩個分支分別擴增不同親代 haplotype 的 mirrored subclonal allelic imbalance（MSAI）可能被抹平。MEDICC2 使用兩條 haplotype 各自的整數 CN profile，計算從共同祖先到兩個樣本所需的最少演化事件距離（minimum-event distance，MED），再以 neighbor joining 建 topology，最後重建未取樣祖先的 CN 與 branch events。這是從資料建樹，與固定一棵 SNV tree 後只放置 CNA 的程序不同。[PDF pp.2–4，Fig.1]

事件模型包含連續區段 gain/loss、LOH 及 whole-genome doubling（WGD）。相鄰 genomic segments 可以由同一個事件涵蓋，不必當成獨立位點；同一區域可反覆變動，因此允許 parallel evolution 與 backmutation。haplotype CN 已為 0 的區段不能再靠普通 gain 恢復，反映已丟失 DNA 的物理限制。計算使用 weighted finite-state transducer；單次距離計算隨 segment 數線性增加，但全體 pairwise distance 仍隨樣本／細胞數平方增加。[pp.3–4、12、14–17]

輸入可先由 Refphase 在多樣本間對齊 haplotype，或用 evolutionary phasing 選擇使 MED 最小的 major/minor 配置。後者是模型估計的方向，並不是實測父源／母源、也不是 ONT read 的 HP/PS。論文更區分跨樣本相位對齊與同染色體跨 segment 的 horizontal phasing；這提醒本 repo 不可直接把不同 PS 中的 HP1 當同一條實體染色體。[p.4；pp.16–17；pp.21–22]

## 實驗、可支持的結論與限制

| 實驗 | 資料與結果 | 證據解讀與定位 |
|---|---|---|
| Genome-level simulation | 模擬 chromosome／segment gain/loss、BFB、WGD、inversion/translocation，再投影成 CN，與多種距離／樹方法比較 | 有生成樹，可評估 topology；不是用 MEDICC2 同一 CN 模型直接產生全部 benchmark。[pp.4–5 Fig.2b；pp.17–18] |
| PCAWG | 2,778 個癌症 genome；原始 WGD 標籤一致率 96.0%，bootstrap 判準後 98.8% | 這是與 consensus CN-based WGD 標記的一致率，不是 2,778 棵病人完整演化樹的準確率。[pp.6–7 Fig.2d] |
| Metastatic prostate cancer | 10 病人多區域 WGS；6/10 CN 樹與既有 SNV 樹完全一致，其餘部分一致。A31 的 metastatic lineage 有 subclonal WGD 與 parallel LOH | 真實病人，但比較輸入主要是每個 bulk sample 的 dominant clone；polyclonal mixture 可造成差異。[pp.7–10 Figs.3–4] |
| TNBC single-cell | 重分析 Minussi et al. TN1 的 1,100 與 TN2 的 1,023 細胞，從 allele-specific CN 直接建 cell trees | Fig.5 的 TN2 tree 有 1,023 cells；superclone／subclone 較一致、truncal WGD被找回，仍非獨立 ground-truth topology。[pp.10–11 Fig.5；pp.22–23] |

最貼本題的是 TNBC 實驗：單細胞數量大，且每個細胞可提供 allele-specific CN，與 bulk 的 CCF/multiplicity ambiguity 互補。不過它並不從 raw BAM 自己呼叫 CN；CN caller／segmentation、ploidy、phasing 的錯誤會傳入樹。模型只用改變 CN 的變化，不能直接利用 balanced SV 或 somatic SNV 共現，也以 reference genome 的區段連續性近似腫瘤重排後結構。[pp.12–13 Discussion]

原文 bulk 分析使用 Battenberg 推 purity、ploidy、CN，再取 dominant subclone（包含占比至少 50% 的 subclonal CNA）；single-cell 分析以 alleleCounter 取 1000G SNP counts，並用 FACS ploidy 起始值附近搜尋整數 CN。這些前處理不是 purity 的完美真值。MEDICC2 本身也沒有 `purity × CCF × multiplicity` 的 read-count likelihood；VAF 在其流程主要幫助上游 allele-CN估計，不是 PhyClone 式 SNV observation model。[pp.21–23]

## 資料與程式可取得性

論文 p.24 宣告重現圖表所需資料與程式位於作者 repository，並以 [Zenodo 10.5281/zenodo.7300106](https://doi.org/10.5281/zenodo.7300106) 封存（p.27 ref.75）；原文程式位置是 [Bitbucket schwarzlab/medicc2](https://bitbucket.org/schwarzlab/medicc2)，後續官方亦有 [ICCB-Cologne/medicc2](https://github.com/ICCB-Cologne/medicc2)。PCAWG 原始資料來源於 ICGC release（p.18），TNBC 原始資料沿 Minussi et al. ref.46 追蹤；本輪沒有下載其受控／大型原始 BAM，不把引用到 accession 等同已取得資料。

## 對本 repo 的具體改進

以下是 **inferred 的研究建議**，不是本 repo 已實作。現行計畫切點見根目錄 `plan.md:194–200`；目前 PhyClone observation model 只保留 major/minor CN，見 `research/phyclone_research/PhyClone/phyclone/data/pyclone.py:299–352`。

1. **C0/C1：保留可比較的 haplotype CN 與相位可信度。** 除 `hap1_cn,hap2_cn,ps_block`，應記錄 CN segment、phase 方法、PS內相位可信度及跨PS是否有實測連接。MEDICC2的reference/evolutionary phasing提供不同phase provenance，不能和longphase-s的read-backed HP混用成單一truth。
2. **C2/C3：先驗證 subclonal CN 的邊界。** MEDICC2顯示allele-CN本身帶有lineage訊號；但把 sample-level CN固定塞回SNV likelihood，仍可能錯算 clone 的 multiplicity。先在clonal CN區比較phase-aware genotype restriction；subclonal CN另設實驗，不直接解除現行 `C_h=1` 的C4條件。
3. **C4/C6：以另一種變異建立獨立比較。** 在有多個病人樣本／分離clone時，另跑CN-only MEDICC2，列出其ancestor relations與PhyClone SNV+HP tree的衝突；不要把CN tree直接當truth。可對LOH、WGD、MSAI分別列出衝突事件與支持read。
4. **評估 ablation。** 同一組已知 clone 混合資料做 major/minor-only、正確 haplotype CN、PS內switch error、誤跨PS連接四種輸入；另分WGD/無WGD及parallel LOH場景。比較topology pairwise relations、multiplicity/CCF誤差與校準，避免只看CN樹的branch-length一致性。重抽樣以PS或CN segment/block為單位，不能把同一long read衍生的多個SNV pair當獨立重複證據。[方法啟發：p.20的chromosome bootstrap／segment jackknife；後半是本repo推論]

## 核心判斷

它是「haplotype-specific copy number 能實際改變 topology 推論」的重要基線，適合設計 LOH/WGD/MSAI 模擬與外部 CN-tree 比較；它沒有證明 long-read phasing 比 short-read phasing 重建樹更準，也沒有提供本 repo HCC1395 的病人級 single-cell 真值。
