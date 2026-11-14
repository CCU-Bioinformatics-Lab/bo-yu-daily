# HG008 bulk 重建 vs 參考樹：規劃（2026-11-13）

本週主軸第 4 項（11-11 週會附錄 C）。**狀態：第一輪重建完成（11-13）。** D1–D4 由使用者 11-13 直接決定（ClairS PASS、SNV 位點 haplotag、只用 1+1、ONT），見文末「重建」兩節。

**真值來源：** 沒有演化真值；參考是 8 株選殖株的樹（p14／p19，PacBio）加 119 顆單細胞（p23，short read，單細胞例外）。**讀長：** bulk 用 ONT 63× 或 PacBio 116×（p23）。**輸入：** 一個 bulk sample。**生成程式：** 本 repo `tools/`。

流程圖：`plan_flow_icons.png`（圖示版，給投影片；`python3 -I make_flow_icons.py` 產生 SVG／HTML，再用 Firefox headless 截圖）。R2 的比例條是 p23 單細胞 8／63／32／16 顆（共 119）；「重建」比例條是示意。

## 資源〔repo〕

| 資源 | 路徑 | 提供什麼 |
|---|---|---|
| tumor BAM（p23） | `/big8_disk/yungjen114/data/HG008/ONT/HG008.bam`、`PacBio/HG008.bam` | read 計數 |
| NIST somatic SNV v0.4 | `.../NIST/somatic-smvar_v0.4_20261006/GRCh38/*_somatic_tumornormal.vcf.gz` | 9,810 個單鹼基 SNV；INFO 有 `chrN_hap1／hap2`，FORMAT 有 TCN、TAC |
| NIST full_tumornormal | 同目錄 `*_full_tumornormal.vcf.gz` | 約 460 萬列，HG008-N 已 phase（`1|0`），可直接給 haplotag |
| NIST CNV v0.6 draft | `.../NIST/somatic-stvar-CNV_v0.6_20261006/GRCh38/` | 分 haplotype 的 CN、LOH |
| 8 株選殖株、119 顆單細胞 | `/big8_disk/boyu114/benchmark_data/GIAB/HG008/` | 參考樹形、p23 各分支細胞比例 |
| reference | `.../HG008/reference/GRCh38-GIABv3/` | 不能換成實驗室常用 GRCh38 |

## 待週會決定

| # | 問題 | 候選 |
|---|---|---|
| D1 | SNV 來源 | NIST benchmark（高信心、偏 truncal）／ClairS 配對 normal（要安裝、重跑）／ClairS-TO 現成結果（tumor-only，假 call 較多；列入只因已經跑好，11-13 更正）|
| D2 | 每個 SNV 的 HP | read haplotag 後計數（和 diplosim → haploclone 同口徑）／NIST 組裝的 hap 標籤（只當核對） |
| D3 | 用哪些區域 | 只用 1+1（和模擬驗證一致）／全部，帶 CN |
| D4 | 平台 | ONT 63×／PacBio 116×（較深，和選殖株同平台） |

## 風險〔推論〕

- 選殖株（p14／p19）和 bulk（p23）在第 13 代前就分開培養：選殖株只給樹形，組成要和 p23 單細胞比。〔repo〕`../2026-11-07_hg008_tree_rebuild/HOW_TREE_WAS_BUILT.md`
- NIST SNV 偏 truncal，subclone 的 SNV 可能很少。
- bulk 與選殖株共有的分支 SNV 只有數百個（選殖株 CN 乾淨、2–7 株共有的 301 個）。

## 先算的兩個數字（2026-11-13）〔實測〕

`count_nist_branch_cn.py` → `nist_branch_cn.txt`。分支分類沿用 `../2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv`（主設定）。

**NIST 名單在參考樹分支上的 SNV（CN 乾淨、2–7 株共有）：139 個，幾乎都在最上層一個分支。**

