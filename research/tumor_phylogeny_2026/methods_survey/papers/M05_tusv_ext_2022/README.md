---
paper_id: M05
category: "C1"
category_label: "短讀或未說平台（無 single-cell 真值）"
subtype: "c1_bulk_short_read"
sc_truth_strength: "none"
title: "TUSV-ext: Reconstructing tumor clonal lineage trees incorporating SNVs, CNAs and SVs"
year: 2022
doc_type: "method"
material: "mixed"
platform_class: "short_or_unspecified"
platform_detail: ["multi-region bulk short-read WGS", "simulated (no platform)"]
long_read_role: "none"
long_read_features: []
single_cell_truth: "simulated_only"
single_cell_tech: []
input_is_single_cell: false
tree_type: ["clone_tree", "cn_event_tree"]
cross_tags: ["structural_variant", "latent_allele_phasing", "multi_region"]
keywords_en: ["tusv-ext", "ilp", "gurobi", "multi-region bulk", "snv", "structural variation", "sv breakpoint", "allele-specific copy number", "latent allele phasing", "dollo", "deconvolution", "prostate cancer"]
keywords_zh: ["整數線性規劃", "結構變異", "等位基因特異拷貝數", "多區域取樣", "潛在定相"]
summary_zh: "ILP 聯合 SNV/SV/CNA 建樹；phasing 是潛變數。"
category_index: "../../../../PAPER_CATEGORIES.md"
---

# M05 TUSV-ext（Fu et al., Bioinformatics 2022, ISMB）閱讀筆記

## 書目、版本與檔案

