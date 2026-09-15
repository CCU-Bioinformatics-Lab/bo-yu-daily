# PhyClone 主論文研究論證鏈

## 一句話

[STATED] PhyClone 是一個從一個或多個相關腫瘤 bulk-sequencing 樣本的 allele-specific read counts、copy number 與 tumour content，聯合推斷 SNV 分群及 clone phylogeny 後驗分布的 Bayesian non-parametric 方法；其關鍵是 FS-CRP tree-structured clustering prior、把 clonal prevalence 積分掉的 collapsed likelihood、以及 auxiliary-variable Particle Gibbs inference。（Abstract；§2 開頭，p.2；§2.1–2.3，pp.2–4；Discussion，p.8）

## Problem → Gap → Idea → Method → Evidence → Contribution

### 1. Problem：bulk mixture 使 clone 的演化關係難以辨認

[STATED] 癌症由 somatic mutations 驅動，不同基因型細胞亞群（clones）的組成與演化關係會影響 malignant ontogeny、治療抗性與轉移，因此重建 clonal history 是 cancer genomics 的基本問題。（Abstract；Introduction，p.1）

[STATED] Single-cell sequencing 能更直接刻畫演化，但在病人樣本上的成本與技術門檻限制其使用；bulk sequencing 仍是常用資料來源，而每個樣本混合多個細胞族群，必須做 computational deconvolution。（Introduction，p.1）

### 2. Existing gap：只分群不等於有 phylogeny；ISA 也只給弱識別性

[STATED] 多個既有方法聚焦把具有相同 cellular prevalence 的 mutations 分到同群，這可找出 clonal populations，卻忽略 clones 間的 phylogenetic relationship。（Introduction，p.1）

[STATED] 在 infinite-sites assumption（ISA）下，祖先 mutation 的 cellular prevalence 不應低於後代；但單一或資訊不足的 bulk samples 常無法區分 sibling 與 ancestor–descendant 關係。多區域樣本中 prevalence order 的反轉能證明兩者位於不同 branches，但整體仍只有 partial identifiability。（Introduction，pp.1–2）

[STATED] Mutation loss（例如 genomic instability 導致大片段 deletion）會破壞 mutation/cellular-prevalence 的 additivity constraint，而這在 genome-unstable cancers 並非罕見。（Introduction，p.2）

[INFERRED] 因此真正的計算問題不是產生唯一一棵「看起來合理」的樹，而是在 clone 數未知、topology 數量指數成長、prevalence 為連續高維 nuisance parameters、資料又只部分識別 topology 的情況下，保留 compatible phylogenies 的不確定性。

### 3. Core idea：在離散 tree-structured clustering space 做 collapsed Bayesian inference

[STATED] 作者用 Bayesian posterior 表達 bulk data 只部分解析 clonal phylogeny 的事實，並以新提出的 forest-structured Chinese restaurant process（FS-CRP）同時對未知 cluster 數與 tree topology 給 prior。（Introduction，p.2；§2.1，pp.2–3）

[STATED] 每個 sample 的 clone-exclusive prevalence 取 Dirichlet prior；某 node mutation 的 cellular prevalence 是該 node 整個 descendant subtree 的 clonal prevalence 總和。這同時施加 simplex（總和為一）與 ISA 的 inheritance constraint。（§2.1，pp.2–3；§2.2，p.3）

[STATED] 將 node prevalence 積分掉後，posterior sampling 發生在不隨 samples 數增加而增加維度的 tree/clustering space；tree-dependent integral 由 dynamic programming 在 `O(|V|^2)` 計算。（§2.2.1，p.3；Discussion，p.8）

[STATED] 為探索 variable-size tree space，PhyClone 以 bottom-up SMC 建樹，再把它嵌入 Particle Gibbs；mutation ordering `sigma` 被當作 auxiliary variable 重抽，以解除固定順序無法到達所有 trees 的問題；另加 subtree prune-regraft 與固定 topology 的 mutation reassignment moves 改善 mixing。（§2.3–2.3.2，pp.3–4）

[STATED] PhyClone 可接受 PyClone-VI 等 non-phylogenetic pre-clustering：預先同群的 mutations 不可被拆開，但不同 pre-clusters 可在同一 tree node 合併，故 phylogenetic constraints 仍可 refine 原分群。（§2.2.2，p.3）

[STATED] 對 mutation loss/additivity violation，模型加入 per-SNV binary outlier state；outlier 不加入 tree，其 cellular prevalence 取 Uniform prior 並數值積分。（§2.2.3，p.3）

[INFERRED] 這個 outlier extension 是「把不相容 SNV 排除出樹」的 robustification，不是顯式表示 mutation 在哪條 edge 發生 deletion，也不會直接輸出 loss event history。

### 4. Input → computation → output