| 參考樹分支 | p23 單細胞 | 選殖株 SNV | 在 NIST | 在 NIST 且 1+1 |
|---|---:|---:|---:|---:|
| 7 株（除 3E4） | 111／119 | 127 | 126 | 88 |
| 2D6, 2E6 | 未驗證 | 31 | 2 | 2 |
| SC14, SC24, SC28, SC9 | 48／119 | 14 | 0 | 0 |
| SC14, SC28 | 16／119 | 68 | 0 | 0 |
| SC24, SC9 | 未驗證 | 17 | 0 | 0 |
| 各株 private | — | 3,593 | 0 | 0 |

- NIST 只抓到 111 顆細胞那一層；48、16 顆那兩層一個都沒有。〔實測〕
- 原因〔推論〕：NIST 名單來自 tumor 組裝（VCF header：VAF 由 HG008-T v3.4 assembly 的 contig 算出），組裝只代表多數細胞；CCF 約 0.4、0.13 的 SNV 進不了組裝。
- 所以只用 NIST，bulk 重建最多只能比「truncal vs 111 顆那層」一個分支，而且兩者 CCF 只差約 1.0 對 0.93，很難分開。要比到更深的分支，SNV 要從 read 直接 call（ClairS 配對 normal）。

**1+1 區比例**（NIST CNV v0.6 PASS，鋪滿 2,500 Mb）：

- 全基因組 43.4% 是 1+1；37.5% 是 0+1、14.1% 是 1+0（單拷貝 LOH），2+0 3.0%；兩條份數不同的 1+2 1.4%、2+1 0.5%（合計約 2%，投影片第 10 頁用）；其他 < 0.1%。
- NIST 9,810 個 SNV：48.8% 在 1+1、28.6% 在單拷貝區、18.5% 不在 CNV PASS 區段內。
- 只用 1+1 時，分支 SNV 從 139 剩 96（大分支 88）。

**對 D1、D3 的意義〔推論〕：** D1 只選 NIST 不夠，要比深層分支就得 call 低 CCF 的 SNV；D3 選只用 1+1 會再少約三成 SNV，但不改變「深層分支沒有 SNV」這件事。

## ClairS 從 read 直接 call（2026-11-13）〔實測〕

- 設定：ClairS 0.5.1（本機原始碼安裝），tumor ONT `HG008.bam`（63×，p23）配 normal `HG008-N-D.bam`（94×），model `ont_r10_dorado_sup_5khz_ss`，chr1–22、X。腳本 `/bip8_disk/boyu114/hg008_clairs_ont/run.sh`，約 2.4 小時。
- 15,137 個 PASS SNV；NIST 9,810 個裡抓回 8,886 個（90.6%）。
- `count_clairs_branch.py` → `clairs_branch.txt`：深層分支只多抓到一點（48 顆那層 6/14，16 顆那層 3/68）。

## 原始 read 逐點數 alt（2026-11-13）〔實測〕

`pileup_deep_clades.py` → `pileup_deep_clades.txt`（samtools mpileup，MAPQ ≥ 20，不濾 base quality）。目的：分出「read 裡有、但 ClairS 沒判 PASS」和「bulk 裡根本沒有」。

| 參考樹分支 | 位點 | ClairS PASS／LowQual／沒 call | 有 ≥2 條 alt read 的位點 | 合併 tumor VAF | 預期 VAF〔推論〕 |
|---|---:|---|---:|---:|---:|
| SC14, SC24, SC28, SC9（48 顆） | 14 | 6／4／4 | 14 | 0.141 | 約 0.20 |
| SC14, SC28（16 顆） | 68 | 3／9／56 | 50 | 0.057 | 約 0.07 |
| 2D6, 2E6（未驗證） | 31 | 3／2／26 | 10 | 0.051 | — |
| SC24, SC9（未驗證） | 17 | 0／0／17 | 0 | 0.001 | — |

