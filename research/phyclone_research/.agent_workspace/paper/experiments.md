# 主論文實驗重建

## 共通設計

[STATED] Baselines：PhyloWGS、Pairtree、CONIPHER、Orchard、fastBE（§2.4、Table 1，p.4）。除首輪 TSSB-Low 後因 runtime 排除 PhyloWGS外，後續比較通常是其餘五種方法。

[STATED] Synthetic datasets 全以 PyClone-VI v0.1.6 pre-cluster：100 initial clusters、100 random restarts、binomial allele-count density；HGSOC 用原研究 clusters。Pre-clusters 供給 CONIPHER、Pairtree、Orchard、fastBE 與 PhyClone。每 trial 每 method 最多 48 h。（§2.4.2，p.5）

[STATED] Point metrics 用 default/top-scoring single tree；PhyClone 最終 tree 是 MAP joint-likelihood。Posterior metrics 是所有 unique solutions 的 likelihood-weighted average。（§2.4.2–2.4.3，pp.5–6）

[STATED] 統計檢定：每個 benchmark/metric 先做 Friedman global test；`P<.01` 才做 pairwise post-hoc Nemenyi，亦用 `P<.01` 判顯著，再由 mean difference 決定方向。（§2.4.3，p.6）

### Metrics

| Metric | What it evaluates | Direction | Locator |
|---|---|---:|---|
| V-measure | mutation clustering agreement with ground truth | higher better | §2.4.3, pp.5–6 |
| AD F-score | mutation-pair ancestor–descendant relation recovery | higher better | §2.4.3, pp.5–6；supp. Fig.9 |
| LPR | reconstructed clonal cellular-prevalence matrix vs ground truth（VAF reconstruction loss） | lower, including negative, better | §2.4.3, p.6 |
| RRE | likelihood-weighted evolutionary relationship recovery against all ISA-valid topologies fitting the true prevalence matrix | lower implied better; exact formulation deferred | §2.4.3, p.6 |

[STATED] LPR 對所有 methods 都用 PhyClone marginalization algorithm 打分，以避免 scoring bias；RRE/LPR 只報 TSSB 與 Pairtree datasets，因 CONIPHER data 不符合 perfect phylogeny、RRE enumeration 失效。（§2.4.3，p.6）

## E1. Outlier component under simulated mutation loss

**Question.** Outlier state 是否能緩解 deletion/loss 對 additivity 的大型違反？

**Dataset/setup.** [STATED] FS-CRP prior 生成 trees/clusters；隨機挑 loss proportion `{0,0.1,0.2}` 的 mutations，將其放同 chromosome，再選其 origin node 的 descendant 當 loss node；loss node 及下游 prevalence 均扣掉該 set。每比例 100 trials；每 trial 600 SNVs、depth 1000、8 samples、tumour content 1.0。（§2.4.1.1，pp.4–5）

**Comparison/metric.** PhyClone outlier-naive（PC-N）vs outlier-enabled（PC）；V-measure、AD F-score。（§3.1、Fig.2，p.6）

**Result.** [STATED] PC-N 隨 loss fraction 增加而明顯惡化；PC 對 loss robust 得多，且 loss=0 時加入 outlier 看不出 performance cost。（§3.1、Fig.2，p.6）

**Supported claim.** [STATED] Outlier state 對此類大幅 additivity violation 有效。

**Caveat.** [STATED] 作者明說 dataset inherent bias favours PhyClone，因此省略其他 methods；這只是一個 internal ablation。Fig.2 不提供檢定或精確 effect-size table。（§3.1，p.6）

## E2. TSSB-Low：Bayesian accuracy and scalability

**Question.** 在明確 Bayesian generative model 下，不同 modelling/inference strategies 的 accuracy 與 efficiency 如何？

**Dataset/setup.** [STATED] TSSB prior；diploid heterozygous mutations、depth 1000、purity 1.0；TSSB-Low 100 SNVs，samples `{2,4,8,16}`，另含 128 samples。（§2.4.1.2，p.5）

**Baselines.** 六方法，含 PhyloWGS；作者指出 TSSB model 與 PhyloWGS model 等價，故生成設定應偏袒它。（§3.2，p.6）

**Result.** [STATED] PhyClone 在 RRE、LPR、AD F-score 顯著勝所有方法；V-measure 顯著勝 PhyloWGS；沒有方法在任何上述 metric 顯著勝 PhyClone。PhyloWGS runtime 顯著慢於所有方法、超過一個數量級，且樣本越多差距越大。（§3.2，pp.6–7；Fig.3；supp. Figs 10C–D, 11）

**Interpretation.** [STATED] 作者據此說 fully Bayesian inference 可更準，pre-clustering 可在未犧牲 accuracy 下加速；並因 PhyloWGS runtime 及未優於其他方法，後續排除。（§3.2，p.6）

**Caveat.** [INFERRED] 「fully Bayesian 更準」由單一 generator family 支持，且 PhyClone 與 PhyloWGS 都 Bayesian、結果差異同時混合了 inference design/pre-clustering 等因素，不是 Bayesian-vs-non-Bayesian 的單因子實驗。

## E3. Robustness across phylogenetic generators

**Question.** 優勢是否跨越不同 simulation mechanisms，而非只在 FS-CRP/self-generated data 出現？

**Datasets.** [STATED]

- TSSB-High：10,000 SNVs；depth 1000；samples `{2,4,8,16}`；purity 1.0。（§2.4.1.2，p.5）
- Pairtree published simulations：subclones `K={3,10,30,100}`，samples `M={1,3,10,30,100}`，depth `D={50,200,1000}`，mutations `K*N`, `N={10,20,100}`，4 replicates，共 576 datasets。（§2.4.1.3，p.5）
- CONIPHER no-noise：published dataset 2；150 trials；按 samples 分 `2–3`, `4–7`, `8+`。（§2.4.1.4，p.5）

