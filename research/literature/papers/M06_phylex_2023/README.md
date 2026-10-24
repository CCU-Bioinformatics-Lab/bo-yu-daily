---
paper_id: M06
category: "C3a"
category_label: "single-cell 真值樹 × 短讀或未說平台"
subtype: "c3a_sc_benchmark_truth"
sc_truth_strength: "benchmark_truth"
title: "PhylEx: Reconstructing clonal tree for phylo-phenotypic characterization of cancer using single-cell transcriptomics"
year: 2023
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["bulk WGS/WES", "Smart-seq3 and 10x scRNA", "DLP pseudobulk"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "sc_derived_benchmark_truth"
single_cell_tech: ["DLP scDNA (reference tree, OV2295 cell lines)", "Smart-seq3", "10x scRNA"]
input_is_single_cell: true
tree_type: ["clone_tree"]
cross_tags: ["single_cell_input", "cell_level_cooccurrence", "roth_lab", "cell_line_truth"]
keywords_en: ["phylex", "tssb", "slice sampler", "bulk plus scrna", "cell-level snv co-occurrence", "smart-seq3", "10x", "dlp", "pyclone likelihood", "high-grade serous ovarian cancer", "her2 breast cancer"]
keywords_zh: ["單細胞轉錄體", "共現", "克隆樹", "卵巢癌", "貝氏推論"]
summary_zh: "bulk+scRNA 共現建樹；以 DLP scDNA 樹為真值。"
category_index: "../../PAPER_CATEGORIES.md"
---

# M06 PhylEx（Jun et al., Nat Commun 2023）閱讀筆記

## 書目、版本與檔案

| 項目 | 內容 |
|---|---|
| 書目 | Jun S-H, Toosi H, Mold J, Engblom C, Chen X, O'Flanagan C, Hagemann-Jensen M, Sandberg R, Aparicio S, Hartman J, **Roth A**, **Lagergren J**. *Reconstructing clonal tree for phylo-phenotypic characterization of cancer using single-cell transcriptomics.* **Nat Commun 14:982 (2023)**。DOI [10.1038/s41467-023-36202-y](https://doi.org/10.1038/s41467-023-36202-y)，PMID 36813776，PMC9946941 |
| 日期 | Received 2021-06-17，accepted 2023-01-20，published 2023-02-22 |
| 授權 | CC BY 4.0（OA） |
| 本地檔 | `paper.pdf` = **出版社正式版**，**16 頁**。nature.com 下載的 PDF 與 PMC OA S3 的 PDF 逐位元相同（`cmp`）。`paper.txt` 由 `pdftotext -layout` 產生 |
| 補充 | `supplement.pdf` = Supplementary Information（MOESM1），**19 頁**。下載原因：bulk genotype marginalization 的例子與模擬細節只在補充材料 |
| 來源 URL | `https://www.nature.com/articles/s41467-023-36202-y.pdf`；補充 `https://pmc-oa-opendata.s3.amazonaws.com/PMC9946941.1/41467_2023_36202_MOESM1_ESM.pdf` |
| 頁碼規則 | `[p.N]` 指本地 PDF 實體頁；`[S p.N]` 指 supplement.pdf 實體頁 |

## 問題與模型

### 資料 [p.11]

- **Bulk**：`B = {(b_n, d_n, M_n, m_n)}`，也就是 variant reads、depth，以及 TitanCNA 給的 **major／minor CN**（每個 SNV 一組）。
- **scRNA**：`S = {b_{c,n}, d_{c,n}}`，用 Smart-Seq3 或 10X 測得的 per-cell、per-locus variant／total reads。
- 不需要事先做 cell genotyping（不必先把 read 二值化）[p.4, p.9]。

### 聯合後驗 [p.11–12, Eq.1–2]

```text
ℓ(B,S | T,z,ϕ) = ℓ(B | T,z,ϕ) · ℓ(S | T,z,ϕ)            # 給定 tree 時兩種資料條件獨立
P(T,z,ϕ | B,S) ∝ ℓ(B|T,z,ϕ) · ℓ(S|T,z,ϕ) · P0(ϕ|T,z) · P0(z,T)
```

### Prior [p.11–12]

- **`P0(z,T)`：TSSB**（tree-structured stick-breaking），用來指派 SNV 到 node 並生成 topology。
  - `ν_u ~ Beta(1, λ0·λ^{|u|})` 控制樹高；`ψ_{u,k} ~ Beta(1, γ)` 控制分支寬度。
  - 作者建議 `γ ≤ 1`。
- **`P0(ϕ|T,z)`：沿用 PhyloWGS／PhyloSub 的階層 prior**。
  - 把 cellular prevalence ϕ 轉成 clone fraction `η_u = ϕ_u − Σ_{children} ϕ_{u'}`，再放 Dirichlet prior。
  - 這等同強制 sum condition `Σ_children ϕ ≤ ϕ_parent`，且 `0 ≤ ϕ ≤ 1`。
- **Root**：root 是 healthy cells，只有一個 child（progenitor clone）[p.11]。

### Bulk likelihood [p.12, Eq.4–7；S p.1]

```text
P(b_n | ·) = Σ_{g ∈ G(M_n, m_n)} Binom(b_n; d_n, θ(g, ϕ_{z_n}, ε)) · 1/|G(M_n, m_n)|

θ(g, ϕ, ε) = ε                          if v(g) = 0
           = ϕ(1−ε) + (1−ϕ)ε            if v(g) = c(g)
           = ϕ · v(g)/c(g) + (1−ϕ)ε     otherwise
```

- `v(g)`：genotype g 中帶 variant 的 copy 數；`c(g)`：總 copy 數。
- `G(M, m)` 的列舉方式 [S p.1]：variant 可以在 major 或 minor allele 上，在該 allele 上的 copy 數可以是 1 到該 allele 的 CN。
  - 例：`G(2,1) = {AA/B, BA/A, BB/A}`。
  - 所以 `|G| = M + m`，每個 genotype 的權重都是 `1/(M+m)`。
- 論文說 marginalization 沿用 PyClone 補充材料的做法 [p.12]。
- **程式實作**（`src/clone_node.cpp::BulkLogLikWithGenotypeByRegion`，2026-10-17 讀 GitHub HEAD）：
  - 對 `var_cn = 1..minor_cn` 與 `1..major_cn` 兩段各自累加 `Binom(b; d, ξ)`，最後除以 `total_cn`。
  - `ξ = (1−ϕ)ε + ϕ·var_cn/total_cn`；若 `var_cn == total_cn`，改成 `ϕ(1−ε)`。
  - 與論文 Eq.5–7 和補充例子一致。
- 程式另有兩種輸入模式（**論文正文未描述**）：
  - `BulkLogLikWithTotalCopyNumber`：只有 total CN，variant copy 數用 binomial prior。
  - `BulkLogLikWithCopyNumberProfile`：給 CN 機率向量。
- **多區域**：likelihood 依 region 迴圈計算（程式的 `region` 參數）；論文也有多區域實驗 [p.4–5]。

### scRNA likelihood [p.12–13, Eq.8–13]

- 給定 T、z，以及 cell 對 clone 的指派 `ζ_c`，cell c 在 locus n 的突變狀態 `μ_{c,n} ∈ {0,1}` 就被決定（cell 繼承祖先 node 上所有 SNV）。
- 讀數模型：
  ```text
  μ=0:  b_{c,n} ~ BetaBinomial(d_{c,n}, ε, 1−ε)                                  # 只有測序錯誤
  μ=1:  b_{c,n} ~ (1−δ)·BetaBinomial(d, α0, β0) + δ·BetaBinomial(d, α_n, β_n)    # 單等位（bursty）＋雙等位表現
  ```
  - 實際設定 `α0 = β0 = 0.01`，`δ'_n = 0.5`。
  - `α_n`、`β_n` 由前處理以 Beta-Binomial 共軛估計 [S p.1]。
- Cell prior `P(ζ_c) ∝ 1`，取均勻，**不用** clone fraction η，因為 cell 可能被選擇性取樣 [p.13]。
- **對 cell 指派做 marginalize**：
  ```text
  ℓ(S | T,z,ϕ) = Π_c Σ_{ζ_c} Π_n P(b_{c,n} | T,z,ζ_c,d_{c,n}) · P(ζ_c)
  ```
  每個 cell 的計算量是 O(|V|)。
- **「共現」的實質**（分析推論）：
  - 共現並不是一個獨立的 pairwise 項。
  - 同一 cell 的多個 locus 必須由同一個 node 的祖先 SNV 集合解釋，所以 `Π_n` 寫在 `Σ_ζ` 裡面，這一點把同一 cell 上的 SNV 綁在一起。
  - 若兩個 SNV 在同一 cell 同時出現 variant read，只有把兩者放在同一條祖先鏈上，才能得到高 likelihood。

### 推論 [p.3, p.13]

- 用 TSSB 的 **slice sampler** 對每個 SNV 重新指派 node，順序類似 Gibbs，Neal 2003。
- 每輪接著用 PhyloWGS 的 **Metropolis–Hastings** 更新 ϕ。
- 輸出 posterior 樣本與 MAP tree，以及 clonal genotype 與 cell 指派。
- 每次重新指派 SNV 的成本，從純 bulk 的 O(1) 變成 O(C·|V|) [p.13]。

## CN、multiplicity、purity、haplotype 怎麼處理

- **CN**：
  - bulk 的 major／minor CN 是固定輸入（TitanCNA），每個 SNV 一組，**沒有 clone-specific CN**，也不推論 CN。
  - scRNA 部分完全不建模 CN。
  - 作者把 CN 與 scRNA 的聯合建模列為 next challenge [p.9]。
  - 模擬時，把各 clone 的 CN 依 η 加權平均後取整數當輸入，刻意讓輸入的 CN 不精確 [S p.2]。
- **Multiplicity**：在 G(M, m) 上均勻 marginalize，variant 可在 major 或 minor 上，multiplicity 可以是 1 到該 allele 的 CN。沒有 CN timing（突變在 CNA 前或後）的 prior，也不分辨。
- **Purity**：
  - **沒有 purity 參數**。progenitor clone 的 ϕ 本身就是腫瘤細胞比例，root 是 healthy；模擬時 progenitor 的 ϕ 設為 0.5 [S p.1–2]。
  - 在 θ 中，沒有帶突變的細胞（包括 normal 與其他 tumor clone）只貢獻錯誤率 ε。分母用的是同一個 `c(g)`，所以 **normal 與 tumor 的 CN 差異沒有建模**（分析推論，依 Eq.7 與程式）。
  - 這比 PyClone／PhyClone 的三族群 `(1−t, t(1−f), tf)` 簡化。
- **Haplotype**：
  - bulk 只有 major／minor，沒有 germline haplotype 身分，也沒有 read 層級 phasing。
  - scRNA 的「單等位表現」是轉錄層級的 burst 現象，不是 haplotype 觀測值。

## 實驗與可支持的結論

### 示意例 [p.3–4, Fig.1]

- 設定：100 SNV、20 cells，cherry tree，沒有 CNA。
- PhyloWGS 只看 bulk VAF，推出 linear tree；PhylEx 靠共現推出正確的 branching。
- 用來說明「只用 bulk 時 topology 不可識別」。

### 模擬 [p.4–5, Fig.2；S p.1–3]

- 樹：binary 與 multifurcating，有或無 CN 演化；bulk depth 1000。
- 比較方法：
  - TSSB：作者自己實作 PhyloWGS 方法論，因為 PhyloWGS 本體需要 subclonal CN 輸入。
  - Canopy、ddClone、B-SCITE。
- 指標：V-measure、ancestral reconstruction error（SNV pair 祖先矩陣的 MAE）。
- 結果：
  - PhylEx 佔優，且隨 cell 數增加而變好。
  - 「單區域 bulk + scRNA」優於「多區域 bulk-only」。無 CN 時 bulk-only 的 V-measure 約 0.85，PhylEx 在 400 cells 時大於 0.95。

### HGSOC cell lines [p.4–8, Table 1]

- 資料：OV2295 與 OV2295R2，DLP pseudobulk + Smart-Seq3；360 cells、67 SNV（其中 21 個不納入評估）。
- 參考：以 DLP clonal tree 為準。
- 結果：PhylEx 的 V-measure 0.870±0.013、ancestral error 0.038；Canopy 為 0.494／0.178，TSSB 為 0.237／0.204。
- 10X 資料：SNV 覆蓋太稀疏，平均每 cell 只覆蓋 0.45 個 locus，進步有限 [p.6–8, Table 3]。

### HER2+ 乳癌 [p.8–10]

- 資料：5 區 WES + Smart-Seq3，369 cells、418 SNV。
- 結果：MAP tree 是線性；沒有 ground truth。

### 可支持與不能支持的結論

- **可支持**：
  - 在 SNV 有足夠 cell 覆蓋時（full-length scRNA），cell 層級的共現能修正 bulk-only 的 topology 不可識別性。
  - 在 HGSOC 上，與一個 DLP 參考樹高度一致。
- **不能支持**：
  - CN 劇烈的情況：bulk 的 CN 是固定的 per-SNV 輸入。
  - 大規模 SNV：作者建議挑選 SNV [p.9]。
  - 10X 等淺層 scRNA。
  - Posterior 校準：只報 MAP 或點估計。

## 程式碼與可取得性

- **主程式**：<https://github.com/junseonghwan/PhylEx>，C++（boost、gsl、eigen），**GitHub 上沒有 license**，最後 push 2023-11-27，3 stars。
- **分析與前處理**：<https://github.com/junseonghwan/PhylExAnalysis>，R，BSD-2-Clause，最後 push 2023-03-29。
- 論文 Code availability 寫的是 PhylExAnalysis 加 Zenodo [p.14]。以上皆為 `gh api`，2026-10-17 查。
- **輸入**：
  - bulk TSV，欄位 `ID, b, d, major_cn, minor_cn`；多區域用逗號分隔。
  - scRNA 的 per-cell variant／total reads。
  - 依 `interface.cpp`，bulk 也可以改給 total CN 或 CN 機率。
- **資料**：處理後資料在 Zenodo [10.5281/zenodo.4950446](https://doi.org/10.5281/zenodo.4950446)；原始資料在 EGA（受管制）[p.14]。

## 對本 repo 的用途

### 與 PhyClone 的關係

- **論文描述與 repo 資訊**：
  - Andrew Roth 是 co-corresponding author；第一作者 Jun 與 Lagergren 在 KTH。
  - **PhylEx 主要是 Lagergren 組的方法、Roth 共同指導**。methods_survey 把它寫成「Roth lab」只對了一半。
- **分析推論**：
  - 兩者的 bulk 發射模型同出 PyClone 系譜，都在 major／minor 的 genotype 上 marginalize。
  - 但 PhylEx 的 θ 是簡化版：沒有 normal 族群的 CN，也沒有 purity t。PhyClone 是 `(1−t, t(1−f), tf)` 三族群，有 `normal_cn` 與 `tumour_content` 輸入（見 PhyClone notes 02）。
  - 兩者的 multiplicity prior 也不同：
    - PhylEx：variant 在 minor 上也允許，權重是均勻的 `1/(M+m)`。
    - PhyClone：只列舉 major 上的 1..major_cn，再加上「突變在 CNA 之後」的狀態。
  - Tree prior 與推論都不同：PhylEx 用 TSSB + slice sampler + MH（沿用 PhyloWGS 的 ϕ prior）；PhyClone 用 FS-CRP + PG／SMC，並把 ϕ 在 grid 上積分掉。
  - **共同點**：都是「bulk likelihood × 額外資料 likelihood」，在給定 tree 時相乘。PhylEx 證明這個範式可以放在 Roth 系的 bulk 模型上運作。

### 把 cell 層級共現換成 read 層級共現：要改哪些項（推論）

| PhylEx 的項 | read 層級（ONT long read）版本要怎麼改 |
|---|---|
| 觀測單位是 cell c，`Π_n` 寫在 `Σ_ζ` 裡面 | 觀測單位改成「同時覆蓋多個 SNV 位點的 read r」。一條 read 來自一個 cell 的一條 haplotype 拷貝，所以 `Σ_ζ` 要改成「來源 clone × 來源 haplotype × 該拷貝是否帶突變」的混合 |
| `P(ζ_c) ∝ 1`（cell 取樣有偏，所以用均勻） | bulk read 的來源 clone 機率**要用 clone fraction η 與 CN 加權**（`∝ η_u · CN_u(segment, HP)`），不能用均勻；normal 族群也要計入（需要 purity） |
| `μ_{c,n}` 由祖先關係決定（0/1） | 一條 read 是否帶 SNV j，取決於該 clone 在該 haplotype 上的 multiplicity：帶突變的拷貝比例是 `w/x`（HP1）或 `z/y`（HP2）。同一條 read 上兩個 SNV 的聯合狀態，取決於它們是否落在同一條 haplotype、同一個拷貝上（拷貝層級的 phasing，比 cell 層級更細） |
| scRNA 的 Beta-Binomial 混合（bursty、單等位表現） | **整個移除**。DNA read 沒有轉錄 burst，改成每個位點的簡單錯誤率（ONT 的 SNV basecall error），可再加 HP 指派錯誤 |
| bulk likelihood 與 sc likelihood 條件獨立再相乘 | **不再獨立**：共現 read 本身也是 bulk read。若同一條 read 的 allele 同時算進 `b_n`、`d_n` 與 pair 項，就會重複計算。需要 composite likelihood（例如 pair 項只用 read pair 的聯合 allele，或把共現 read 從邊際 count 扣掉） |
| 成本 O(C·\|V\|) | 成本變成 O(#共現 read × \|V\| × haplotype 狀態)。可以先依（SNV pair, HP, allele pattern）壓縮成計數表，成本變成 O(#pair × \|V\|) |

**關鍵差異**：

- cell 層級的共現直接回答「兩個 SNV 是否在同一 clone 的祖先鏈上」。
- read 層級的共現回答的是「兩個 SNV 是否在同一條 haplotype 的同一個拷貝上」。這同時涉及 tree 與 multiplicity／CN timing。
- 好處是能約束 multiplicity；但同一 haplotype 上的 pair 只有在兩者都位於讀長範圍內（約數十 kb）時才有資訊。
- **不同 haplotype 上的 SNV pair 不會在同一 read 上共現**，所以無法從共現推祖先關係，只能靠 HP 拆分後的 VAF。
- 結論：read 層級共現對 topology 的資訊**只限於同一 PS block 內、同一 haplotype 上的 SNV pair**，覆蓋範圍遠小於 scRNA 的 cell 層級共現。

### 可行的最小實驗（推論）

1. 在 HCC1395 的 PhyClone MAP tree 上，對同一 PS block、同一 HP 的 SNV pair 統計共現 read 的 2×2 allele 表，與各 tree 預測的「祖先、後代、兄弟」期望模式比較。
2. 先當成事後的 tree 驗證統計量，再決定是否放進 likelihood。
3. 這相當於 PhylEx 正文 Fig.1 的 read 版：檢驗 bulk-only 推出的 linear chain 是否被共現 read 否定。

## 核心判斷

1. PhylEx 是「bulk likelihood × 共現 likelihood」範式在 Roth 系 bulk 模型上的直接先例。共現靠「對 cell 指派 marginalize，同一 cell 的所有 locus 共用一個 node」實現。
2. 它的 bulk 模型比 PhyClone 簡化：沒有 purity，沒有 normal CN，CN 是 per-SNV 固定的 major／minor，不推論 CN 也沒有 timing。推論用 TSSB slice sampler + MH，不是 PG／SMC。
3. 換成 long-read 的 read 層級共現時，需要四項改動：cell prior 改成 η × CN 加權；`μ` 改成拷貝層級的 multiplicity 機率；移除 scRNA burst 模型；處理 bulk 邊際與共現 read 的重複計算（推論）。
4. read 層級共現只在同一 PS block、同一 HP 內有資訊，對 topology 的覆蓋遠小於 scRNA。它的主要增益可能在 multiplicity 與 timing，而不是分支（推論）。
