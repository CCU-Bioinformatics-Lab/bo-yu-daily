# diplosim 移植對照表（Rust ↔ CONIPHER）

日期：2026-10-30。CONIPHER 版本：`TRACERx_simulation_tool` commit `facd2d7`。下文 `evolution.py:48` 這類行號，都指 `research/simulation_pipeline_research/upstream/TRACERx_simulation_tool/src/`。Rust 行號指 `diplosim/src/`。

標記：〔程式〕讀程式碼得到；〔實測〕實際執行得到；〔推論〕分析推論，沒有執行驗證。

## 1. 結論

- 每個 CONIPHER 檔案對應一個 Rust 模組：`topology.py` → `topology.rs`，`evolution.py` → `evolution.rs`，`sequencing.py` → `sequencing.rs`，`noise.py` → `noise.rs`，`conversion.py` 與存檔 → `output.rs`，`tx_simulation` → `lib.rs::simulate`。
- 新寫的只有 `hp.rs`（兩個 HP 擴展）、`params.rs` 的輸入檢查、`main.rs` 的 CLI。
- 亂數無法和 numpy 逐位元相同。目標是「同分佈」。同一個 seed 的輸出逐位元相同。〔實測〕
- `prop_snv_on_b = 0` 時，diplosim 和 CONIPHER（1 個 sample、所有 clone 都在）的輸出分佈一致（見第 6 節）。〔實測〕

## 2. 資料形狀

| Rust 型別 | 意思 | 對應 CONIPHER |
|---|---|---|
| `Params`（`params.rs`） | 所有參數，CLI 解析後先跑 `validate` | `tx_simulation` 的參數（`simulate.py:13-46`） |
| `Tree { nodes, edges, root, initial_cc, leaves }`（`topology.rs`） | 節點編號照 CONIPHER（葉 1..n，內部節點與 root 往上編號） | `simulate_topology` 的回傳值與 `leaves`（`simulate.py:162-164`） |
| `enum Event`（`evolution.rs`） | `Wgd, GainA, GainB, GainBoth, Snv, LossA, LossB, CnlohA, CnlohB` | 事件名稱字串（`evolution.py:164-181`） |
| `enum Mode { Total, Dcf }` | `Dcf` 時 `loss_A`、`cnloh_A` 不減突變 copy | `dcf_loss_A`、`dcf_cnloh_A`（`evolution.py:135-140, 177-178`） |
| `struct Genotype { a, b, mutated }` | `[cnA, cnB, 帶突變的 copy 數]` | `np.array([1, 1, 0])`（`evolution.py:115`） |
| `BTreeMap<NodeId, BTreeMap<Pos, Vec<Event>>>` | 每個節點、每個 position 的事件，已洗牌 | `profile_events`（`evolution.py:99-105`） |
| `enum Allele { A, B }` | 每個 position 的 SNV 在哪條 allele；A = HP1，B = HP2 | 新寫（CONIPHER 一律在 A） |
| `Sample { purity, proportions }`（`sequencing.rs`） | 一個 bulk sample；proportions 含 normal | `sample_clone_proportions`（`sequencing.py:28-39`） |
| `VariantRow`（`sequencing.rs`） | 一個 position 一列 | `variant_df` 的一列（`sequencing.py:134-146`） |
| `HpCounts`（`hp.rs`） | HP1／HP2／HP0 的 ref、alt | 新寫 |

用 `BTreeMap` 的理由：走訪順序固定，同 seed 才會得到相同輸出。

## 3. 函式對照

### 3.1 `topology.rs`（全部沿用）

| Rust | CONIPHER | 標記 | 說明 |
|---|---|---|---|
| `split`（`topology.rs:57`） | `split`（`topology.py:9`） | 沿用 | 隨機切成左右兩組葉子，各 ≥ 1 |
| `make_tree`（`topology.rs:68`） | `make_tree`（`topology.py:21`） | 沿用 | 加 root（normal），接到 `initial_cc` |
| `make_tree_internal`（`topology.rs:81`） | `make_tree_internal`（`topology.py:32`） | 沿用 | 遞迴建二元樹，edge 順序相同 |
| `prune_tree`（`topology.rs:97`） | `prune_tree`（`topology.py:46`） | 沿用 | 隨機刪葉子到剩 `n_clones + 1` 個節點。CONIPHER 用遞迴，這裡用迴圈 |
| `simulate_topology`（`topology.rs:109`） | `simulate_topology`（`topology.py:64`） | 沿用 | |
| `Tree::new` 算 `leaves`（`topology.rs:27`） | `simulate.py:163-164` | 沿用 | 葉子 = 不當 parent 的 child |
| `Tree::descendants_below`（`topology.rs:42`） | `get_descendants(edge)[1:]`（`evolution.py:357`） | 沿用 | 不含 edge 的 child 本身 |
| `Tree::children`（`topology.rs:36`） | `[c for p, c in edges if p == x]`（`evolution.py:119`） | 沿用 | |

