# PhyClone 驗證、benchmark 與限制

這份文件只整理論文與 supplementary material 真正做過的 validation；「程式能跑完」不等於「tree 已被 biological truth 證實」。

## 1. Code correctness：先驗證 sampler 沒有把數學寫壞

Supplementary Section S2.3 使用兩類測試。

### 1.1 Exact enumeration test

在 mutation 數量很小、所有 topology 可以完整列舉的問題上：

1. 生成小型 simulated data；
2. 對所有可行 tree/cluster configuration 精確枚舉 posterior；
3. 跑 PhyClone PG-SMC；
4. 比較 inferred posterior 與 exact truth；
5. 要求所有 posterior values 在預先定義 tolerance 內接近 truth；
6. 對 bootstrap、semi-adapted、fully-adapted proposal versions 都重複。

它測到的不只是某一個 function，而是 Tree、distribution、proposal、SMC/PG 等多個元件一起運作時有沒有 inference-breaking bug，因此本質上是 integration-level correctness test。

### 1.2 Marginalisation likelihood comparative test

這個測試固定一棵 ground-truth tree 與 mutation clustering：

1. 用 PhyClone 的 CCF-grid/tree dynamic-programming marginalisation 計算 likelihood；
2. 另一邊從 Dirichlet prevalence 抽樣，使用 importance sampling 近似同一個 likelihood；
3. 每個 trial 的 importance sampler 用 1,000,000 次 draws；
4. 至少 10 個獨立 simulated trees/trials；
5. 用 independent two-sample, two-tailed t-test 檢查兩組 likelihood distribution 是否統計上相同。

這能驗證「把 prevalence 積分掉」與「顯式抽 prevalence」是否在 distribution 層面一致，但不會直接證明 real tumour tree 正確。

## 2. Synthetic benchmark families

論文把 PhyClone 與 PhyloWGS、Pairtree、CONIPHER、Orchard、fastBE 比較，資料包含：

| Dataset family | 目的 |
|---|---|
| FS-CRP loss | 在 PhyClone 自己的 FS-CRP tree prior 下加入 mutation loss，測 outlier/loss model |
| TSSB-Low / TSSB-High | 控制 mutation/node/sample 規模，測 Bayesian inference 與 scalability |
| Pairtree | 使用 pre-clustered datasets，改變 sample、mutation、depth、copy-number 等條件 |
| CONIPHER-NN | noise-free perfect-phylogeny 情境，比較 clustering/tree reconstruction |
| CONIPHER noise | 包含 sequencing error 或 mutation loss 導致 ISA violation |
| Copy-number perturbed | 測 sample-specific CN error 對 methods 的影響 |
| HGSOC | 三位病人的 real multi-sample tumour data，另有 single-cell/targeted sequencing truth |

