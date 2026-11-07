# HG008：從 8 株 clone 重建演化樹，並和 diplosim 對照（2026-11-07）

問題：HG008 能重建出可信的克隆結構嗎？`diplosim` 能模擬出類似的樹嗎？

真值來源：沒有演化真值，這是細胞株的量測和本實驗的推論。讀長：clone 是 PacBio Revio；獨立檢查用的 119 顆單細胞是 UG100 short read（單細胞例外）。輸入：NIST 公開的 8 株 DeepSomatic、PURPLE、CNVkit 結果。生成方法：見下方腳本。

用到的會議：2026-11-04（決議 2、未決事項 2、3）。標記：〔實測〕本實驗計算；〔推論〕本檔推論。

**狀態：主架構已有單細胞支持，末端還沒有驗證。** 見 `../2026-11-07_hg008_sc_check/`。除了 3E4 的 7 株、{SC14, SC24, SC28, SC9}、{SC14, SC28} 這三層有支持；{2D6, 2E6} 只有部分支持；{SC24, SC9}、SC6 的位置和多數 private 枝沒有驗證。

## 目前的樹〔推論〕

```text
├─ 3E4
└─ 其餘 7 株（127 個 CN 乾淨的 SNV，17 條染色體）
   ├─ SC6
   └─ 其餘 6 株（4 個 SNV，2 條染色體，最弱）
      ├─ 2D6, 2E6（31）
      └─ SC14, SC24, SC28, SC9（14）
         ├─ SC14, SC28（68）
         └─ SC24, SC9（17）
```

主設定是 VAF ≥ 0.25、QUAL ≥ 20。五種門檻設定選出的分枝都相同（`tables/clades_*.tsv`）。CN 乾淨是指缺 SNV 的株，拷貝數不低於帶 SNV 的株，而且還保有兩條單倍型。

## 目前的結果〔實測〕

- **SNV 相容性：** CN 乾淨、由 2–7 株共有的 301 個 SNV 中，261 個落在這棵樹上（`tables/tree_summary.tsv`）。
- **和 `diplosim` 對照：** 從較大的樹抽 8 葉時，Colless 13（第 87 百分位）、末端枝比例 0.85（第 94）、內部／末端枝長度比 0.24（第 6）、末端枝變異係數 0.38（第 3）（`tables/diplosim/comparison.tsv`）。HG008 只有一棵樹，所以這只代表不矛盾。
- **拷貝數不完全符合這棵樹：** chr5 157–181 Mb 和 chr12 6–23 Mb 的型態不符，PURPLE 和 CNVkit 都看到。

## 失敗和修正

- **第一次的比法不公平：** 沒有合併單子節點，HG008 看起來明顯偏離 `diplosim`。合併並抽 8 葉後，差距大多消失。
- **低 QUAL 的假 call：** 衝突模式的 QUAL 中位數約 6–8，真實分枝約 36。門檻由 truncal SNV 的分布決定。
- **PURPLE 不分辨單倍型：** 兩株都是 2+0 時可能留下不同單倍型，所以規則收緊為缺 SNV 的株要有 minor ≥ 1。

## 限制

- **批次混淆：** 2D6、2E6 同屬 p14 批，SC14、SC24、SC28、SC9 同屬 p19 批。單細胞排除了 4 株分枝是批次假象，但 {2D6, 2E6} 只有部分支持。
- **和 `diplosim` 的枝長比較要保守看：** 8 條 private 枝大多沒有單細胞支持，所以末端枝比例和變異係數的證據比樹形弱。
- **沒有原始 read：** VCF 只有 PASS call，所以「沒有 call」和「沒有突變」無法分開。
- **`branch_cn_events.tsv`、`branch_hp_split.tsv`、`mutation_loss.tsv`、`subclone_cn_timing.tsv`：** 來自 `tools/hg008_clone_events.py`，它用 `snv_patterns.tsv`，沒有 QUAL 過濾。
- **`diplosim` 的拷貝數沒有比：** `diplosim` 逐位置抽 CNA，沒有區段；預設只放在 truncal。

## 重跑

```bash
D=/big8_disk/boyu114/benchmark_data/GIAB/HG008
T=lab_report/2026-11-07_hg008_tree_rebuild/tables
python3 -I tools/download_hg008_clones_sc.py $D 6
python3 -I tools/hg008_clone_tree.py $D $T
python3 -I tools/hg008_tree_rebuild.py $D $T
python3 -I tools/hg008_clone_events.py $D $T
python3 -I tools/hg008_vs_diplosim.py $T diplosim/target/release/diplosim $T/diplosim 300
```
