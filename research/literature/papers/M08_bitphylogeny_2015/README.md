---
paper_id: M08
category: "C1"
category_label: "短讀或未說平台（無 single-cell 真值）"
subtype: "c1_read_cooccurrence_short"
sc_truth_strength: "none"
title: "BitPhylogeny: a probabilistic framework for reconstructing intra-tumor phylogenies"
year: 2015
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["454/Roche bisulfite amplicon reads (IRX2 locus, Sottoriva colon cancer)", "single-cell exome (Hou 2012 MPN)", "simulated"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "simulated_only"
single_cell_tech: ["single-cell exome (Hou 2012 MPN, input only, no truth tree)"]
input_is_single_cell: true
tree_type: ["clone_tree"]
cross_tags: ["read_cooccurrence_model", "transferable_to_long_read", "methylation", "single_cell_input", "no_copy_number"]
keywords_en: ["bitphylogeny", "tssb", "tree-structured stick-breaking", "read-level pattern", "methyltype", "co-occurrence", "joint clustering and tree inference", "clones at inner nodes", "bisulfite sequencing", "colon cancer", "myeloproliferative neoplasm", "single-cell exome", "mcmc", "mpear"]
keywords_zh: ["樹狀 stick-breaking", "read 層級 pattern", "共現", "甲基化", "clone 與樹聯合推論", "大腸癌", "骨髓增生性腫瘤"]
summary_zh: "每條 read 的多位點 pattern 當一次抽樣，用 TSSB 聯合推 clone 與樹；沒有 CN。"
category_index: "../../PAPER_CATEGORIES.md"
---

# M08 BitPhylogeny（Yuan, Sakoparnig, Markowetz, Beerenwinkel；Genome Biology 2015）

閱讀日：2026-10-19。標記：「論文描述」＝正文明寫；「推論」＝我的分析。`[L.N]` 指本地 `paper.txt` 的行號。

**收錄理由（使用者決定，2026-10-19）**：這篇論文證明，**同一條 read 上多個位點的共現 pattern 可以直接放進機率模型，同時推論 clone 和樹**。它是把 long-read phased pattern 接進 clone tree 模型的最早範式。

## 書目、版本與檔案

- Yuan K\*, Sakoparnig T\*, Markowetz F, Beerenwinkel N. **BitPhylogeny: a probabilistic framework for reconstructing intra-tumor phylogenies.** *Genome Biology* 16:36, 2015-02-13。DOI [10.1186/s13059-015-0592-6](https://doi.org/10.1186/s13059-015-0592-6)。CC BY 4.0。
- 全文：[PMC4359483](https://pmc.ncbi.nlm.nih.gov/articles/PMC4359483/)。

| 本地檔 | 內容 | 來源 |
|---|---|---|
| `paper.xml` | 出版社全文 JATS XML | Europe PMC REST `PMC4359483/fullTextXML` |
| `paper.txt` | 由 XML 轉出的純文字。公式 (1)–(12) 從 MathML 轉成一行，標 `[EQ]` | 本地轉檔 |

**版本說明**：
- 出版社 PDF、PMC PDF、Springer PDF 都回傳 HTML 擋頁，所以沒有存 PDF。XML 是同一份出版社正文。
- XML 只含正文。Additional file 1（Fig. S1–S3）和 file 2（R Markdown）沒有下載，也沒有讀。

**程式碼**：
- 論文 [55] 指向 `bitbucket.org/ke_yuan/bitphylogeny`。2026-10-19 檢查時回傳 404，已失效。
- GitHub [keyuan/bitphyloR](https://github.com/keyuan/bitphyloR)：R 版，3 stars，最後 push 是 2016-03-18。我沒有讀這份程式碼。

## 問題與模型

### 資料單位（論文描述）

一筆觀測 `x_n ∈ {0,1}^M` 是**一整個 marker pattern**。`x_{i,n}=1` 表示位點 i 甲基化或突變 [L.89]。論文用了兩種 pattern：

- **methyltype**：一條 bisulfite read 上 IRX2 locus 各 CpG 的甲基化狀態 [L.25, L.57]。
- **genotype**：一個 single cell 在 712 個 SNV 的 0/1 狀態 [L.69]。

作者明寫，這和 PyClone 那類「用 bulk SNV 頻率」的方法是根本不同的資料型態 [L.26]。

### 生成模型（論文描述，Eq. 1–2 [L.92–94]）

```
π ~ TSSB(λ, α0, γ)                 # tree-structured stick-breaking：節點權重 + 樹形
ε_n | π ~ Discrete(π)              # 每筆 pattern 整筆來自同一個 clone ε_n
θ_ε ~ p(· | θ_pa(ε))               # clone 參數由 parent 轉移而來
x_n ~ p(· | ε_n, θ_ε)
```

- TSSB：`ν_ε ~ Beta(1, λ^|ε| α0)` 決定節點自身與後代的分配，`ψ_ε ~ Beta(1, γ)` 決定兄弟間的分配 [L.92]。
- clone 可以在**內部節點**，不只在葉節點。這是作者強調的、和經典 phylogeny 的差別 [L.23]。
- 固定 `λ=2, α0=0.3, γ=0.1` [L.127]。

### Emission（論文描述，Eq. 3 [L.99]）

```
p(x_n | θ_ε) = Π_i σ(θ_{i,ε})^{x_{i,n}} · (1 − σ(θ_{i,ε}))^{1 − x_{i,n}}
```

- 給定 clone 時，位點之間條件獨立。作者用 Fig. S1 檢查 IRX2 的 CpG 符合這個假設 [L.100]。
- SNV 模型把缺失位點直接略過，假設 missing completely at random [L.119]。

### 共現資訊從哪裡進入模型（推論）

- Eq. 3 是逐位點相乘，但**整條 pattern 共用同一個 `ε_n`**。所以同一條 read 上的位點只能一起被指派到同一個 clone。
- 這就是共現約束。它沒有 TreeClone（M02）那種顯式的 pair 計數項，而是透過「整條 read 只能有一個 clone 來源」來實現。
- 因此 read 帶的位點越多，指派越確定，樹也越被約束。作者也寫，read 越長，SNV phasing 越好 [L.33]。

### 父子轉移（論文描述，Eq. 4–10 [L.102–121]）

- methylation：`θ_ε` 是兩個 Laplace(±μ, Λ) 的混合。混合權重 `w_i` 依 parent 的狀態，由 rate matrix 的 `P(t) = exp(At)` 決定。branch length `t_ε` 也是參數 [L.102–112]。root prior 偏好全未甲基化 [L.114]。
- SNV：rate matrix 讓「突變 → 正常」的機率為 0，也就是演化層級不可逆 [L.121–122]。
- 觀測層級仍允許錯誤。所以 posterior 可能出現 back mutation 的樣子：ST13 在 clone b 有突變，在 c 沒有 [L.73]。

### 推論與摘要（論文描述）

- Gibbs sampler 依 TSSB 原作法 [16]，另加 **swap clone** move：交換兩個節點的參數、資料與 mass，用 Metropolis 比決定接受。root 不能是空的 [L.127]。
- 聚類摘要：MPEAR（R `mcclust`）[L.128]。
- 樹的摘要 [L.131]：
  1. 每個 sample 計算 `π_ε > 0.01` 的節點數，稱為 big node number。
  2. 找出出現最多次的 big node number 組。
  3. 在這一組內，取 complete-data likelihood 最高的樹 (Eq. 12)。
- 速度：2,000 筆 pattern 時，每次 iteration 約 1 秒（單核）[L.143]。

## 評估

| 資料 | 內容 | 真值 |
|---|---|---|
| 模擬 [L.43–54] | 5 種樹（monoclonal、polyclonal 低／中／高、mutator）× 4 種 noise（0、1、2、5%）；8 個位點、2,000 筆觀測 | 模擬樹 |
| Sottoriva 2013 大腸癌 [L.57–66] | 454/Roche bisulfite amplicon，IRX2 locus；腫瘤 CT、CU、CX、HA；每個 gland 平均 >1,500 reads；錯誤率 0.4% | **無**。原研究的樹沒有錯誤模型，無法比較 [L.66] |
| Hou 2012 MPN [L.69–73] | 58 個 single cell 的 exome，712 SNV；allele dropout 43%；平均 56% 缺失 | **無**。只檢查 bulk normal 落在 root、bulk tumor 落在最進展的 clone c |

**結果（論文描述）**：
- 有 noise 時，聚類（v-measure）勝過 hclust 和 k-centroids 這兩個 baseline。
- 樹距離方面，BitPhylogeny 在所有設定都比 baseline 的 minimum spanning tree 更接近真值。
- 無 noise 的 polyclonal 樹上，v-measure 約 0.9，略低於 baseline。原因是 clone 只差一個位點、大小又不對稱時，模型偏好合併 [L.49]。
- 樹距離是作者自訂的 consensus node-based shortest path distance [L.53, Methods]。

## 作者自述的限制

- 只用單一 locus（IRX2），可能不反映完整演化史 [L.83]。
- MCMC 慢 [L.83]。
- 假設位點獨立 [L.83]。
- 缺少通用的樹距離 [L.84]。

另外兩點是我的推論：
- 沒有 copy number，沒有 purity，也沒有 read count／VAF 模型。
- 真實資料都沒有真值樹，準確度只來自模擬。

## 對本研究的意義（推論）

### 為什麼值得移植

- 它是「read 當成 clone 的抽樣單位」的完整貝氏模型，而且 clone 數與樹形一起推論。
- longphase-s 的 phased ONT read 正好提供這種單位：一條 read、一個 PS、一個 HP、多個位點。

### 直接搬到 ONT bulk SNV 會遇到的 5 個問題

1. **一條 read 上的 somatic SNV 很少。**
   - methylation 的 CpG 很密，所以每條 read 有多個位點。somatic SNV 很稀疏，多數 ONT read 只蓋到 0 或 1 個。
   - 只蓋到 1 個 SNV 的 read，在這個模型下只提供計數資訊。
   - 要先量化：每個 cell line 有多少 read 在同一 PS 內蓋到 ≥2 個 somatic SNV。
2. **haplotype 結構不是 MCAR。**
   - 來自 HP1 的 read 永遠不可能帶 HP2 上的突變。這不是隨機缺失。
   - emission 要改成依 read 的 HP 條件化：`p(x_n | ε, h_n)`。
3. **bulk 混合要做 CN 校正。**
   - `π_ε` 在這裡是「read 來自 clone ε 的比例」，不是 cellular prevalence。
   - read 比例 ∝ prevalence × 該 HP 在該 clone 的 copy 數 `C_h`。normal 的 read 會落在 root。
   - BitPhylogeny 完全沒有這一層。
4. **multiplicity。**
   - clone 內某 HP 只有 m／C_h 的 copy 帶突變時，這條 read 帶突變的機率是 m／C_h，不是 0 或 1。
   - Eq. 3 的 `σ(θ)` 是連續機率，形式上可以表示這個值。但轉移核會把 θ 推向 ±μ，需要改寫。
5. **規模。**
   - ONT bulk 有數百萬條 read，不能逐條 Gibbs。
   - 只保留有資訊的 read，例如同 PS 內有 ≥2 個 somatic 位點的 read。相同 pattern 合併成計數。

### 和 PhyClone 的接法

- PhyClone 的單位是 SNV cluster，prior 是 FS-CRP，不是 TSSB。整套換掉 prior 的代價太大。
- 較可行的做法：保留 PhyClone 的 cluster likelihood，**再乘上一項 read-pattern likelihood**。
  - 對每條多位點 phased read 計算 `P(pattern | tree, prevalence, C_h, m) = Σ_clone w_clone(h) · Π_site p(x_site | clone, h)`，對來源 clone 邊際化。
  - 在 SMC／PG 加入節點時更新這一項。
- 和 TreeClone（M02）相比：TreeClone 只用 pair、CN=2 寫死；BitPhylogeny 能吃任意長度的 pattern。兩者都沒有 CN 模型。

## 分類判定

- 平台：454 bisulfite amplicon read 和 Illumina single-cell exome 都不是 ONT／PacBio long read，所以平台軸算短讀（C1）。
- 子類 `c1_read_cooccurrence_short`：模型核心是 read 層級的多位點共現，可以移植到 long read。
- MPN 案例的輸入是 single cell，但沒有真值樹，準確度只來自模擬，所以不算 C3。
