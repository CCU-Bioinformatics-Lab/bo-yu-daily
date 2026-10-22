# 01 論文描述的模擬設計

本檔只記錄**論文與補充文件的描述**〔論文〕。程式的實際行為見 [02](02_CODE_PIPELINE.md)。

來源：主文 `references/phyclone_main.pdf`（Hurtado et al. 2025, *Bioinformatics* 41(7) btaf344）；補充文件 `references/phyclone_supp.pdf`。頁碼是 PDF 頁碼。

## 1. Generative model（補充 S1.3，p.2–3；Fig S1／S2，p.12）

PhyClone 的模擬資料就是從這個 prior 抽樣：

```text
b | α        ~ CRP(α)                      # 把 N 個 SNV 分成 |b| 個 cluster
F | b        ~ Uniform(所有 |b| 個節點的 rooted forest)
T            = F 加一個 dummy root r，r 連到 F 的所有 root
ρ_m | κ      ~ Dirichlet(κ·1_|V|)          # 每個 sample m 各抽一次 clonal prevalence
ρ̄_vm         = Σ_{v' ∈ subtree(v)} ρ_v'm   # cellular prevalence（CCF）= 子樹 clonal prevalence 總和
x_nm         ~ PyClone(x | d, π, ρ̄_{v_n m}, t)
```

- forest 的 prior 是 `1 / (|b|+1)^(|b|-1)`，由 Cayley 公式推得。
- 多 sample 只是每個 sample 各抽一個 Dirichlet。樹與分群在 sample 間共用。

## 2. Emission：PyClone allele count model（補充 S1.1–S1.2，p.1–2）

每個 SNV 把細胞分成三群：normal（N）、沒有該突變的腫瘤細胞（R）、有該突變的腫瘤細胞（V）。

```text
ξ(G, ρ̄, t) = [ (1−t)·c(G_N)·μ(G_N) + t(1−ρ̄)·c(G_R)·μ(G_R) + tρ̄·c(G_V)·μ(G_V) ] / Z
Z          = (1−t)·c(G_N) + t(1−ρ̄)·c(G_R) + tρ̄·c(G_V)
μ(G)       = min(max(b(G)/c(G), ε), 1−ε)
x | d      ~ Binomial(d, ξ) 或 BetaBinomial(d, ξ, γ)
```

- `t` 是 tumour content（purity），`c(G)` 是 total CN，`b(G)` 是帶突變的 allele 數，`ε` 是定序錯誤率。
- genotype 未知時，對候選 genotype 取平均：`p(x) = Σ_i π_i · f(x | G_i)`。
- 候選 genotype 用「major copy number」法（S1.2）：
  - 突變在 CN 事件**之前**：`G_R = G_N`，`G_V` 帶 1 到 `c_major` 個突變 allele。
  - 突變在 CN 事件**之後**：`G_R` 全是 ref，`G_V` 只帶 1 個突變 allele。
  - 每個候選 genotype 的 prior 相等。例：major=2、minor=1 時有 `(AA,AA,AAB)`、`(AA,AA,ABB)`、`(AA,AAA,AAB)` 三個，各 1/3。

## 3. Outlier model（補充 S1.7，p.7–8）

- 每個 SNV 有 outlier prior `ν_n`。outlier 的 CCF 視為 Uniform，用數值積分消掉。
- 有 cluster 輸入時，可依「突變集中在少數染色體」判定 cluster 可能是 loss，給高 prior（預設 0.4），其他給低 prior（預設 0.0001）。p-value 用 10,000 次重抽，門檻 0.01。

## 4. Benchmark 資料集怎麼生成（主文 §2.4.1，p.4–5；Fig S14 說明，p.25）

主文說資料是「新模擬資料＋已發表模擬資料＋真實資料」的組合（p.4）。

