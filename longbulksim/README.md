# longbulksim：long read bulk 腫瘤模擬器

輸入一組摘要參數（clone 數、SNV 數、CN 比例、purity、depth 等，像 CONIPHER 的 `tx_simulation`），或一棵手寫的 HP-aware clone tree spec。輸出一個 bulk ONT 樣本的 PhyClone 輸入、HP 計數、SNV pair 共現表，以及獨立的真值目錄。

範圍：molecule 層計數。每條 read 是一個 molecule，屬於一個 lineage、一條 HP、一個 copy。不產生 FASTQ／BAM（`plan.md` §5.8.4 L2-R 留到之後）。v0.2 加入觀測誤差：HP 錯標、phase switch、鹼基錯誤（見「觀測誤差」）。v0.3 加入選填的 het map tagging（見「HP tag」）。v0.4 加入參數模式（見「參數模式」），這是主要入口。v0.5 加入 somatic caller 的漏抓（見「Caller 漏抓」）。

## 參數模式（主要入口）

```bash
cd longbulksim
python3 -m longbulksim.generate OUT --n-sims 10 --seed 1                      # 全部用預設值
python3 -m longbulksim.generate OUT --n-clones 5 --tree-shape branched --purity 0.3 --depth 50
python3 -m longbulksim.generate --help
```

使用者不寫樹。樹、CCF、SNV、CN 由參數產生；產生的 spec 存在 `OUT/sim_<i>/truth/spec.yaml`，參數存在 `manifest.json`。

| 參數 | 意思 | 預設 | 預設的來源 |
|---|---|---|---|
| `--n-sims`、`--seed` | 模擬數、seed | 1、1 | |
| `--n-clones` | clone 數（含 trunk） | 3 | TRACERx 單區域中位（merge 後） |
| `--tree-shape` | random／linear／branched | random | |
| `--p-linear` | random 時直線樹的機率 | 0.63 | TRACERx 單區域（≥ 3 clones） |
| `--ccf-alpha` | clone 細胞比例的 Dirichlet 參數 | 0.5 | 校正到 subclone CCF 中位 0.45（TRACERx） |
| `--min-ccf`、`--min-gap` | subclone 最小 CCF、與 parent 的最小 CCF 差 | 0.05、0.05 | 與 TRACERx merge 規則相同 |
| `--n-snv` | SNV 數 | 450 | TRACERx 每區域中位（WES） |
| `--prop-truncal` | truncal SNV 比例 | 0.91 | TRACERx 單區域中位（merge 後） |
| `--n-segments` | CN segment 數 | 129 | TRACERx 每 tumour 中位 |
| `--wgd` | yes／no | yes | TRACERx 57% tumour ploidy ≥ 3 |
| `--prop-gain`、`--prop-loss`、`--prop-loh` | trunk CN 類別的 bp 比例（相對 1:1 或 WGD 的 2:2） | WGD：0.083／0.328／0.267；非 WGD：0.124／0／0.274 | TRACERx 中位 |
| `--prop-subclonal-cn` | 有 subclonal CN 改變的 segment 比例 | 0.096 | TRACERx 區域內 bp 比例中位 |
| `--purity`、`--depth` | purity、depth | 0.41、50 | TRACERx 區域 purity 中位；PCAWG depth 中位 |
| `--snv-density` | 每 Mb SNV 數（決定 read 共現） | 12.9 | HCC1395 |
| `--het-map`、`--phased`、`--mistag`、`--switch-rate`、`--base-error` | 觀測參數 | 不用 map、0.859、0、0、0 | 見「HP tag」「觀測誤差」 |
| `--caller` | none／clairs／deepsomatic：移除這個 caller 會漏掉的 SNV | none | 見「Caller 漏抓」 |

- 具體的 CN 狀態（例如 3:1、2:0）與 subclonal 改變（例如 +1 HP1），從 TRACERx 同一類別、同一 ploidy 組的 segment 重抽。HP 方向隨機。
- multiplicity、CN timing、突變遺失由事件順序產生，不設定（和隨機樹相同）。
- 觀測到的 SNV 數比 `--n-snv` 少約 5%：truncal SNV 若在 clonal LOH 之前、位在被刪掉的 HP 上，所有 clone 都不帶，真實資料也看不到，所以移除。
- 研究主軸是單一 bulk 樣本，所以沒有 CONIPHER 的 `n_samples`、`min/max_clones_per_sample`。CONIPHER 的 `fract_noise`（假 cluster）改由 long read 觀測誤差取代。
- 1,000 個預設 spec 的實測：直線 0.625、subclone CCF 中位 0.452、truncal 0.907、gain 0.077、loss 0.347、LOH 0.230、subclonal CN 0.078、遺失中位 0.7%（Q90 2.8%）。LOH 和 subclonal CN 低於設定，因為那些區段的部分 SNV 被 LOH 移除（SNV 加權）。

