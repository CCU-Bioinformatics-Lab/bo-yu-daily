# HG008 bulk 重建 vs 參考樹：規劃（2026-11-13）

本週主軸第 4 項（11-11 週會附錄 C）。**狀態：只有規劃，還沒跑。** D1–D4 帶到週會決定。

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

- 全基因組 43.4% 是 1+1；37.5% 是 0+1、14.1% 是 1+0（單拷貝 LOH），其他 < 5%。
- NIST 9,810 個 SNV：48.8% 在 1+1、28.6% 在單拷貝區、18.5% 不在 CNV PASS 區段內。
- 只用 1+1 時，分支 SNV 從 139 剩 96（大分支 88）。

**對 D1、D3 的意義〔推論〕：** D1 只選 NIST 不夠，要比深層分支就得 call 低 CCF 的 SNV；D3 選只用 1+1 會再少約三成 SNV，但不改變「深層分支沒有 SNV」這件事。