- 預期 VAF = 單細胞比例 ÷ 2（假設 1+1、purity 1）：48/119 → 0.20，16/119 → 0.067。
- **48 顆、16 顆兩層的 SNV 在 bulk read 裡確實存在。** ClairS 漏掉多數，是偵測極限，不是突變不在 p23。
- **背景雜訊約 0.001**：SC24, SC9 的 17 個位點幾乎沒有 alt read，可當對照。16 顆那層的 0.057 高出約 50 倍。normal 的 alt read 合計：48 顆層 6、16 顆層 40、SC24,SC9 層 11（normal 約 94×，約每位點 0.006）。
- SC24, SC9 分支在 p23 bulk 裡看不到。可能是這個分支不在 p23，或分支本身不可靠（參考樹標「未驗證」）。
- 限制：每層只有 14–68 個位點；合併 VAF 不能說明單一位點。只查「已知位點」，等於先知道答案再去看；真正的 bulk 重建沒有這份名單。

**對 D1 的意義〔推論〕：** 深層分支的訊號在 read 裡有，但單一位點只有 2–10 條 alt read，一般 caller 判不出來。D1 的選項因此多一個問題：要不要降低門檻（例如收 LowQual），代價是假陽性變多。這留到週會。

## 重建：設定與事先定好的比法（2026-11-13，跑之前寫）

使用者 2026-11-13 直接決定 D1–D4（不帶週會）：**D1 ClairS PASS；D2 在 SNV 位點做 haplotag；D3 只用 1+1；D4 ONT 63×。**

**輸入**（`build_input.py`）：
- SNV：ClairS PASS 單鹼基 SNV，落在 NIST CNV v0.6 PASS 的 1+1 區段。
- 計數：自己從 tumor BAM 數（MAPQ ≥ 20），不用 ClairS 的 AF，讓 base 和 A1 用同一份計數。
- HP：NIST `full_tumornormal` 的 HG008-N 已 phase 的生殖系 het SNV。每條 read 看它蓋到的 het SNV（SNV 位點 ±20 kb 內），至少 2 個、且 ≥ 70% 同一邊，才算 HP1／HP2；其他算 unphased。`snv_hp` = alt read 多的那一邊。
- purity 設 1.0（細胞株，未實測）。另用 1+1 區 truncal SNV 的 VAF 中位數 × 2 核對。

**haploclone 設定：** 和模擬驗證相同。`-d binomial -b 1000 -n 3000 --num-chains 4`，seed 1、2；base 用 `data.tsv`，A1 用 `data_hp.tsv`。

**參考標籤**（只用來評分，不給 haploclone）：`../2026-11-07_hg008_tree_rebuild/tables/snv_classes_vaf0.25_qual20.tsv` 的 pattern。truncal ＝ 8 株都有；111 層 ＝ 2D6,2E6,SC14,SC24,SC28,SC6,SC9；48 層 ＝ SC14,SC24,SC28,SC9；16 層 ＝ SC14,SC28。

**事先定的比法：**
1. **主要：111 層有沒有和 truncal 分開。** 算「對上」要同時滿足兩件事：111 層 SNV 的多數落在一個 clone，而且這個 clone 和 truncal 多數所在的 clone 不同；這個 clone 是 truncal clone 的後代。
2. **CCF：** 每個參考層多數所在 clone 的 CCF，和單細胞比例比（1、0.93、0.40、0.13），差 ≤ 0.1 算對上。
3. **48、16 層：** PASS 裡只有 6、3 個，事先預期不會自成一群。只報告它們落在哪裡。
4. **沒有參考標籤的 clone：** 報告數量和 CCF。這些 clone 無法驗證，可能是 p23 才有的分支，也可能是假陽性。
5. **base vs A1：** 只有一個 sample，沒有 CI，只描述。兩個 seed 的差當雜訊大小。依模擬結果，預期樹形沒有差別。

**跑之前的預期〔推論〕：** truncal 和 111 層的 CCF 只差約 0.07，可能合成一群。這個結果事先就不確定。

### 輸入的實際內容〔實測〕

`build_input.py` 輸出在 `/bip8_disk/boyu114/hg008_haploclone/input/`（不進 repo）。