| 資料集 | 來源 | 樹與分群 | 計數生成 | 規模 |
|---|---|---|---|---|
| FS-CRP Loss | 新模擬 | FS-CRP prior | PhyClone 自己的模型 | loss 比例 {0.0, 0.1, 0.2} × 100 trials；600 SNV、depth 1000、8 samples、tumour content 1.0 |
| TSSB-Low／High | 新模擬 | tree-structured stick breaking prior | diploid heterozygous、tumour content 1.0、depth 1000 | samples {2,4,8,16}（Low 另有 128）；Low 100 SNV、High 10,000 SNV |
| Pairtree | 已發表（Wintersinger 2022） | Pairtree 模擬器 | Pairtree 模擬器 | K {3,10,30,100} × samples {1,3,10,30,100} × depth {50,200,1000} × SNV/cluster {10,20,100} × 4 replicates，共 576 |
| CONIPHER Noise／No-noise | 已發表（Grigoriadis 2024） | CONIPHER 模擬器 | CONIPHER 模擬器；Noise 含定序錯誤或 mutation loss 造成的 ISA 違反 | 各 150 trials，依 sample 數分 2–3、4–7、8+ |
| Copy Number Error | 由 CONIPHER No-noise 擾動 | 同 CONIPHER | 每個 sample 有比例 p ∈ {0.0, 0.1, 0.2} 的 region 改 CN：major 或 minor ±1，或兩者同時 ±1 | 150 × 3 = 450 |
| HGSOC | 真實資料（McPherson 2016） | 單細胞＋bulk 推論的參考樹 | WGS 或 WGS＋targeted 的真實計數 | 3 病人 × 2 版本 |

### FS-CRP Loss 的 loss 步驟（p.4–5）

1. 依 loss 比例隨機選出要丟掉的 SNV。例：100 個 SNV、比例 0.2 → 選 20 個。
2. 選一個 loss-node。它必須是這些 SNV 所在節點的後代。
3. 把這組 SNV 放到同一條染色體上，模擬 subclonal 染色體區段 loss 的 locality。
4. loss-node 與其所有後代，從 cellular prevalence 中扣掉這組 SNV 的 prevalence。

主文明說這個資料集「天生偏向 PhyClone」，所以只比較有／無 outlier 的 PhyClone（p.6）。

## 5. 推理設定（主文 §2.4.2，p.5）

- 合成資料先用 PyClone-VI v0.1.6 分群：初始 100 clusters、100 restarts、binomial density。HGSOC 用原論文的 cluster。
- PhyClone v0.7.0：4 chains、burn-in 100、5000 MCMC iterations、100 particles、Beta-Binomial、semi-adapted kernel。outlier 版加 `--assign-loss-prob`。輸出取 MAP joint likelihood 的樹。
- 每個 trial 限時 48 小時。

## 6. 程式正確性測試（補充 S2.3，p.10–11）

這兩組測試也用模擬資料，對應的程式見 [02 §5](02_CODE_PIPELINE.md)。

- **Exact enumeration（S2.3.1）**：小資料窮舉 posterior，和 PG-SMC 的結果比對。三種 kernel（semi-adapted、fully-adapted、bootstrap）都要通過。
- **Marginalisation（S2.3.2）**：固定真樹，比較 PhyClone 的 grid 邊際 likelihood 與 importance sampler（Dirichlet 提案、1,000,000 iterations）。每組至少 10 棵樹，用雙尾 two-sample t-test 判定兩個分布相同。

## 7. 論文沒有交代的部分

- 隨機種子、CRP 的 α、CN 的抽樣分布、genotype 的抽樣方式。
- loss-node 怎麼從合格的後代中選出。
- TSSB 的超參數與生成程式。
- 生成程式與評估 pipeline 都沒有公開。〔論文；另見 `../phyclone_research/notes/zh-TW/00_SOURCE_MAP.md`〕

本機資料可以反推一部分參數，見 [03](03_BENCHMARK_DATASET_FORMAT.md)。
