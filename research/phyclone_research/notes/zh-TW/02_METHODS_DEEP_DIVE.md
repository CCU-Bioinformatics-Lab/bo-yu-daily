# PhyClone 方法深入解析

## 1. 輸入與推論目標

[明示 STATED] 對於一個或多個彼此相關的腫瘤樣本，每個體細胞 SNV 都會提供參考／替代等位基因的讀序計數、等位基因特異性拷貝數，以及腫瘤含量估計值。推論目標是取得克隆／節點數量、突變至節點的指派，以及克隆祖先關係的後驗分布；進行樹狀結構推論時，會將各樣本的盛行率積分消去。（正文 §2 與 Fig.1，p.2；§2.2，p.3。）

[實作 IMPLEMENTED] 目前主要輸入 schema 要求 `mutation_id`、`sample_id`、`ref_counts`、`alt_counts`、`major_cn`、`minor_cn`、`normal_cn`；`tumour_content`、`error_rate`、`chrom` 則為選填（`data/validator/PhyClone_schema.json`）。缺少腫瘤含量時設為 1.0，缺少錯誤率時設為 0.001；major CN 為 0 的資料列，以及未出現在所有保留樣本中的突變，皆會被移除（`data/pyclone.py:197-280`）。純度與 CN 是固定輸入，不會由模型推論。

可選的叢集檔案要求 `mutation_id`、`cluster_id`，並可包含 `sample_id`、`cellular_prevalence`、`outlier_prob`、`chrom`。[實作 IMPLEMENTED] 每個提供的叢集會成為一個不可分割的 `DataPoint`：叢集本身不能拆分，但數個 `DataPoint` 可以合併至同一節點，且整個預先分群的叢集只能整體視為離群值或整體不視為離群值（`data/pyclone.py:82-115,184-194`）。

## 2. 變數及其意義

| 符號 | 定義 | 生物學意義 | 推論角色 |
|---|---|---|---|
| `N`, `S` | 突變、樣本 | 觀察到的基因座與相關檢體 | 資料集維度 |
| `x`, `d` | 替代等位基因讀序數與總讀序數 | 某基因座上的定序支持度 | 等位基因計數概似 |
| `G=(G_N,G_R,G_V)` | 正常、癌細胞參考型、癌細胞變異型的基因型 | 三種細胞群中的拷貝／突變等位基因狀態 | 預期 VAF 與基因型混合 |
| `t` | 腫瘤含量（tumour content；即腫瘤純度） | 定序細胞中惡性細胞所占比例 | 發射分布中的混合權重 |
| `rho_v` | 節點 `v` 的克隆盛行率 | 僅屬於該克隆、不含其後代克隆的惡性細胞比例 | Dirichlet 潛在質量 |
| `rho_bar_v` | 節點 `v` 的細胞盛行率／CCF | 攜帶起源於 `v` 之突變的惡性細胞比例 | PyClone 發射分布 的引數 |
| `b` | 突變的分割 | 具有共同演化起源／歷程的突變 | 未知的分群 |
| `alpha` | CRP 集中度參數 | 無直接生物學意義 | 控制叢集數量的先驗 |
| `F`, `T=(V,E)` | 有根森林與含虛擬根節點的有根樹 | 克隆祖先關係 | 拓樸狀態 |
| `C_v`, `V_v` | `v` 的子節點、其子樹中的節點 | 攜帶祖先突變的後代 | 盛行率加總限制 |
| `kappa` | 對稱 Dirichlet 集中度參數 | 無直接生物學意義 | 盛行率先驗；程式碼實作 `kappa=1` |
| `o_n`, `nu_n` | 離群值指標與先驗 | 可能已流失或與錯誤模型不相容的突變 | 穩健混合模型狀態 |
| `sigma` | 資料點的排序 | 無 | SMC/PG 輔助變數 |
| `L` | 盛行率網格解析度參數 | 無 | 數值積分的成本／精確度 |

## 3. 等位基因計數發射分布

### 方程式

對基因型 `G`，定義總拷貝數 `c(G)=a(G)+b(G)`，以及受定序錯誤上下限限制的變異比例：

