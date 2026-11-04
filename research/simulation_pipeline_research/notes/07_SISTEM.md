# 07 SISTEM 的模擬資料生成程式

調查日期：2026-10-24。對象：`samsonweiner/sistem`（Weiner & Bansal, *Bioinformatics* 2025, doi:10.1093/bioinformatics/btaf634, PMC12701798）。
試跑紀錄：`lab_report/2026-10-24_clonesim_sistem_trial/sistem/README.md`（2026-11-04 刪除，已排除的路線；未進 git，無法取回）。
程式碼行號以 git `627f888` 為準，路徑都相對於 `sistem/`。

## 1. 結論

- **真值可以當 PhyClone 的 bulk baseline，但計數要重抽，也要自己寫轉換程式。** SISTEM 會寫出 clone tree、每個 SNV 的起源 node 與 allele，以及 allele-specific CN 和每個 site 的 ref／alt 計數。這幾項都已實測。它的 ref／alt 計數模型有問題（見下一點與 §10），不要直接拿來測 PhyClone。
- **allele 0／1 可以當 HP1／HP2 的真值。** 同一條染色體的所有拷貝都保留起始 homolog 的 allele 標籤。這個標籤在全基因組都一致，也沒有 phasing 誤差。〔程式〕
- **CN 綁在 clone 上，timing 也由事件順序決定。** SNV 若發生在 amplification 之前，會被一起複製（multiplicity > 1）。SNV 所在 region 若後來被刪除，SNV 就會消失（mutation loss）。〔程式＋實測〕
- **bulk 計數模型有三個問題。** 第一，alt 數是 `round(depth × fraction)`，沒有 binomial 抽樣。第二，`fraction` 沒有用 CN 加權。第三，depth 用各 clone CN 的「不加權」平均。所以觀察 VAF 和真正的混合 VAF 不同。〔程式＋實測：alt 和公式 438／438 相符；誤差最大 0.12〕
- **沒有 seed 參數。** 在外部先設 `np.random.seed()`，結果就逐 byte 可重現。〔實測〕
- **缺口**：沒有 read 共現、phasing 誤差、germline het SNP 與 PS block。clone 比例與 purity 真值都沒有寫成檔案，要從 pickle 的樹去算。〔程式〕

## 2. 版本與授權

| 項目 | 內容 | 證據 |
|---|---|---|
| 版本 | 1.0.5。PyPI 套件與 git `627f888`（2026-05-30）的 `sistem/` 逐檔相同 | 〔實測：`diff -r`〕 |
| 授權 | GPL-3.0-only。可以呼叫；把它的程式碼複製進我們的 repo，會受 GPL 約束 | 〔程式：`LICENSE`、`setup.cfg`〕 |
| 依賴 | numpy、scipy、scikit-learn、biopython、pyfaidx。single-cell reads 另需 `dwgsim` 與 `samtools` | 〔程式：`pyproject.toml`；`data/reads.py` L77、L86〕 |
| 安裝 | 本機沒有 `python3-venv`，所以改用 `pip install --target <dir>/pylib sistem==1.0.5`，再設 `PYTHONPATH` | 〔實測〕 |
| 論文的 benchmark | 只評估 DICE-bar（single-cell CNA 建樹），沒有評估 bulk SNV 建樹 | 〔論文〕 |

## 3. 流程

```
Parameters ─► SelectionLibrary（region／arm／hybrid）─► Anatomy（site 間距離、migration）
                                    │
GrowthSimulator.simulate_agents()   ▼   clone 層級的 agent：每代 birth/death、driver CNA/SNV、migration
                                    │   停止條件：每個 site ≥ min_detectable，或 t > t_max
sample_cells()                      ▼   每個 site 依 clone 大小多項抽樣 ncells_prim／ncells_meta 個 cell
simulate_clonal_lineage()           ▼   ① 回溯祖先，建 clone tree
                                        ② 用 coalescent 解開多分岔；min_mut_fraction 合併或刪除小 clone
                                        ③ 從 root 往下重放 driver 事件，再加 passenger CNA 與 SNV
                                        ④ 在 root 下加一個 'diploid' leaf（ncells_normal 個 cell）
                                        ⑤ 摺疊單鏈 node ─► 寫 clone_tree.nwk、事件、CNP、SNV profile
gen_readcounts_bulk(tree)           ▼   每個 site 一個 bulk sample ─► readcounts.tsv
```

