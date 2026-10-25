# longbulksim：long read bulk 腫瘤模擬器

輸入一棵 HP-aware clone tree spec。輸出一個 bulk ONT 樣本的 PhyClone 輸入、HP 計數、SNV pair 共現表，以及獨立的真值目錄。

v0.1 範圍：molecule 層計數。每條 read 是一個 molecule，屬於一個 lineage、一條 HP、一個 copy。不產生 FASTQ／BAM（`plan.md` §5.8.4 L2-R 留到之後）。

## 用法

```bash
cd longbulksim
python3 -m longbulksim specs/stress.yaml OUT --seed 1            # 壓力測試樹，200×
python3 -m longbulksim specs/typical.yaml OUT --seed 1 --depth 200
python3 -m unittest discover -s tests                            # 約 15 秒，18 個測試
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

## 輸出

| 路徑 | 內容 |
|---|---|
| `input/data.tsv` | PhyClone 8 欄。major／minor 取細胞最多的 tumour CN 狀態 |
| `input/data_hp.tsv` | 加上 HP 欄位，給 `tools/phyclone_hp.py`。`snv_hp` 由 tagged alt read 多數決，不是真值 |
| `input/segments.tsv` | root 狀態 A、另一狀態 B、真值 phi |
| `input/pairs.tsv` | `plan.md` §1.3 的 `PAIRS.tsv` 欄位，加 `distance`。只計 tagged read |
| `truth/` | `truth.tsv`、`truth_tree.tsv`、`clusters_truth.tsv`（欄位同 `tools/hp_truth_tree_to_phyclone.py`），`genome.json`，`reads.tsv.gz`（每條 read 的 lineage／HP／copy） |
| `manifest.json` | spec、seed、read span 來源、read 數 |

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
| 隨機樹 vs cohort | 直線比例、purity、2:1／2:0 early 比例、subclonal CN 量吻合；突變遺失高於 TRACERx 嚴格下限；deletion 型遺失偏高 | `tools/random_tree_validation.py` |

read span 分布：`longbulksim/data/hcc1395_ont_t50_n00_read_span.tsv`，由 `tools/measure_read_span.py` 從 HCC1395 ONT `t50_n00` 三個 40 Mb 區域量測（394,298 條 primary read；mean 13.1 kb，N50 21.4 kb）。

## v0.1 沒有做的事

- phasing 誤差（switch error、HP 錯標）。read 的 tag 一律等於真實 HP。依目前目標先不做。
- 定序錯誤、mapping 誤差、read 跨越 segment 邊界。
- 多 sample。研究主軸是單一 bulk 樣本。
- WGD 以兩條 HP 各自 gain 表示，不是同一時間發生。
- 一個 segment 有三種以上 tumour CN 狀態時，`segments.tsv` 無法表示，會報錯。

決策紀錄見 [`DECISIONS.md`](DECISIONS.md)。