### 3.2 `evolution.rs`（全部沿用）

| Rust | CONIPHER | 標記 | 說明 |
|---|---|---|---|
| `tree_profiles`（`evolution.rs:167`） | `tree_profiles`（`evolution.py:4`） | 沿用 | 依序：SNV → CNA → WGD → 合併洗牌 → 套用 |
| `snv_assignment`（`evolution.rs:246`） | `snv_assignment`（`evolution.py:48`） | 沿用 | subclonal 數 = `int(n × (1 − prop_truncal_snvs))`，無條件捨去 |
| `partition`（`evolution.rs:228`） | `partition`（`evolution.py:35`） | 沿用 | `minimum_branch_length = 1` 時每條邊 ≥ 1 個 SNV |
| `conditioned_choice`（`evolution.rs:199`） | `conditioned_choice`（`evolution.py:22`） | 沿用 | 保留怪行為（見第 5 節） |
| `np_split`（`evolution.rs:216`） | `np.split`（`evolution.py:39, 43`） | 沿用 | 切點超過長度時給空段，和 numpy 相同 |
| `create_event_dict`（`evolution.rs:260`） | `create_event_dict`（`evolution.py:64, 368`） | 沿用 | CONIPHER 也替「剩下的」position 抽事件，但只用到 key；這裡不抽 |
| `wgd_assignment`（`evolution.rs:270`） | `wgd_assignment`（`evolution.py:75`） | 沿用 | subclonal WGD 放回抽樣 |
| `concat_all_events`（`evolution.rs:284`） | `concat_all_events`（`evolution.py:91`） | 沿用 | 每個（節點, position）的事件隨機洗牌 |
| `mutation_node_assignment`（`evolution.rs:320`） | `mutation_node_assignment`（`evolution.py:114`）、`dcf_mutation_node_assignment`（`evolution.py:143`） | 沿用 | 兩個函式合成一個，用 `Mode` 區分。結果相同：每個 clone = 祖先事件（由上往下）＋自己的事件 |
| `Event::apply`（`evolution.rs:104`） | `generate_events`（`evolution.py:164`）、`apply_events`（`:108`）、`dcf_apply_events`（`:135`） | 沿用 | 一個 match 分支對應一個 lambda |
| `cna_assignment`（`evolution.rs:351`） | `cna_assignment`（`evolution.py:184`） | 沿用 | 含 `prop_pos_gained + prop_pos_lost > 1` 時調低 gain（`evolution.py:186-187`） |
| `get_npos_cnas`（`evolution.rs:433`） | `get_npos_cnas`（`evolution.py:213`） | 沿用 | `round()` 用 round-half-to-even（Python 行為） |
| `get_mutloss`（`evolution.rs:480`） | `get_mutloss`（`evolution.py:249`） | 沿用 | |
| `only_mutloss_cnas`（`evolution.rs:540`） | `only_mutloss_cnas`（`evolution.py:286`） | 沿用 | |
| `assign_cnas`（`evolution.rs:560`） | `assign_cnas`（`evolution.py:294`） | 沿用 | 含兩種 cap 與 warning |
| `prevent_subclonal_cnas`（`evolution.rs:644`） | `prevent_subclonal_cnas`（`evolution.py:350`） | 沿用 | 保留 `[1:]`（見第 5 節） |
| `EdgeLabel` 計數 | `cna_edge_labels`（`evolution.py:207`）、`snv_edge_labels`（`:60`）、`wgd_edge_labels`（`:86`） | 沿用 | |
| `choose_without`（`evolution.rs:156`） | `np.random.choice(x, k, replace=False)` | 沿用 | 回傳順序是隨機的，和 numpy 相同 |

