# HG008：加上同一條 read 的共現（C4），L111 能不能和 truncal 分開（2026-11-15）

**狀態：** 進行中。使用者 2026-11-15 直接決定（不帶週會）。

## 1. 問題

11-13 只用 read 計數（base、A1）時，L111（細胞比例 0.93）4 次都沒有和 truncal（1.0）分開（`../2026-11-13_hg008_bulk_rebuild/README.md`）。`../2026-11-15_hg008_snv_pairs/` 顯示 read 共現看得出 L111 在 truncal 下面。這一步把共現加進 haploclone，看 L111 能不能分成獨立的一群。

## 2. 設定（一次只改一件事：A1 → A1＋共現）

- SNV、計數、HP、purity：和 11-13 ONT 的 A1 完全相同（`/bip8_disk/boyu114/hg008_haploclone/input/data_hp.tsv`，5,816 個 SNV）。只多加 `segment_id` 欄（全部 1+1，同一個 segment `s1`）。
- `segments.tsv`：一列，`s1`，A、B 兩個狀態都是 HP1 1 份、HP2 1 份，phi 0。
- `pairs.tsv`（`build_pairs.py`）：
  - SNV 對：同一條染色體、距離 ≤ 100 kb、兩個 SNV 的 `snv_hp` 相同（不是 NA）。不用參考樹標籤篩選，因為真實使用時沒有標籤。
  - read：MAPQ ≥ 20，跨過兩個 SNV。read 的 HP 用 11-13 的規則：read 上距離 SNV ±20 kb 內至少 2 個 HG008-N 已定相的 germline het，≥ 70% 一致。只數 HP 等於這對 SNV HP 的 read。
  - pattern：1 ＝ alt，0 ＝ ref；其他鹼基不算。
- haploclone：`--hp-mode a1 --pairs pairs.tsv --hp-data data_hp.tsv --segments segments.tsv`，共現評分用預設（`--pair-eps 0.01`，權重 1）。其他和 11-13 相同：`-d binomial -b 1000 -n 3000 --num-chains 4`，seed 1、2。

## 2b. 第二個條件：共用比例的評分（2026-11-15 加，跑之前寫下）

- 依 `../2026-11-15_cooccurrence_sim_design/` §1，現行逐對評分預期會讓 L111 併回 truncal。使用者 11-15 決定照該文件 §6 的順序實作，第 1 步是評分。
- haploclone 新選項 `--pair-pool`（branch `pair-pool`）：同一對 node 之間的所有 SNV 對，先加總 read 數，再算一次 Beta 分數。預設不加時，輸出和原版相同（`cargo test` 全過，只有 4 個需要已刪除的 Python 版 PhyClone 原始碼的測試無法執行）。
- 其他輸入和設定與 §2 完全相同，只多 `--pair-pool`。輸出 `run_a1c4pool_h{1,2}`。判定同 §3。

## 3. 事先定的判定

- 用 11-13 的評分腳本 `../2026-11-13_hg008_bulk_rebuild/eval_hg008.py`，判定和 11-13 相同：
  - **主要：** L111 和 truncal 分開，而且 L111 所在群在 truncal 群下面（check 1）。
  - CCF：各層所在群的 CCF 和細胞比例差 ≤ 0.1（check 2）。
- 2 個 seed 都通過才算「分得出來」；只有 1 個通過算「不穩定」。
- 對照：11-13 的 A1（同一份資料，沒有共現）4 次都沒通過。

## 4. 執行與暫停（2026-11-15 18:05）

- 兩個條件都開跑：逐對評分（17:04 起）、`--pair-pool`（17:45 起）。
- **太慢，停掉。** 逐對評分每 100 次 iteration 約 47 分鐘，4,000 次約要 31 小時；`--pair-pool` 更慢。原因是 46,220 對 SNV 每次都要全部重算，而其中約 97% 來自沒有標籤的密集區（`../2026-11-15_cooccurrence_sim_design/` §4：多半是旁系同源序列造成的假訊號）。整體 01 read（13,124）多於 10 read（10,489），也表示這些 SNV 對在干擾。
- 使用者 11-15 同意停掉，先做 diplosim 的共現模擬。之後要重跑時，先用不看標籤的規則過濾密集區（例如 1 kb 內有 ≥ 5 個其他 SNV 的位點不用），規則要在跑之前寫下。沒有結果。
