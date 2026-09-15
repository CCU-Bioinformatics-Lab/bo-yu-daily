# 主論文方法重建

## 1. Inputs and target

[STATED] 對一個或多個 related tumour samples，PhyClone 接受每個 somatic SNV 的 allele-specific counts、copy-number information 與 tumour-content estimate；觀察資料 `X={x_n}` 用於 PyClone allele-count likelihood。（§2 開頭、Fig.1，p.2；§2.2，p.3）

[STATED] 推斷目標是 posterior distribution over clone phylogenies，包括 clone/node 數、每個 node 的 originating mutations、mutation 的 phylogenetic ordering；clonal prevalence 在 tree inference 時被 marginalize，事後可用 MAP 或 sampling reinstantiated。（§2 開頭，p.2）

## 2. Random variables and representations

| Symbol | Meaning | Biological/statistical role | Main-paper locator |
|---|---|---|---|
| `N` | SNV 數；indices `[N]={1,...,N}` | 基本 data items | §2.2, p.3 |
| `X`, `x_n` | 全部／第 n 個 SNV 的 read-count 與 CN data | emission observations | §2.2, p.3 |
| `b` | `[N]` 的 disjoint partition；每個 `b in bold b` 是一個 mutation cluster | 相同 evolutionary history 的 mutations | §2.1–2.2, pp.2–3 |
| `alpha` | CRP concentration | 控制 partition/cluster-number prior | §2.2, p.3 |
| `T=(V,E)` | rooted forest 加 empty root 後的 tree | clone ancestry | §2.1, p.2；Fig.1 |
| `v_n` | 包含 mutation n 的 cluster 所對應 node | mutation-to-clone assignment | §2.2, p.3 |
| `rho_v` | node v 的 clonal prevalence | malignant cells that originate at v；clone-exclusive mass | §2.1–2.2, pp.2–3 |
| `bar(rho)_v` | node v 的 cellular prevalence | 帶有 v 上 mutation 的 malignant-cell fraction | §2.2, p.3 |
| `T_v`, `V_v`, `C_v` | v-rooted subtree、其 nodes、v 的 children | 定義 descendant sum | §2.2, p.3 |
| `kappa` | Dirichlet parameter（主文未進一步解釋） | prior over node prevalences | collapsed joint, §2.2.1, p.3 |
| `o_n` | SNV n 是否為 outlier 的 binary indicator | 是否離開 tree model | §2.2.3, p.3 |
| `nu_n` | SNV n 的 outlier prior probability | controls loss/error robustness | §2.2.3, p.3 |
| `sigma` | mutation-index permutation | SMC growth order / PG auxiliary variable | §2.3–2.3.1, pp.3–4 |

## 3. FS-CRP prior

[STATED] FS-CRP 的生成過程有三步（§2.1，pp.2–3）：

1. 以 CRP 把 SNVs 分成 partition `b`，prior 為 `p(b|alpha)`。
2. 對與 cluster 數相同的 nodes，均勻抽一個 directed rooted forest of multifurcating arborescences；每 cluster 與 node 一對一。把 forest 的所有 roots 接到一個新 empty root，得到單根 tree。prior 記為 `p(T|b)`。
3. 每個 sample 抽一個長度等於 nodes 數的 Dirichlet vector `rho`，使 sample 內 clonal prevalences 加總為 1。

[INFERRED] `|b|+1=|V|` 的 `+1` 是 empty root 所佔 mass；主文未單獨說明 empty-root mass 的 biological interpretation，需 supplement/code 驗證。

## 4. Clonal prevalence → cellular prevalence

主文核心 identity（§2.2，p.3）：

```text
bar(rho)_v = sum_{v' in V_v} rho_{v'}
           = rho_v + sum_{v' in C_v} bar(rho)_{v'}
```