〔程式：`ancestry.py` L237–298、L339–369、L425–484；`lineage/lineage.py` L167–279〕

## 4. 輸入參數

和 [05](05_OTHER_SIMULATORS.md)「輸入與輸出比較」的列對齊。

| | SISTEM | 證據 |
|---|---|---|
| 給參數的方式 | Python API（`Parameters` dataclass），或 `wrapper/sistem_wrapper.py` 加 YAML | 〔程式：`parameters.py` L73–131〕 |
| 樹的大小 | **沒有直接參數。** 由生長、取樣數與 `min_mut_fraction`（預設 0.05）決定。實測 seed 1 有 9 個 tumour node，seed 2 有 15 個 | 〔程式＋實測〕 |
| sample 數 | `nsites`。每個 site 產生一個 bulk sample | 〔程式：`reads.py` L246、L273〕 |
| SNV 數 | **沒有直接參數。** 每條邊的 passenger SNV 數 ~ Binomial(邊長〔代數〕, `SNV_pass_rate`) | 〔程式：`lineage/mutation.py` L57–62；`lineage/reevolve.py` L33–42〕 |
| depth | `coverage`。DP ~ Poisson(coverage × mean(CN_c)/2)，其中 mean 是各 clone 的不加權平均 | 〔程式：`reads.py` L297–301〕 |
| clone 比例 | 不能指定。由 agent 生長後多項取樣的 cell 數決定 | 〔程式：`ancestry.py` L363–368〕 |
| purity | `ncells_normal`。site 0 的 purity = 1 − n_normal／n_total；其他 site 照同一個比例補 normal。**每個 site 的 purity 幾乎一樣** | 〔程式：`reads.py` L260–270；實測：0.832／0.832／0.832〕 |
| CN | driver：`focal_driver_rate`、`arm_rate`、`chromosomal_rate`、`WGD_rate`。passenger：`focal_pass_rate`。其他：`focal_gain_rate`、`chrom_dup_rate`、`length_mean`（單位是 region）、`mag_mean` | 〔程式：`parameters.py` L89–100〕 |
| mutation loss | 沒有參數。deletion 刪到帶 SNV 的 region 時自然發生 | 〔程式：`genome/chromosome.py` L90–96；實測 7／265、16／252 個（SNV, 後代 leaf）組合〕 |
| noise | 沒有。沒有定序誤差、沒有 binomial 抽樣、沒有 outlier | 〔程式：`reads.py` L302；實測：VAF 0 的 156 列 alt 全為 0〕 |
| 種子 | 沒有參數。所有亂數都用 numpy 全域 RNG（包含 scipy `poisson.rvs`／`expon.rvs`） | 〔程式：`grep seed` 只找到 metastasis seeding〕 |

## 5. 輸出檔與欄位

例子取自 seed 1（`lab_report/.../sistem/out_seed1/`）。

| 檔案 | 欄位 | 例子 | 說明 |
|---|---|---|---|
| `clone_tree.nwk` | Newick，node 名稱＋邊長（代數） | `(diploid:2558,(((P9815_13:468,B930_6:468)P9815_8:11,…)P9815_2:2078)P0;` | root `P0` 是正常的起始細胞。**沒有 cell 數** |
| `clone_tree_full.nwk` | 摺疊前的樹 | `((((…(P9815_13:462)P9815_12:6,…` | 單鏈 node 還沒合併 |
| `SNV_events.tsv` | `Cell/Clone, Driver, Chrom, Allele, Region Index, Ref Region Index, Position, BP` | `P9815_2 False chr2 1 46 45 430075 1` | `Position` 是 region 內的 offset。基因組座標 = Ref Region Index × region_len + Position。`Region Index` 是當下染色體序列裡的位置 |
| `CNA_events.tsv` | `Cell/Clone, Type, Driver, Chrom, Allele, Arm, Start Index, Length, Copies, Ref Region Indices` | `P9815_2 focal_deletion False chr2 0 None 44 2 None 46,47` | 事件記在新產生它的 node 上 |
| `observed_CNPs.tsv`／`ancestral_CNPs.tsv` | `Cell/Clone, Chrom, Start, End, Hap CN, Total CN` | `A374_3 chr1 1 5000000 1,1 2` | `Hap CN` = allele 0, allele 1。Start 是 1-based |
| `SNV_profiles.tsv` | `Cell/Clone, Chrom, Pos, GT` | `B930_6 chr1 3057266 C/T` | 每個 allele 一個鹼基。只看有沒有，不看拷貝數 |
| `readcounts.tsv` | `Chrom, Pos, <site…>`，格式 `total,alt` | `chr1 33216222 123,34 180,57 124,34` | Pos 是 0-based offset。site 名稱是 P、A、B… |
| `CN_averages.tsv` | `Chrom, Start, End, Site, CN` | `chr1 5000001 10000000 0 1.928` | 每個 site 依 cell 數加權的 total CN（含 normal） |
| `migration_graph.tsv` | `P-A 2` | | site 間的 migration 次數 |
| `sim.log` | 每代 clone 數、族群大小、平均 fitness | | **不是參數紀錄** |