### 3.3 `sequencing.rs`

| Rust | CONIPHER | 標記 | 說明 |
|---|---|---|---|
| `simulate_sample`（`sequencing.rs:60`） | `all_samples`（`sequencing.py:51`）＋ `simulate_sample_leaves`（`:28`） | 沿用，簡化 | 只有 1 個 sample，所有非 root clone 都在。purity ~ U(min, max)；比例 = Dirichlet(1,…,1) × purity；normal = 1 − purity |
| `expected`（`sequencing.rs:83`） | `calculate_vaf`（`sequencing.py:66`）、`calculate_ccf`（`:107`）、`calculate_dcf`（`:115`） | 沿用 | 逐 position 算；含 `ccf ≤ dcf` 的 assert（`:118`） |
| `make_sequencing_data`（`sequencing.rs:134`） | `make_sequencing_data`（`sequencing.py:7`）、`get_total_reads`（`:95`）、`get_variant_reads`（`:102`）、合併 SNV 邊（`simulate.py:157`） | 沿用 | depth ~ Poisson(coverage × cn ÷ 平均 cn)；alt ~ Binomial(depth, VAF) |
| `VariantRow::est_vaf`（`sequencing.rs:40`） | `Est_VAF`（`sequencing.py:145`） | 沿用 | |

### 3.4 `noise.rs`

| Rust | CONIPHER | 標記 | 說明 |
|---|---|---|---|
| `add_noise`（`noise.rs:10`） | `add_noise`（`noise.py:5`） | 沿用 | 假 cluster 編號 = 最大節點編號 + 1, 2, …；CCF = randint(1,100)/100；alt 重抽。和原版一樣，所有列的 `True_VAF` 都重算（`noise.py:17`） |

### 3.5 `output.rs`

| Rust | CONIPHER | 標記 | 說明 |
|---|---|---|---|
| `assign_loci`（`output.rs:31`） | `assign_chr_pos_correct`（`conversion.py:35`）、REF／ALT（`conversion.py:12`） | 沿用 | 依染色體長度抽 CHR、POS；重複時回傳錯誤（CONIPHER 是 assert） |
| `write_all`（`output.rs:84`） | `convert_tree_building_format`（`conversion.py:4`）、存檔（`simulate.py:100-106`） | 沿用＋新欄位 | `<name>.tsv` = `df_og` 欄位＋ `ALLELE, HP1_REF, HP1_ALT, HP2_REF, HP2_ALT, HP0_REF, HP0_ALT`；`<name>_TX.tsv` = `df_tx` |
| `info_rows`（`output.rs:205`） | `make_patient_info_df`（`simulate.py:113`） | 沿用＋新欄位 | 加入所有參數、seed、抽到的 purity、warnings |
| `write_truth`（`output.rs:241`） | `create_edge_snv_df`（`simulio.py:59`）、`_events.tsv`（`simulate.py:106`） | 沿用＋新寫 | `truth/genotypes.tsv`（每個 position、每個 clone 的 A、B、MUT、MUT_DCF）、`truth/snv_edges.tsv`、`truth/events.tsv` |
| `np_round2`、`py_round`、`py_float`（`lib.rs:25-35`） | `df.round(2)`、Python `round()`、pandas `to_csv` 的數字格式 | 沿用 | |

### 3.6 新寫

| Rust | 標記 | 為什麼 |
|---|---|---|
| `Params::validate`（`params.rs:92`） | 新寫 | CONIPHER 不檢查輸入。這裡在入口擋掉 CONIPHER 會當掉或沒有意義的值（第 4 節） |
| `hp::draw_alleles`（`hp.rs:28`） | 新寫 | 擴展 1：每個 position 以 `prop_snv_on_b` 的機率選 B（DECISIONS 2026-10-30「對稱改名」） |
| `hp::relabel`（`hp.rs:37`） | 新寫 | 擴展 1：B position 的所有 clone 基因型（total、dcf）A、B 對調；事件名稱同步改名 |
| `hp::split_counts`（`hp.rs:71`） | 新寫 | 擴展 2：把 CONIPHER 的 ref／alt 拆成 HP1／HP2／HP0（DECISIONS 2026-10-30 方案 ②） |
| `main.rs` | 新寫 | CLI（clap），參數名稱照 CONIPHER，只有 `n_clones`、`n_snv` 改名 |