- [STATED] Biological meaning：mutation 若在 node v 起源，ISA 令它傳給所有 descendants，所以 harbour 該 mutation 的 cellular fraction 是 v-subtree 中所有 clone-exclusive fractions 的總和。
- [STATED] Statistical meaning：tree topology 把各 `rho_v` 經線性 descendant-sum map 轉成 emission 使用的 `bar(rho)_v`。
- [INFERRED] Consequence：對任一 parent/descendant pair，parent mutation 的 cellular prevalence 至少與 descendant 相同；siblings 的 cellular prevalence 總和受到其共同 ancestor mass constraint。

## 5. Basic likelihood

主文公式（§2.2，p.3）：

```text
p(X | rho, b, T) = product_{n=1}^N f(x_n | bar(rho)_{v_n})
```

- [STATED] `f` 是 PyClone model 的 allele-count emission，經 copy number 與 tumour content correction。（§2.2，p.3，指向 Supplement Methods S1.1–S1.2）
- [STATED] Conditional on `rho,b,T`，主文將 mutations 的 likelihood 寫成 product。
- [INFERRED] Tree 對 read counts 的影響全由 assignment `v_n` 與 induced cellular prevalence `bar(rho)_{v_n}` 進入；basic main-paper equation 沒有額外 sequence-context 或 phylogenetic branch-length term。
- [STATED] 主文為簡化以 single-sample notation 說明；multi-region extension 為每個 region/sample 各抽一個 Dirichlet prevalence vector。（§2.2，p.3）

## 6. Collapsed joint distribution

主文公式（§2.2.1，p.3）：

```text
p(X,b,T)
 = integral_{Delta_|V|} p(X,b,T,rho) d rho
 = p(b|alpha) p(T|b)
   integral_{Delta_|V|} p(rho|kappa) p(X|rho,b,T) d rho
 = p(b|alpha) p(T|b)
   integral_{Delta_|V|} p(rho|kappa)
   product_n f(x_n|bar(rho)_{v_n}) d rho
```

其中 simplex `Delta_k={rho in R_+^k : sum_i rho_i=1}`。

- [STATED] Inference role：積分掉 node prevalences，降低直接抽 continuous parameters 的維度與 sampling burden。
- [STATED] Tree dependence 使積分 non-trivial；Supplement §S1.5 給 dynamic programming algorithm，主文宣稱 complexity `O(|V|^2)`。（§2.2.1，p.3）
- [INFERRED] 因每個 sample 的 `rho` 已 marginalize，離散 state dimension 不隨 sample count 增長；但 likelihood evaluation 的總成本仍可能隨 samples 增加。Discussion 的「parameter space does not depend on number of samples」不能讀成 total runtime 完全與 sample count 無關。（Discussion，p.8）

## 7. Pre-clustering

[STATED] 可用 PyClone-VI 等快速 non-phylogenetic method 先分群；理論上可不做，但 WGS-size data 強烈建議做，否則 computational complexity 劇增。（§2.2.2，p.3）

[STATED] 約束是單向的：同一 pre-cluster 內的 mutations 永遠保持一起（不可 split）；不同 pre-clusters 可被 PhyClone merge 到同一 node。（§2.2.2，p.3）

[INFERRED] 因此下游 posterior 的 resolution ceiling 受 pre-clustering false merges 限制，而 false splits 尚可由 node merge 修補。

## 8. Outlier model

主文 joint likelihood（§2.2.3，p.3）：

```text
p(X,b,T,o)
 = product_n [nu_n * integral_0^1 f(x_n|rho)d rho]^{I(o_n=1)}
   * p(b|alpha)p(T|b)
   * integral_Delta p(rho|kappa)
       product_n [(1-nu_n) f(x_n|bar(rho)_{v_n})]^{I(o_n=0)} d rho
```