〔程式：`data/profiles.py` L46–62、L88–113、L162–200、L202–267；`ancestry.py` L472–483〕

## 6. 演化模型

- **agent = clone。** clone 定義為「driver 突變序列相同的一群 cell」。每代每個 clone 依 fitness 抽 birth 數（Binomial(popsize, birth_prob)）。新的 driver 事件會產生新的 clone。〔論文；程式：`lineage/cell.py` L169–178；`ancestry.py` L109–150〕
- **selection**：region 模型給每個 region 一個係數。OG 被放大會提高 fitness，TSG 被放大會降低 fitness。另有 arm 模型與 hybrid 模型（hybrid 才有 driver SNV）。〔論文〕
- **site 與時間**：每代先做 birth/death，再做 migration。migration 機率 = ε × 距離的倒數。時間單位是代。〔論文；程式：`ancestry.py` L158–215〕
- **取樣**：結束時，每個 site 依 clone 大小多項抽 cell。〔程式：`ancestry.py` L363–368〕
- **clone tree 怎麼來**：
  1. 每個被觀察到的 clone 下面接一個「取樣 leaf」，並記下 cell 數。〔`lineage/lineage.py` L173–177〕
  2. 用 coalescent 解開多分岔，產生沒有名字的中間 node。〔L91–165〕
  3. 小於 `min_mut_fraction` 的 clone 會被合併或刪除。〔L205–251〕
  4. 單鏈 node 摺疊後，事件併到 child。〔L258–279〕
- **對 PhyClone 的意義**〔推論＋實測〕：
  - 只有 leaf 帶 cell 數，所以真值樹的 internal node 的 clonal prevalence 都是 0。
  - 被觀察到的祖先 clone，會變成「internal node 加一個取樣 leaf」。
  - 沒有被觀察到的祖先會保留成 internal node。這些 node 可能沒有任何 SNV：seed 1 有 3 個、seed 2 有 6 個空 node。轉 PhyClone 前要把它們併掉。
  - leaf 名稱（例如 `P9815_13`）是 coalescent 自動命名，不是原本的 clone ID。

## 7. 基因組模型

- **region**：每條染色體切成長度 `region_len`（預設 5 Mb）的 region。CN 和 SNV 都以 region 為單位追蹤。〔程式：`genome/utils.py` L25–33〕
- **座標**：預設用 hg38 的 chr1–22 長度與 arm 比例，不需要 reference FASTA。座標「長得像」hg38，但 SNV 在 region 內的位置是 `randint(region_len)`，沒有對應真實序列。〔程式：`genome/utils.py` L38；`lineage/mutation.py` L167–170〕
  - `get_num_regions` 的 `rem = nregions % region_len` 寫錯了。所以最後一個 region 一定會加上，而且是不完整的 region。落在它上面的 SNV，座標可能超過染色體長度。〔程式：L29〕
  - 給 `ref`／`alt_ref` FASTA 時，allele 0 用 ref，allele 1 用 alt_ref。〔程式：`parameters.py` L21–22〕
