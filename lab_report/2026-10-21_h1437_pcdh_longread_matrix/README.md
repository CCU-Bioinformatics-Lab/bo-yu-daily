# H1437 PCDH long-read epiallele 矩陣分群（B09 long-read 做法，2026-10-21）

## 結論

照 B09 的 long-read 做法重跑 H1437 後，**只有 tumor HP1 有明顯、穩定的 read 分群**：

- 矩陣大小固定時，tumor HP1 的結構強度（z_ff）中位數是 10.75。tumor HP2、normal HP1、normal HP2 只有約 4.5–5。
- tumor HP1 的最上層分岔約 4：6（minor fraction 中位數 0.375）。其他三組都只分出 1 條離群 read（0.05）。
- tumor HP1 的分群跨 window 一致：CpG 不重疊的相鄰 window 中，共有的 read 分群一致度中位數 1.00，隨機打散是 0.51–0.53。

這個型態較符合「HP1 有兩份 copy，各自漂移」，較不符合「有 subclone」：
- subclone 是一群細胞，應該讓 HP1 和 HP2 都分岔，而且比例相近。
- 實際上只有 HP1 分岔，比例接近 1：1，而 tumor HP1：HP2 的 read 數約 1.9：1。

這是推論，還沒有證明（見「解讀」）。

## 問題

`lab_report/2026-10-20_h1437_pcdh_hp_entropy/` 發現 tumor HP1 的 10-mer entropy 較高。entropy 只看單一 10-CpG window，分不出三種來源：
1. subclone。
2. 同一個細胞內多份 HP1 的差異。
3. 隨機 epimutation。

本實驗改用 B09 的 long-read 做法：依 HP 建大 window 的「read × CpG」矩陣，再分群。目的是看分群是否穩定，以及 HP1、HP2 是否同時分岔。

## 資料

- tagged BAM：`/big8_disk/boyu114/bam_save/h1437_pcdh_haplotag_2026-10-20/H1437_{tumor,normal}_full.PCDH.haplotag.bam`。
- 來源是 Google somatic data 的全深度 H1437 tumor／normal CRAM，用 longphase-s haplotag 標過。產生方式見 `lab_report/2026-10-20_h1437_pcdh_hp_entropy/`。
- 只用 5mC。

| 組別 | 有 HP 的 read 數 | 平均 read 長度 | 約略深度 |
|---|---|---|---|
| tumor HP1 | 1,355 | 27.6 kb | 51X |
| tumor HP2 | 708 | 28.2 kb | 27X |
| normal HP1 | 623 | 31.2 kb | 26X |
| normal HP2 | 572 | 32.8 kb | 25X |

對照 B09 的 PD6646：深度約 266X，read 平均 10.3 kb。我們的深度低很多，但 read 長很多。

## 做法

```bash
python3 tools/pcdh_longread_matrix.py <TAGGED_BAM> <LABEL> <OUT_TSV>               # greedy（接近論文）
python3 tools/pcdh_longread_matrix.py <TAGGED_BAM> <LABEL> <OUT_TSV> --fixed 150   # 固定 150 CpG × 20 read
python3 tools/pcdh_longread_matrix.py --selftest
python3 tools/pcdh_longread_summary.py <OUT_TSV ...>
python3 tools/pcdh_cluster_consistency.py <OUT_TSV ...>
```

### 和 B09 的對照

B09 沒有公開 code，Table S1 的 window 座標也只是圖片。下表依 B09 Methods 實作，標「我們」的是本 repo 自己的選擇。

| 步驟 | B09 做法 | 本實驗 |
|---|---|---|
| CpG call | modkit extract calls 預設 | MM/ML，機率 ≥ 0.8 → 1，≤ 0.2 → 0，其他算缺值（我們） |
| 分 HP | WhatsHap | longphase-s haplotag |
| window | semi-sliding，約 3 個 exon，平均 29.5 kb | 30 kb，每次移 15 kb（我們） |
| 建矩陣 | greedy：在保留足夠 read 的前提下，CpG 越多越好；每條 read 缺值 ≤ 20%、連續缺值 ≤ 5 | 同樣的缺值門檻；只找**連續**的 CpG 區間（我們） |
| read 數門檻 | 目標 > 50–100（266X）；KX004 是 > 25–50（121X） | ≥ 20（我們，配合較低深度） |
| CpG 數門檻 | 目標 > 50；正文寫至少 25 | ≥ 25 |
| 補值 | Hamming kNN，k = 3，多數決，不足時用欄多數 | 相同 |
| 分群 | Hamming 距離 UPGMA；記錄最上層兩群與 5 群的比例 | 相同 |
| 結構檢定 | 無（論文和真值樹比對） | 加了兩種 null（我們，見下） |

