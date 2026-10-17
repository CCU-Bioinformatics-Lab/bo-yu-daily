# M01 PhyClone（Hurtado, Bouchard-Côté, Roth；Bioinformatics 2025）

閱讀日：2026-10-17。標記：「論文描述」＝正式版主文或 supplement 明寫；「程式實作」＝我看過 repo 程式碼；「推論」＝我的分析。

## 書目、版本與檔案

- Hurtado E, Bouchard-Côté A, Roth A. **PhyClone: accurate Bayesian reconstruction of cancer phylogenies from bulk sequencing.** *Bioinformatics* 41(7):btaf344, 2025。DOI [10.1093/bioinformatics/btaf344](https://doi.org/10.1093/bioinformatics/btaf344)。PMID 40511985，PMCID PMC12964358。
- 日期：Received 2024-08-07；Revised 2025-05-20；Accepted 2025-06-11；Advance Access 2025-06-13（[p.1]）。授權 CC BY 4.0。
- Preprint：bioRxiv [10.1101/2024.08.14.607069](https://doi.org/10.1101/2024.08.14.607069) v1（2024-08-17，只有這一版，CC-BY-NC-ND）。

| 本地檔 | 版本 | 頁數 | 來源 |
|---|---|---|---|
| `paper.pdf` | **出版社正式版（VoR）**，PMC OA 收錄的 OUP 排版檔 | 10 | PMC OA S3：`https://pmc-oa-opendata.s3.amazonaws.com/PMC12964358.1/PMC12964358.1.pdf`（md5 `c9ce4f30d0dcdb3e7ed81231f7ad5189`，與 PMC metadata 一致） |
| `supplement.pdf` | 正式版的 Supplementary Methods／Figures／Table S1 | 28 | 同上，`btaf344_supplementary_data.zip` 內的 `supp.pdf`（zip 另含三個 xlsx，未放入本目錄；repo 的 `research/phyclone_research/btaf344_supplementary_data/` 已有一份） |
| `preprint_biorxiv_v1.pdf` | bioRxiv v1（只為比對差異而保留） | 14 | `https://www.biorxiv.org/content/10.1101/2024.08.14.607069v1.full.pdf` |
| `*.txt` | `pdftotext -layout` | — | — |

頁碼：`[p.N]` 指 `paper.pdf` 實體頁；`[S p.N]` 指 `supplement.pdf` 實體頁；`[pre p.N]` 指 preprint 實體頁。

附註：本地 `paper.pdf` 與 `research/phyclone_research/phyclone.pdf` 的 SHA-256 不同（前者 `a4b29606…`，後者 `413500e0…`），兩者都是 10 頁、OUP Arbortext 排版，差異可能只是下載來源的封裝。我沒有逐字比對兩者。

## 正式版與 preprint 的差異（重點）

逐段比對 `paper.txt` 與 `preprint_biorxiv_v1.txt`，以下皆為「論文描述」。

| 項目 | Preprint v1（2024-08） | 正式版（2025-06） |
|---|---|---|
| 比較方法 | CONIPHER、Pairtree、PhyloWGS（3 個）[pre p.6] | 加入 **Orchard、fastBE**，共 5 個 [p.4]；新增方法功能比較表 Table 1 [p.4] |
| PhyClone 版本 | 0.5.0 [pre p.7] | **0.7.0** [p.5] |
| outlier 設定 | 主實驗用 outlier prior 0.0（無 outlier），另跑 PhyClone-O，low/high = **0.05／0.5** [pre p.7] | 主實驗**一律含 outlier**，low/high = **0.0001／0.4**；也寫明 100 particles [p.5]。結果章節第一節改成 outlier（3.1），並宣告之後只用含 outlier 版本 [p.6] |
| Pairtree 模擬資料 | 拆成 low（216）／high complexity（432） [pre p.6] | 合併為 K×M×D×N 的 576 個資料集 [p.5] |
| 新增實驗 | 無 | **CN 擾動實驗**（CONIPHER-NN 上以 p=0/0.1/0.2 擾動 major/minor CN，Fig. S14）[p.7, S p.25]；**posterior 指標 LPR、RRE**（Fig. S10）[p.6]；**節點數／樣本數比**分析（Fig. S12–S13）[p.7] |
| 評估後處理 | 只簡述 subset 到 ground truth SNV | 明寫 subset 後空節點併入父節點 [p.5] |
| TSSB-Low 結論 | PhyClone 在 V-measure 與 AD F-score 顯著勝過所有方法 [pre p.8] | 改寫為 RRE、LPR、AD F-score 勝過所有方法，**V-measure 只顯著勝過 PhyloWGS** [p.6]（主張變保守） |
| CONIPHER noise | CONIPHER 與 PhyClone 無顯著差異 [pre p.9–10] | PhyClone、CONIPHER、fastBE 三者無顯著差異，皆勝 Pairtree、Orchard [p.7] |
| HGSOC | 只比 PhyClone／PhyClone-O／CONIPHER（Pairtree 失敗） | 加入 Orchard、fastBE；patient 3 只有 PhyClone 移除 lost clusters [p.8]；Table S1 有數值 [S p.27] |
| ISA 用語 | 「additivity assumption」為主 | 明確寫成 ISA，並解釋 multi-region 可用 prevalence 順序反轉判 sibling [p.1] |
| Supplement | Supplementary Figure 1–8 | 新增完整 Supplementary Methods：PyClone emission、genotype prior、**multi-root 懲罰（C=1000）**、DP 演算法、SMC target、PG σ 規則、sub-tree PG、outlier prior 指派法、快取與正確性測試 [S p.1–11] |
| 資料／程式可得性 | Zenodo 13240566 | Zenodo 13240565（資料＋各方法輸出）與 15062184（benchmark 用的 PhyClone 快照）[p.9] |

方法本身（FS-CRP、PyClone emission、DP 邊際化、PG＋SMC、SPR／reassign move、outlier）兩版一致；差異集中在 benchmark 範圍、outlier 預設與 supplement 的完整度。

## 問題與模型

**輸入**：每個 SNV 每個 sample 的 ref/alt counts、major/minor/normal CN、tumour content；一個或多個 sample [p.2]。可選 pre-clustering（PyClone-VI）[p.3]。

**Prior（FS-CRP）**（論文描述）[p.2；S p.2–3]：
```
b | α            ~ CRP(α)                          # SNV 分群
F | b            ~ Uniform(rooted forests on |b| nodes);  p(F|b) = 1/(|b|+1)^(|b|-1)  (Cayley)
T                = F 的所有 root 接到 dummy root r
ρ_s | T          ~ Dirichlet(κ·1_|V|)  每個 sample 各一      # clonal prevalence
ρ̄_v              = ρ_v + Σ_{v'∈C_v} ρ̄_v'                # cellular prevalence（ISA：SNV 傳給所有後代）
```
最終樹另乘 multi-root 懲罰 p(r|b) ∝ C^-(r-1)，C=1000，使單根樹比雙根樹大 1000 倍 [S p.3–4]。這是 supplement 才有的實作性調整（論文描述）。

**Likelihood（PyClone emission）**（論文描述）[S p.1–2]：
```
ξ(G, ρ̄, t) = [ (1-t)c(G_N)μ(G_N) + t(1-ρ̄)c(G_R)μ(G_R) + tρ̄c(G_V)μ(G_V) ] / Z
Z          = (1-t)c(G_N) + t(1-ρ̄)c(G_R) + tρ̄c(G_V)
μ(G)       = min(max(b(G)/c(G), ε), 1-ε)
f(x | ρ̄)   = Σ_i π_i · {Binomial | BetaBinomial}(x | d, ξ(G_i, ρ̄, t)[, γ])
```
G=(G_N, G_R, G_V) 是 normal、reference（無此突變的癌細胞）、variant 三群的 genotype。

**Multiplicity／CN 邊際化（"major copy number" genotype prior）**（論文描述）[S p.2]：
- 突變在 CN 事件**之前**：G_R = G_N，G_V 的 total CN = c_major + c_minor，variant copies = 1..c_major。
- 突變在 CN 事件**之後**：G_R total = c_major+c_minor（全 ref），G_V 有 1 個 variant copy。
- 所有候選 genotype **等權重**。例：major=2、minor=1 → (AA,AA,AAB)、(AA,AA,ABB)、(AA,AAA,AAB) 各 1/3。
- 無 allele-specific CN 時，major 設為 total、minor 設 0。

程式實作（`phyclone/data/pyclone.py::get_major_cn_prior`，tag 0.8.0）：與上式一致——before 情形產生 `(normal, normal, total)` 與 μ=x/total（x=1..major），total≠normal 時再加 after 情形 `(normal, total, total)`、μ=1/total；`log_pi` 均等。`major_cn==0` 的 SNV 直接被移除；`tumour_content` 缺則設 1.0；`error_rate` 預設 1e-3。

**prevalence 邊際化（DP）**（論文描述）[p.3；S p.4–5]：把 ρ̄ 離散到 L+1 格點，post-order 對子節點做卷積：
```
D_v^k(ρ̄) = Σ_{ρ̄'≤ρ̄} R_{v_k}(ρ̄') D_v^{k-1}(ρ̄-ρ̄')
S_v(ρ̄)   = Σ_{ρ̄'≤ρ̄} (ρ̄-ρ̄')^(κ-1) D_v^{|C_v|}(ρ̄')      # κ=1 時為累加
R_v(ρ̄)   = ℓ_v(ρ̄) S_v(ρ̄),   ℓ_v(ρ̄) = Π_{n∈v} f(x_n|ρ̄)
p(X|b,T)  = R_r(1)
```
複雜度 O(V(NL + CSL²)) [S p.5]；主文寫 O(|V|²) [p.3]。multi-sample 時每個 sample 各自卷積後相乘（推論：由「每 sample 各一 Dirichlet」與複雜度含 S 推得）。

**Outlier 模型**（論文描述）[p.3；S p.7–8]：
```
p(X,b,T,o) = Π_n [ν_n ∫_0^1 f(x_n|ρ)dρ]^{I(o_n=1)} × p(b|α)p(T|b) ∫ p(ρ|κ) Π_n [(1-ν_n) f(x_n|ρ̄_{v_n})]^{I(o_n=0)} dρ
```
outlier 的 CCF 取 Uniform 並數值積分。ν_n 可由「cluster 級 data-informed 指派」給：先選 CCF 最高者為 truncal，以 truncal cluster 的染色體分布為背景，對每個非 truncal cluster 抽 10,000 次算「涵蓋染色體數少於觀察值」的比例當 p 值，p<0.01 給 high prior（預設 0.4），否則 low（0.0001）[S p.8]。也就是說，outlier 先驗本身是**基因體位置聚集度**的 heuristic，用來近似「CN loss 造成的 mutation loss」（論文描述）。

**推論**（論文描述）[p.3–4；S p.6–7]：
- SMC 由下而上長森林：每步把 σ(t) 的 SNV 加到某個現有 root node，或開新 node 並隨機選一個（可空）現有 roots 子集作為子節點。target γ_t = p(X_t,b_t,T_t)，增量權重有封閉式 [S p.6]。
- 三種 kernel：bootstrap、fully-adapted、**semi-adapted**（預設；加入既有 node 時枚舉，開新 node 時隨機選子集）[S p.6]。
- **Particle Gibbs**：把 σ 視為輔助變數，交替抽 σ|T（只取能生成目前樹的 permutation：葉節點內 shuffle、子樹之間 bridge shuffle 交錯、再接父節點的 SNV；outlier 再隨機交錯）與 T|X,σ（conditional SMC）[S p.7]。
- **sub-tree PG**：隨機挑一個 SNV，以其所在 node 的父節點為子樹根重抽，緩解 PG degeneracy [S p.7]。
- 額外 MCMC move：SPR（Gibbs 選新的接點）與不改 topology 的 SNV 重新指派 [p.4]。α 在 iteration 間重抽 [S p.9]。
- 輸出：posterior trace；點估計用 MAP joint likelihood [p.5]，也有 consensus 與 topology report（程式實作，見 CLAUDE.md 指令）。

## CN、multiplicity、purity、haplotype 怎麼處理

- **CN**：外部給定、每個 SNV 每個 sample 一組 clonal major/minor CN；**不處理 subclonal CN**，作者列為主要限制，並建議未來參照 Frankell 2023 [p.8]（論文描述）。
- **Multiplicity**：不推論為參數，而是在 genotype prior 上**均勻混合後邊際化**（before-CN：1..major；after-CN：1）[S p.2]。multiplicity 與 CN timing 只在 likelihood 內部被加總掉，沒有輸出（論文描述；推論：posterior 可事後計算，但程式沒提供）。
- **Purity**：tumour content t 外給、固定 [S p.1]；不推論（論文描述）。
- **WGD**：沒有獨立模型；只能透過 major/minor CN 的數值間接反映（推論）。
- **Mutation loss**：用 outlier 吸收，不是在樹上明確建模「哪個 clone 失去哪些 SNV」（論文描述）；HGSOC patient 3 示範能正確移除兩個 lost cluster [p.8]。
- **Haplotype**：完全沒有。不用 phasing、不用 read 共現、不區分 major 是哪一個 haplotype（論文描述）。

## 實驗與可支持的結論

設定（論文描述）[p.4–5]：PhyClone 0.7.0，4 chains、100 burn-in、5000 iterations、100 particles、Beta-Binomial、semi-adapted；每方法每 trial 48 h 上限；所有方法共用 PyClone-VI 前分群（100 clusters、100 restarts、binomial）；HGSOC 用原論文 cluster。

| 資料 | 規模 | 主結果（論文描述） |
|---|---|---|
| FS-CRP loss | 600 SNV、depth 1000、8 samples、purity 1.0；loss 比例 0/0.1/0.2，各 100 trials | 無 outlier 版隨 loss 增加變差；有 outlier 版穩定，且 loss=0 時不受損 [p.6 Fig. 2] |
| TSSB-Low | 100 SNV，2–128 samples | RRE、LPR、AD F-score 顯著勝過全部；V-measure 只勝 PhyloWGS；PhyloWGS 慢一個數量級以上 [p.6] |
| TSSB-High | 10,000 SNV | AD F-score 勝 Orchard、Pairtree、CONIPHER；V-measure 被 CONIPHER 顯著勝過（唯一例外）[p.7] |
| Pairtree sims | 576 資料集（K≤100、M≤100 samples） | AD F-score 勝 Pairtree、Orchard、fastBE；LPR 勝 CONIPHER、fastBE、Pairtree [p.7] |
| CONIPHER NN／noise | 各 150 trials | NN 上多數勝出；noise 上與 CONIPHER、fastBE 平手 [p.7] |
| CN 擾動 | CONIPHER-NN 上 10%／20% 區域 CN ±1 | 各方法受影響都很小；作者歸因於共用 PyClone-VI 前分群 [p.7, S p.25] |
| HGSOC（McPherson 2016）| 3 patients，WGS 與 WGS+targeted | patient 3：PhyClone AD F 0.82／0.93，CONIPHER 0.70／0.80，fastBE 0.73／0.80 [S p.27] |

可支持的範圍（推論）：
- 「在模擬資料上通常不輸、常勝」有統計檢定支持（Friedman–Nemenyi，p<.01），但多數模擬 purity=1.0、CN 簡單（TSSB 只有 diploid heterozygous）[p.5]；**CN 複雜度高的情境證據薄**，CN 擾動實驗又被前分群掩蓋，無法單獨評估 PhyClone 的 CN 邊際化有多穩健。
- 真實資料只有 3 位 HGSOC 病人，n 太小，不能推廣到「真實資料普遍較佳」。
- 「樣本數越多越好」與「clone 數不應遠超過 sample 數」[p.7] 是 multi-sample 結論；**single-sample 是 PhyClone 最弱的區域**，正好是本 repo（每株一個 tumor、多個 nominal purity subsample）的情境（推論）。
- 所有方法都吃同一份前分群，所以 V-measure 差異主要反映「合併/拆分 cluster」能力，而不是從零分群（推論）。

## 程式碼與可取得性

- Repo：[Roth-Lab/PhyClone](https://github.com/Roth-Lab/PhyClone)，Python 3，**GPL-3.0**，9★；最新 tag **0.8.0**（2026-01-22），之前 0.7.1（2025-08-07）、0.7.0（2025-03-04）；最後 push 2026-09-24（gh API，查詢日 2026-10-17）。本 repo submodule 指在 0.8.0（commit `27383246`）。
- 論文 benchmark 用 0.7.0；Zenodo 快照 [10.5281/zenodo.15062184](https://doi.org/10.5281/zenodo.15062184)；資料與各方法輸出 [10.5281/zenodo.13240565](https://doi.org/10.5281/zenodo.13240565) [p.9]。
- 輸入：tidy TSV，欄位 `mutation_id, sample_id, ref_counts, alt_counts, major_cn, minor_cn, normal_cn, tumour_content, error_rate(可選)`；cluster 檔 `mutation_id, cluster_id`（可加 `sample_id, cellular_prevalence, outlier_prob, chrom`）（程式實作：`phyclone/data/validator/*.json`、`data/pyclone.py`）。不在所有 sample 都出現的 SNV 會被移除（程式實作）。

## 對本 repo 的用途

全部為「推論」。

1. **最直接的切入點是 genotype prior π**：目前 π 對 (before/after CN, multiplicity) 均勻。longphase 的 HP 可以把它從均勻改成資料驅動：
   - SNV 所在 phase set 的 HP1/HP2 與 haplotype-specific CN（Wakhan 這類工具）對上後，可知 SNV 在 major 還是 minor haplotype，multiplicity 上限由該 haplotype 的 CN 決定，而不是一律 1..c_major。
   - 若 alt reads 全落在某一 HP，且該 HP 的 CN=2，可用 alt reads 內「同一 haplotype 拷貝數」比例區分 multiplicity 1 或 2。
   - 這只改 `get_major_cn_prior` 的輸出（cn、mu、log_pi），**DP、SMC、PG 都不必動**，是最小可行改動。
2. **read 共現作為額外 likelihood 項**：pair likelihood（參考 M02 TreeClone 的 4 類 haplotype count）對兩個 SNV 的 ancestor／descendant／sibling 關係給分，可乘在 p(X|T) 上。難點：DP 是「每 node 一個 ρ̄ 網格」，pair 項依賴兩個 node 的 ρ̄ 與祖先關係，若要精確整合需擴充 DP；較省事的做法是只依 topology（祖先關係）打分，不積分 ρ̄。
3. **outlier 先驗**：目前用「染色體聚集度」猜 loss；有 HP 資訊後可改用「SNV 所在 HP 在某些 sample 的 CN 降為 0」直接給 high outlier prior（LOH 造成的 loss）。
4. **single-sample 弱點**：本 repo 的 subsample 是同一 DNA 的稀釋，不是獨立 region，prevalence 順序不會在不同 sample 間反轉，多 sample 帶來的 identifiability 很有限。read 共現正好補這個缺口（TreeClone 的 Simulation 2 示範了單 sample 下 phasing 能分辨 branching）。
5. **最小實驗**：取 HCC1395（有 golden tree 文獻）單一 purity，跑 (a) 原版 PhyClone、(b) 只改 genotype prior 為 HP-informed 的版本；比較 multiplicity 後驗、MAP topology 與 AD F-score（相對參考樹）。不動推論核心，只換輸入的 cn/mu/log_pi。

## 核心判斷

- PhyClone 的方法核心（FS-CRP＋DP 邊際化＋PG-SMC）在 preprint 與正式版間沒變；正式版主要多了 Orchard／fastBE、預設 outlier、posterior 指標與完整 supplement。
- CN／multiplicity 處理是 PyClone 式的「clonal CN＋均勻 genotype 混合」，沒有 subclonal CN、沒有 haplotype、沒有 timing 輸出，這正是 longphase HP 可以插入的地方。
- benchmark 的優勢集中在 multi-sample 模擬；single-sample、高 CN 複雜度、低 purity 的證據都薄，而這正是本 repo 的資料條件。
- 最低成本的改進是改 genotype prior；read 共現項要整合進 DP 則需要新的推導。