- **兩個 allele = haplotype**：起始基因組每條染色體有 `allele=0` 與 `allele=1` 兩個 homolog（`genome/genome.py` L18–23）。arm／chromosome duplication、WGD 產生的新拷貝，都繼承來源的 `allele`（`genome/chromosome.py` L66；`lineage/cell.py` L52–99）。所以 allele 0 在全基因組、所有 clone 都指同一組 parental 拷貝，可以直接對應 HP1。〔程式＋推論〕
- **沒有 germline 變異**：沒有 het SNP，所以沒有 phasing 的錨點，也沒有 PS block。〔程式〕

## 8. CNA 模型

- **4 種機制**：focal amplification／deletion（長度 ~ Exp(`length_mean`) 個 region，倍數 ~ Geom(1/`mag_mean`)）、arm 的 duplication／deletion、整條染色體的 duplication／deletion、WGD。〔程式：`lineage/mutation.py` L74–139〕
- **allele-specific**：每個事件只作用在一個 homolog，並記下它的 `Allele`。〔程式：`lineage/cell.py` L41–86〕
- **driver 與 passenger**：driver CNA 在 agent 階段發生，會影響 fitness。passenger CNA 在 lineage 階段加在樹的邊上，而且避開 driver region。〔程式：`lineage/reevolve.py` L33–42；`selection/region_library.py` L156–168〕
- **沿著樹遺傳**：child 會 deepcopy parent 的基因組，再套用自己的事件（`lineage/cell.py` L31–33；`reevolve.py` L128–156）。所以 CN 是樹邊上的事件，sample 之間一致，也會有 subclonal CN。〔程式〕
- **實測**：seed 1 有 31 個 focal amp、26 個 focal del。seed 2 另有 3 個 arm duplication、2 個 chromosomal deletion。兩個例子都沒有 WGD（`WGD_rate` 預設 1e-8）。

## 9. SNV 模型

- **數量與位置**：每條邊的 passenger SNV 數 ~ Binomial(邊長, `SNV_pass_rate`)。染色體拷貝依長度隨機挑，SNV 放在其中一個非 driver region。〔程式：`lineage/mutation.py` L57–62、L141–170〕
- **allele**：SNV 落在哪一個拷貝，`SNV_events.tsv` 的 `Allele` 就是那個拷貝的 allele。〔程式：`lineage/cell.py` L35–38〕
- **跟 CN 的關係**：
  - 每個 region 拷貝有唯一 ID。SNV 存成 `SNVs[region 拷貝 ID][位置]`。〔程式：`genome/chromosome.py` L50–99〕
  - SNV 在 amplification 之前發生：新的拷貝會複製 SNV，multiplicity 就 > 1。SNV 在 amplification 之後發生：只在一個拷貝上。〔程式：L74–88〕
  - deletion 會一起刪掉 SNV，產生 mutation loss。〔程式：L90–96〕
  - 實測 multiplicity：seed 1 有 177 列是 1、4 列是 2；seed 2 有 85 列是 1、7 列是 2、9 列是 4。〔實測〕
- **同一位置兩次突變**：程式沒有禁止。`get_mutated_basepairs` 用 set 去重，所以兩次突變會合成一列。實測沒有出現。〔程式：`data/utils.py` L197–210〕
- **技術陷阱**：region ID 的位元遮罩 `MBIT` 是模組全域變數（`utilities/utilities.py` L124）。讀 pickle 的樹之前，要先呼叫 `init_mbit(max(regions).bit_length())`，否則 `get_reg_id` 會出現 `NameError`。〔實測〕

## 10. bulk 計數模型

程式（`data/reads.py` L223–317）。以下用 s 表示一個 site，用 c 表示一個 leaf clone（含 diploid）：

```
p_c          = n_c / Σ n                          # cell 比例，含 normal
x_alt,c      = clone c 中，帶這個 SNV 的 region 拷貝數（兩個 allele 合計）
x_tot,c      = clone c 中，這個 region 的拷貝數
fraction     = Σ_c p_c · x_alt,c / x_tot,c         # L296：先算各 clone 的 VAF，再平均，沒有用 CN 加權
DP           ~ Poisson(coverage · mean_c(x_tot,c) / 2)   # L299–301：mean 不用 p_c 加權
alt          = round(DP · fraction)               # L302：沒有 binomial 抽樣
```

