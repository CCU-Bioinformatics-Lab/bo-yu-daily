# 交接：COLO829 的突變比例與事件驗證

日期：2026-11-06。接手前先讀 `CLAUDE.md`、`meeting_record/2026_11_04_meeting_summary.md`，再讀本檔與同目錄 `README.md`。

## 使用者要回答的問題

腫瘤的體細胞突變，是否偏向爸爸或媽媽其中一方？這會影響 `diplosim` 的「每個 SNV 獨立 50%」假設（11-04 會議 N2）。

使用者的決定：**HP1、HP2 就先當作爸爸、媽媽來看，不要再繞這點。** COLO829 有 phase 資料，所以請查它是不是真的偏向。實際親源沒有量，寫結論時要標明，但不要用這點迴避問題。

## 目前的答案

**COLO829 沒有證據顯示真的偏向。** 61:39 主要來自 LOH。

| 比法 | 結果 | 位置 |
|---|---|---|
| 原始 hap1:hap2（Sohn VCF） | 27,410 比 17,400（61:39） | `../2026-11-06_colo829_hap_snv_ratio/` |
| 扣掉超過 5 Mb 無 SNV 的片段 | 9.34 比 9.31 個／Mb | 同上 |
| 2:1 區，read 直接判斷（ONT R10，獨立資料） | 1,639 比 1,425（minor 46.5%） | 本目錄 |
| chr1p | 488 比 470 | 本目錄 |

2:1 區的小差距不能解讀成偏向：2 份那條在複製後目標多一倍，1 份那條的 VAF 也較低。

## 已確認的事件

- 約 765 Mb 只剩一條單倍型，都有多份（2、3、4 份）。
- 第 3 份 chr1p 在 der(1;10) 上：read 直接連接 chr1 和 chr10，等位基因落在 minor。
- 三批 COLO829 的 chr1p 不同：Sohn 約 0，PAO 約 0.3，R10 約 1。
- Y 染色體在 tumor 丟失。

## 不要再犯的錯

1. **不要把零 SNV 當成過濾假象。** 我犯過這個錯。Sohn 圖 S2B 顯示 `haplotype2-0000059` 真的沒有覆蓋度。
2. **hub 的 coverage bigWig 不分單倍型。** 論文把 read 投射到兩條，所以只反映總 CN。
3. **不要把不同批的 COLO829 當成同一份。** Sohn 的 VCF 和實驗室的 CRAM 核型不同。
4. **VAF 不是 CCF。** m × CCF ≈ VAF × 該單倍型份數，要分開寫假設。
5. **長度配對可能配錯。** 第一次把 chr16 配錯過；作者標明的配對才可靠。
6. **不要偽裝 User-Agent，也不要繞過網站的瀏覽器檢查。** PMC 的補充檔就被擋，要改走其他公開來源。
7. **短讀數字只當生物假說。** 不能當 `diplosim` 的預設值或驗證目標。HCC1395 仍暫停。

## 還沒做

依我建議的順序：

1. **補讀圖 S3–S12。** 尤其 S3D、S3E（chr1 的突變和拷貝）、S4（各區 VAF）。bioRxiv 連結格式：`https://www.biorxiv.org/content/biorxiv/early/2025/10/13/2025.10.10.681725/DC<n>/embed/media-<n>.pdf`。
2. **查「7 條零 SNV contig 全在 hap2」。** 看 Verkko 怎麼定 hap 標籤；機率約 1.6%。
3. **分開 2:1 區的早期和晚期突變，再比兩條。** 這才能回答 53.5% 比 46.5% 有多少來自複製後的目標差異。可以用 VAF：早期突變在 2 份那條的 VAF 應接近 0.67。
4. **用 2:2 區比同一 phase block 內的兩條。** 目前 2:2 區只判斷「接近各半」，沒有比較 block 內的計數。
5. **換樣本。** COLO829 只有一個細胞株。候選：HG008（共用副本 `/big8_disk/yungjen114/data/HG008`，還沒查親代資料）、CASTLE 細胞株。

先和使用者確認要不要做，不要一次全做。

## 資料與程式

| 內容 | 路徑 |
|---|---|
| Sohn VCF | `/big8_disk/boyu114/benchmark_data/colo829_t2t_sohn2026/somatic_snvs.vcf.gz` |
| 衍生資料（雜合位點、突變定相、覆蓋度抽樣） | `/big8_disk/boyu114/benchmark_data/colo829_t2t_sohn2026/derived/` |
| 實驗室 ONT | `/big8_disk/data/COLO829/ONT_R10/`、`/big8_disk/data/COLO829/ONT_PAO/`（只讀） |
| ClairS 突變 | `/big8_disk/data/COLO829/ONT_R10/ClairS_v0_4_1/snv.vcf.gz` |
| SV、CN 真值（hg19 座標） | `/big8_disk/boyu114/benchmark_data/COLO829/zenodo_3988185/` |
| 作者程式 | GitHub `StergachisLab/T2T-COLO829BLT-Manuscript`（`hCN/CBS_DNAcopy.qmd`、`hCN/plot_log2hcn.py`） |
| 論文全文（本機） | `research/literature/surveys/tumor_evolution_history_2026-11-05/fulltext_cache/E6-12.txt` |
| 工具 | `tools/colo829_event_evidence.py`、`colo829_junction_reads.py`、`colo829_event_summary.py`、`colo829_hap_snv_ratio.py` |

外部下載的檔案用 `python3 -I` 讀。腳本不要放在資料目錄。

## Git 狀態

- 分支 `diplosim-v1`。`a4e7828`、`7b5ddb0` 已 commit，**沒有 push**。
- 本次新增與修改（本目錄、舊紀錄的更正、工具、索引、網站）**還沒 commit**，等使用者要求。
- `daily/`、`report/2026_11_04_slides/`、`diplosim/docs/figs/diplosim_features_igv.png` 的變更不屬於這項工作，不要一起 commit。

## 網頁

- 學習網站：https://claude.ai/artifact/X9wunWVDa91z4Peqnps2AK （來源 `research/literature/surveys/tumor_evolution_history_2026-11-05/site/`，執行 `python3 build_site.py`）
- COLO829 圖：https://claude.ai/artifact/MTXJp1qQstYQuD7xwM1Rcd （來源 `../2026-11-06_colo829_hap_snv_ratio/explainer.html`，用 `tools/draw_colo829_hap_explainer.py` 產生）

兩者都是私人頁面。

## 回報方式

使用者希望繁體中文、白話、先講結論；看不懂時會要你換個說法。解釋事件先畫圖。模擬器改動要先列 2–3 個方案（M1），這次沒有改 `diplosim`。
