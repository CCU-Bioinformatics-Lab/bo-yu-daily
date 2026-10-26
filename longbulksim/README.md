# longbulksim：long read bulk 腫瘤模擬器

輸入一棵 HP-aware clone tree spec。輸出一個 bulk ONT 樣本的 PhyClone 輸入、HP 計數、SNV pair 共現表，以及獨立的真值目錄。

範圍：molecule 層計數。每條 read 是一個 molecule，屬於一個 lineage、一條 HP、一個 copy。不產生 FASTQ／BAM（`plan.md` §5.8.4 L2-R 留到之後）。v0.2 加入觀測誤差：HP 錯標、phase switch、鹼基錯誤（見「觀測誤差」）。

## 用法

```bash
cd longbulksim
python3 -m longbulksim specs/stress.yaml OUT --seed 1            # 壓力測試樹，200×
python3 -m longbulksim specs/typical.yaml OUT --seed 1 --depth 200
python3 -m longbulksim specs/stress.yaml OUT --mistag 0.025 --switch-rate 1 --base-error 0.004
python3 -m unittest discover -s tests                            # 約 25 秒，27 個測試
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
phased_fraction: 0.859
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

read span 分布：`longbulksim/data/hcc1395_ont_t50_n00_read_span.tsv`，由 `tools/measure_read_span.py` 從 HCC1395 ONT `t50_n00` 三個 40 Mb 區域量測（394,298 條 primary read；mean 13.1 kb，N50 21.4 kb）。

## 尚未做的事

- 位點相關的錯誤。v0.2 的 base error 在位點與 read 之間獨立，但實測有長尾（HCC1395BL：1.2% 位點 > 5%）。
- switch 只影響 HP tag，不影響 PS block 切分（`ps_block` = segment）。
- mapping 誤差、read 跨越 segment 邊界。
- 多 sample。研究主軸是單一 bulk 樣本。
- WGD 以兩條 HP 各自 gain 表示，不是同一時間發生。
- 一個 segment 有三種以上 tumour CN 狀態時，`segments.tsv` 無法表示，會報錯。

決策紀錄見 [`DECISIONS.md`](DECISIONS.md)。