## 手寫 spec（進階）

```bash
python3 -m longbulksim specs/stress.yaml OUT --seed 1            # 壓力測試樹，200×
python3 -m longbulksim specs/typical.yaml OUT --seed 1 --depth 200
python3 -m longbulksim specs/stress.yaml OUT --mistag 0.025 --switch-rate 1 --base-error 0.004
python3 -m longbulksim specs/stress.yaml OUT --het-map longbulksim/data/hcc1395bl_phased_het.npz
python3 -m unittest discover -s tests                            # 約 30 秒，47 個測試
```

需要 `numpy`、`scipy`、`pyyaml`（系統 `python3` 已有）。PhyClone 用 `~/venvs/phyclone` 跑輸出的 TSV 即可，不需要裝本 package。

## 隨機樹（TRACERx 藍圖）

```bash
python3 -m longbulksim.random_tree SPECS_DIR --count 100 --seed 1 --n-snv 200 --depth 50
python3 -m longbulksim SPECS_DIR/spec_0000.yaml OUT --seed 1
```

每個 spec 取一棵 TRACERx 421 單區域真實樹（拓樸、區域 CCF、purity、各 clone 的相對突變數），再配上同一個 tumour 的 allele-specific CN profile。每個 segment 的 trunk 狀態放在 root 邊上，subclonal 改變放在一個 clone 的邊上。multiplicity、CN timing 與突變遺失（含非 LOH deletion）都由事件順序自然產生，不設定。spec 的 `source` 欄記錄藍圖來源與 merge／事件數。與 cohort 的比對見 `lab_report/2026-10-25_random_tree_generator/`。

## Spec 格式

```yaml
purity: 0.40          # 細胞 purity（模擬真值，不是 nominal tumor fraction）
depth: 200            # 二倍體 normal 區的平均 depth
phased_fraction: 0.859  # 沒有 het_map 時才使用
het_map: hcc1395bl_phased_het.npz  # 選填（v0.3），見「HP tag」
mistag_rate: 0        # 選填，預設 0（見「觀測誤差」）
switch_rate_per_mb: 0
base_error: 0
clones:               # fraction = 佔 tumour 細胞的比例，總和為 1
  C1: {parent: null, fraction: 0.10}
  C2: {parent: C1, fraction: 0.35}
segments:
  A: {chrom: chr1, start: 10000000, length: 1550000}
edges:                # 進入該 clone 的邊上的事件，依序套用
  C1:
    - {snv: s1, hp: HP1, segment: A, count: 10}   # 一個 role = count 個 SNV，CN 歷史相同
  C2:
    - {gain: A, hp: HP1}                          # 複製 HP1 的 copy 0（copy: 可指定）
    - {snv: s4, hp: HP1, segment: A, copy: 0}     # gain 之後，只在 copy 0 → multiplicity 1
    - {loss: B, hp: HP2}
    - {cnloh: D, keep: HP1}                       # 移除 HP2，HP1 複製一份
```

模擬器從 root 依序重播事件，得到每個 clone 的 genome（segment → HP → copies，每個 copy 是它帶的 SNV role 集合）。突變遺失、multiplicity、CN timing 都由重播決定，不手寫。

## HP tag（v0.3）

沒有 `het_map` 時，每條 read 以機率 `phased_fraction` 被標記，和位置無關。

有 `het_map` 時，照 longphase-s germline haplotag 的規則（`src/haplotag/HaplotagStrategy.cpp` 的 `judgeReadHap`）：
- read 沒有覆蓋任何 phased het SNP → 不標。
- read 覆蓋的 het SNP 跨兩個以上 PS block → 不標。
- 「allele 一致比例 ≥ 0.6」這條規則不模擬。read 在 het SNP 上都帶正確的 haplotype allele。

這個規則沒有可調參數。`phased_fraction` 不使用。

- 內建 map：`longbulksim/data/hcc1395bl_phased_het.npz`。來源是 SEQC2 HCC1395BL germline het SNP，用 `longphase-s phase --ont` 在 HCC1395BL ONT 上 phase（`tools/hcc1395_hp_split_prepare.sh`）。共 1,804,018 個 het SNP、4,060 個 PS block。
- 建立其他 map：`python3 -m longbulksim.het_map PHASED.vcf.gz OUT.npz`。
- 座標要對應 GRCh38。spec 的 segment 如果落在沒有 het SNP 的區域，tag 比例會變低。內建 map 只含 SEQC2 high-confidence 區域內的 het SNP。所以隨機樹 spec（人工座標）的 alt read tag 比例中位是 0.68（20 個 spec：0.58–0.74）。壓力測試樹與典型樹是 0.87／0.94，真實 HCC1395 是 0.87。
- 與真實資料的比對見 `lab_report/2026-10-26_longbulksim_ppc/`。