```text
mu(G) = min(max(b(G)/c(G), epsilon), 1-epsilon).
```

預期的變異讀序機率為：

```text
xi(G,rho_bar,t) = [(1-t)c(G_N)mu(G_N)
                 + t(1-rho_bar)c(G_R)mu(G_R)
                 + t rho_bar c(G_V)mu(G_V)] / Z,

Z = (1-t)c(G_N) + t(1-rho_bar)c(G_R) + t rho_bar c(G_V).
```

觀察到的替代等位基因計數服從 Binomial 或 Beta-Binomial：

```text
p(x|d,G,rho_bar,t) = Binomial(x|d,xi)
```

或 `BetaBinomial(x|d, mean=xi, precision=gamma)`。若基因型具有不確定性，則：

```text
f(x|rho_bar) = sum_i pi_i p(x|d,G_i,rho_bar,t).
```

[明示 STATED] 這些方程式見 Supplement S1.1，pp.1–2。[實作 IMPLEMENTED] 細胞群質量 `(1-t, t(1-f), tf)`、經 CN 加權的 VAF、基因型 `logsumexp`，以及 Beta-Binomial 的 `a=xi*precision`、`b=precision-a`，分別對應至 `utils/math_utils.py:179-244` 與 `data/pyclone.py:299-403`。

### 基因型先驗

[明示 STATED] major-copy-number 先驗會列舉突變發生於 CNA 之前時的 multiplicity `1..major_cn`；當腫瘤總 CN 與正常 CN 不同時，另加入突變發生於 CNA 之後的狀態。所有候選狀態具有相同權重。若無法取得等位基因特異性 CN，可將總 CN 當作 major CN，並將 minor CN 設為 0。（Supplement S1.2，p.2。）[實作 IMPLEMENTED] `get_major_cn_prior`（`data/pyclone.py:324-352`）與此建構方式一致。

[推論 INFERRED] 這會在固定 CN 的條件下，將突變發生時機／multiplicity 的不確定性積分消去；它不會建立亞克隆 CN 模型，也不會推論 CN 的不確定性。

## 4. FS-CRP 先驗與樹狀結構表示法

[明示 STATED] 首先抽樣突變分割：

```text
b | alpha ~ CRP(alpha),
p(b|alpha) proportional to alpha^|b| product_{B in b} (|B|-1)!.
```

在給定 `|b|` 的條件下，均勻抽取一個有根森林，並將森林中的所有根連接至空的虛擬根節點 `r`。對未調整的森林而言：

```text
p(F|b) = 1/(|b|+1)^(|b|-1).
```

（Supplement S1.3，pp.2–3。）[實作 IMPLEMENTED] CRP 與 Cayley 項出現在 `tree/distributions.py:43-65`；`Tree` 會明確儲存虛擬根節點與具有生物學意義的整數節點（`tree/tree.py:19-43`）。

### 最終狀態的單一根偏好

[明示 STATED] 最終狀態評分會懲罰虛擬根節點下具有多個子節點的情形；使用 `C=1000` 時，一個次根節點相較於兩個次根節點具有 1000 倍偏好，後續每增加一個根亦同時受到相同比例的懲罰，並包含拓樸 multiplicity 正規化。（Supplement S1.3.1，pp.3–4。）[實作 IMPLEMENTED] `tree/distributions.py:12-14,67-121` 與 `tree/base.py:93-100` 實作了根節點及子節點順序的 multiplicity 項。

因此，精確的說法是：**在節點數固定的條件下，初始森林先驗為均勻分布**，但最終評分包含強烈偏好單一根的結構正則化項。

### 已解決的符號衝突

當 `V` 包含虛擬根節點時，正文 §2.2（p.3）支持 `|V|=|b|+1`。Supplement S1.3（p.3）則在加入虛擬根節點後寫成 `|b|=|V|`。[實作 IMPLEMENTED] 虛擬根節點具有一個盛行率網格分量，而完整評分會將其質量／CCF 固定為 1。因此，補充資料中的等式應視為差一的符號錯誤。

## 5. 克隆盛行率與細胞盛行率