- ClairS PASS 落在 1+1 的 SNV：5,816 個，全部至少有 1 條 alt read。中位深度 54。
- 參考標籤：truncal 3,845、111 層 136、48 層 5、16 層 2、其他分支 182、不在選殖株名單 1,646。
- purity 核對：truncal VAF 中位數 0.482，× 2 ＝ 0.96，和設定的 1.0 接近。
- 77.2% 的 alt read 判得出 HP。`snv_hp`：HP1 2,432、HP2 2,428、判不出 956。
- 709 個 SNV 兩條 HP 都有 alt read。可能原因是定序錯誤或 phase 錯；A1 只用 `snv_hp` 那一邊和 unphased 的 read，另一邊的 read 完全不用〔程式〕`haploclone/rust/src/data/hp.rs:290-335`；判不出 HP 的 956 個，A1 對兩邊取平均。

## 重建結果（2026-11-13）〔實測〕

`eval_hg008.py` → `haploclone_eval.txt`。trace 在 `/bip8_disk/boyu114/hg008_haploclone/`（不進 repo）。每次約 50 分鐘（base）到 70 分鐘（A1）。

| 執行 | 樹（clone：CCF，SNV 數） | 111 層和 truncal 分開？ | 48 層 5 個落在 | 16 層 2 個落在 |
|---|---|---|---|---|
| base seed 1 | 0：0.96（5,267）→ 1：0.45（549） | 否 | clone 1（5/5） | clone 1 |
| base seed 2 | 0：0.96（5,295）→ 1：0.44（521） | 否 | clone 1（5/5） | clone 1 |
| A1 seed 1 | 0：0.97 → 1：0.59（264）、2：0.34（361），1 和 2 是兄弟 | 否 | clone 2（3/5） | clone 2 |
| A1 seed 2 | 0：0.97 → 1：0.44（519）→ 2：0.20（68） | 否 | clone 1（5/5） | 1、2 各 1 |

**對照事先定的比法：**
1. **主要（111 層分開）：4 次都沒有。** 111 層 136 個 SNV 有 128–133 個和 truncal 在同一群（CCF 0.96–0.97）。和跑之前的預期一致：CCF 只差約 0.07，分不開。
2. **CCF：** truncal 群 0.96–0.97（細胞比例 1.0）、48 層所在群 0.34–0.45（細胞比例 0.40），都在 0.1 內。16 層沒有自己的群，不算對上。
3. **48、16 層：** 48 層的 5 個 SNV 有 3–5 個落在同一個次群，CCF 接近 0.40。16 層只有 2 個 SNV，和預期一樣沒有自成一群。
4. **沒有參考標籤的 SNV：** CCF 約 0.45 的次群裡，大部分 SNV（453–476 個）不在選殖株名單裡（VAF 中位數 0.21）。它們可能是 p23 在選殖株分出去以後才長出來的突變，也可能是假陽性。這份資料分不出來。〔推論〕
5. **base vs A1：** base 兩個 seed 樹形相同（都是 2 群）。A1 兩個 seed 樹形不同：一次是兩個兄弟群（0.59、0.34），另一次是一條鏈（0.44 → 0.20）。SNV 對的關係一致率：base 兩個 seed 之間 0.945，A1 兩個 seed 之間 0.968，base 和 A1 之間 0.870–0.884。這個一致率被 truncal 的大群主導（約 90% 的 SNV），所以反映不出次群樹形的差別。

**能說明：** 從 ONT bulk 用 ClairS PASS 加 1+1 區，haploclone 能找回 truncal 群，以及一個 CCF 約 0.4–0.45 的次群；參考樹 48 層的 SNV 落在這個次群。**不能說明：** 111 層和 16 層能不能找回來，因為 111 層的 CCF 太接近 1，16 層在 PASS 裡只有 2 個 SNV。也不能說明 HP 有沒有幫助：A1 多分出一群，但兩個 seed 的樹形不同，這個差別無法驗證。

## PacBio 重跑（2026-11-14，跑之前寫）

使用者 2026-11-14 要求用 PacBio 重跑，只改 D4，其他設定和比法都不變。

