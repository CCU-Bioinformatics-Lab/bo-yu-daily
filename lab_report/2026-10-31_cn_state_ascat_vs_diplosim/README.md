# CN 狀態分布：ASCAT（真實 HCC1395）vs diplosim `--prop-pos-lost 0.45`（2026-10-31）

問題：只調 `prop_pos_lost` 無法讓 PPC 第 ③ 類 4 項同時進入範圍。HCC1395 和 diplosim 的 CN 差在哪種狀態？

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論；〔程式〕＝讀程式得到。

## 1. 結論

- **diplosim 只產生 5 種 CN 狀態：(1,0)、(2,0)、(2,1)、(3,1)、(4,2)**〔實測〕。每個位置最多一個 CNA 事件，而且預設沒有 WGD〔推論；`diplosim/src/params.rs:77` `clonal_wgd: false` 是程式〕。
- **LOH 的比例相同，但種類不同。**
  - diplosim 的 LOH 有一半是 deletion LOH (1,0)：24.3%。真實只有 2.3%〔實測〕。
  - 真實有 20.7% 是「LOH 之後又 gain」，例如 (3,0)、(4,0)、(5,0)、(6,0)。diplosim 是 0〔實測〕。
- **diplosim 沒有 total CN ≥ 5。** 真實有 15.7%。平均 total CN 是 真實 3.25、diplosim 2.38〔實測〕。
- **multiplicity 2 以上：** 真實 43.9%，diplosim 17.7%〔實測，粗估〕。
- 這能解釋為什麼調參數不夠〔推論〕：
  - (1,0) 位點只有一半 depth，會讓 depth 變異÷平均偏高。
  - 真實的 LOH 位點多半 copy 較多、multiplicity 較高。這會影響「SNV 在 depth 較少那條 HP」。

## 2. 資料與做法

```bash
python3 -I tools/cn_state_ascat_vs_diplosim.py /tmp/<scratch>   # 約 1 分鐘
```

- 真實：PPC 的 31,595 個 ClairS SNV 中通過 alt ≥ 3、VAF ≥ 0.08 的位點，CN 取自 `lab_report/2026-10-30_ascat_hcc1395_5khz/tables/snv_cn.tsv`。
- 模擬：diplosim 0.45，40 個 seed（35 個成功），n_clones 2–8，過同樣的門檻。CN 用 bulk 的 `CN_A`、`CN_B` 四捨五入。
- multiplicity 粗估：round(VAF × total CN)，兩邊同一公式（purity 1）。

## 3. 結果

| 狀態 (total, minor) | ASCAT | diplosim 0.45 |
|---|---:|---:|
| (2,0) | 0.272 | 0.233 |
| (3,1) | 0.209 | 0.321 |
| (4,2) | 0.129 | 0.152 |
| (3,0) | 0.123 | 0 |
| (4,0) | 0.050 | 0 |
| (5,1) | 0.048 | 0 |
| (5,2) | 0.037 | 0 |
| (1,0) | 0.023 | **0.243** |
| (2,1) | 0.021 | 0.052 |
| 其他（total ≥ 4 的組合） | 0.088 | 0 |

| 摘要 | ASCAT | diplosim 0.45 |
|---|---:|---:|
| LOH（minor = 0） | 0.502 | 0.475 |
| total = 1 | 0.023 | 0.243 |
| total ≥ 5 | 0.157 | 0 |
| 平均 total CN | 3.25 | 2.38 |
| multiplicity ≥ 2 | 0.439 | 0.177 |

## 4. 限制

- ASCAT 的 ploidy 3.06 可能偏高，total CN 可能整體多 1（README of ASCAT run §5）。但「LOH 後又 gain」和 (1,0) 很少這兩點，不受尺度影響〔推論〕。
- 模擬的 subclonal CN 會得到小數，四捨五入成整數狀態。
- multiplicity 是從 VAF 粗估，含 binomial 雜訊。

## 5. 後續：同位置多次 CNA（`prop_pos_second_cna`）與 `--loss-events cnloh_B`（2026-10-31）

都搭配 `--prop-pos-lost 0.45`，約 35 個 seed。指令：`python3 -I tools/cn_state_ascat_vs_diplosim.py <tmp> --prop-pos-lost 0.45 [--loss-events cnloh_B] --prop-pos-second-cna V`。

| 狀態／摘要 | ASCAT | second 0.5 | cnloh_B＋second 0.3 | cnloh_B＋second 0.5 |
|---|---:|---:|---:|---:|
| (2,0) | 0.272 | 0.246 | 0.399 | 0.353 |
| (3,1) | 0.209 | 0.190 | 0.247 | 0.187 |
| (3,0) | 0.123 | 0.082 | 0.082 | **0.124** |
| (4,2) | 0.129 | 0.096 | 0.122 | 0.096 |
| (4,0) | 0.050 | 0.026 | 0.016 | 0.042 |
| (5,2) | 0.037 | 0.037 | 0.027 | 0.039 |
| (5,1) | 0.048 | 0.006 | 0.004 | 0.010 |
| (1,0) | 0.023 | 0.184 | 0 | 0 |
| (2,1) | 0.021 | 0.064 | 0.053 | 0.053 |
| LOH | 0.502 | 0.544 | 0.500 | 0.535 |
| total ≥ 5 | 0.157 | 0.082 | 0.051 | 0.106 |
| 平均 total CN | 3.25 | 2.69 | 2.84 | 3.04 |
| multiplicity ≥ 2 | 0.439 | 0.216 | 0.262 | 0.276 |

〔實測〕cnloh_B＋second 0.5 最接近：(3,0)、(4,0)、(5,2) 幾乎相同，平均 CN 3.04。剩下的差距：(2,0) 多 8 個百分點、(5,1) 少、multiplicity ≥ 2 只有一半。