**Results.** [STATED]（§3.3、Fig.4，pp.7–8；supp. Fig.10）

- AD F-score：PhyClone 跨 datasets 顯著勝 Orchard、Pairtree；對 CONIPHER 的優勢除 TSSB-High V-measure 外多數顯著；在 pre-clustered Pairtree 上顯著勝 fastBE。
- V-measure：TSSB-High 上顯著勝 Pairtree/Orchard；唯一顯著勝 PhyClone 的 case 是 CONIPHER 在 TSSB-High V-measure。
- Posterior Pairtree：PhyClone RRE 勝 CONIPHER/fastBE；LPR 勝 CONIPHER/fastBE/Pairtree。
- Posterior TSSB-High：PhyClone LPR 勝全部；RRE 勝 Pairtree/fastBE/Orchard。RRE/LPR 沒有 method 顯著勝 PhyClone。

**Sample/node scaling result.** [STATED] 所有 methods 隨 node 數增加而退化，ranking 大致維持；退化與 nodes/samples ratio 有關。作者推論 bulk sequencing 不應期待解析遠多於 sample 數的 clones。PhyClone 隨 samples 增加的 median 改善與 IQR 收窄更明顯。（§3.3，p.7；supp. Figs 12–13）

**Caveats.** [INFERRED] Pairtree factorial grid 的 576 數量與列出的 full Cartesian product（4×5×3×3×4 = 720）表面不一致，可能因 combinations 被排除；需 supplement/XLSX 解決。作者的 clone-vs-sample rule 是結果導向的 general suggestion，不是 formal identifiability theorem。

## E4. Noise / ISA violation and CN perturbation

**Question.** Mutations 不滿足 ISA（sequencing error 或 mutation loss）時，方法是否仍能重建？CN error 是否改變 ranking？

**Dataset.** [STATED] CONIPHER dataset 1（noise），150 trials，依 sample count 三組；另使用 copy-number-perturbed CONIPHER-NN。（§2.4.1.4，p.5；§3.4，p.7）

**Result.** [STATED] Noise dataset 的 AD F-score 中 PhyClone、CONIPHER、fastBE 無顯著差異，且三者均顯著勝 Pairtree/Orchard；PhyClone 同樣從 samples 增加得到最大 median improvement 與 variability reduction。（§3.4、Fig.5，pp.7–8）

[STATED] CN-perturbed dataset 無 method 任一 metric 顯著勝 PhyClone；PhyClone 在 V-measure 與 AD F-score 顯著勝 fastBE/Orchard/Pairtree，AD F-score 亦勝 CONIPHER。CN error 增加的影響看起來很小；作者推測是所有方法共用的 PyClone-VI pre-clustering 對 sample-specific CN error 有 robustness，因 PyClone emission 保留 mutational-genotype uncertainty。（§3.4，p.7；supp. Fig.14）

**Caveat.** [STATED/INFERRED] CN robustness 的機制是作者以「we believe」「likely」提出的解釋，不是單獨驗證；所有 methods 共用同一 preprocessing 會掩蓋 downstream algorithms 對 raw CN error 的差別。

## E5. Real HGSOC mutation-loss reconstruction

**Question.** Real cancer 中經 single-cell/targeted validation 的 ancestral mutation loss，PhyClone 能否正確處理？

**Dataset/setup.** [STATED] 三位 HGSOC patients；patients 2、3 有 complex loss。兩種資料：WGS，以及把 overlapping SNVs 的 WGS counts 換成 targeted-deep counts 的 WGS+Targeted。Ground-truth trees 來自 single-cell WGS/targeted deep sequencing。輸入含完整 processed/clustered SNVs，但 metric 前只保留 ground-truth-defining subset，並把因此變空的 nodes collapse 到 parent。（§2.4.1.5，pp.5–6）

**Method adjustment.** [STATED] HGSOC 用原研究 clusters；CONIPHER `min_cluster_size=3`，使小 loss clusters 有機會被推斷。（§2.4.2，p.5）

**Results.** [STATED]

- Patients 2、9：PhyClone、CONIPHER、fastBE 看似都能以不同 resolution 重建；Orchard 只在 patient 9 的 WGS+Targeted 準確。（§3.5，p.8；supp. Figs 15–16/Table 1）
- Patient 3：WGS 與 WGS+Targeted 下，PhyClone 都正確辨識並排除 ground-truth below-root 中 lost 的兩個 SNV clusters；CONIPHER/fastBE 未移除 lost SNVs，無法完整重建；PhyClone metrics 勝所有方法。（§3.5、Fig.6，pp.8–9；supp. Table 1）
- Pairtree 對三位病人都難以產生 valid single-rooted DAG，因此主文敘事聚焦其餘 methods。（§3.5，p.7）

**Caveats.** [INFERRED] `n=3` patients、cancer type 單一；ground truth 由 SNV subset 定義，評分又把推斷樹裁成該 subset 並 collapse nodes，可能低估 extra-node/assignment errors。主文「correctly identify and remove」是 outlier classification，不表示定位實際 deletion branch。

## 主文沒有提供、須由其他 analysts 補齊

- 每個 Nemenyi pair 的 exact P-value、rank、mean difference。
- 48-h timeout 的數量與 missingness handling。
- Figures 2–5 的 raw rows/cell ranges；posterior-solution weighting details。
- HGSOC supplementary Table 1 的具體 metric values。
- Pairtree 參數格與 576 datasets 的計數差異。