- ClairS：tumor `PacBio/HG008.bam`（116×）配 normal `PacBio/HG008-N-D.bam`（68×），model `hifi_revio_ssrs`。腳本 `/bip8_disk/boyu114/hg008_clairs_pacbio/run.sh`。
- 輸入：`build_input.py --bam .../PacBio/HG008.bam --clairs .../hg008_clairs_pacbio/out/output.vcf.gz --sample HG008_p23_PacBio`。
- haploclone、評分：和 ONT 相同。
- 限制：tumor 變深，normal 變淺，平台也換了。結果和 ONT 不同時，分不出是哪一個造成的。

### PacBio 結果（2026-11-14）〔實測〕

ClairS PacBio：約 1.7 小時。PASS 11,238 個，NIST recall 91.0%（ONT 90.6%）。ClairS 有、NIST 沒有的 2,309 個（ONT 6,251 個）。深層分支：48 層 7/14、16 層 3/68，和 ONT（6/14、3/68）幾乎一樣。`clairs_branch_pacbio.txt`。

輸入：1+1 區 4,995 個 SNV，中位深度 107，purity 核對 1.00。標籤：truncal 3,871、111 層 137、48 層 5、16 層 2、其他分支 182、不在名單 798。兩條 HP 都有 alt read 的 SNV 153 個（ONT 709）。

重建：`haploclone_eval_pacbio.txt`。

| 執行 | 樹（clone 的 CCF，一條鏈） | 111 層 137 個落在 | 48 層 5 個落在 | 16 層 2 個落在 |
|---|---|---|---|---|
| base seed 1 | 1.00 → 0.56 → 0.30 | 1.00 群（136） | 0.30 群（5） | 0.30 群 |
| base seed 2 | 1.00 → 0.56 → 0.28 | 1.00 群（137） | 0.28 群（5） | 0.28 群 |
| A1 seed 1 | 1.00 → 0.90 → 0.55 → 0.24 | 1.00 群 89、0.90 群 48 | 0.24 群（4） | 0.24 群 |
| A1 seed 2 | 1.00 → 0.90 → 0.55 → 0.24 | 1.00 群 88、0.90 群 49 | 0.24 群（5） | 0.24 群 |

**對照事先定的比法：**
1. **主要（111 層分開）：4 次都沒有。** 但 A1 兩個 seed 都多分出一個 CCF 0.90 的群，111 層約 35%（48–49 個）落進去。這一群也收了 98–105 個 truncal SNV，比 111 層還多，所以不是乾淨的分開。base 沒有這一群。
2. **CCF：** truncal 群 1.00，對上。48 層所在群 0.24–0.30，細胞比例 0.40，**差超過 0.1，沒對上**（ONT 是 0.34–0.45，有對上）。原因〔推論〕：48 層和 16 層的 SNV 合在同一群，CCF 被拉低。
3. **48、16 層：** 7 個 SNV 合成同一個小群（28–40 個 SNV），在一個 CCF 約 0.56 的群下面。0.56 群裡大多是不在選殖株名單的 SNV（151–170 個），無法驗證。
4. **seed 穩定性：** 和 ONT 不同，PacBio 兩個 seed 的樹形相同（base 都是 3 群，A1 都是 4 群）。SNV 對關係一致率：base 兩個 seed 之間 0.987，A1 兩個 seed 之間 0.960，base 和 A1 之間 0.867–0.873。
5. **base vs A1：** 差別在兩個 seed 都重複出現：A1 多出 0.90 群，111 層 SNV 有約三分之一落進去。這是目前第一個「加 HP 後結構不同、而且方向接近參考樹」的觀察。但只有一個 sample、兩個 seed，0.90 群也混了更多 truncal SNV，不能說 HP 改善了重建。〔推論〕

**ONT vs PacBio：** PacBio 的樹比較穩、群比較多（一條 3–4 層的鏈，和參考樹的巢狀結構同方向），但 48 層的 CCF 反而沒對上。平台、tumor 深度、normal 深度同時改變，分不出是哪一個造成的。