- 正確的混合 VAF 是 Σ p_c·x_alt,c ／ Σ p_c·x_tot,c。只要各 clone 的 CN 不同，兩者就不同。實測 438 列中，有 39 列差超過 0.02，最大差 0.12。〔實測〕
- normal：diploid leaf 掛在 root 下，基因組是沒有突變的二倍體（`lineage/utils.py` L61–69），在 L263 計入 site 0。其他 site 依 site 0 的 normal／tumour 比例補 normal（L266–270）。〔程式〕
- purity 真值沒有寫成檔案。要用 cell 數重算。〔程式〕
- 多個 site 就是多個 sample。所有 site 共用同一棵樹與同一組 SNV。SNV 在某個 site 不存在時，那一列是 `DP,0`。〔程式＋實測〕

## 11. 實測結果

| 測試 | 結果 |
|---|---|
| 安裝 | `pip --target` 成功（numpy 2.2.6、scipy 1.15.3、Python 3.10.12） |
| 小模擬（chr1–4、3 個 site） | seed 1 約 14 秒，seed 2 約 5 秒 |
| 同一個 seed 跑兩次 | 12／12 個輸出檔逐 byte 相同（含 `sim.log`、`tree.pkl`），`readcounts.tsv` md5 都是 `786b79fb…` |
| 不同 seed、不設 seed | seed 2 結果不同；兩次不設 seed，結果也不同 |
| alt 是否等於 round(DP × fraction) | 300／300（seed 1）、138／138（seed 2） |
| purity | seed 1 為 0.8323／0.8320／0.8325；seed 2 約 0.830 |
| depth（coverage=100） | seed 1 介於 53–278，平均 112 |
| 轉換程式 | `tools/sistem_to_phyclone.py`（2026-11-04 刪除，已排除的路線；未進 git，無法取回） 從 repo 路徑重跑，輸出和 scratch 版逐檔相同 |

`data.tsv` 開頭幾列（seed 1）：

```
mutation_id     sample_id ref_counts alt_counts major_cn minor_cn normal_cn tumour_content
chr1:3057266    P         96         0          1        1        2         0.832285
chr1:5272308    P         55         33         1        1        2         0.832285
chr1:33216222   P         89         34         2        1        2         0.832285
```

## 12. 對照 04 缺口表

| 04 的缺口 | SISTEM 有沒有補 | 證據 |
|---|---|---|
| SNV 落在哪條 haplotype | **有**：`SNV_events.tsv` 的 `Allele` | 〔程式＋實測〕 |
| allele-specific CN 跟著 haplotype | **有**：`Hap CN` 的 allele 0／1 和 SNV 的 `Allele` 是同一套標籤 | 〔程式〕 |
| CN segment 結構 | **有**：region（5 Mb）與 focal 長度；同一個 region 裡的 SNV 共用 CN | 〔程式〕 |
| CN 跟著 clone 走、sample 間一致 | **有** | 〔程式〕 |
| CN timing | **有**：由樹上事件的先後決定 | 〔程式＋實測 multiplicity 2、4〕 |
| subclonal CN | **有** | 〔實測：CN 狀態有 1/1、2/1、4/1、6/1 等〕 |
| purity < 1 | **部分**：可以設，但每個 site 幾乎一樣，而且沒寫成檔案 | 〔程式＋實測〕 |
| read 共現 | **沒有**：bulk 只有計數。single-cell reads 是 dwgsim 產生的 short read | 〔程式：`reads.py` L86〕 |
| phasing 誤差 | **沒有** | 〔程式〕 |
| 真實座標、PS block | **部分**：用 hg38 長度當座標；沒有 germline het SNP，也沒有 PS block | 〔程式〕 |
| 無偏的樹形 prior | **不適用**：樹由 selection 加 agent 生長產生，有另一種偏向（internal node prevalence 為 0、有空 node） | 〔程式＋推論〕 |
| 輸出 TSV 與真值檔 | **部分**：有 TSV，但沒有 `tree.json`、沒有 clone 比例；要靠 pickle 加轉換程式 | 〔實測〕 |

## 13. 轉成 PhyClone 與 HP 輸入要補什麼