B09 有 single-cell colony 真值樹，我們沒有。所以本實驗加了結構檢定，取代真值比對。

### 結構檢定（我們加的，B09 沒有）

- **統計量**：補值前，每對 read 在共同 CpG 上的 normalized Hamming 距離，取其變異數。read 若分成幾群，距離會一大一小混在一起，變異數就變大。
- **null 1（column permutation）**：每個 CpG 欄內打散 read 的值，缺值位置不動。這會破壞 read 內 CpG 之間的連鎖。
- **null 2（fixed row/column sums，curveball）**：保留每條 read 和每個 CpG 的甲基化總數，只交換組合。這也排除了「每條 read 整體偏高或偏低」造成的假結構。結果以這個 null 為主（z_ff、p_ff）。

模擬自我檢查（`selftest.txt`，20 read × 200 CpG，3% call 錯誤、6% 缺值）：

| 模擬情境 | z_col | z_ff |
|---|---|---|
| CpG 互相獨立 | 0.4 | 0.4 |
| 只有 per-read 偏移，沒有 clone | 4.7 | −2.4 |
| 單一 clone | 0.1 | 0.2 |
| 兩個 clone，70／30，10% CpG 不同 | 12.6 | 13.9 |
| 兩個 clone，50／50，5% CpG 不同 | 6.4 | 5.9 |

null 1 會把 per-read 偏移誤判成結構，null 2 不會。兩種 null 都抓得到真的 clone。

### 矩陣大小的混淆

greedy 會把每個矩陣推到剛好 20 條 read，再盡量放大 CpG 數。tumor HP1 較深，所以矩陣較大：中位數 380 CpG，其他組約 190–218。矩陣越大，檢定力越強。所以另外跑 `--fixed 150`：每個矩陣固定 150 個 CpG，隨機取 20 條 read。主要結論以 fixed 結果為準。

## 結果

### 結構強度

`--fixed 150`（`summary.fixed150.txt`）：

| 組別 | window 數 | 甲基化中位數 | z_col 中位數 | z_ff 中位數 | p_ff ≤ 0.01 的 window | 最上層 minor fraction |
|---|---|---|---|---|---|---|
| tumor HP1 | 48 | 0.52 | 12.96 | **10.75** | 94% | **0.375** |
| tumor HP2 | 30 | 0.50 | 5.91 | 5.01 | 80% | 0.050 |
| normal HP1 | 31 | 0.65 | 8.07 | 4.53 | 74% | 0.050 |
| normal HP2 | 25 | 0.71 | 7.34 | 4.57 | 80% | 0.050 |

同一 window 配對比較 z_ff：
- tumor HP1 對 tumor HP2：9.14 對 5.01，HP1 較高的有 25 / 30。
- tumor HP1 對 normal HP1：11.12 對 4.53，tumor 較高的有 25 / 31。
- tumor HP2 對 normal HP2：5.48 對 4.57，tumor 較高的有 13 / 21。

greedy（`summary.greedy.txt`）的方向相同：tumor HP1 的 z_ff 是 32.10，其他三組是 6.0–6.9；minor fraction 是 0.350，其他是 0.05–0.10。

### HP1 與 HP2 是否同時分岔（tumor，fixed）

- 兩條 HP 都有的 window 有 30 個。
- minor fraction ≥ 0.25 的 window：HP1 有 25 個，HP2 有 4 個。
- 同一 window 中，HP1 和 HP2 的 minor fraction 差 ≤ 0.1 的只有 5 / 30。

### 跨 window 一致性（`consistency.*.txt`）

只比較 CpG 區間不重疊的相鄰 window。重疊的區間共用資料，一致度會被高估。

| 組別 | greedy：window 對數 | 一致度（打散） | fixed：window 對數 | 一致度（打散） |
|---|---|---|---|---|
| tumor HP1 | 8 | **1.00**（0.53），8 對都 ≥ 0.9 | 6 | **1.00**（0.51），6 對都 ≥ 0.9 |
| tumor HP2 | 13 | 0.71（0.55） | 3 | 0.67（0.69） |
| normal HP1 | 11 | 0.87（0.62） | 4 | 1.00（0.61） |
| normal HP2 | 10 | 0.89（0.68） | 3 | 0.59（0.63） |

每對 window 共有的 read 中位數只有 7–13 條。

## 解讀（分析推論）