```text
related bulk tumour samples
  allele-specific ref/alt counts + CNV + tumour content
                    ↓
optional PyClone-VI pre-clustering (recommended for WGS)
                    ↓
FS-CRP prior over mutation partition b and forest/tree T
                    ↓
PyClone emission f(x_n | cellular prevalence), CN/purity corrected
                    ↓
integrate node clonal prevalences rho over simplex
                    ↓
bottom-up SMC inside Particle Gibbs + MCMC mixing moves
                    ↓
posterior over node count, mutation-to-node assignment, topology
  (+ posterior/MAP re-instantiation of prevalences if requested)
```

[STATED] Input/output 的明確依據是 §2 開頭與 Fig.1（p.2）、§2.1 結尾（p.3）及 Discussion（p.8）。

### 5. Evidence：作者如何測試每一層主張

1. [STATED] **Outlier mechanism**：FS-CRP-loss simulations（600 SNVs、depth 1000、8 samples、purity 1.0、loss fraction 0/0.1/0.2，各 100 trials）比較 PhyClone with/without outlier。Outlier-naive 版本隨 loss 增加而下降；outlier 版本較 robust，無 loss 時沒有可見代價。（§2.4.1.1，pp.4–5；§3.1、Fig.2，p.6）
2. [STATED] **Bayesian accuracy/scalability**：TSSB-Low（100 SNVs；2/4/8/16，另含 128 samples）來自與 PhyloWGS 等價的生成模型，理應偏袒 PhyloWGS；PhyClone 在 RRE、LPR、AD F-score 顯著勝全部方法，V-measure 顯著勝 PhyloWGS；PhyloWGS 慢逾一個數量級，故後續不納入。（§2.4.1.2，p.5；§3.2、Fig.3，pp.6–7；supplementary Figs 10–11）
3. [STATED] **跨生成模型 robustness**：在 TSSB-High、Pairtree、CONIPHER-no-noise 資料上比較 clustering、ancestry 與 posterior metrics。PhyClone 在 AD F-score 從未被其他方法顯著勝過；唯一被顯著勝出的主文例子是 TSSB-High V-measure 被 CONIPHER 勝過。（§3.3、Fig.4，pp.7–8；supplementary Fig.10）
4. [STATED] **noise / ISA violations**：在 CONIPHER-noise，PhyClone、CONIPHER、fastBE 的 AD F-score 無顯著差異，三者顯著勝 Pairtree 與 Orchard；copy-number-perturbed no-noise dataset 上無方法顯著勝 PhyClone。（§3.4、Fig.5，pp.7–8；supplementary Fig.14）
5. [STATED] **real mutation loss**：三位 HGSOC 病人，以 single-cell/targeted evidence 為 ground truth；patient 3 的兩種 count datasets 中，PhyClone 正確排除兩群 lost SNVs 並重建完整 topology，CONIPHER/fastBE 未排除而無法完整重建；PhyClone 的 patient-3 metrics 最佳。（§2.4.1.5，pp.5–6；§3.5、Fig.6，pp.7–9；supplementary Table 1）

### 6. Contribution：最小且可防守的結論

[STATED] 方法貢獻有三個相互依賴的部分：（i）FS-CRP non-parametric prior 聯合表達 mutation clustering 與 forest/tree topology；（ii）tree constraints 下 marginalize clonal prevalence 的 collapsed inference，使 sample 數增加不增加參數空間維度；（iii）auxiliary-order Particle Gibbs/SMC sampler，高效探索 tree space。（Discussion，p.8）

[STATED] 實證貢獻是：在多種 synthetic generators、樣本數與 real HGSOC mutation-loss case 上，PhyClone 通常與或優於 contemporaneous baselines，且能利用 pre-clustering 處理 WGS-scale SNVs。（Abstract；§3.2–3.5，pp.6–8；Discussion，p.8）

[INFERRED] 最具辨識力的創新不是單一 likelihood，而是把成熟的 PyClone emission 與新的 tree prior、collapsed integration、PG search 組合成「樣本越多時仍能有效利用跨樣本 constraints」的 posterior inference system。

## 不應過度延伸的說法

- [INFERRED] 「No method significantly outperformed PhyClone」不等於 PhyClone 在所有條件均實質最佳，也不等於 equivalence；它只表示在作者的 Friedman–Nemenyi threshold (`P < .01`) 下未檢出顯著劣勢。
- [STATED] 主文未提供多數 pairwise effect sizes 或 exact P-values；量化幅度必須由 XLSX/supplement 重建，不能由主文文字自行補數字。
- [STATED] Outlier simulation 明確被作者承認偏向 PhyClone，且只比較兩個 PhyClone variants；它驗證 component behavior，不是跨方法優勢。（§3.1，p.6）
- [STATED] 實際 real-data 證據只有三位 HGSOC patients，patient 3 是最強 loss reconstruction example；不應外推成所有 cancer/CNV contexts。（§2.4.1.5，p.5；§3.5，pp.7–8）

