# OUTLINE_v5 審查摘要（2026-10-19）

兩位審查者：邏輯漏洞審查者、生物資訊教授。兩位都判「不通過」。
已用 `research/literature/paper_categories.tsv` 核對下列事實；修改結果見 `OUTLINE_v5.1.md`。

## 必改（兩位都指出，或事實錯誤）

| # | 頁 | 問題 | 修法 |
|---|---|---|---|
| 1 | P3、P9 | 判準不一致。P3 說 1 篇「有」，P9 說「不存在」。B04 在 TSV 是 `partial`。P3「有」的 11 篇混了 benchmark_truth 2、reference_tree 7、partial 2 | P3 改四欄：驗證用真值／局部佐證／只有參考樹／無。標題改「0 篇同時有」 |
| 2 | 判準 | 「拿 sc 樹驗證建樹」只有 M01、M06 符合；A01–A05、B03、R01 只建參考樹 | 判準分三級，寫進 BRIEF |
| 3 | P4 | 列入條件沒有一致套用：PhyClone 無特徵卻列入 | 列入條件改成「有觀測到的 long-read 或 read 層級 phasing 特徵」，逐篇套用。PhyClone 改為對照列 |
| 4 | P4 | 「有／無」裝不下「局部」「只在程式碼」 | BRIEF 定義：局部、只在程式碼、只做驗證，一律算「無」，細節放講稿 |
| 5 | P5 | 「計數層級沒有同 read 共現」錯。TreeClone 模擬產生同 read 配對計數；Pharming 把 SNV 隨機放到 haplotype | 改成「沒有 read 序列，所以沒有 HP tag 與 phase block」 |
| 6 | P5 | 二分法漏了一層：MEDICC2 只模擬拷貝數 profile | 改三層：事件層、計數層、read 層 |
| 7 | P5 | 「依二項分布抽」無出處 | 改成「抽 read 數」 |
| 8 | P7 | A02 是肺癌（NSCLC），不是卵巢癌。A03 也是 single-nucleus 標靶；Strand-seq 是全基因體 | 改兩組：標靶 panel（R01、A03、A05）、淺層全基因體（A01、A02、B03、M06、A04） |
| 9 | P7 | 「真值樹」措辭太強；M06 的 bulk 是 DLP pseudobulk，不是另一批定序 | 標題改「多半只是參考樹」 |
| 10 | P8 | H01 在 TSV 是短讀，不應列入長讀表；B03 有 ONT 卻漏列 | P8 依 `long_read_role` 列；H01 刪除 |
| 11 | P8、P9 | 子株混合只知道組成，做不出真值樹 | 改成「可驗證 CCF 與 purity，不能驗證樹形」 |
| 12 | P5、P9 | 結論寫在查核前，沒附篇數 | 已查：有模擬 7 篇；read 層 1 篇；產生長讀 0 篇 |

## 應改

- P4 的 B04 列：挑樹的病人（S14）與做 scDNA 的病人（S8、S20）不同；scDNA 結果是 CN 分群，不是演化樹。放講稿。
- P6 補 PhaseTools 定相一步；「可改成長讀版」是推論，移到講稿。
- P6 講稿的長讀版難點（教授推論）：read 要先整條指派給一個 clone，再放上該 clone 全部突變，同 read 共現的真值才對；haplotype 切分要用 trio，不能用 longphase 自己產生真值；深度要夠；BAMSurgeon 對 ONT 支援不明；hs37d5 要轉 GRCh38。
- 段落橋接：P4→P5、P6→P7 各補一句。
- R01 在選文窗口外，P3 講稿說明。

## 黑話

頁面與講稿不放論文代號。第一次出現要白話解釋：HP、PS（phase block）、CCF、SV、DLP+、Tapestri、Strand-seq、HG002、VCF。模擬器名（TSSB、FS-CRP、Pairtree、CONIPHER、BAMSurgeon）改白話，只在講稿提一次。

## 待查核答案（教授查得）

1. 22 篇都沒有產生長讀的模擬。SMC-Het 只把長讀列為未來工作。
2. single-cell 樹種類：A01 CN 樹；A02 SNV 樹；A03 SNV＋刪除 panel 樹；A04 SV＋haplotype CN 人工樹；A05 SNV 樹（20 基因）；B03 CN 細胞樹；R01 SNV clone 樹。細胞數見 v5.1 P7。
3. 資料存取：受控 A01–A04、B04、R01、M06；MTA B03 的 ONT；公開 A05、B01、M01（只有計數）；M07 在 EGA（條件未查）；H01 accession 未列；M02、M04、M05 無資料。（第二輪更正：「沒有一篇公開 ONT BAM」不成立；B01 的 ONT 可下載。）
4. PhyClone 的四種模擬器都是計數層，只輸出 ref／alt 計數。

# 第二輪審查（OUTLINE_v5.1，2026-10-19）

兩位都判「通過（附修改建議）」。修入 `OUTLINE_v5.2.md`：

- 判準補三條：只做驗證不算有特徵（平台算短讀）；「同 read 共現」含 SV 斷點；「BAM 可下載」照規則第 3 條，受控／協議／只有計數算「無」。
- P4：刪單細胞突變過程研究列，改 7 篇；PhyClone BAM 可下載改無。
- P6：頁面改論文描述「植入特定 haplotype 的 read 池」；「真值檔記錄 haplotype」移講稿並標推論。
- P7：「2 篇」改「2 棵」，講稿對應 P3 的 2 篇；M06 改為前人淺層全基因體 clone 樹、評分用 360 顆 scRNA；A03 補 16 位病人；A04 補 8 位病人。
- P8：只做驗證的兩篇放最下一行；頁面改「可下載的 ONT 只有細胞株與小鼠子株」。
- P9：「最接近的那篇」才是只用長讀事後挑樹。
- 新增用詞首次出現頁表；講稿移除代號。