## 4. 刻意的差異

| 差異 | 做法 | 理由 |
|---|---|---|
| 亂數 | ChaCha8，`--seed` 決定全部抽樣；沒給 seed 就隨機抽一個並寫進 `_info.tsv` | numpy 的亂數序列無法重現。目標是同分佈 |
| 單一 sample | 不提供 `n_samples`、`min／max_clones_per_sample`、`all_leaf_observed` | DECISIONS 2026-10-29 |
| 所有 clone 都在 sample | Dirichlet 給每個非 root clone 一個比例 | 等於 CONIPHER `n_samples = 1`、clone 數 = `n_nodes` 時的行為〔程式〕 |
| 不畫圖 | 不移植 `simulio.py` 的 graphviz、`plot_variant_data` | 不影響資料 |
| `n_clones = 1` 拒絕 | `validate` 回錯誤 | CONIPHER 在 `topology.py:25` 讀 `parents[1]`，1 個葉子時沒有這個元素，會當掉〔程式〕 |
| purity 必須 > 0 | `0 < min ≤ max ≤ 1` | CCF、`Fract_a` 都除以 purity（`sequencing.py:71, 112`） |
| `minimum_branch_length = 1` 而 subclonal SNV 數 < 邊數 | `validate` 回錯誤 | CONIPHER 在 `evolution.py:37` assert 失敗 |
| `constant_multiplicity = false` 而 CNA 數 > position 數 | `simulate` 回錯誤 | CONIPHER 印出 `ERROR! ABI FIX!!` 後當掉（`evolution.py:333-334`）〔程式〕 |
| CHR／POS 重複 | `simulate` 回錯誤 | CONIPHER 在 `conversion.py:42` assert 失敗 |
| `prop_pos_lost = 0` 且 `prop_mutloss_positions > 0` | 浮點除以 0 得 −inf，`prop_lost_truncal` 變 0，mutation loss 被 cap 成 0 並寫 warning | CONIPHER 用 Python float 會丟 `ZeroDivisionError`〔推論，未實測〕 |
| `_treeedges.tsv` 欄位 | 依名稱寫 `Parent, Child, CNA_gains, CNA_losses, SNVs, WGD, Truncal` | CONIPHER 用位置改欄名（`simulate.py:175`）。第一條邊沒有 CNA 時，pandas 的欄位順序可能不同，欄名可能錯位〔推論，未實測〕 |
| TSV 沒有 index 欄 | 純 TSV，第一列是欄名 | CONIPHER `to_csv` 預設寫 pandas index |
| 擴展 1：SNV 在 B | 照 CONIPHER 模擬（SNV 在 A），再對 B position 的 A、B 對調 | DECISIONS 2026-10-30。等於把該 position 的 `gain_A↔gain_B`、`loss_A↔loss_B`、`cnloh_A↔cnloh_B` 改名 |
| 擴展 2：HP 拆分 | 見下 | DECISIONS 2026-10-30 方案 ② |

擴展 2 的步驟（`hp.rs:71`）：

1. depth、alt 照 CONIPHER 抽，不改。
2. X = SNV 所在 allele，O = 另一條。對 sample 中每個 clone（含 normal `[1,1,0]`）加權：F_X = Σ p·cn_X，F_O = Σ p·cn_O，M = Σ p·mut。
3. alt 全部給 HP_X。
4. ref = depth − alt。ref_O ~ Binomial(ref, F_O ÷ (F_X − M + F_O))，ref_X = ref − ref_O。
5. 分母 ≤ 0（沒有任何帶 ref 的 copy，只會在 purity = 1 時發生）時用 0.5，兩條 HP 不偏。
6. HP1 = allele A，HP2 = allele B。
7. 四個數（HP1 ref、HP1 alt、HP2 ref、HP2 alt）各有 Binomial(count, 1 − `prop_tagged`) 條變成 HP0。
8. 結果：HP1＋HP2＋HP0 的 ref = CONIPHER 的 REF_COUNT，alt 同理。

noise SNV（`fract_noise > 0`）：用 noise 重抽後的 alt 拆分。copy 數用原本那個 position 的基因型（noise 只改 cluster、CCF、alt，不改基因型）。