- **tumor HP1 有真的 read 分群。** 它在保留 read 與 CpG 總數的 null 下仍顯著，而且在不重疊的 CpG 區間上分法一致。所以這不是單一 CpG 的隨機錯誤，也不是 per-read 偏移。每條 read 帶著一個跨數十 kb 一致的「身分」。
- **這個型態較支持「HP1 有兩份 copy」：**
  - 只有 HP1 分岔，HP2 沒有。subclone 是一群細胞，兩條 haplotype 都會累積 epimutation，所以應該兩條都分岔，比例也相近。
  - HP1 的分岔約 4：6，接近 1：1。tumor HP1：HP2 read 數約 1.9：1，AF 峰值 0.6–0.7。這兩點都符合「HP1 有 2 份，HP2 有 1 份」，而且每份 HP1 各貢獻約一半的 HP1 read。
  - 推論的情境是：HP1 先複製，兩份 copy 之後各自累積 epimutation，變成兩種 barcode。
- **還不能排除 subclone。** 如果 subclone 只在 HP1 上累積較多 epimutation，也會看到類似型態。例如 HP1 甲基化較低，變動可能較活躍。這個情境較不簡約，但沒有被排除。
- **normal 也有弱結構**（z_ff 約 4.5，約 75–80% 的 window 顯著）。可能的原因：normal 細胞株本身是寡克隆、call 錯誤在 read 內局部相關，或其他技術因素。所以判讀要以 normal 為基準，看 tumor 比 normal 高多少，不能只看 p 值。
- **對建樹的意義**：若 HP1 的分群來自兩份 copy，這是同一細胞內的 copy 差異，不是細胞之間的 lineage。這時 PCDH barcode 在 H1437 上反映的是 CN 事件，不能直接當成 subclone 證據。

## 限制

- 深度低。矩陣只有 20 條 read。跨 window 檢查中，每對只有 7–13 條共有 read，window 對數也只有 3–13 對。
- read 數門檻、window 大小、只找連續 CpG 區間，都是我們的選擇，不是 B09 原設定。
- 結構檢定是我們加的，B09 沒有。null 2 只控制 read 與 CpG 的總數，不控制 read 內局部相關的 call 錯誤。
- UPGMA 的最上層分岔常常只切出 1 條離群 read（minor 0.05）。所以 minor fraction 低不代表沒有結構，要搭配 z_ff 看。
- PCDH 區的 CN 沒有實測，「HP1 有 2 份」只來自 read 數比例與 AF。
- phasing 錯誤也可能讓 HP1 混入 HP2 的 read。不過 normal 的 HP1 沒有分岔，而且每條 read 平均約 28 kb，蓋到很多 het SNP，所以這個可能性較低。這點沒有直接檢查。
- 只做 H1437 一株。

## 下一步

1. **用 somatic SNV 檢查。** PCDH 區有 24 個 PASS somatic SNV。若某個 SNV 在 HP1 上只出現在約一半的 read，檢查這些 read 是否剛好落在同一個甲基化群。若是，可以支持「兩份 HP1 copy 在複製後各自累積變異」。
2. 查 H1437 在 chr5q31 的 haplotype-specific CN（例如用 longphase-s 或其他 CN caller），確認 HP1 是否有 2 份。
3. 對 HCC1954 做同樣的檢查。

## 檔案

| 檔案 | 內容 |
|---|---|
| `H1437_{tumor,normal}_full.greedy.tsv` | greedy 矩陣，每個 window × HP 一列 |
| `H1437_{tumor,normal}_full.fixed150.tsv` | 固定 150 CpG × 20 read |
| `*.clusters.tsv` | 每條 read 在各 window 的 UPGMA 群（2 群與 5 群） |
| `summary.{greedy,fixed150}.txt` | `tools/pcdh_longread_summary.py` 輸出 |
| `consistency.{greedy,fixed150}.txt` | `tools/pcdh_cluster_consistency.py` 輸出 |
| `selftest.txt` | 兩種 null 的模擬自我檢查 |

主表欄位：`cpg_from`／`cpg_to` 是矩陣實際用的 CpG 區間；`dist_var` 是統計量；`z`／`p_perm` 用 null 1；`z_ff`／`p_ff` 用 null 2（200 次）；`top_minor_frac` 是最上層分岔較小那群的比例；`k5_fracs` 是 5 群的比例。

## 相關實驗

- `lab_report/2026-10-20_h1437_pcdh_hp_entropy/`：分 HP 的 10-mer entropy。
- `lab_report/2026-10-20_hcc1395_pcdh_entropy/`：10-mer 指標和 B09 做法的差異。
