# HG008 與 HCC1395／SEQC2 的獨立證據盤點（2026-11-06）

日期：2026-11-06。用到的會議：2026-11-04（議題 3、4，決議 2，未決事項 2、3）。

範圍：只讀 repo 既有文件、論文和資料目錄，沒有下載資料，也沒有新實驗。標記：〔論文〕〔repo〕〔實測〕（只指本 repo 既有報告的結果）〔推論〕。

## 結論

- **HG008 是唯一值得往下走的來源。** 它有 8 株單細胞衍生 clone（PacBio）和 119 顆單細胞。〔repo〕
- **HCC1395／SEQC2 不能驗證樹。** 它的樹由 bulk 推論，單細胞只有 CNV；而且主要是 short read，目前也暫停 HCC1395 的新實驗。〔論文〕
- **兩個來源都沒有完整的演化真值樹。** 最多只能驗證克隆結構和部分順序，不能證明完整的演化路徑。〔推論〕

## 各項證據

### HG008

真值來源：沒有演化真值，都是細胞株的量測。讀長見下表。公開。批次：bulk 和單細胞都是 p23。

| 證據 | 量了什麼 | 支持哪一層（N3） | 需求表 | 本機 |
|---|---|---|---|---|
| NIST small variant v0.4、SV／CNV v0.6 | truncal SNV、單倍型拷貝數 | 觀測特徵；部分 CN 事件先後 | 符合（以 long read 組裝為主），但只是 draft | 有 |
| 8 株 clone（2D6、2E6、3E4、SC14、SC24、SC28、SC6、SC9） | 每株 PacBio Revio、DeepSomatic、PURPLE、Severus | 克隆結構；部分分枝順序 | 符合 | 沒有 |
| 119 顆 PTA 單細胞（UG100，中位 23×） | 逐細胞 SNV | 克隆結構；巢狀關係 | **不符合 long read**，見「要決定的事」 | 沒有（VCF 64 GB、CRAM 4.8 TB） |
| 120 顆低深度 CNV（Ginkgo） | 「8 個」CNV 型態，README 的初步描述 | 克隆結構（只有 CN） | 不符合 long read | 沒有 |
| dGH 影像（p21、p53、p101） | WGD 細胞比例：9／40、28／40、20／20 | 演化路徑的局部時間序列（只有 WGD） | 不是定序資料 | 只有論文數字 |
| 其他 passage（例如 p2 ONT） | 不同代的 bulk | 可能看時間變化，還沒查 | 符合 | 沒有 |

**已有的結果，不必重算才知道方向。** `lab_report/2026-10-27_hg008_sc_tree_check/`（結果表還在，輸入的 clone 樹已刪）：〔實測〕

- truncal 枝：119／119 顆都帶。
- {SC9, SC14, SC24, SC28}：48 顆帶；{SC14, SC28}：16 顆帶，而且全在那 48 顆內。
- 8 條 private 枝：單細胞無法證實。
- chr10：同一段在不同 lineage 失去不同 haplotype，至少獨立發生兩次。這是推論。

**HG008 的限制：**

- clone 在 p14、p19 分離，bulk 和單細胞是 p23。clone 擴增時新增的突變要扣除。〔repo〕
- 8 株不等於 8 個遺傳 clone。〔repo〕`/big8_disk/yungjen114/data/HG008/USAGE_AND_LIMITATIONS.zh-TW.md`
- 119 顆單細胞不是已完成的 clone tree。PTA 有擴增錯誤和 dropout。〔repo〕
- 這是培養中的演化，不等於病人腫瘤。〔推論〕
- HG008 論文的前 200,000 字元（共約 230,000）沒有提到單細胞 WGS，也沒有每代突變率。〔論文〕WebFetch 摘錄。

### HCC1395／SEQC2（Fang 2021）

真值來源：沒有演化真值。讀長：主要是 short read，另有 PacBio 40×。公開。

| 證據 | 量了什麼 | 支持哪一層（N3） | 需求表 |
|---|---|---|---|
| Fig. 4a PhyloWGS 樹 | bulk 推論的 S1–S10 | 不是獨立證據；它本身是推論 | 不符合 long read |
| 10x scCNV（1,270 顆） | 細胞的 CNV 分群 | 克隆結構（只有 CN），不是 SNV 樹 | 不符合 long read |
| AmpliSeq、WES、PacBio 驗證 | 突變是否真實 | 觀測特徵（call set） | 只有 PacBio 符合 |
| purity titration | VAF 和 purity 的關係 | 觀測特徵 | 不符合 long read |

依 L4 排除這一欄不符合的項目，不再展開。HCC1395 的 call set 只當既有歷史參考。

### 會議裡的克隆數

- **Fig. 4a 畫了 8 個節點（S1、S2、S4、S5、S7、S8、S9、S10）。** S3、S6 低於 10%，沒畫，所以編號到 S10。〔論文〕PDF p. 7。
- **「五個克隆群」沒有對上。** 在 Fang 2021 的 PDF 文字搜尋 five，只看到定序分組和資料分組，沒有五個克隆。我沒有逐張看 Extended Data 的圖。
- **「六個克隆」也沒有對上。** 在 six 的搜尋結果中，只看到定序中心和 caller 等數量。

## 三層能驗證到哪裡〔推論〕

| 層 | 最好的證據 | 狀況 |
|---|---|---|
| 觀測特徵 | NIST benchmark、已有的 long read bulk | 夠用，但不能證明樹 |
| 克隆結構 | 8 株 clone，加上單細胞交叉檢查 | 可行，需要先取得資料 |
| 演化路徑 | clone 的巢狀關係、WGD 的時間序列、CN 事件前後的 multiplicity | 只有片段，沒有完整路徑 |

## 要決定的事

1. **單細胞能不能當驗證參考？** `CLAUDE.md` 要求驗證參考只用 long read，但 11-04 會議老師重視單細胞分群，所以有衝突。最新會議優先，但沒有明說可以用 short read 單細胞。建議問老師。
2. **HG008 的克隆結構，能不能當 `diplosim` 的驗證目標？** 這要先定義「像」是什麼，還有比較的單位。還沒有方案，屬於未決事項 3。

## 來源

- `research/literature/surveys/sc_longread_datasets_2026-10-26/fulltext.md` §1、§4
- `lab_report/2026-10-25_hg008_truth_tree_plausibility/`、`lab_report/2026-10-27_hg008_sc_tree_check/`
- `research/hcc1395_golden_tree_research/`（`02_tree_reconstruction.md`、`03_validation_evidence.md`、`07_branching_topology_paper_check_20260825.md`、PDF）
- HG008 組裝預印本：DOI 10.64898/2026.05.01.722316（WebFetch 摘錄）
- NCBI FTP `HG008/NIST/HG008-T_clones/`：2026-11-06 看到 `20240718p14/`、`20240805p19/` 兩個目錄