- [STATED] `o_n=0`：SNV 加入 tree 並用 descendant-constrained cellular prevalence。
- [STATED] `o_n=1`：SNV 以 standard PyClone likelihood、Uniform cellular-prevalence prior 獨立建模，該 prevalence 以 numerical integration marginalize。
- [INFERRED] 模型以 outlier absorption 處理 mutation loss；它辨識「此 SNV 不適合當作 tree-preserved mutation」，沒有在主文公式中指定 deletion edge、loss clone 或 repeated loss mechanism。
- [INFERRED] 任何造成 additivity/ISA incompatibility 的原因（loss、未建模 CN、count error）都可能被同一 outlier state 吸收，故 biological interpretation 不唯一。

## 9. Inference algorithm

### 9.1 Bottom-up SMC

[STATED] SMC 維護 particles，依 mutation order `sigma` 逐一加入 observation 並 reweight，最後近似 posterior；forest 由 leaves 向 roots（post-order）生長，使 partial likelihood 能配合 DP marginalization 高效計算。（§2.3，pp.3–4）

對下一 mutation `sigma(t+1)`，proposal 候選為（§2.3，p.4）：

1. 加入現有某個 root node；對每個 root परिण tree 計算 probability。
2. 建立新 node，從現有 root nodes 隨機選一個可為空的 subset 當 children。

[STATED] 演算法先隨機選 join-existing 或 create-new；新 node 的 child subset 是隨機抽樣，作者稱這是 proposal quality 與 computational complexity 的折衷。

### 9.2 Particle Gibbs 解 ordering restriction

[STATED] 固定 `sigma` 並不能生成所有 trees：若 `x=sigma_i`, `y=sigma_j`, `i<j`，則 x 為 y 祖先的 tree 不可到達；甚至第一個 element 除非 singleton tree 否則不能當 root。（§2.3.1，p.4；supplementary Figs 5–7）

[STATED] PG 把 SMC 嵌入 MCMC，交替抽 constrained `sigma` 與 `(T,b)`；`sigma` 必須使現有 tree 可由 SMC 生成。由任何 iteration 可到 singleton tree，而 singleton 下 `sigma` uniform，作者據此主張 sampler 可到所有 trees。（§2.3.1，p.4）

### 9.3 Additional MCMC moves

[STATED] 兩個額外 moves 都不改 node 數（§2.3.2，p.4）：

- **Subtree prune-regraft**：隨機選 node，detach 其 subtree，計算掛到每個候選 node 的結果 probability，再 Gibbs-sample attachment。
- **Mutation/node reassignment**：shuffle data order；逐點考慮移到其他 node。只有從原 node 移除該 data point 不會清空原 node 時才做，因此 topology 維持 isomorphic。

[INFERRED] Node-number mixing 必須由 Particle-Gibbs tree update，而非這兩個 auxiliary moves 提供。

## 10. Experimental inference settings and selected output

[STATED] Benchmark 的 PhyClone v0.7.0 使用 4 independent chains、100 burn-in、5000 MCMC iterations、100 particles、Beta-Binomial allele-count density、semi-adapted proposal kernel；loss-enabled 版本用 `--assign-loss-prob`，low/high outlier priors 分別 0.0001/0.4；最終 tree 取 MAP joint-likelihood。（§2.4.2，p.5）

[STATED] 這些是 benchmark settings，不應未經 code/default verification 稱為現行 CLI defaults。

## 11. Main-paper-only unresolved method details

- `p(b|alpha)`、uniform forest prior `p(T|b)` 的 closed form，及 `kappa` 的確切設定：主文未完整列式；指向 Supplement。
- PyClone `f` 對 ref/alt counts、copy number genotype、purity 的完整 equation：主文未列；指向 Supplement S1.1–S1.2。
- DP quadrature/discretization 與 `O(|V|^2)` derivation：主文未列；指向 Supplement S1.5。
- SMC target density、weights、resampling schedule、semi-adapted proposal 定義：主文未列；指向 Supplement S1.6.1。
- Convergence diagnostics、chain combination、posterior solution weighting細節：主文未說明。