`draw_alleles` 每個 position 固定抽一個 uniform。所以同一個 seed，不同 `prop_snv_on_b` 會得到相同的樹、depth、alt，只差 allele 標籤（測試 `putting_every_snv_on_b_swaps_the_alleles_of_the_conipher_genotypes`）。〔實測〕

## 5. 保留的 CONIPHER 怪行為

| 怪行為 | 位置 | 決策 |
|---|---|---|
| `minimum_branch_length > 1` 時，`conditioned_choice` 用 SNV 編號當切點索引，邊可能分到 0 個 SNV | `evolution.py:22-32, 41-42` | DECISIONS 2026-10-30 照搬 |
| `mutloss_truncal = false` 不排除 truncal SNV | `evolution.py:266-269` | DECISIONS 2026-10-29（暫緩，照搬） |
| `prevent_subclonal_cnas` 用 `get_descendants(...)[1:]`，SNV 所在 clone 本身仍可能被選中 | `evolution.py:351` | DECISIONS 2026-10-29（暫緩，照搬） |
| `n_subclonal_wgd` 放回抽樣，同一節點抽到兩次只算一次 WGD | `evolution.py:83` | DECISIONS 2026-10-29（暫緩，照搬） |
| `get_npos_cnas` 的 cap、四捨五入（half-to-even）與「總數 > n 時減 1」 | `evolution.py:213-246` | 照搬 |
| `prop_mutloss_positions` 太大時自動調低 `prop_lost_truncal` | `evolution.py:217-222` | 照搬，warning 寫進 `_info.tsv` |
| 每個（節點, position）的事件獨立洗牌，WGD 沒有時間點 | `evolution.py:101-103` | 照搬（S5 待決） |
| dcf profile：`loss_A`、`cnloh_A` 不減突變 copy | `evolution.py:135-140` | 照搬 |
| 加 noise 時所有列的 `True_VAF` 重算並 cap 在 1 | `noise.py:17` | 照搬 |
| 少於 1% 的 SNV `TRUE_CCF = 0` 時不發 warning | `simulate.py:77-81` | 照搬 |

## 6. 驗證

測試：`cd diplosim && cargo test --release`（`tests/behaviour.rs`，14 個）。〔實測〕

- 樹有 `n_clones + 1` 個節點且連通；每個 SNV 恰在一條邊上；`minimum_branch_length = 1` 時每條邊 ≥ 1 個 SNV。
- `prop_snv_on_b = 0` → `ALLELE` 全是 A，`HP2_ALT` 全是 0。
- `prop_tagged = 1` → HP0 全是 0；`prop_tagged = 0.8` → HP0 約占 20%。
- 每一列 HP1＋HP2＋HP0 = REF_COUNT／VAR_COUNT（含 CN、WGD、mutation loss、noise）。
- 沒有 CN 時，SNV 在 A 與在 B 的兩組各自 HP1 depth ≈ HP2 depth（差 < 2%）；alt 只在 SNV 所在 HP 或 HP0。
- 沒有 CN、沒有 mutation loss 時，truncal SNV 的 `TRUE_CCF = 1`。
- 同 seed 兩次執行，所有輸出檔逐位元相同。

和 CONIPHER 比分佈（2026-10-30）〔實測〕：CONIPHER `tx_simulation(n_nodes=5, n_positions=300, n_samples=1, min/max_clones_per_sample=5)`，diplosim `--n-clones 5 --n-snv 300 --prop-snv-on-b 0`，各 200 個 seed，比每次模擬的平均 DEPTH、VAF_OBS、TRUE_VAF、TRUE_CCF、TRUE_DCF、MUT_CN、CN_A、CN_B、TOTAL_CN、PURITY 等。

| 設定 | 結果 |
|---|---|
| 預設 | 全部 \|z\| < 1.4 |
| clonal＋subclonal WGD、`prop_mutloss_positions` 0.1、truncal 比例 0.5 | 全部 \|z\| < 1.9 |
| `fract_noise` 0.1、`n_noise_clones` 2 | 全部 \|z\| < 1.2 |
| `minimum_branch_length` 10 | 非空邊數平均：CONIPHER 3.487、diplosim 3.485（各 6000 seed，se 0.010） |

限制：比的是平均值，不是完整分佈形狀。比較腳本放在 session scratchpad，沒有放進 repo。
