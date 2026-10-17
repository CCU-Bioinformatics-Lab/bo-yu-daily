# M02 TreeClone（Zhou, Sengupta, Müller, Ji；Ann. Appl. Stat. 2019）

閱讀日：2026-10-17。標記：「論文描述」＝arXiv v2 正文明寫；「推論」＝我的分析。本篇沒有可讀的程式碼。

## 書目、版本與檔案

- Zhou T, Sengupta S, Müller P, Ji Y. **TreeClone: Reconstruction of tumor subclone phylogeny based on mutation pairs using next generation sequencing data.** *Annals of Applied Statistics* 13(2):874–899, 2019-06。DOI [10.1214/18-AOAS1224](https://doi.org/10.1214/18-AOAS1224)（Crossref 核對卷期頁碼）。
- arXiv [1703.03853](https://arxiv.org/abs/1703.03853)：v1 2017-03-10，**v2 2017-10-25**。

| 本地檔 | 版本 | 頁數 | 來源 |
|---|---|---|---|
| `paper.pdf` | **arXiv v2 preprint（非期刊排版版）** | 30 | `https://arxiv.org/pdf/1703.03853`（v2，LaTeX，2017-10-26 產生） |
| `paper.txt` | `pdftotext -layout` | — | — |

**版本說明**：Project Euclid 的期刊 PDF（Unpaywall 標為 bronze OA）被 Incapsula 擋下，無法以 curl 取得，所以**只讀了 arXiv v2**。Crossref 上的期刊摘要與 v2 摘要逐字相同（只差一個逗號），但 v2 早於期刊出版約 1.5 年，正文可能有審稿後修改；期刊頁碼 874–899（26 頁）與 v2（30 頁）不同。下文 `[p.N]` 一律指本地 arXiv PDF 實體頁。期刊版可能另有 supplement，我沒有看到。

## 問題與模型

**資料單位**：mutation pair＝兩個相近、可被同一 paired-end short read 同時覆蓋的 SNV [p.3]。用 LocHap 找出（實際資料只取兩個 SNV 的 local haplotype variant）[p.21–22]。

**觀測**（論文描述）[p.8]：每個 sample t、pair k 的每條 read 記成 8 類之一
```
s ∈ {00, 01, 10, 11,  -0, -1,  0-, 1-}
      complete (4)    左缺    右缺     # "-" = 該 read 沒蓋到該位點（partially missing read）
(n_tk1..n_tk8) | N_tk ~ Multinomial(N_tk; p_tk1..p_tk8)
p_tkg = v_tk1·p̃_tkg (g=1..4);  v_tk2·p̃_tkg (g=5,6);  v_tk3·p̃_tkg (g=7,8)
```
v（complete／左缺／右缺的比例）視為非資訊性缺失，**不推論**，在 likelihood 中當常數 [p.8]。

**Subclone genotype**（論文描述）[p.6–7]：z_kc 是 2×2 矩陣（2 個 allele × 2 個位點，元素 0/1）。因 pair 之間沒有 phase，鏡像欄位不可區分，16 種降為 **Q=10** 種：(00,00)、(00,01)、(00,10)、(00,11)、(01,01)、(01,10)、(10,10)、(01,11)、(10,11)、(11,11)。normal clone z_k1=(00,00)。

**Likelihood**（論文描述）[p.9, Eq. 2–3]：
```
A(s, z_kc) = 0.5 · Σ_{j=1,2} I(s_1 = z_kcj1) · I(s_2 = z_kcj2)      # I(- = ·) ≡ 1
p̃_tkg     = Σ_{c=1..C} w_tc · A(s^(g), z_kc) + w_t0 · ρ_g
```
- 生成過程：選 clone（機率 w_tc）→ 選兩個 allele 之一（各 0.5）→ 讀出該 allele 在兩位點的狀態 [p.8]。**每個 clone 恰好 2 個 allele 等機率被抽到，這就是 CN=2 寫死在 likelihood 裡的地方**（推論，由「0.5×兩 allele」直接推得）。
- w_t0ρ_g 是「background subclone」，吸收定序／比對錯誤與太小的 clone；ρ 不依 k 變動，(ρ1..ρ4)、(ρ5,ρ6)、(ρ7,ρ8) 各自加總為 1 [p.9]。
- 只有 marginal SNV 時可當成右缺 read，多項式退化成二項式 [p.9]。

**Tree prior**（論文描述）[p.9–11]：
```
C            ~ Geometric(α)                         # p(C) = (1-α)^(C-1) α
p(T | C)     ∝ Π_c (1 + η_c)^(-β)                    # η_c = 節點深度（Chipman 1998 CART prior）
m_·c | parent ~ Trunc-Pois(λ; [1, |L_Tc|])           # 子 clone 新增突變的 pair 數，至少 1
M_c          ~ Choose(L_Tc, m_·c)                     # 均勻挑哪些 pair 增加突變
(j*, r*)     ~ Unif(Z_kTc)                            # 在父 clone 未突變的 (allele, locus) 中均勻挑一格設為 1
```
約束：子 clone 繼承父 clone 所有突變（**無 loss**）；每代每個 pair 至多新增 1 個突變；已有 4 個突變的 pair 不再變 [p.10]。所有節點（含內部節點）都是存在的細胞族群 [p.5]。
- w 的 prior：w_t1（normal 比例＝1−purity）~ Beta(a_p, b_p)，可放 purity 的資訊性先驗；其餘 w_tc/(1−w_t1) ~ Dirichlet(d0, d, …, d)，d0≪d [p.11]。

**推論**（論文描述）[p.11–13]：
- 固定 (T, C) 時：Z 逐列 Gibbs（只在滿足 T 的 row 中抽），w、ρ 用 MH；以 parallel tempering（C++／OpenMP）處理多峰 [p.11]。
- (T, C) 的跨維度更新：C 限在 [C_min, C_max]（模擬多為 2–5，真實資料到 7），從所有 (T,C) **均勻提議**；借 fractional Bayes factor 想法，把 read count 拆成訓練 b=0.95 與測試 0.05，訓練集 posterior 同時當資訊性 prior 與 x 的 proposal，接受率只在測試集上計算，使不可解的正規化常數相消 [p.12]。
- 點估計：(Ĉ, T̂) 取後驗眾數，再取該條件下的 MAP 樣本 [p.13]。

## CN、multiplicity、purity、haplotype 怎麼處理

- **CN**：只用 copy-neutral（CN=2）區域的 pair，作者明寫「Like most existing methods」[p.3]，真實資料也只取 CN neutral 區 [p.22]（論文描述）。
- **Multiplicity**：沒有獨立參數。z_kc 允許同一位點兩個 allele 都突變（例如 (10,10)），等於允許「homozygous」狀態，但仍假設 CN=2，沒有對應的 LOH 或 CN 事件模型（論文描述＋推論）。嚴格來說這違反 infinite sites（同一位點在兩個 allele 各突變一次），論文沒有討論（推論）。
- **Purity**：w_t1＝normal 比例，被當成參數推論，可用外部 purity 設資訊性 Beta prior [p.11]（論文描述）。
- **Haplotype**：只有**每個 pair 內部**的局部 phasing；pair 之間沒有 phase，因此用 Q=10 的鏡像等價類 [p.7]。沒有 germline het SNP、沒有 phase block（論文描述）。

### 為何限 CN=2（分析）

1. likelihood 的「0.5 × 兩個 allele」假設每個 clone 在該位點恰好兩份拷貝且等量被定序 [p.9]；CN≠2 時抽到各 allele 的機率應正比於各 haplotype 拷貝數，且不同 clone 的 CN 可不同，使 w_tc 必須乘上 clone 的總拷貝數再正規化（類似 PyClone 的 Z 分母）（推論）。
2. genotype 空間 z_kc 是固定 2×2；CN≠2 時每個 clone 每個 pair 的 haplotype 數可變，Q 會隨 CN 爆增，tree prior 的「每代新增一格」也要加入 duplication／loss 事件（推論）。
3. 作者處理的是 WES short read，CN-neutral 的 pair 已經不多（69 對），沒有動機擴充（推論）。

### 能否推廣到 long reads 與 CN≠2（分析，全部推論）

- **Long reads**：多項式觀測模型不依賴 read 長度，可直接用；long read 讓 pair 數量大增、距離從數百 bp 擴到數十 kb，complete read 比例變高（v_tk1 上升）。但 pair 不再是「相鄰兩點」，而是一個 read 上可能有 3 個以上 SNV；論文說能擴到更多 SNV [p.24–25]，代價是類別數 2^m 爆增。實務上可先限制成 pair，或以 phase set 為單位。
- **pair 不獨立**：long read 下同一 SNV 會出現在很多 pair 中，TreeClone 把各 pair 的 likelihood 相乘，等於重複計算同一 SNV 的邊際 read（推論）。需要改成 SNV 邊際項＋pair 條件項，或用 composite likelihood 加權。
- **germline phase**：longphase 給每條 read HP1/HP2。只要 SNV 所在 read 帶 HP tag，pair 間的鏡像歧義就消失（每個 SNV 都知道在哪個 haplotype），Q=10 會回到 16 種且可跨 pair 對齊；甚至可以不需要兩個 SNV 在同一 read，而是「同一 HP」就足以給出 allele 指派。
- **CN≠2**：把 A(s,z) 改成 haplotype-specific CN 加權：`A(s, z_kc) = Σ_h (cn_{c,h}/Σ_h' cn_{c,h'}) · P(s | haplotype h 在 clone c 的狀態)`，並讓 p̃ 的分母像 PyClone 一樣乘上各 clone 總 CN。若 haplotype-specific CN 由外部工具（Wakhan）給定且是 clonal，這是可行的直接推廣；subclonal CN 則需把 CN 事件放進 tree prior。
- **Purity**：維持 w_t1 參數即可，也可以像 PhyClone 一樣外給。

## 實驗與可支持的結論

| 實驗 | 設定（論文描述） | 結果（論文描述） |
|---|---|---|
| Sim 1(a) | K=100 pairs、T=5 samples、C∈{3,4,5}、depth∈{50,200,1000}，資料由 prior 生成 | C_err＝T_err＝0 全部；Z_err ≤0.07 [p.14 Table 1]；PSRF 多在 1.04–1.38，C=5、depth 1000 時 3.72 [p.15 Table 2] |
| Sim 1(b) | T∈{1,3,5} | 單 sample 也能估對 C 與 T，Z_err 0.13–0.29 [p.15 Table 3] |
| Sim 1(c) | 左右缺失率 0–0.5 | 0.5（完全沒有 complete read）時 Z_err 升到 0.12，其餘 0 [p.16 Table 4] |
| 只用 marginal SNV | 全部當右缺 read | C、T 仍正確，Z 只能恢復到單一位點 [p.16] |
| Sim 2 | 單 sample、C=4、有 branching，depth 500 | TreeClone 後驗眾數（0.26）恢復真樹；Cloe、PhyloWGS 把 CCF 相近的 M2、M3 併成一群而得線性樹；PairClone 無樹 [p.17–19]；加 400 個 marginal SNV 也無助 Cloe／PhyloWGS 分辨 branching [p.19] |
| Sim 3 | 模仿肺癌資料：T=4、K=69、C=6 | 後驗眾數（0.38）恢復真樹；小 clone 的 genotype 誤差較大 [p.20–21] |
| 肺腺癌 WES | 4 個鄰近 region、100 bp PE、69 pairs、平均深度 156 | 推得 C=6，眾數樹後驗 0.27；Bayesian χ² 無 lack of fit；Cloe 推線性樹、PhyloWGS 推不同分支 [p.22–24] |

可支持的範圍（推論）：
- 「phasing 可分辨 marginal VAF 無法分辨的 branching」有 Sim 2 的清楚示範，但只有**一組**模擬，而且資料由 TreeClone 自己的 prior 生成，對它有利。
- 模擬的 C_err、T_err 全為 0，但 C_max 只到 5–7、K≤100；沒有評估更大的樹或更多 pair，也沒有運算時間。
- 真實資料沒有 ground truth；樹後驗眾數只有 0.27，不確定性高。
- 比較對象只有 Cloe、PhyloWGS、PairClone，且各跑一次，沒有重複或統計檢定。

## 程式碼與可取得性

- 論文寫 `http://www.compgenome.org/treeclone`（實作為 C++／OpenMP）[p.1, p.11]。2026-10-17 查詢：該網址 301 轉到 `https://ccte.uchicago.edu/treeclone`，HTTPS 連線逾時，**無法取得程式**。
- GitHub 搜尋 `treeclone` 沒有找到作者的 repo（同名 repo 都與本論文無關）。授權、最後更新皆不明。
- 輸入：LocHap 輸出的 mutation-pair read count（8 類計數、每 sample）[p.5, p.21]。

## 對本 repo 的用途

全部為「推論」。

1. **可直接借用的式子**：8 類 read 的多項式模型＋partially missing read 的處理（v 視為常數）。long read 上兩個 SNV 的 read 天然分成「兩點都蓋到」與「只蓋一點」，可原封不動套用。
2. **與 PhyClone 的關鍵差異**：
   - TreeClone 是 feature allocation（每個 clone 對每個 pair 有 genotype），PhyClone 是 tree-structured clustering（SNV 分到 node）。把 pair likelihood 接到 PhyClone 時，可以從 PhyClone 的樹與 SNV 指派**導出** z_kc：SNV a 在 node u、SNV b 在 node v，clone c 是否帶 a、b 取決於 c 是否為 u、v 的後代；再加上 a、b 各在哪個 haplotype（來自 longphase HP），就能決定 z_kc，不必像 TreeClone 一樣把 Z 當參數抽。
   - TreeClone 用均勻 (T,C) 提議＋資料分割的跨維度 MCMC；PhyClone 的 PG-SMC 在這點上明顯更可擴展。
3. **與 longphase HP/PS 的接點**：HP tag 解掉鏡像歧義（Q=10→16，且可跨 pair 對齊），PS 決定哪些 SNV 可放在同一個 haplotype 座標系；不同 PS 之間仍有歧義，處理方式可沿用 TreeClone 的鏡像等價類。
4. **CN≠2 推廣**：把 A(s,z) 依 haplotype-specific CN 加權（見上節），這也是 PhyClone 的 genotype prior 與 TreeClone pair likelihood 能共用同一套 haplotype CN 輸入的地方。
5. **最小實驗**：在 HCC1395 或 H2009 的 CN=2 區域（避開 CN 問題），用 longphase haplotag 後的 CRAM 抽出同 read 上的 SNV pair 與 8 類計數；先只算「給定 PhyClone MAP 樹時的 pair log-likelihood」，比較 PhyClone 後驗中的不同 topology 是否被 pair 資料明顯區分。這不需改推論，只是事後打分，可快速判斷 pair 訊號強度。

## 核心判斷

- TreeClone 是目前唯一正式發表、以 read-level SNV pair 的 haplotype 計數為 likelihood 主體推 clone tree 的方法；「read 共現進推樹」本身不是新點子。
- 它的 CN=2 限制寫死在「0.5×兩 allele」的 likelihood 與 2×2 genotype 空間，沒有 multiplicity、沒有 CN timing、沒有 germline phase。
- long read＋longphase HP 可以同時解掉它的兩個瓶頸：pair 數太少與 pair 間無 phase；但需處理 pair 間共享 SNV 造成的重複計數。
- 只讀了 arXiv v2，期刊版的正文修改與可能的 supplement 未核對；程式目前取不到。