完整 benchmark archives 的 latest Zenodo record 是 [15065504](https://zenodo.org/records/15065504)；論文引用的 concept DOI 是 [10.5281/zenodo.13240565](https://doi.org/10.5281/zenodo.13240565)。本 repo 沒有複製數 GB 的 benchmark tarballs，只保存 metadata/DOI 與 paper supplementary metric workbooks。

## 3. Metrics

### 3.1 V-measure

衡量 mutation clustering accuracy。它回答：「方法把一起起源/具有相同 evolutionary history 的 mutation 分得像不像 ground truth？」

### 3.2 Ancestor–descendant F-score

衡量 pairwise ancestor/descendant relation reconstruction。它比單純看 cluster assignment 更接近「tree edge/order 是否合理」。

### 3.3 Log perplexity ratio（LPR）

posterior metric，用來評估 model posterior 對資料的解釋能力。論文只在符合適當 assumptions 的 TSSB 與 Pairtree datasets 報告 posterior metrics。

### 3.4 Relationship reconstruction error（RRE）

先枚舉所有符合 ISA 且符合 ground-truth cellular prevalence matrix 的 valid topologies，再評估方法重建的 pairwise evolutionary relationship 距離。CONIPHER dataset 不符合 perfect phylogeny，因此該 enumeration-based RRE 不適用；論文沒有把這個 metric 強行套在 CONIPHER 上。

### 3.5 時間與 sample scalability

另比較 running time，並觀察 sample 數量增加時 accuracy、median performance 與 variability 的變化。論文的主要趨勢是：PhyClone 受益於更多 samples，且在大 sample 數時比部分方法更能維持 performance。

## 4. 統計比較規則

每個 benchmark metric 的方法差異先做 Friedman test；若 global test `P < .01`，再做 pairwise Nemenyi post-hoc test，並以 mean difference 判斷方向。

這是「在該 benchmark、該 metric、該 sampling 設定下的方法比較」，不是 universal superiority proof。多重 dataset/model family、方法設定與 metric assumptions 都會影響 interpretation。

## 5. Real-data validation：HGSOC

論文使用三位 high-grade serous ovarian cancer patients 的資料；其中 patients 2、3 有複雜 mutation loss。Ground truth 來自既有研究的 single-cell、whole-genome 與 targeted deep sequencing evidence。

Validation flow：

1. 以 WGS 或 WGS + targeted deep sequencing counts 建立 PhyClone-compatible input；
2. 以 ground-truth-selected SNVs 評估 inferred tree；
3. 對各方法 output 做 post-processing，只保留 ground-truth defining mutations；
4. 比較 method tree 與 ground-truth clone assignment/phylogenetic relationships；
5. 檢查能否把真實 lost SNV clusters 移到 outlier/lost state。

Paper 的具體觀察是：patient 3 中，PhyClone with outlier modelling 能移除兩個在 ground-truth clone 下方被 loss 的 SNV clusters；這使它在該 patient 的 metrics 上優於未能移除這些 lost SNVs 的方法。

### Real-data claim ceiling

- 只有三位病人，不是 large clinical cohort。
- Ground truth 只定義於被 single-cell/targeted sequencing 選中的 mutation subset。
- WGS 與 targeted counts 的 preprocessing/provenance 不由 PhyClone workflow 自己完成。
- Ground truth 是一個 orthogonal evidence set，不是每個 cell/每個 mutation 的無誤絕對真相。

## 6. 重要 limitations

### 6.1 Sub-clonal copy-number variation

論文明確指出，底層 PyClone mutational-genotype correction 無法建模 sub-clonal CNV。這會影響 allele-count → CCF emission，進而影響 cluster/tree posterior。更多 samples 可以減輕 ambiguity，但不等於消除 CNV model misspecification。

### 6.2 Clone count vs sample count

論文觀察到 node 數增加時所有 methods 的 performance 會下降，且 degradation 與 node/sample ratio 有關。因此 bulk data 不應被期待可靠解析遠多於 sample 數的 clones。

### 6.3 Loss simulation 的方法偏向

FS-CRP loss simulation 直接使用 PhyClone 的 prior/data-generating structure，對 PhyClone 的 loss model 有內在有利條件。這類結果可證明「在該 model family 下能 recovery」，不能單獨代表對所有 cancer evolution process 都公平。

### 6.4 Pre-clustering 的 trade-off

pre-clustering 降低計算量，特別適合 WGS；但 cluster constraints 也會改變 posterior search space。雖然 PhyClone 可以 merge 不同 input clusters，仍應把 PyClone-VI version、seed、cluster file hash 與 settings 當成 provenance。

### 6.5 Posterior summary 不是 validation

MAP tree、consensus tree、high sampled count 或 high joint likelihood 都是 inference summaries；它們不等於 convergence proof、truth recovery 或 biological causality。需要另外保存 chain mixing、topology diversity、simulation truth recovery、orthogonal CN/driver evidence 與 grouped holdout 等 validation receipt。

## 7. 對目前 tumor-tree repo 的直接提醒

1. PhyClone 的 `error_rate` 是 input-level optional column，缺省 `0.001`；目前 repo 的 active runtime 尚未有這個設定，文件 target 才固定記錄 `0.001`，在 C++／Python 同步前不得宣稱已生效。
2. PhyClone 的 `tumour_content` 是 input-level optional column；目前 repo 的 purity boundary 是 canonical `rho_ASCAT`，不應重新引入 legacy `tumor_dna_fraction`。
3. PhyClone 的 outlier/loss model 是獨立 modeling choice；目前 repo 若未實作 mutation-loss state，就只能對 non-additivity 做 validation/claim ceiling，不能暗示已經能 infer loss。
4. PhyClone 的 pre-clustering 與 HDF5 trace 不是 current C++ backend contract；若要借用概念，應以 design/ADR/contract tests 明確記錄差異。
5. 論文使用的 correctness tests（exact enumeration、marginalisation comparison）很適合轉成 current finite-K model 的 contract tests，但輸入 schema、prior、tree state 與 output semantics 必須重新定義。