轉換程式：（2026-11-04 刪除，已排除的路線；未進 git，無法取回）`tools/sistem_to_phyclone.py SIM_DIR OUT_DIR`。呼叫端要先把 `simulate_clonal_lineage` 回傳的 Tree pickle 成 `tree.pkl`（試跑的 `run_sim.py` 有做）。〔實測〕

| PhyClone 欄位／真值 | 來源與規則 | 陷阱 |
|---|---|---|
| `mutation_id` | `chrom:pos`（取 `readcounts.tsv` 的 0-based Pos） | 不要和 CNP 的 1-based Start 混用 |
| `sample_id` | site 名稱（P、A、B） | |
| `ref_counts`／`alt_counts` | DP − alt、alt | alt 沒有 binomial 抽樣，VAF 也沒用 CN 加權。要更真實，就用 `truth_snv.tsv` 的期望值自己重抽 |
| `major_cn`／`minor_cn` | 該 site 中 cell 數最多的 tumour clone，在該 region 的 (allele 0, allele 1) 取 max／min | CN 是以 region 為單位。subclonal CN 只能選一個。帶 SNV 的 clone 和 dominant clone 的 CN 可能不同 |
| `normal_cn` | 2 | |
| `tumour_content` | 1 − n_diploid／n_total（照 `reads.py` L260–270 重算） | 檔案裡沒有。site 間幾乎相同，不能測「每個 sample purity 不同」 |
| 真值 cluster | SNV 的起源 node（tree events，等同 `SNV_events.tsv` 的 `Cell/Clone`） | 同一個 node 的 SNV 算一群。空 node 要併掉 |
| 真值 `tree.json` | node：`snvs`、`clonal_prev`（leaf cell 數／tumour cell 數）、`cellular_prev`（子樹合計）；去掉 root `P0` 和 `diploid` | 只有 leaf 的 clonal_prev > 0。Newick 沒有 cell 數，一定要用 pickle |
| HP 拆分計數 | 每個 allele h：期望 depth = DP·Σp_c·CN_h,c／Σp_c·CN_c，期望 alt = DP·Σp_c·alt_h,c／Σp_c·CN_c。寫在 `truth_snv.tsv` 的 `exp_ref_hp0…exp_alt_hp1` | 這是我們的 CN 加權模型，不是 SISTEM 的公式。phasing 誤差與 unphased read 要另外加 |

要做 read 層的 HP 資料：`data/sequence.py::build_cell_ref` 能寫出每個 clone、每個 homolog 的 FASTA，而且已經帶 SNV。把這些 FASTA 依 allele 與 cell 比例接到 long-read 模擬器（例如 PBSIM、Badread），就有 HP 真值與同 read 共現。這一步要自己寫，而且要先給 reference FASTA。〔程式＋推論〕

## 14. 對既有調查的修正

- 04／05 調查說「外部 `np.random.seed()` 應可重現」：**已證實**。〔實測〕
- 04 調查說「leaf 是觀察到的 clone，帶細胞數」：cell 數只存在記憶體（`info['count']`），**沒有寫進 Newick 或任何 TSV**。〔程式〕
- 05 調查說「期望 VAF 用各 clone 的 x_alt/(x_ref+x_alt) 加權，所以含 CN 效應」：只對了一半。各 clone 的 VAF 有含 CN 效應，但跨 clone 時沒有用 CN 加權，而且 alt 是取整，不是抽樣。〔程式＋實測〕
- 05 調查說「多個轉移 site 是多個 sample」：正確，但 site 間的 purity 是同一個比例。〔程式〕

## 15. 限制與未確認

- 只測了 `RandomRegionLibrary` 加 `StaticAnatomy`。arm／hybrid 模型、driver SNV、WGD 都沒有實際跑到。
- 沒有把 `data.tsv` 丟給 PhyClone 跑，也沒有測大型設定（22 條染色體、1e6 個 cell）的時間與記憶體。論文 Table 1 寫：3 個 site、min_detectable 5e5，約 20 分鐘、約 1 GB。〔論文〕
- single-cell reads（`gen_reads`）沒有跑，因為本機沒有裝 `dwgsim`。
- 論文的 Supplementary（模型細節）沒有讀。本檔的模型描述以程式為準。
- seed 的可重現性只在同一台機器、同一組 numpy／scipy 版本下驗證過。