對節點 `v` 而言：

```text
rho_bar_v = sum_{v' in V_v} rho_v'
          = rho_v + sum_{v' in C_v} rho_bar_v'.
```

[明示 STATED] 在 ISA 假設下，起源於 `v` 的突變會由所有後代繼承，因此其細胞盛行率等於整個子樹的質量；`rho_v` 則是該克隆專有的質量。（正文 §2.2，p.3；Supplement S1.3，p.3。）概似為：

```text
p(X|rho,b,T) = product_n f(x_n | rho_bar_{v_n}).
```

[實作 IMPLEMENTED] 節點的發射分布網格會對指派至該節點的資料點加總，子節點會進行卷積，而輸出的克隆質量等於父節點 CCF 減去所有子節點 CCF 的總和（`tree/tree_node.py:35-69`；`tree/utils.py:7-68`；`process_trace/map.py:24-40,127-157`）。多樣本網格共享 `b,T`，但每個樣本維度會獨立處理。

## 6. 邊際化概似與動態規劃

### 方程式與目的

```text
p(X,b,T) = p(b|alpha)p(T|b)
           integral_Delta p(rho|kappa)
             product_n f(x_n|rho_bar_{v_n}) d rho.
```

`Delta` 是質量總和為一的非負單純形（simplex）。[明示 STATED] 將 `rho` 積分消去，可在探索樹狀結構的後驗分布時移除連續盛行率變數。（正文 §2.2.1，p.3；Supplement S1.4，p.4。）剩餘的離散樹／分割狀態，其維度不會隨樣本數增加，但評估成本會增加。

### 網格遞迴

在 `Phi={0,1/L,...,1}` 上近似每個 CCF。對以 `v` 為根的子樹，令 `ell_v(rho_bar)` 為局部發射分布 的乘積。子節點的遞迴結果會卷積至 `D_v`；`v` 上的剩餘質量則積分至 `S_v`；接著：

```text
R_v(rho_bar) = ell_v(rho_bar) S_v(rho_bar),
tree likelihood = R_r(1).
```

對實作中的 `kappa=1`，`S_v` 是累積總和。請參閱 Supplement S1.4–S1.5，pp.4–5，以及 Algorithm 1，p.13。[實作 IMPLEMENTED] `tree/tree_node.py:43-69`、`tree/utils.py:7-68`、`tree/distributions.py:151-163` 是直接對應的網格實作。

### 複雜度說法的調和

正文 §2.2.1 以 `O(|V|^2)` 作為簡略說法。Supplement S1.5 則給出含參數的上界：

```text
O(V (N L + C S L^2)),
```

其中 `V` 為節點數、`N` 為突變／資料貢獻數、`C` 為最大出度、`S` 為樣本數、`L` 為網格參數。程式碼包含逐樣本的網格卷積，並在大型網格時由直接卷積切換為 FFT（`tree/utils.py:28-68`）。應採用補充資料的上界；不得宣稱執行時間與樣本數無關。

## 7. 推論

### 由下而上的 SMC

[明示 STATED] 在排序 `sigma` 下，SMC 每次加入一個資料點，目標分布為 `gamma_t=p(X_t,b_t,T_t)`。一個資料點可以加入既有的森林根節點，或形成新的根節點，位於森林根節點的一個子集之上；該子集可以為空集合。（Supplement S1.6–S1.6.2，p.6。）

提議分布的選項包括：

- bootstrap：成本低廉、近似先驗的隨機提議；
- fully adapted：列舉並評分所有狀態，包括 `2^R` 個子節點子集；
- semi-adapted：對加入既有根節點的指派進行評分，但僅抽樣一個新根節點的子集。

[明示 STATED]/[實作 IMPLEMENTED] 半調適式（semi-adapted）是實務上的折衷方案，也是論文基準測試與目前 CLI 所選用的方式（`smc/kernels/semi_adapted.py:31-130`）。當相對 ESS 低於目前預設門檻 0.5 時，會觸發多項分布重抽樣（multinomial resampling；`smc/swarm/swarm.py:21-61`；`smc/samplers/standard.py:22-44`）。