| 項目 | 內容 |
|---|---|
| 書目 | Fu X, Lei H, Tao Y, Schwartz R. *Reconstructing tumor clonal lineage trees incorporating single-nucleotide variants, copy number alterations and structural variations.* **Bioinformatics 38(Suppl 1):i125–i133 (2022)**，ISMB 2022 proceedings。DOI [10.1093/bioinformatics/btac253](https://doi.org/10.1093/bioinformatics/btac253)，PMID 35758777，PMCID PMC9236577 |
| 日期 | PMC 引文寫 2022 Jun 27；Europe PMC first publication 2022-06-01 |
| 授權 | CC BY 4.0（OA） |
| 本地檔 | `paper.pdf` = **出版社正式版**（PMC OA 套件中的 VoR PDF，md5 `c552d4ef88b789dad436d5124641178b`，與 PMC metadata 一致），**9 頁**；`paper.txt` 由 `pdftotext -layout` 產生 |
| 來源 URL | `https://pmc-oa-opendata.s3.amazonaws.com/PMC9236577.1/PMC9236577.1.pdf`（PMC Open Access S3） |
| 未下載 | Supplementary Methods S1（完整 ILP，Eq. S27–S46）。本筆記只依正文的 ILP 摘要 |
| 頁碼規則 | `[p.N]` 指本地 PDF 實體頁。p.1 對應期刊頁 i125，p.9 對應 i133 |

## 問題與模型

### 輸入 [p.2–3]

輸入是多區域 bulk DNA 的 variant call（VCF），整理成三個矩陣：

- `F ∈ ℝ^{m×(l+g+2r)}`：各 sample 的平均 copy number。依序是 l 個 SV breakpoint、g 個 SNV、r 個 segment 的**兩個 allele**各一欄。
- `Q`：breakpoint 或 SNV 落在哪個 segment。
- `G`：哪兩個 breakpoint 屬於同一 SV。

注意，SNV 的輸入是「estimated mean copy number」（F 的一欄），**不是 read count** [p.3]。

### 目標式 [p.3, Eq.1]

```text
min_{U,C}  |F − U·C|₁  +  λ1·R  +  λ2·S
```

| 符號 | 意義 |
|---|---|
| `U ∈ ℝ^{m×N}` | 各 sample 的 clone 頻率，每列和為 1，**root normal clone 也在 U 裡** |
| `C ∈ ℤ^{N×(l+g+2r)}` | 每個 clone 的 breakpoint 與 SNV copy number，以及兩個 allele 的 segment CN |
| `N` | `2n−1`，即 binary tree 的節點數 |

**R：phylogenetic cost**（Eq.7–14）[p.4]：

```text
R = Σ_{edges (i,j)} Σ_s ( |Δ allele1 CN| + |Δ allele2 CN| )
```

這是沿樹 edge 加總的 allele-specific segment CN 變化 L1。等同假設每次只增減一個 copy、所有 segment 速率相同 [p.3]。

**S：VAF 一致性懲罰**（Eq.21–26）[p.4–5]：

```text
w_{p,b}   = Σ_s q_{b,s} (f_{p,s,allele1} + f_{p,s,allele2})    # 混合後的 segment 總 CN
π_{p,b}   = f_{p,b} / w_{p,b}                                  # 觀測 VAF
z_{p,b} ≥ | π_{p,b} · Σ_k u_{p,k}(c_{k,b,0} + c_{k,b,1})  −  Σ_k u_{p,k} c_{k,b} |
S       = Σ_p Σ_b z_{p,b}
```

也就是要求「模型推出的混合 variant CN ÷ 混合 segment CN」接近觀測 VAF，並以線性化（乘開）的 L1 形式寫進 ILP。

λ1、λ2 依問題規模用固定公式設定（§2.2.3）[p.5]。

### Tree 約束 [p.4]

- **Tree 結構**：binary tree。用 edge 矩陣 E 與 ancestor 矩陣 A，加上破環約束 `a_ij + a_ji ≤ 1`、`a_ii = 0`（Eq.2–3）。
- **Root 狀態**：root 沒有 SNV／breakpoint，每個 allele 的 CN 都是 1；所有 CN ≤ c_max（Eq.4–6）。
- **SNV 與 breakpoint 採 Dollo**：
  - 用 W 指示 variant 第一次出現在哪條 edge；同一 SV 的兩個 breakpoint 必須在同一條 edge 出現（S44–S46）。
  - 作者明說 SNV 的 no-homoplasy 假設「more dubious ... permit out of algorithmic necessity」。
- **Loss 與 duplication 只能跟著 CN 事件**：variant 的 loss 必須伴隨所在 segment、同一 allele 的 CN loss；duplication 也只能伴隨該 segment 的 duplication [p.4]。

### Allele phasing（latent）[p.4, Table 1, Eq.15–20]

- **論文描述**：
  - 引入 binary 變數 `D ∈ {0,1}^{(l+g)×2}`。`d_b = 1` 表示 breakpoint 或 SNV b 在第一個 allele，`d_b = 0` 表示在第二個 allele。
  - 再定義 `c_{i,b,0}`、`c_{i,b,1}`：clone i 在 b 位置的兩個 allele segment CN。
  - Eq.15–18 是 big-M 約束：在非新生 edge 上，variant CN 的變化量 `c_{j,b} − c_{i,b}` 必須與它所在 allele 的 segment CN 變化量一致。
  - Eq.19–20：`c_{k,b} ≤` 它所在 allele 的 segment CN。
- **Allele 標記規則**：
  - 前處理時，各 sample 一律把 copy number 較大的 allele 排成「第一個 allele」。
  - 理由是同一 segment 不太可能同時有 duplication 與 loss，所以「first segment shares a common allele in each sample」。
- **分析推論**：
  - 這個「第一個 allele」是 **major／minor 排序**，不是 germline haplotype 身分。
  - 當不同 sample 或 clone 之間出現 mirrored allelic imbalance（某 clone 失去 A、另一 clone 失去 B）時，「大的就是第一個」會把兩條 haplotype 混成一條。
  - 這是 TUSV-ext 的結構性弱點。

### 推論：coordinate descent [p.3]

1. 隨機初始化 U，且每列和為 1。
2. 固定 U 解 C（一個大 ILP，同時決定 tree E／A、W、D）。
3. 固定 C 解 U（只看 `|F − UC|`）。
4. 交替直到收斂或達到最大 iteration 數，可加 random restart。

- 每一步都是 Gurobi ILP。
- clone 數 n 由使用者指定上限，事後 collapse 頻率為 0 或 branch length 為 0 的 node。實務上約 9 個 clone 以內，再多就太慢 [p.5]。
- **擴展性處理**（§2.3）[p.5]：
  - 先抽樣 breakpoint 與 SNV，例如 ≤120 個 variant，用這批推樹。
  - 未抽中的 variant 再逐一列舉 edge 與 allele `d ∈ {0,1}`，選擇最能解釋其估計 CN 的位置。
  - 這一步考慮 variant 在 CNA 之前取得（CN 等於 segment CN）或之後取得（CN = 1），並對後代 CN 取期望。

## CN、multiplicity、purity、haplotype 怎麼處理

- **CN**：
  - allele-specific segment CN 是**推論變數**（C 的最後 2r 欄），F 中的混合 allele CN 是觀測值。
  - 有 clone-level 的 integer CN，也有 CN 演化成本 R。
  - 與 PhyClone 把 CN 當固定輸入不同。
- **Multiplicity**：
  - `c_{k,b}` 是 SNV 在 clone k 的整數 copy 數，上限是所在 allele 的 CN（Eq.19–20），所以 multiplicity 是明確變數。
  - 沿樹的變化受 allele CN 變化約束（Eq.15–18）。
- **Purity**：
  - 沒有獨立 purity 參數。normal 是 root clone，其在 U 中的頻率即 `1 − purity`。
  - 實例：真實資料 A32 推得 sample A、E 有少量 normal（clone 8）[p.8]。
- **Haplotype／phasing**：
  - SNV 與 breakpoint 在哪個 allele 由 latent 變數 D 決定。
  - allele 身分是「major 排第一」的排序，不是 germline haplotype。
  - 沒有用 read 層級的 phasing 或 linkage。
- **Read count 噪音**：
  - 主目標是 L1 距離，沒有 binomial 或 beta-binomial likelihood。
  - 模擬時才用 Poisson／binomial 產生 read count [p.6]。

## 實驗與可支持的結論

### 模擬 [p.5–7]

- **資料生成**：SV 長度服從 Poisson；SNV 隨機放置；allele-specific duplication／deletion／translocation／inversion 比例 2:2:1:1；CNA 由 SV 產生；depth 100。
- **Task 1**：已知 clone 數，leaf-only 模式。
  - 與 CNT-MD、原版 TUSV 比較 C 與 U 的 RMSE，以及 normalized RF distance。
  - TUSV-ext 較好；sample 數為 1 時所有方法都差（Fig.2–3）。
- **Task 2**：variant 上限 120。
  - 與 PyClone、TUSV 比較 breakpoint／SNV 的 co-clustering average precision 與 clone 數誤差。
  - sample 數為 1 時 PyClone 較好；sample 數為 5 或 10 時 TUSV-ext 較好。
  - clone 數為 7 時效能下降，要把每個 iteration 的時限拉到 5000 s 才恢復（Fig.4–5）。
- **Robustness**：不同 random start 會得到不同解；多跑幾個 start、選最好的有幫助（Fig.6）[p.6–7]。

### 真實資料 [p.7–8]

- 資料：Gundem 2015 前列腺癌 A32，5 個區域。
- 做法：8 次 subsample（約 80 breakpoint、40 SNV），每 iteration 4000 s；用 CASet／DISC 選最相近的兩個 run 作為共識。
- 結論：推得比原論文更複雜的 polyclonal seeding。
- **沒有 ground truth**，屬於定性描述。

### 可支持與不能支持的結論

- **可支持**：
  - 在作者的 simulator（CNA 由 SV 產生、SNV 依 Dollo 演化）下，三種 variant 聯合 deconvolution 比只用部分 variant 類型的方法好。
  - 多樣本是必要的。
- **不能支持**：
  - 對大量 variant 的可擴展性：靠 subsample 加事後 mapping。
  - Topology 的 uncertainty：作者自己列為缺口 [p.8]。
  - 單樣本 bulk 的表現。
  - phasing（D）推得對不對：論文沒有評估。

## 程式碼與可取得性

- Repo：<https://github.com/CMUSchwartzLab/TUSV-ext>，Python 2，**MIT**，最後 push 2025-01-24（`gh api`，2026-10-17 查），21 stars。
- 依賴：需要 **Gurobi license**；另有 ete2、PyVCF 等。
- 輸入：一個目錄，內含每個 sample 一個 VCF，內有 SV breakpoint、CNV、SNV 及其 processed copy number。
- 參數：`-n` leaf 數、`-c` c_max、`-t` iteration 數、`-r` restart 數、`-sv_ub`／`-const` subsample 上限、`-b` 自動設定 λ。
- 輸出：`C.tsv`、`U.tsv`、`T.dot`。
- 程式核對很有限：只看到 `tusv-ext.py` 把輸入矩陣命名為 `F_phasing`，未抽中的 SNV 由 `snv_matching.snv_assign` 指派。ILP 本體（`model/solver.py`）沒有讀。

## 相關後續：Sc-TUSV-ext 與 TUSV-int

### Sc-TUSV-ext

- **書目**：Bristy NA, Fu X, Schwartz R. *J Comput Biol* 32(8):723–737 (2025)，Epub 2025-03-06，DOI [10.1089/cmb.2024.0613](https://doi.org/10.1089/cmb.2024.0613)，PMC12501414。
- **讀取範圍**：只讀了 bioRxiv v1（10.1101/2023.12.07.570724，13 頁，暫存於 job tmp，未放入 papers）與 JCB 摘要。
- **相對 TUSV-ext 的改動**（依 bioRxiv v1）：
  1. **資料**：從 bulk 改為 scDNA。先用 MEDICC2 的 minimum-event distance 對 cell 做 hierarchical clustering，得到 n 個 clone。每個 clone 取眾數 CN，組成 `C_obs`。
  2. **目標式**：改成 `min_{Z, C_est} |Z·C_est − C_obs| + λR`。
     - Z 是 n×n binary 的 clone 對應矩陣，取代 U 的混合比例。
     - **沒有 S 項**：single-cell 不需要 VAF 混合一致性。
  3. **保留項目**：ILP、coordinate descent（Z 與 C_est 交替）、SNV／SV 的 Dollo，以及 loss 必須伴隨 CN loss 的約束。
  4. 未抽中 variant 的 mapping 機制沿用。
- JCB 正式版是否有進一步修改，沒有核對。

### TUSV-int

- **書目**：Bristy NA, Schwartz R. *Bioinformatics Advances* 5(1):vbaf234 (2025)，published 2025-09-29，DOI [10.1093/bioadv/vbaf234](https://doi.org/10.1093/bioadv/vbaf234)，PMC12571511，OA。
- **讀取範圍**：從 Europe PMC 的 full-text XML 抽取正文閱讀，未下載 PDF。
- **相對 TUSV-ext 的改動**：
  1. **資料**：bulk DNA-seq（多樣本），加上 scRNA-seq 推得的 **RNA clone allele-specific CN** `C_RNA`（由 Numbat 或 SIGNALS 產生）。
  2. **目標式**：
     ```text
     min_{U,C,M}  |F − U·C|  +  |C′ − M·C_RNA|  +  λ1·R  +  λ2·S
     ```
     - M 是 DNA clone 對 RNA clone 的 0/1 對應：每個 DNA clone 恰好對應一個 RNA clone，每個 RNA clone 最多對應一個 DNA clone。
     - C′ 等於 C 的 segment CN 欄。
  3. **scRNA 的貢獻**：只提供「clone 層級 CN profile 的錨點」。正文沒有看到使用 scRNA 上 SNV 的 cell-level 共現；這點與 PhylEx 不同，**依正文推斷，未核補充材料**。
  4. **保留項目**：Dollo 與 loss 伴隨 CN loss 的約束、coordinate descent、Gurobi，以及 TUSV-ext 的 allele 約束。
  5. 比較方法包括 TUSV-ext 與 Canopy2。
- Repo：<https://github.com/CMUSchwartzLab/TUSV-INT>，MIT，最後 push 2025-10-06。

## 對本 repo 的用途

### 可借用的設計（推論）

1. **「variant loss 只能伴隨同一 allele 的 CN loss；duplication 只能伴隨 segment duplication」**：這組 Eq.15–18 式約束，可以直接改寫成 PhyClone 中 SNV 在 haplotype 層級的 Dollo 規則，並與 HP 連動。
2. **Allele-specific CN 的演化成本 R**：可作為 haplotype CN 沿樹變化的 prior 或 penalty。PhyClone 目前沒有 CN 演化項。
3. **「先抽樣 variant 推樹，再把其餘 variant 映射上去」的兩段式流程**：與 PhyClone 預先 clustering 的用法類似，可作為擴展性對照。

### 若把 latent 的 D 換成觀測到的 HP（推論）

- **省下的變數與約束**：
  - D 的 `2(l+g)` 個 binary 變數直接固定。
  - Eq.15–20 的 big-M 形式中，凡含 `d_b` 的項都變成常數。原本「兩組各帶一個 big-M 開關的約束，由 D 選其一」，會退化成只對已知 HP 那一側的線性約束。ILP 變小，LP relaxation 也變緊。
  - 未抽中 variant 的 mapping 不用再列舉 `d ∈ {0,1}`。
- **Allele 身分**：
  - 「大的 CN 排第一」的規則可以換成以 longphase HP1／HP2 為準的 germline haplotype 身分。
  - 這樣就能表達 mirrored allelic imbalance：同一 segment 在不同 clone 失去不同 haplotype。
- **前提**：PS block 的 HP 方向要與 segment 層級的 haplotype CN 對齊，跨 PS block 會有翻轉問題（與 M04 相同）。
- **觀測量**：S 項可以拆成 HP1／HP2 兩份 VAF 一致性。HP-tagged read 的 variant 比例對應的是 `c_{k,b} / c_{k,b,d_b}`（單一 haplotype 內的比例），比總 VAF 更直接約束 multiplicity。

### 與 PhyClone 的差異

| 面向 | TUSV-ext | PhyClone |
|---|---|---|
| 框架 | 決定論 ILP 最佳化 | Bayesian |
| 資料模型 | L1，無 read count likelihood | Binomial／Beta-Binomial |
| CN | 推論 allele-specific CN 與 CN tree | CN 是固定輸入 |
| Tree | binary、clone 數固定 | 森林式 CRP（FS-CRP），clone 數不固定 |
| 規模 | 約 120 個 variant | 上千個 SNV |
| Purity | normal 是 root clone | 輸入參數 |

### 可行的最小實驗（推論）

**不建議跑 TUSV-ext 本體**：需要 Gurobi、Python 2，SNV 輸入是 mean CN。較便宜的做法：

1. 在本 repo 自己的原型裡，實作「SNV 的 Dollo loss 必須伴隨同一 HP 的 CN loss」這條約束，當作 PhyClone 樹的事後一致性檢查。
2. 在 HCC1395 的 PhyClone MAP tree 上，統計違反 HP 一致性的 SNV 比例。

## 核心判斷

1. TUSV-ext 是少數把 SNV／SV phase 到 allele，並要求 loss 必須伴隨同一 allele CN loss 的 bulk 方法。但 phase 是 latent 的 binary D，allele 身分是「major 排第一」，不是 germline haplotype。
2. 它用 L1 加 ILP，沒有 read count likelihood、沒有 uncertainty，規模只到約 120 個 variant 與 9 個 clone。可借用的是約束的寫法，不是推論引擎。
3. 換成觀測到的 HP，可以固定 D、消掉一半的 big-M 分支，並修正 mirrored allelic imbalance 的身分混淆（推論）。這是「HP 讓 phasing 從 latent 變成觀測值」最乾淨的例子。
4. 後續兩篇的改動：Sc-TUSV-ext 把資料換成 scDNA clone CN，目標式改成 `|Z·C_est − C_obs|`；TUSV-int 加入 scRNA clone CN 的錨定項。兩者都沒有加入 read 層級的連鎖或 phasing。
