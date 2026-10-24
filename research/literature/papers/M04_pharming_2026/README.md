---
paper_id: M04
category: "C1"
category_label: "短讀或未說平台（無 single-cell 真值）"
subtype: "c1_single_cell_input_no_truth"
sc_truth_strength: "none"
title: "Pharming: Joint Clonal Tree Reconstruction of SNV and Copy Number Aberration Evolution from Single-Cell DNA Sequencing of Tumors"
year: 2026
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["low-pass scDNA (ACT, DLP+)", "simulated"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "simulated_only"
single_cell_tech: ["ACT", "DLP+"]
input_is_single_cell: true
tree_type: ["clone_tree", "cn_event_tree", "mutation_tree"]
cross_tags: ["single_cell_input", "haplotype_specific_cn", "snv_cna_joint"]
keywords_en: ["pharming", "scdna-seq", "low-pass single-cell", "act", "dlp+", "joint snv cna tree", "haplotype-specific copy number", "cnrein", "dollo snv loss", "infinite alleles cna", "triple-negative breast cancer", "ovarian cancer cell lines"]
keywords_zh: ["單細胞 DNA 定序", "SNV 與 CNA 聯合演化樹", "haplotype 特異 CN", "三陰性乳癌", "卵巢癌細胞株"]
summary_zh: "單細胞 SNV+CNA 聯合 clone tree；只有模擬真值。"
category_index: "../../PAPER_CATEGORIES.md"
---

# M04 Pharming（Weber et al., J Comput Biol 2026）閱讀筆記

> **版本警示**：本地 `paper.pdf` 是 **bioRxiv v1 preprint（2024-11-18）**，不是 JCB 正式版。JCB 版需付費、未取得；RECOMB 2025 LNCS 版是 5 頁 extended abstract（LNCS pp.294–298），也沒有取得。下文頁碼、式子、實驗數字全部出自 bioRxiv v1。

## 書目、版本與檔案

| 項目 | 內容 |
|---|---|
| 正式版 | Weber LL, Hart A, Ochoa I, El-Kebir M. *Pharming: Joint Clonal Tree Reconstruction of Single-Nucleotide Variant and Copy Number Aberration Evolution from Single-Cell DNA Sequencing of Tumors.* **J Comput Biol 33(1):2–18 (2026 Jan)**。DOI [10.1177/15578666251374694](https://doi.org/10.1177/15578666251374694)，PMID 40944534 |
| 正式版日期 | PubMed 的 `ArticleDate`／Epub 是 2026-01-30；但 PubMed entrez 日期是 2025-09-13，所以 online-first 應在 2025-09 左右（實際上線日沒有從出版社頁面確認）。版權為一般 SAGE 授權，**非 OA** |
| 會議版 | RECOMB 2025, LNCS 15647, pp.294–298，DOI [10.1007/978-3-031-90252-9_25](https://doi.org/10.1007/978-3-031-90252-9_25)（Crossref 確認頁碼；未讀） |
| Preprint | bioRxiv [10.1101/2024.11.17.623950](https://doi.org/10.1101/2024.11.17.623950)，**只有 v1**（bioRxiv API 查詢，2026-10-17），posted 2024-11-18，CC-BY-NC 4.0 |
| 本地檔 | `paper.pdf` = bioRxiv v1 full text，**29 頁**（含 Appendix A／B 與補充圖）；`paper.txt` 由 `pdftotext -layout` 產生 |
| 來源 URL | `https://www.biorxiv.org/content/10.1101/2024.11.17.623950v1.full.pdf` |
| 頁碼規則 | 本文 `[p.N]` 指本地 PDF 實體頁（從 1 起算）。bioRxiv 頁腳印的頁碼比實體頁少 1（實體 p.2 印 "1"） |

JCB 版與 preprint 的差異沒有核對。JCB 摘要（PubMed）只提到 TNBC 一個案例，沒提到 ovarian cell line；正式版是否刪掉或改寫 ovarian 實驗，不確定。

## 問題與模型

### 資料

- 輸入是 low-pass scDNA-seq（DLP+、ACT），共 n 個 cell、m 個 SNV。
  - `A=[a_ij]`、`D=[d_ij]`：每個 cell、每個 SNV 的 variant 與 total read count。
  - `C=(X̄,Ȳ)∈(ℕ×ℕ)^{n×r}`：外部 caller（CHISEL、SIGNALS、CNRein）給的 per-cell、per-segment allele／haplotype-specific CN，**相對於兩條 germline haplotype** [p.3]。
  - `σ:[m]→[r]`：SNV 到 segment 的對應 [p.3]。

### Genotype `(x,y,w,z)` [p.3]

- **論文描述**：SNV j 在某 cell 的 genotype 寫成 `(x,y,w,z)`。`(x,y)` 是兩條 haplotype 的 copy number；`w`、`z` 是 haplotype x、y 上帶 mutation 的 copy 數。
- **Def.1 clonal tree** [p.3–4]：每個 node 對 r 個 segment 標 `x,y`，對 m 個 SNV 標 `w,z`。需滿足三條件：
  1. 每個 SNV 只在一條 edge 上 gain。
  2. `0≤w(v,j)≤x(v,σ(j))`、`0≤z(v,j)≤y(v,σ(j))`。
  3. 同一 segment 的每個 CN state `(x̂,ŷ)` 最多只在一條 edge 上被引入。
- 原文 gain 條件寫成 `z(u,j)=0 且 z(v,j)>1`。依上下文應是 `>0`，判斷是筆誤 [p.3]。
- **Def.2 latent VAF**：`f(v,j)=(w+z)/(x+y)` [p.4]。

### 演化假設 [p.3]

- **SNV 採 Dollo**：只 gain 一次，可以因 CN loss（含 LOH）而 lost。loss 透過 `w,z` 隨 `x,y` 下降來表達，沒有獨立的 back-mutation。
- **CNA 採 infinite alleles**：每個 segment 的每個 CN state 在樹上只出現一次。作者承認實際會違反，但認為大 segment 上大致成立。

### Likelihood 與 cost [p.4]

```text
P(a_ij | d_ij, T, φ, ε) = Binom(a_ij; d_ij, p),
    p = f(φ(i), j)·(1−ε) + (1 − f(φ(i), j))·ε/3

χ(i,ℓ) = |x(φ(i),ℓ) − x̄_iℓ| + |y(φ(i),ℓ) − ȳ_iℓ|      # 觀測 CN 與 node CN 的 L1 偏差

J(T,φ) = −Σ_i Σ_j log P(a_ij | d_ij, T, φ, ε) + λ Σ_i Σ_ℓ χ(i,ℓ)
```

- PDF 式子印成 `−Σ Σ P(...)`，少了 log。程式 `pharming/data.py` 用的是 `-binom.logpmf(...)`，所以正確形式是 negative log-likelihood（**程式實作**）。
- 預設 `λ=1000` [p.8]。這等於幾乎強制 node CN 等於觀測 CN。
- **JCTI 問題**（Problem 1）[p.4]：給定 C、A、D、λ、ε，找出 clonal tree T（含 genotype g）與 cell assignment φ，使 `J` 最小。
- 作者聲稱可由 (Perfect Phylogeny) Flipping Problem 歸約證明 **NP-hard** [p.4]。正文沒有附證明。

### Divide-and-conquer 推論 [p.4–7, p.14–16]

作者列出四個 key insight [p.4]：

1. SNV gain 聚成 `k≪m` 個 cluster（`ψ:[m]→[k]`）。
2. 同一 cluster 的 SNV 共用 DCF（`δ:[k]→[0,1]`），可以從 pseudobulk 估。
3. SNV 與 CNA 落在同一 segment 時，會互相提供時序訊號。
4. 單一 SNV 或單一 segment 的子樹本身就是 clonal tree。相容的子樹可以合併。

輔助結構 [p.5]：

- **CNA tree S**（Def.3）。
- **SNV tree T̂**（Def.4）：單一 SNV 的 `(x,y,w,z)` 演化。
- **SNV cluster tree 𝒯**（Def.5）。
- 從 T 收縮對應的 edge，就能得到上述三種樹，並由此定義「consistent」。

三階段演算法：

1. **初始化** [p.6, p.14]：
   - 在 pseudobulk 上跑 Pharming 內建、改寫過的 DeCiFer，得到 k 個 DCF。改寫處是要求同一 segment 的 SNV tree 必須與同一棵 CNA tree 一致；segment 太多時可以抽樣 segment。
   - 接著列舉所有滿足 **Sum Condition** `δ(u) ≥ Σ_children δ(v)` 的 SNV cluster tree（Def.6）[p.6]。
2. **單 segment 推論（STI，Problem 2）** [p.6–7, p.15–16]：
   - 對每組（SNV cluster tree 𝒯, CNA tree S∈𝒮[ℓ]），用 product graph 加 Gabow–Myers 列舉所有同時與兩者 consistent 的 clonal tree T[ℓ]。
   - 對每棵 T[ℓ] 做 **coordinate descent**，交替兩步：
     - 給定 genotype，把每個 cell 指派到 cost 最低的 node。
     - 給定 φ，為每個 SNV 選 cluster q 與允許的 SNV tree T̂∈𝒯̂[q]，藉此決定 `(w,z)`。
   - Tie-break：偏好靠近 root 的 cluster，以及沒有 loss 的 SNV tree [p.16]。
3. **合併（TMI，Problem 3）** [p.7]：
   - 兩棵 segment 樹共用同一棵 SNV cluster tree，所以只需列舉不同 segment 的 CN 事件在 SNV cluster 之間的相對順序。
   - 依 `m_ℓ` 加權隨機排序 segment，逐步合併，每步保留 top-n。
   - k 用 sweep 選，準則是 BIC：`BIC(k) = k·log m − 2 Σ log P(a|d,T,φ,ε)` [p.7, p.16]。

**分析推論**：整體是決定論的 combinatorial heuristic，沒有 posterior、沒有 uncertainty。topology 搜尋空間在初始化時就被 DCF 加 Sum Condition 截斷，所以 DCF 估錯會直接限制可達的樹。

## CN、multiplicity、purity、haplotype 怎麼處理

- **CN**：
  - 外部 caller 給 per-cell haplotype-specific CN，作為「軟約束」，偏差用 λ·L1 懲罰 [p.4]。
  - 樹上的 CN state 是推論變數，但受 infinite alleles 約束 [p.3]。
  - 每個 segment 各自獨立，不建模相鄰 segment 的依賴 [p.10–11，作者列為 future work]。
- **Multiplicity**：
  - 由 `w`、`z` 明確表示，而且是分 haplotype 的 multiplicity。
  - 每個 SNV 的整條 `(x,y,w,z)` 路徑由所選的 SNV tree 決定，所以 multiplicity 與 CN timing（SNV 在 CN 事件之前或之後 gain）是同一個離散選擇 [p.6–7, p.15–16]。
  - 實驗評估時，SNV tree recall 與 genotype similarity 都「modulo multiplicity and allele specificity」[p.9, p.18–19]，所以論文**沒有直接驗證 multiplicity 或 SNV haplotype 指派是否推對**。
- **Purity**：
  - single-cell 設定沒有 purity 參數。normal cell 會被指派到 root normal clone（root CN 預設 (1,1)，CLI 有 `--root_x/--root_y`）[p.15；repo README]。
  - DCF 由 pseudobulk 估，所以 purity 只間接影響 DCF。
- **Haplotype**：
  - CN 的 x/y 跟著 caller 的 haplotype 標記（CNRein 的 haplotype-specific CN）[p.3, p.9]。
  - **SNV 落在哪條 haplotype**（w 或 z 非零）是 latent，由 SNV tree 的選擇決定。
  - Likelihood 只看 `f=(w+z)/(x+y)`，**read count 本身不分 haplotype**。因此 SNV 的 haplotype 指派只能透過 CN 演化約束間接識別，例如某條 haplotype 後來 LOH，帶在它上面的 SNV 就會被一起丟掉。
  - 模擬時「each SNV is phased at random」[p.17]。
- **Read 連鎖**：沒有使用。每個 SNV 各自用 binomial，彼此獨立。

## 實驗與可支持的結論

### 模擬 [p.7–9, p.16–17]

- **設定**：n=1000 cell，m=5000 SNV，r=25 segment，k=5，coverage ∈ {0.01, 0.05, 0.25}×，CN error ∈ {0, 0.035}，每組 5 replicate，共 30 個 instance；ε=0.001，k∈{3..6}，λ=1000，top-5，單一 random ordering。
- **比較方法**：Phertilizer、Baseline+SCITE、LAZAC（LAZAC 只比 CNA 相關指標）。
- **指標**：cell placement accuracy、CNA tree recall、SNV tree recall、genotype similarity、SNV loss F1。
- **結果**（CN error 0.035）：

  | 指標 | Pharming | Phertilizer | Baseline+SCITE | LAZAC |
  |---|---|---|---|---|
  | cell placement | 0.90 | 0.58 | 0.70 | – |
  | CNA tree recall | 0.80 | 0.48 | 0.72 | 0.08 |
  | SNV tree recall | 0.73 | 0.30 | 0.51 | – |
  | genotype similarity | 0.88 | 0.76 | 0.86 | – |

  SNV loss F1 是 0.57：recall 0.85，precision 0.57 [p.8–9]。

### 真實資料

- **TNBC TN3**（ACT，1101 cells，0.02×，m=12,662，r=171）：BIC 選 k=3；93% SNV 在 trunk；subclonal cluster 的 CMB 在 clade 內中位數 0.29、clade 外 0 [p.9]。
- **TNBC TN1**（1100 cells，0.031×，r=335）：
  - **無法整個 genome 一次推**，改成每條 chromosome 各推一棵，共用 DCF 與 SNV cluster tree [p.9–10]。
  - chr3 有 11 個 segment 推出 genome doubling。
  - pooled VAF 在 latent VAF 1/4 處出現 1/2 的次峰。作者承認方法難以分辨 SNV 在 WGD 之前或之後 [p.10]。
- **Ovarian DLP+**（890 cells，r=409）：每個 cell line 分開跑，而且只用抽樣的 segment；WGD 與既有文獻一致 [p.11]。

### 可支持與不能支持的結論

- **可支持**：在其 simulator 下（infinite alleles、SNV 隨機 phase、Dirichlet clone proportion），joint 推論的 cell placement 與 CNA／SNV tree recall 優於比較方法。
- **不能支持**：
  - 真實資料沒有 ground truth，只用 CMB 與 pooled VAF 做 consistency check。
  - scalability 未解：TN1 要切成 chromosome，ovarian 要抽 segment。
  - multiplicity 與 SNV haplotype 指派的正確性沒有被評估。

## 程式碼與可取得性

- Repo：<https://github.com/elkebir-group/Pharming>，Python 加 C++（`clonelib`，pybind11），**BSD-3-Clause**，最後 push 2026-10-09（`gh api`，2026-10-17 查），2 stars。
- 依賴：networkx、pyomo、glpk、lemon、boost-cpp。
- 輸入格式：
  1. read count TSV，無標頭欄位 `[chr segment snv cell var total]`。
  2. allele-specific CN CSV。
- 輸出：pickled `Solution`；`pred_cell.csv`、`pred_mut.csv`、`pred_mut_loss.csv`；`pred_genotype.csv`，欄位 `node,snv,x,y,xbar,ybar,segment`。
- 程式核對（只看 `data.py`、`clonal_tree.py` 的相關段落）：
  - cell 的 cost 是 `-binom.logpmf(var,total,adj_vaf)`，其中 `adj_vaf = vaf(1−α) + (1−vaf)α/3`。
  - CN 偏差項以 `lamb * cna_node_cost` 加權。

## 對本 repo 的用途

### 可借用的設計

1. **`(x,y,w,z)` 狀態空間**（推論）：
   - 只要把 x/y 讀成 longphase 的 HP1/HP2，就和本 repo 想要的「HP-specific CN + 分 haplotype multiplicity」幾乎一一對應。
   - PhyClone 現在的 genotype prior（`get_major_cn_prior`）是對 major／minor 上的 multiplicity 均勻列舉。它不區分 major／minor 與 HP1／HP2，也不允許 SNV 在 minor allele 上（見 PhyClone notes 02）。
   - 改用 `(x,y,w,z)` 後，可以把 genotype prior 換成「SNV tree 列舉」：在給定的 haplotype CN 事件序列下，列出 SNV gain 時點，以及 w/z 隨後的變化。
2. **SNV tree 列舉，作為 CN timing 的離散化**（推論）：
   - 對 bulk 來說，每個 SNV 只需在少數幾棵 SNV tree 之間 marginalize，這相當於 DeCiFer 式的 descendant-set 列舉。
   - 這比 PhyClone 現在的「multiplicity 均勻 prior」多了 CN 事件順序的資訊。
3. **CN infinite alleles 加 SNV Dollo** 的組合可以直接當模型假設。但 WGD 前後時序難以分辨的問題 [p.10] 在 bulk 會更嚴重。

### 與 longphase HP／PS 的接點（推論）

- Pharming 的 likelihood 只用總和 `(w+z)/(x+y)`。如果有 HP-tagged read，可以把每個 SNV 的 read 拆成兩份：
  ```text
  a_j^HP1 ~ Binom(d_j^HP1, ρ·w/x 的 clone 混合版)
  a_j^HP2 ~ Binom(d_j^HP2, ρ·z/y 的 clone 混合版)
  ```
  這樣 w 與 z 就分別可識別。SNV 落在哪條 haplotype，就從 latent 變成「觀測到的 phasing」，有 phase-switch 誤差時再加一個小錯誤率。
- **限制**：
  - PS block 的 HP1／HP2 標籤只在同一 block 內一致。要與 segment 層級的 haplotype CN（BAF 方向）對齊，必須做 block 內的 BAF／HP 對齊，跨 block 則可能翻轉。
  - 這正是 CNRein、CHISEL 等 caller 處理 phasing 的地方，本 repo 需要自己處理 longphase PS 與 CN segment 的對齊。

### 能否搬到 bulk

- **論文描述**：作者在 Discussion 說可以「easily extendable to bulk ... with only minor adjustments」[p.11]，但沒有實作，也沒有實驗。
- **分析推論**：
  - 搬到 bulk 時，cell assignment φ 要改成 clone proportion；`χ` 要改成 bulk segment 的 BAF／depth likelihood（觀測的是混合後的 CN，不是 per-cell CN）。
  - DCF 加 Sum Condition 的列舉可以保留。
  - 最大問題是 bulk 沒有 per-cell CN 去定錨 CN 事件的祖先關係：CNA tree 的順序要靠 subclonal CN 的比例推，可識別性會大幅下降。
  - 這時 long-read 的 HP 拆分加上同一 read 上 SNV 的共現，可以部分補回 cell-level 的連鎖資訊。

### 可行的最小實驗（推論）

1. 選 HCC1395 一個有 subclonal LOH 的 segment，列舉該 segment 的 CNA tree，並對每個 SNV 列舉 SNV tree。
2. 比較兩種 likelihood 對每個 SNV 的 SNV tree 後驗熵：(a) 只用總 VAF；(b) 用 HP 拆分的 read count。
3. 熵下降的幅度，就代表 HP 對 multiplicity／timing 的貢獻。
4. 不需要先改 PhyClone 的樹搜尋。

### 與 PhyClone 的差異

| 面向 | Pharming | PhyClone |
|---|---|---|
| 資料 | scDNA，per-cell | bulk 多樣本 |
| 推論 | 決定論 heuristic（列舉 + coordinate descent + 逐步合併 + BIC） | Bayesian PG／SMC，有 posterior |
| CN | 推論 CN tree | CN 是固定輸入 |
| SNV loss | 允許 Dollo loss | 不允許 loss，用 outlier 吸收 |

## 核心判斷

1. Pharming 的 `(x,y,w,z)` 是目前最貼近「HP-specific CN + 分 haplotype multiplicity」的現成狀態表示。但它的 SNV haplotype 指派是 latent，read 層級不分 haplotype；HP 拆分的 likelihood 是它沒有的。
2. 它是 single-cell、決定論 heuristic。可借用的是狀態空間與 SNV tree 列舉，不是推論框架。
3. 「可搬到 bulk」只是作者一句話，沒有證據。bulk 版的困難在 CNA tree 失去 per-cell 定錨，long-read 的 HP 與共現正好補在這裡。這是本 repo 可以主張差異的位置（推論）。
4. 論文沒有評估 multiplicity 與 SNV haplotype 指派的正確性，也承認 WGD 前後時序無法分辨。HP 拆分可以直接檢驗這兩點（推論）。