### Particle Gibbs 與突變排序

固定的由下而上排序，會使部分祖先狀態無法抵達。[明示 STATED] PG 會在針對 `p(T|X,sigma)` 執行 conditional SMC，以及重新抽樣有效的 `sigma|T` 之間交替；後代突變排在父節點突變之前，同層節點的序列以 bridge-shuffle 方式交錯，而離群值則在根節點處穿插。（正文 §2.3.1，p.4；Supplement S1.6.3，p.7；Figs.S5–S8。）[實作 IMPLEMENTED] 此機制實作於 `smc/utils.py:19-135`、`mcmc/particle_gibbs.py:8-49` 與 `smc/samplers/conditional.py`。

### 額外的移動步驟

- 僅當來源節點不會因此變空時，資料點重新指派才會抽樣另一個既有節點／離群值；拓樸與節點數維持不變（`mcmc/gibbs_mh.py:7-66`）。
- Prune-regraft 會切下某個子樹，並重新抽樣其連接位置；叢集數／節點數維持不變（`mcmc/gibbs_mh.py:69-129`）。
- 整棵樹／子樹 PG 可改變節點數。模型沒有另外命名的 reversible-jump split/merge 移動。
- 子樹 PG 的設計目標是透過更新較短路徑來降低 PG 的路徑退化問題（Supplement S1.6.4，p.7），但其實作在 0.7.0 與 0.8.0 中都保留一項 TODO，指出可能缺少子樹選擇項（`mcmc/particle_gibbs.py:52-110`）。此功能預設關閉。其形式正確性為 UNRESOLVED（未釐清）。

### 暖機期（burn-in）

[實作 IMPLEMENTED] 暖機期（burn-in） 採用啟發式的 無條件 SMC，捨棄所有 burn-in 狀態，並以期間所見 `log_p_one` 最高的狀態（而非最後一個狀態）初始化主要鏈（`run.py:316-369`）。它不以後驗分布為目標，屬於初始化程序，而非後驗證據。

## 8. 離群值／流失模型

### 論文發表的模型

```text
p(X,b,T,o) = product_n [nu_n integral_0^1 f(x_n|rho)d rho]^{I(o_n=1)}
             × p(b|alpha)p(T|b)
             × integral p(rho|kappa)
                 product_n [(1-nu_n)f(x_n|rho_bar_vn)]^{I(o_n=0)} d rho.
```

[明示 STATED] 離群值會排除在受繼承限制的樹之外，其 PyClone 概似則在一個獨立且服從 Uniform(0,1) 的 CCF 上積分。提議／排序／子樹更新均納入離群值。（正文 §2.2.3，p.3；Supplement S1.7，pp.7–8。）這可容納與模型不相容的情形，但不會定位發生流失的邊。

### 資料導向先驗

[明示 STATED] 補充資料以最大 CCF 選出主幹叢集，針對每個非主幹叢集產生 10,000 次染色體背景抽樣，並以 `p<0.01` 為判定門檻，將離群先驗設為低值 0.0001 或高值 0.4（S1.7.1，p.8）。[實作 IMPLEMENTED] 目前程式碼還會略過小於四個突變的叢集，並要求預期／觀察到的獨特染色體數量比值 `>1`；雖然補充資料文字列出基因組位置，實作並未使用（`data/cluster_outlier_probabilities.py:24-67,90-151`）。若缺少必要的中繼資料，則退回使用全域先驗。

### 尚未解決的論文／程式碼不一致

論文發表的離群值項只有一重均勻積分。0.7.0 與 0.8.0 的程式碼卻計算：

```text
L^-2 sum_j sum_{i<=j} f_i
```

而不是直接的矩形近似 `L^-1 sum_i f_i`（`data/base.py:29-34`）。對常數概似而言，每個樣本的程式碼結果是 `(L+1)/(2L)`，而非 1。每個離群值都會重複乘上此因子，可能改變離群值的後驗勝算。目前沒有任何文件化推導或專門測試可以解決此問題：**CONFLICT（衝突）、UNRESOLVED（未釐清）；很可能是實作不一致。**