## Caller 漏抓（v0.5）

`caller`（CLI `--caller`，兩種模式都有）預設 `none`：每個 SNV 都進 `input/`，和之前相同。

設成 `clairs` 或 `deepsomatic` 時，每個 SNV 用觀測到的 alt 數與 depth，以 P(call) = sigmoid(b0 + b1·log(alt) + b2·log(depth)) 抽一次（alt = 0 時不會被 call）。沒被 call 到的 SNV 從 `data.tsv`、`data_hp.tsv`、`pairs.tsv` 移除；`truth.tsv` 的 `detected` 欄記錄結果。

- 係數：`longbulksim/data/caller_detection_hcc1395.tsv`。來源是 CASTLE HCC1395 ONT tumor（84×、purity 約 1）上的 ClairS v0.4.0 ssrs 與 DeepSomatic PASS call，對照 SEQC2 HighConf 真值。
- 大約門檻：ClairS 要 ≥ 10 條 alt read，DeepSomatic 要 ≥ 5 條。
- 預設參數（purity 0.41、50×）下，ClairS 只 call 到 72% 的 truncal、17% 的 subclonal SNV；DeepSomatic 是 92%、45%。
- 曲線在 purity 約 1 的樣本上校正，用在低 purity 樣本時可能高估漏抓。只模擬漏抓，不模擬偽陽性。
- 校正與影響分析：`lab_report/2026-10-26_caller_detection/`。

## 觀測誤差（v0.2）

| 欄位（CLI） | 意思 | 套用位置 |
|---|---|---|
| `mistag_rate`（`--mistag`） | tagged read 被標成另一條 HP。以整條 read 為單位 | `sample.py`：`Reads.obs_hp` |
| `switch_rate_per_mb`（`--switch-rate`） | 每個 segment 內的 phase switch 點（Poisson、位置均勻）。read 中點之前有奇數個 switch 時，`obs_hp` 反轉 | `sample.py` |
| `base_error`（`--base-error`） | 每條 read 在每個 SNV 位點，allele 被讀反（ref↔alt，對稱） | `simulate.py:observe()` |

- `counts()`、`snv_hp`、`pairs.tsv` 都用 `obs_hp` 和觀測 allele。三個輸入檔看到同一份錯誤。
- 錯誤率為 0 時不抽亂數。所以舊 seed 的 `input/` 與 v0.1 逐位相同（`ZeroErrorsMatchV01`）。
- 整條 read 錯標不會讓分支 pair 出現 n11。錯標的 read 移到另一條 HP 的 pair 表，在那裡兩個位點都是 ref（n00）。會產生假矛盾的是 base error 和 phase switch。
- 校正值與 C4 的敏感度見 `lab_report/2026-10-25_c4_robustness/`。

## 輸出

| 路徑 | 內容 |
|---|---|
| `input/data.tsv` | PhyClone 8 欄。major／minor 取細胞最多的 tumour CN 狀態 |
| `input/data_hp.tsv` | 加上 HP 欄位，給 `tools/phyclone_hp.py`。`snv_hp` 由 tagged alt read 多數決，不是真值 |
| `input/segments.tsv` | root 狀態 A、另一狀態 B、真值 phi |
| `input/pairs.tsv` | `plan.md` §1.3 的 `PAIRS.tsv` 欄位，加 `distance`。只計 tagged read |
| `truth/` | `truth.tsv`、`truth_tree.tsv`、`clusters_truth.tsv`（欄位同 `tools/hp_truth_tree_to_phyclone.py`），`genome.json`，`reads.tsv.gz`（每條 read 的 lineage／HP／copy／觀測 HP `obs_hp`），`phase_switches.tsv` |
| `manifest.json` | spec、seed、錯誤率、read span 來源、read 數 |

`tools/eval_hp_truth_phyclone.py OUT/truth RUN_DIR` 可直接評分。

## 已驗證

| 檢查 | 結果 | 測試 |
|---|---|---|
| 重播的 genome 等於手寫樹 | 壓力測試樹與典型樹的 GENOME、LOST 完全相同 | `test_model.py` |
| 跨越 read 數 vs 間距 | 模擬 50／41／20／1／0；HCC1395 實測 52／44／21／2／0（0–1k／1–5k／5–20k／20–50k／50–100 kb 中位數） | `SpanningReadsMatchHCC1395` |
| 共現遵守樹 | 分支 pair（s4×s6）n11 = 0；祖孫 pair（s3→s5）n01 = 0；alt read 不出現在另一條 HP。把共現打亂後三項都失敗 | `ReadCooccurrenceFollowsTree` |
| 計數 | 每個 role 的合併 VAF 在期望值 4 SE 內；二倍體區 depth 誤差 < 3% | `CountsMatchExpectedVAF` |
| 端到端 | PhyClone `run`、`phyclone_hp.py --hp-mode a2`、`map`、`eval_hp_truth_phyclone.py` 都能讀輸出 | 手動 smoke run |
| 隨機樹的 CCF 投影 | 1,426 棵藍圖都符合加總規則；不 merge 時 clone 數不變 | `test_random_tree.py` |
| 隨機樹可用 | 100 個 spec 都能 replay；每個 SNV 至少一個 clone 帶；每個 segment 最多兩種 tumour CN 狀態 | `test_random_tree.py` |
| 零誤差 = v0.1 | `stress.yaml` seed 7 的 4 個 `input/` 檔 sha256 與 v0.1.0 相同 | `ZeroErrorsMatchV01` |
| 錯誤率 | 量到的錯標率、鹼基錯誤率在設定值 4 SE 內；switch 數在 Poisson 4 SE 內；`obs_hp` 反轉 = read 中點前 switch 數為奇數 | `test_errors.py` |
| 錯誤流到 pair | base error 讓 s4×s6 出現 n11；錯標讓 s3×s4（HP1）出現 n01，但 s4×s6 的 n11 仍為 0；switch 讓 s3×s4（HP1）出現 n01 | `ErrorsReachPairs` |
| 隨機樹 vs cohort | 直線比例、purity、2:1／2:0 early 比例、subclonal CN 量吻合；突變遺失高於 TRACERx 嚴格下限；deletion 型遺失偏高 | `tools/random_tree_validation.py` |
| PPC vs 真實 HCC1395 | split-HP、跨越 read、HP 深度吻合；有 het map 時，位點間 tag 比例的分布與聚集也吻合（SD 0.248 vs 0.250）；depth 過度離散、< 1 kb 同 HP 聚集（kataegis）不吻合；mistag 0.025 重複計算 | `lab_report/2026-10-26_longbulksim_ppc/` |
| caller 漏抓 | alt = 0 不會被 call；VAF 固定時 depth 高較易被 call；DeepSomatic 比 ClairS 敏感；漏掉的 SNV 不在任何輸入檔；偵測數符合曲線期望值；`none` 保留全部 | `test_caller.py` |
| 參數模式 | clone 數與樹形照設定；CCF 規則；truncal 比例；gain 比例；無 WGD 時沒有 loss 類；比例總和 > 1 時報錯；CLI 端到端 | `test_param_tree.py` |
| het map 規則 | 不覆蓋 het → 不標；跨 PS block → 不標；end 不含；只收 phased 位點；`phased_fraction` 不影響輸出 | `test_het_map.py` |

read span 分布：`longbulksim/data/hcc1395_ont_t50_n00_read_span.tsv`，由 `tools/measure_read_span.py` 從 HCC1395 ONT `t50_n00` 三個 40 Mb 區域量測（394,298 條 primary read；mean 13.1 kb，N50 21.4 kb）。

## 尚未做的事

- depth 過度離散。PPC 實測 depth VMR 3 vs 1。
- PS block 的 HP 方向。真實資料中，每個 block 的 HP1／HP2 方向是任意的；模擬的 `obs_hp` 在所有 block 用同一個方向。`pairs.tsv` 的 `ps_block` 仍是 segment。
- 隨機樹 spec 的座標沒有對應真實 callable 區域，所以用 het map 時 tag 比例偏低。
- 位點相關的錯誤。v0.2 的 base error 在位點與 read 之間獨立，但實測有長尾（HCC1395BL：1.2% 位點 > 5%）。
- switch 只影響 HP tag，不影響 PS block 切分（`ps_block` = segment）。
- mapping 誤差、read 跨越 segment 邊界。
- 多 sample。研究主軸是單一 bulk 樣本。
- WGD 以兩條 HP 各自 gain 表示，不是同一時間發生。
- 一個 segment 有三種以上 tumour CN 狀態時，`segments.tsv` 無法表示，會報錯。

決策紀錄見 [`DECISIONS.md`](DECISIONS.md)。