## 9. 輸出

[實作 IMPLEMENTED] 抽樣程序會寫入 HDF5 trace，其中包含輸入概似網格、鏈／迭代／計時／alpha／節點／離群值／根節點統計，以及去除重複的樹狀態（`utils/save_hdf5.py`）。後處理提供：

- MAP：預設選取 `log_p_one` 最高的狀態；儘管 UI 文字稱為「joint-likelihood」，此分數包含 CRP／樹／離群值先驗，以及邊際化後的概似（`process_trace/process_trace.py:27-58`）。
- Consensus：相容的高權重演化支（clades）；目前預設實際上使用拓樸出現次數乘上指數化的最佳拓樸分數，而不是直接加總每次抽樣的權重（`process_trace/consensus.py:81-111`）。
- Topology report：排序後的不重複拓樸狀態、出現次數，以及可選的 Newick／結果壓縮檔。
- Prevalence TSV：以條件式網格的 max-product／回溯求得 CCF／克隆盛行率，而非後驗平均值或區間（`process_trace/map.py`）。

正文 §2（p.2）提到可透過 MAP **或抽樣（sampling）** 還原盛行率；目前簽出版本僅提供類似 MAP 的回溯，並無後驗盛行率抽樣器。就抽樣而言，此項屬於 `PAPER_ONLY`（僅見於論文）。

## 10. 不得混為一談的參數組合

### 論文發表的 v0.7.0 基準測試設定

[明示 STATED] 四條鏈、暖機期（burn-in）100、5,000 次迭代、100 個粒子、Beta-Binomial、半調適式提議分布（semi-adapted proposal）；啟用離群值的執行使用 `--assign-loss-prob`，低／高先驗為 0.0001/0.4；選出的樹為聯合分數的 MAP。（正文 §2.4.2，p.5。）

### 目前 v0.8.0 CLI 預設值

[實作 IMPLEMENTED] 暖機期（burn-in） 1,000；迭代 10,000 次；一條鏈；網格 101 點；粒子 100；精度 400；Beta-Binomial；semi-adapted；全域離群值機率 0；alpha 起始值為 1，並以 Gamma(0.01,0.01) 超先驗機制更新；一輪重新指派與一輪 prune-regraft；子樹機率 0；重抽樣門檻 0.5（`cli.py:243-447`、`run.py:382-392`）。README 建議至少使用四條鏈。

### 目前直接呼叫 Python API 的預設值

[實作 IMPLEMENTED] `run()` 的預設值則為 burn-in 100、迭代 5,000 次、精度 1.0（`run.py:31-57`）。當要求使用 缺失先驗旗標 時，CLI callback 還會啟用 `1e-4` 的全域離群值機率；直接呼叫 `run(assign_loss_prob=True,outlier_prob=0)` 可能讓離群值模型維持未啟用狀態。報告預設值時，必須依進入點分別陳述。

## 11. 方法層級衝突登錄表

| 衝突 | 來源 | 狀態 |
|---|---|---|
| 虛擬根節點維度 | 正文 `|b|+1=|V|`；補充資料 `|b|=|V|`；程式碼包含根節點 | RESOLVED（已解決）：補充資料符號誤植 |
| 複雜度 | 正文 `O(|V|^2)`；補充資料／程式碼包含 `N,S,L,C` | RESOLVED（已解決）：採用補充資料的詳細上界 |
| 離群值均勻積分 | 論文為一重積分；0.7.0/0.8.0 為三角形雙重加總 | UNRESOLVED（未釐清）；可能不一致 |
| Bootstrap＋離群值提議 | 0.8.0 抽樣機率為 0.1/0.35/0.55，記錄的機率則為 0.1/0.45/0.45 | 已判定為目前版本的迴歸問題；尚未修正，但不在 benchmark 路徑上 |
| 子樹 PG 轉移 | 補充資料宣稱有完整分數校正；原始碼則質疑 selection term | UNRESOLVED（未釐清）；預設停用 |
| CLI/API 預設值 | 參數預設值有實質差異 | RESOLVED（已解決）：依介面分別報告 |
