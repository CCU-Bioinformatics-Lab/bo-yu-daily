

######## USER: 幫我調查本repo研究目錄中這些論文的正常或是腫瘤輸入資訊有哪些，假設alt,ref reads,purity,copy number等，分別也各自輸出甚麼樹的拓樸?還是clone群數量等

--- ASSISTANT:
研究目錄裡共有 16 篇論文有逐篇筆記：5 篇方法論文（M01、M02、M04–M06）、10 篇應用研究（A01–A05、B01、B03–B05、B07），以及 R01 和 HCC1395 參考樹的論文。以下依這些筆記整理。

## 結論

- **同時用到 ref/alt reads、purity 和 CN，並輸出 clone tree 的只有 3 篇：** PhyClone、B04 的 PyClone-VI→ClonEvol 流程，以及 HCC1395 用的 PhyloWGS。
- **大多數方法不需要 normal 樣本的 reads。** matched normal 只用在上游 somatic calling。PhyClone 只要一個 `normal_cn` 數值。
- **purity 有三種處理方式：**
  - 外部給定：PhyClone。
  - 當成參數推論：TreeClone。
  - 當成 root normal clone 的比例：TUSV-ext、PhylEx。
  - single-cell 方法沒有 purity，它們把 normal cell 分到 root。
- **輸出分三類：**
  - clone tree：節點是 SNV cluster 或 clone。
  - cell tree 或 sample tree：葉是細胞、樣本或 subline。
  - 局部關係圖：沒有完整的樹。
- **clone 數也有三種決定方式：**
  - 推論出來：PhyClone、PhylEx、TreeClone。
  - 用 BIC 選：Pharming。
  - 使用者指定上限，或人工切 clade：TUSV-ext、A01 等。

## 1. 方法論文（M01–M06）

| 論文 | 輸入 | 輸出 |
|---|---|---|
| **M01 PhyClone** | 每個 SNV、每個 sample 的 `ref_counts, alt_counts, major_cn, minor_cn, normal_cn, tumour_content`（purity，外部給定且固定）。可加 cluster 檔。CN 只能是 clonal。沒有 normal reads。 | MAP 或 consensus 樹（Newick），含 SNV→node 和每個 sample 的 cellular prevalence。也輸出 posterior trace 和 topology report。clone 數由 CRP 推論。lost SNV 歸為 outlier。**不輸出 multiplicity** |
| **M02 TreeClone** | 同一 read 上兩個 SNV 的 8 類 read count（00/01/10/11/-0/-1/0-/1-）。只用 CN=2 區域，沒有 CN 輸入。purity 是參數 `w_t1`，可加資訊性 prior | clone 數 C（限在 Cmin–Cmax）、tree T、每個 clone 每個 pair 的 genotype Z，以及各 sample 的 clone 比例 w |
| **M04 Pharming**（scDNA） | 每個 cell 每個 SNV 的 var/total reads、每個 cell 每個 segment 的 haplotype-specific CN (x,y)，以及 SNV→segment 對應。沒有 purity，normal cell 分到 root (1,1) | clonal tree：每個 node 帶 segment CN 和 SNV 的 (w,z) multiplicity。也輸出 cell assignment、SNV loss 和 genotype 表。clone 數 k 由 BIC 選 |
| **M05 TUSV-ext** | 每個 sample 一個 VCF，內含 SNV、SV 和 CNV 的**平均 copy number**（不是 read count）。沒有 purity 輸入，normal 是 U 中的 root clone | `T.dot` binary tree、`C.tsv`（每個 clone 的 allele-specific CN 和 SNV/SV copy 數）、`U.tsv`（每個 sample 的 clone 頻率）。clone 數由使用者指定上限（約 ≤9），事後再合併 |
| **M06 PhylEx** | bulk 的 `b, d, major_cn, minor_cn`（TitanCNA），加上 scRNA 每個 cell 的 var/total reads。沒有 purity 和 normal CN | MAP tree 和 posterior samples、SNV→node、cellular prevalence、cell assignment。clone 數由 TSSB 推論 |

## 2. 應用研究：病人 single-cell（A01–A05）

| 論文 | 輸入 | 輸出 |
|---|---|---|
| **A01 卵巢 cfDNA** | DLP+ scWGS：HMMcopy 給 total CN，SIGNALS 給 haplotype-specific CN。cfDNA VAF 用樹推出的 CCF 校正 | MEDICC2 cell tree，clone 由人工挑 clade 定義。輸出 clone 頻率的時間變化 |
| **A02 SPRINTER** | scDNA 的 read depth（先校正 S-phase）、各 clone pseudobulk 的 SNV | HUNTRESS SNV tree。MEDICC2 CNA tree 固定用同一個 topology。MACHINA 推轉移路徑 |
| **A03 胰臟 snDNA** | Tapestri 每個 cell 的 25 個 SNV genotype＋8 個 SMAD4 amplicon 的 deletion 狀態。CN 從 amplicon depth 估。病理 purity 不進模型 | SCG 分出 7 群。clone phylogeny 由人工排序事件 |
| **A04 AML Strand-seq** | 每個 cell 的 read depth、strand 方向、染色體長度的 haplotype，再推出 SV | 人工整理的 clone 樹。分類結果：monoclonal 2 例、linear 3 例、branched 3 例 |
| **A05 MPAL** | DAb-seq 每個 cell 的 genotype（20 個基因的 panel） | SCITE mutation tree。clone 定義為同 genotype >10 顆細胞，14 名病人共 36 個 clone |

## 3. 應用研究：long-read／haplotype（B01、B03–B05、B07）

| 論文 | 輸入 | 輸出 |
|---|---|---|
| **B01 小鼠 melanoma（ONT）** | 每個 subline 的 bulk ONT SNV（DeepVariant，已扣 normal）。coverage ≤10 標為 missing。Wakhan CN 用 unphased 模式 | ScisTree subline tree（23 片葉、4 個 clade）。TreeHarmonizer 把 SNV/SV/CNA 放到固定樹的 edge 上 |
| **B03 SIGNALS** | DLP+ 的 total CN 和 haplotype block allele counts，推出 HSCN。ONT 只用來驗證 SV | sitka consensus cell tree，由 total CN breakpoint 建出。HSCN 之後才映射到 tips |
| **B04 肺癌 ONT** | short-read VAF＋FACETS 的 CN/purity，進 PyClone-VI 得到 CCF cluster。ONT 跨兩個 SNV 的 read 給 partial order。HP 指派門檻：一個 HP ≥3 條 mutant read、另一個 HP ≤1 條 | ClonEvol 候選樹，再用 long-read pair 篩選（S14 從 branched 改選 linear）。scDNA 只做局部驗證 |
| **B05 MEDICC2** | 每個 sample 或 cell 的 haplotype-specific 整數 CN profile。沒有 SNV reads。purity 和 ploidy 只在上游（Battenberg）用到 | NJ tree（葉是 sample 或 cell），加上祖先 CN、branch 事件和 WGD 判定 |
| **B07 Numbat** | scRNA 的 expression counts＋germline SNP allele counts＋population phasing | CNV segment、每個 cell 的 CNV genotype 機率、single-cell tree 和 clone |

## 4. 參考樹來源

| 論文 | 輸入 | 輸出 |
|---|---|---|
| **R01 McPherson 2016**（PhyClone HGSOC 真值） | WGS SNV reads、DeMix allele-specific CN 和 cellularity，用 Dollo-with-loss 建 sample tree。targeted deep-seq 用 PyClone 分群。single-nucleus 用 SCG genotype | clone tree：p2 有 6 個 clone（A–F）、p3 有 7 個（A–G）、p9 有 3 個。p3 保留 lost SNV，p2 的 truth 已移除 loss |
| **HCC1395 Fang 2021** | bulk WGS/WES 的 VAF＋local CN，進 PhyloWGS。single-cell CNV 只做驗證。**論文沒有公開完整的輸入表和參數** | branching tree：S1（MRCA）分成 S2 和 S8 兩支，共 S1–S10。S3、S6 低於 10%，圖上沒畫。節點標 CCF |

## 注意事項

- 以上內容來自各篇的 `README.md` 筆記。筆記本身已區分「論文描述」「程式實作」「推論」。我沒有回頭讀 PDF 原文。
- `methods_survey/README.md` 另有 46 個方法的總表，有「輸入」和「CN 處理」欄，但沒有「輸出」欄。其中只有 M01–M06 有逐篇筆記，所以上表只涵蓋這 6 篇方法。
- 和本 repo 最接近的資料型態是 bulk ONT＋HP＋purity＋CN。逐項對照最接近的是 M01（主體）、M02（read pair 證據）和 M04（`(x,y,w,z)` 狀態空間）。

如果需要，我可以把這份表存成 `research/tumor_phylogeny_2026/INPUT_OUTPUT_MATRIX.md`，也可以補上 46 個方法的輸出欄。


######## USER: phyclone和pyclone他們的sample定義是甚麼

--- ASSISTANT:
我查了 PhyClone 的論文、README 和程式碼。以下是結論。

## 結論

在 PhyClone 和 PyClone 中，**一個 sample 就是同一個腫瘤（同一病人）的一份 bulk 定序樣本**。常見的是不同區域（multi-region）或不同時間點。所有 sample 共用同一組 clone 和同一棵樹，每個 sample 只有各自的 clone 比例。

## PhyClone

**論文描述：**
- 主文寫的模型是「for multiple samples」，而且明確對應 multi-region sequencing（主文 §2.2）。
- 每個 region 的 clonal prevalence 各自從 Dirichlet 抽樣（主文 §2.2；Supp. S1 p.2）。
- multi-sample 的價值在 prevalence 順序反轉。例如突變 a 在 sample 1 比 b 高，在 sample 2 比 b 低。這時 a、b 必定在不同 clade，可以區分 sibling 和 ancestor（主文 §1）。

**程式實作：**
- `sample_id` 只是一個字串標籤，程式不檢查它代表什麼（`README.md:84`）。
- 每列是一個「mutation × sample」：`ref_counts`、`alt_counts`、`major_cn`、`minor_cn`、`normal_cn`、`tumour_content`。所以 **CN 和 purity 都可以每個 sample 不同**（`README.md:102-106`）。
- 每個突變必須出現在**所有** sample。缺少任一 sample 的突變會被移除（`phyclone/data/pyclone.py:224-247`）。
- 每個 data point 存一個 `(num_samples × grid_size)` 的 likelihood 網格（`pyclone.py:99`）。每個 sample 各自卷積後相乘。
- 輸出的 `SAMPLE_PREVALENCE_TABLE.tsv` 給每個 clone 在每個 sample 的 CCF 和 clonal prevalence。

**每個 sample 有自己的值：**
- read counts。
- CN。
- purity。
- 每個 clone 的 prevalence。

**所有 sample 共用：**
- SNV→clone 指派。
- topology。

## PyClone（含 PyClone-VI）

repo 裡**沒有** PyClone 原始論文（Roth 2014 *Nat Methods*）和 PyClone-VI 論文。以下來自我的背景知識，沒有在 repo 內核對過。

- PyClone 的 sample 定義和 PhyClone 相同：同一病人的多個 bulk 樣本，可以是空間的或時間的。每個 sample 有自己的 tumour content 和 CN。
- PyClone 只把突變分群，每個 cluster 在每個 sample 有一個 cellular prevalence。它**不建樹**，也沒有 sum condition。
- PyClone-VI 的輸入 TSV 欄位和 PhyClone 相同，PhyClone 沿用了它的格式和 emission model。

## 對本 repo 的影響

這部分是分析推論。

- 本 repo 的 `tX_nY` subsample 可以照格式當成多個 `sample_id` 輸入，每個 sample 給不同的 `tumour_content`。
- 但它們是**同一份 DNA 的稀釋**，不是不同區域或不同時間點。所有 clone 的相對比例只會一起縮放，prevalence 順序不會反轉。
- 所以它們**提供不了** PhyClone 論文假設的 multi-sample 可識別性，效果接近「一個 sample 加上更多 reads」（M01 筆記也有相同判斷）。
- `tX_nY` 的百分比是 nominal 值，不是實測值。直接填進 `tumour_content` 會把 purity 誤差帶進 CCF 估計。


######## USER: 這些演化樹論文，都有先推論出各snv的ccf，再把相同的ccf比例的snv，進行分群，變成一個clone嗎?

--- ASSISTANT:
不是全部。只有部分 bulk 方法走「以 CCF 分群 → 一群當一個 clone」的路線。single-cell 和 CN 方法多半不經過 CCF。

## 結論

依照 clone 怎麼定義，這些論文分成三類：

1. **先依 CCF 分群，再建樹（兩段式）。** 這是 bulk 的主流做法。
2. **分群和建樹同時推論。** CCF 是 clone 的參數，不是每個 SNV 先各估一個值。
3. **完全不用 CCF。** clone 由 cell genotype、CN 或 SV 定義。

還有一個細節要分清：PyClone 系列也**不是**「每個 SNV 先算一個 CCF 點估計，再拿去分群」。它把 CCF 當成 cluster 層級的隱變數，和分群一起推論。multiplicity 會在 likelihood 內被加總掉。

## 第一類：先分群，再建樹

| 論文 | 分群依據 | 建樹 |
|---|---|---|
| B04 肺癌 ONT | FACETS CN/purity → PyClone-VI CCF cluster | ClonEvol 候選樹，再用 long-read pair 篩選 |
| R01 McPherson | targeted deep-seq 的 PyClone cluster | Dollo 樹；single-nucleus genotype 在 cluster 層級判斷有無 |
| HCC1395（SuperFreq 部分） | VAF＋local CN 的 clonality 做 hierarchical clustering | SuperFreq 不建樹；樹來自 PhyloWGS |
| M04 Pharming（第一階段） | pseudobulk 上用 DeCiFer 估出 k 個 DCF cluster | 再列舉符合 sum condition 的樹 |

**PhyClone 實務上也屬於這類：**
- 模型本身是 CRP 分群加上樹，能同時推論。
- 但論文的 benchmark 全部先跑 PyClone-VI 前分群（主文 §2.2.2）。
- PhyClone 能**合併**前分群的 cluster，**不能拆開**。所以前分群錯併的兩個 clone，後面修不回來。

## 第二類：分群和樹同時推論

| 論文 | clone 定義 |
|---|---|
| M01 PhyClone（不前分群時） | CRP 分群＋forest prior；CCF 在網格上積分 |
| HCC1395 的 PhyloWGS、M06 PhylEx | TSSB：SNV 指派到 node 和樹一起抽樣 |
| M02 TreeClone | 沒有 CCF；clone 是每個 pair 的 genotype 矩陣 Z＋比例 w |
| M05 TUSV-ext | `F ≈ U·C` 解混；沒有單一 SNV 的 CCF |

## 第三類：不用 CCF

| 論文 | clone 怎麼來 |
|---|---|
| A01、B03、B05、B07 | 依 CN（allele-specific 或 haplotype-specific）建 cell tree，再切 clade |
| A03、A05、R01（single-nucleus） | 依 cell genotype 分群（SCG、或同 genotype >10 顆細胞） |
| A04 | 依共享 SV |
| B01 | 每個 subline 接近單一 clone，直接用 binary genotype 建樹 |

## 為何「同 CCF 等於同 clone」有問題

- **sibling clone 的 CCF 可以相同。** 例如 TreeClone 的 Sim 2：Cloe 和 PhyloWGS 把 CCF 相近的 M2、M3 併成一群，得到 linear tree。TreeClone 用 read pair 才恢復成 branching（M02 筆記）。
- **PhylEx Fig.1 也是同一個問題。** 只看 bulk VAF 會推出 linear tree，加入 cell 層級的共現才變成 branching。
- **CCF 本身依賴 CN 和 purity。** CN 或 purity 錯，或 multiplicity 估錯，同一 clone 的 SNV 會散到不同 cluster。B03 Fig.5 也顯示，mirrored HSCN 會讓同一 clonal SNV 的 VAF 在不同細胞不同。
- **single-sample 時更嚴重。** 沒有 prevalence 順序反轉可用，同 CCF 的 cluster 無法分辨是 sibling 還是祖孫。

這也是本 repo 加入 long-read 證據的主要切入點。同 PS、同 HP 的 SNV pair 在 read 上的共現，可以拆開 CCF 相同、但不在同一條祖先鏈上的 SNV。對應的設計是 `plan.md` 的 C4 和 C5。


######## USER: subclonal CNA 是甚麼樣的問題

--- ASSISTANT:
## 定義

**subclonal CNA**：只有部分腫瘤細胞帶有的 copy number 變化。

- **clonal CNA**：所有腫瘤細胞都有。例如每個腫瘤細胞在某段都是 2:1。
- **subclonal CNA**：只有某些 clone 有。例如 60% 的腫瘤細胞是 1:1，40% 是 2:1。

bulk 定序看到的是兩種狀態的混合。這個區段沒有單一的「major/minor CN」。

## 為何是問題：VAF 不再能唯一換算 CCF

PhyClone 和 PyClone 的 likelihood 假設，每個 SNV 的區段在所有腫瘤細胞中 CN 相同（論文描述，M01 §CN）。subclonal CNA 破壞這個假設。

**例子（推論）：** purity=1，SNV 是 clonal（CCF=1），每個細胞原本帶 1 個 variant copy。60% 的細胞是 1:1，40% 的細胞把一條 allele 複製成 2:1。

| 情況 | 實際 VAF | 若輸入 CN=1:1，模型推出的 CCF | 結果 |
|---|---|---|---|
| SNV 在被複製的 allele | (0.6·1 + 0.4·2) / (0.6·2 + 0.4·3) = **0.583** | 約 1.17，超過 1 | 被截到 1，或被當成 outlier |
| SNV 在沒被複製的 allele | (0.6·1 + 0.4·1) / 2.4 = **0.417** | 約 0.83 | **看起來像 subclonal，產生假 clone** |

若輸入改成 2:1，模型預期的 VAF 只有 1/3 或 2/3，0.583 和 0.417 兩個值都對不上。

**後果：**
- 同一個 clonal SNV 的 VAF 會依它在哪條 allele 而分成兩群。這會產生假的 subclone。
- 不同 clone 的 SNV 可能被併在一起。
- 樹的 topology 因此錯誤。

## 它還帶來四個子問題

1. **SNV 被刪除（mutation loss）。** 帶 SNV 的 allele 在某 subclone 被刪除後，該 subclone 就沒有這個 SNV。SNV 看起來像只在部分細胞，其實是祖先突變後來流失。
   - PhyClone 不建模這件事，只用 outlier 吸收（M01）。
   - McPherson 2016 指出：只看 SNV 時，「祖先 SNV 在後代流失」和「SNV 起源於兄弟節點」的證據相同（R01）。
2. **CN 和樹必須一致。** subclonal CNA 本身是樹上某條 edge 的事件，只有那個 clone 的後代帶有。PhyClone 把 CN 當固定輸入，不檢查 CN 和樹是否一致。
3. **時序更模糊。** SNV 在 CNA 之前還是之後發生，現在要對每個 clone 分別判斷，multiplicity 的組合會變多。
4. **mirrored CN。** 兩個 clone 可能有相同的 total CN，但失去或複製的是不同 haplotype（例如 `2|1` 和 `1|2`）。major/minor 表示法會把這兩種情況混在一起。B03 Fig.5 和 B05 MEDICC2 都示範了這個問題。

## 各論文怎麼處理

| 處理方式 | 論文 |
|---|---|
| **不處理**，只吃 clonal CN | M01 PhyClone（作者列為主要限制，主文 p.8）、M06 PhylEx、M02 TreeClone（只用 CN=2 區域） |
| 外部 caller 給 subclonal CN 當輸入 | PhyloWGS（M06 筆記提到它需要 subclonal CN 輸入）、SubMARine（methods survey） |
| clone 層級的 CN 是推論變數 | M05 TUSV-ext（bulk，`U·C` 解混）、M04 Pharming（scDNA，每個 node 有 CN） |
| 直接看每個細胞的 CN，避開混合問題 | A01、B03 SIGNALS、B05 MEDICC2、B07 Numbat |

規律是：bulk 方法很少真正處理 subclonal CNA；single-cell 方法能直接看到每個細胞的 CN，所以問題比較小。

## 和本 repo 的關係

這部分是分析推論。

- **HCC1395 有 subclonal CNA。** Fang 2021 用 subHMM 和 10x single-cell CNV 看到 subclonal CNA（HCC1395 review 02）。所以照現在的方式，把單一 CN 輸入 PhyClone，在這些區段會有偏差。
- **HP 拆分能幫一部分。**
  - 依 HP1/HP2 分開算 depth 和 VAF，可以知道變的是哪一條 haplotype，也可以知道 SNV 在哪一條上。
  - 上表的兩種情況（0.583 和 0.417）在 HP 拆分後可以分開。
- **HP 不能解決所有問題。** 帶 CNA 的細胞比例仍要另外估計。B03 也指出，mixture 不會因為 HP 準確就消失。
- **目前計畫的範圍。** `plan.md` 的 C4 第一版限定同 PS、同 HP、`C_h=1`、沒有 subclonal CN。實務上要先標出 subclonal CN 區段，從 C4 排除。C2/C3 則要另外做一組 subclonal CN 的壓力測試。


######## USER:  subclonal CN 和 main clone CN的差異在哪裡?

--- ASSISTANT:
## 結論

兩者的差別在**有多少腫瘤細胞帶有這個 CN 狀態**，以及**這個事件在樹上的位置**。

| 面向 | main clone CN（clonal／dominant） | subclonal CN |
|---|---|---|
| 誰帶有 | 所有腫瘤細胞（truncal），或是比例最高的狀態 | 只有部分腫瘤細胞 |
| 在樹上的位置 | trunk edge，在 MRCA 之前 | 樹內部的某條 edge |
| bulk 的 logR／BAF | 對應某個整數 CN 狀態 | 落在兩個整數狀態之間 |
| caller 輸出 | 一組 major/minor | 兩組狀態加上一個比例，例如 Battenberg |
| 對 topology 的資訊 | 幾乎沒有，所有 clone 都一樣 | 有。它本身就定義一個 clone |

## 「main clone CN」有兩種意思，要分開

1. **clonal（truncal）CN**：所有腫瘤細胞都有，是真正的生物狀態。
2. **dominant CN**：caller 報告的多數狀態，只是一個近似。
   - 例如 MEDICC2 的 bulk 分析取占比至少 50% 的 subclone 狀態（B05 筆記）。
   - ASCAT 對每個區段只輸出一個整數狀態。

第二種有一個風險：小 clone 裡的 SNV 會配到**不屬於它的 CN**，因為那個 CN 是大 clone 的。

## 數值例子（推論）

假設某區段，60% 的腫瘤細胞是 1:1，40% 的腫瘤細胞是 2:1，purity=1。

- 平均 total CN = 0.6·2 + 0.4·3 = **2.4**，不是整數。
- minor allele 比例 = (0.6·1 + 0.4·1) / 2.4 = **0.417**。
- 對照：clonal 1:1 是 0.5，clonal 2:1 是 0.333。0.417 介於兩者之間。

caller 只能報一個狀態時，會出現兩種偏差：
- 報 1:1：主 clone 正確，但 40% 細胞的 CN 錯。
- 報 2:1：這 40% 細胞正確，但 60% 細胞的 CN 錯。

**purity 也會造成同樣的訊號。** 改成「clonal 2:1，purity=0.4」：
- minor allele 比例 = (0.6·1 + 0.4·1) / (0.6·2 + 0.4·3) = **0.417**，完全相同。
- 在單一區段內，「subclonal 比例」和「purity」無法分辨。
- 只有全基因體一起看才能分開，因為 purity 是所有區段共用的值，subclonal 比例是每個區段各自的值。

## 在 PhyClone 中的意思

程式實作，見 M01 筆記：
- 每個 SNV、每個 sample 只能輸入一組 `major_cn/minor_cn`。所以 PhyClone 隱含假設這個 CN 是 **clonal** 的：所有腫瘤細胞都相同。
- likelihood 有三群細胞：normal 用 `normal_cn`；reference 和 variant 兩群腫瘤細胞用同一個 tumor CN。沒有「部分腫瘤細胞是另一種 CN」的位置。
- 所以輸入 dominant CN，對小 clone 的 SNV 等於輸入錯誤的 CN。結果就是上一題說的假 subclone，或 SNV 被分錯 cluster。

## 和本 repo 的關係

這部分是推論。

- **multi-sample 時，main clone CN 會隨 sample 改變。** 同一個 CNA 在一個區域可能是 clonal，在另一個區域是 subclonal。本 repo 的 `tX_nY` 是同一 DNA 的稀釋，subclonal CN 在腫瘤細胞中的比例不變，只有 purity 改變。
- **用 nominal purity 有風險。** 若把 nominal 值直接當 purity，purity 誤差會和 subclonal 比例混在一起（上面 0.417 的例子）。建議用全基因體一起估出的 purity，不要直接用 `tX_nY` 的百分比。
- **HP 拆分能看出變的是哪條 haplotype，但比例還要另外估。** HP1/HP2 各自的 depth 可以分出 1:1 和 2:1 混合中被複製的是哪一條。但 40% 這個比例仍要靠 CN 模型估出來。
- **HCC1395 要先標記 subclonal 區段。** HCC1395 已知有 subclonal CNA（Fang 2021 的 subHMM 和 10x single-cell CNV）。這些區段應該先標出來，再決定要排除、另外建模，或在 PhyClone 輸入時特別標記。


######## USER: Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction 幫助我下載這篇論文，了解重建演化樹軟體的benchmark，說不定能分析尚未實作出來的phyclone+longphase-s

--- ASSISTANT:
我下載並讀完了這篇論文，寫了一份閱讀筆記，放在和其他論文相同的目錄結構裡：

`research/tumor_phylogeny_2026/methods_survey/papers/M07_smchet_benchmark_2024/`

- 正式版 PDF、supplement 和 supplementary tables 都已下載。論文是 CC BY 開放取用，PDF 的 MD5 和 PMC 紀錄一致。
- 筆記在 `README.md`，用的標記方式和 M01–M06 相同（「論文描述」和「推論」分開標）。
- 我沒有改 `INDEX.md` 或 methods survey 的總表，因為那幾個檔案裡有你還沒 commit 的修改。也沒有 commit。

## 這個 benchmark 測什麼

- 這是 SMC-Het DREAM Challenge：31 個方法，在 51 個模擬腫瘤上測 **single-sample** bulk 重建。
- 每個方法拿到的輸入是 MuTect 的 SNV VCF，以及 Battenberg 的 allele-specific CN（包含 subclonal CN）和 purity。
- 評分分 7 項：purity、subclone 數、CP 分布、SNV 分群（hard／soft）、phylogeny（hard／soft）。
- **PhyClone 沒有被測過**，因為它比這個挑戰晚發表。比較基準是 PhyloWGS 和 DPClust。

## 和 PhyClone＋longphase-s 相關的結果

1. **單樣本的深層樹不可靠。** 只有 7 個方法做了 phylogeny 這一項。靠近 clonal node 的關係推得比較準，越深越不準；推錯 parent 時多半錯到相近的 node。所以 read pair 證據（C4）的效果應該在深層的 SNV pair 上評估。
2. **subclonal CNA 是主要的誤差來源。**
   - clonal SNV 加上 subclonal loss 的組合最難，CP 會被低估。
   - Battenberg 漏掉了 48 個 subclonal gain 中的 25 個。
   - 這兩點都是 HP 拆分可能有幫助的地方。
3. **NRPCC 是最重要的可控因素。** 公式是 `NRPCC = ρd / (ρψ + 2(1−ρ))`，作者建議至少 32。本 repo 每個 `tX_nY` 都應該先算這個值，而且要用估計出來的 purity 和 ploidy，不能用 nominal 百分比。
4. **作者在 Discussion 寫明，long read 的 mutation-to-mutation 和 mutation-to-SNP phasing 是未來方向。** 這直接支持你的研究動機。但論文本身沒有做任何 long-read 實驗。

## 可以直接用在 PhyClone＋longphase-s 的三點

1. **評分可以直接接上。** 它的 phylogeny 評分比較四個矩陣：co-clustering、ancestor–descendant、它的轉置、cousin。這和 `evaluation_v1.md` 的四類關係（same／ancestor／descendant／branch）幾乎一樣。官方評分程式是公開的，soft 版本還可以用到 PhyClone 的 posterior。
2. **下一步成本最低的實驗。** 拿 Synapse 上的 VCF 和 Battenberg 輸出，轉成 PhyClone 的輸入格式，跑原版 PhyClone，再用官方程式評分。這樣可以得到 PhyClone 在單樣本下的基線，而這正是 PhyClone 論文證據最少的地方。
3. **可以做 long-read 版的 benchmark。** 它模擬資料的方法是先把 reads 依 haplotype 分組，再依 CP 和 CN 調整深度，最後依樹插入突變。底層樣本是 GM24385，也就是 HG002，GIAB 有它的 ONT 資料。照同樣的方法改用 long read，就能做出 HP 真值完全已知的資料，直接測 C2–C4 的效果。

## 要先確認的事

- Synapse 上的資料要登入才能下載。我沒有實際登入確認。
- 參考基因組是 GRCh37（hs37d5），本 repo 的 CRAM 是 GRCh38，不能直接混用。
- BAMSurgeon 能不能處理 ONT long read，我還沒確認。這是做 long-read 版 benchmark 的最大技術風險。

要不要先從第 2 點開始？需要你提供 Synapse 帳號，或先下載資料，我可以接著寫 Battenberg 轉 PhyClone 輸入格式的轉換腳本。


######## USER:  評分可以直接接上，在幫我額外新增驗證方法

--- ASSISTANT:
我在 `evaluation_v1.md` 加了 **§2.7 SMC-Het 相容分數**，列為附加驗證。主要指標不變（§2.2–2.6 的 AD F-score、V-measure、CCF MAE、四類關係矩陣）。這只是規格，評分程式還沒寫，也還沒 commit。

## 新增的內容

公式取自官方評分程式 `tool-SMCHet-scoring`（commit `fa67302`）。論文的 Methods 只有摘要，兩者不一致時以程式為準。

- **七項分數怎麼從 PhyClone 輸出取得：**
  - sc2B、sc3B 的機率矩陣，用 PhyClone 的 posterior trace 計算。
  - **sc1A（purity）記為 `NA`**，因為 PhyClone 只把 purity 當輸入，不會推論。
- **sc3 的算法：** 用 CCM、AD、ADᵀ、cousin 四個矩陣，算 Pearson 相關，再依兩個極端解做正規化。這四個矩陣正好對應 §2.5 的 same／ancestor／descendant／branch。
- **評分範圍採用 SMC-Het 的規則。** 規格另有「缺預測記 NA」的規則，這裡是寫明的例外：
  - 漏掉的 SNV（false negative）加進一個 CP=0 的額外 cluster。
  - PhyClone 移除的 SNV 和 outlier 也放進這個 cluster。
  - 多出來的 SNV（false positive）在計分前排除。
  - 三者都要報數量。
- **規模：** 1 萬個 SNV 時，一個矩陣約 3.2 GB。SNV 太多時用官方的子抽樣，seed 要記錄下來。
- **輸出檔和驗收條件：** 新增 `smchet_scores.tsv`。如果自己重寫評分程式，分數要和官方程式一致，差異在 1e-6 以內。

## 實際驗算後的修正

我寫了一個小腳本，依官方公式重算 sc3，結果改正了我原本的兩個說法：

- **極端解不是 0 分。** 兩個極端解裡，較差的那個正好 0.5 分。在例子中，另一個（全部一群）是 0.542。所以 sc3 的實際下限約 0.5。
- **sc3 分不太出拓樸錯誤。** 真樹是分支（A→B、A→C），預測成線性（A→B→C），sc3 仍有 **0.875**。

所以判斷分支還是線性，不能只看 sc3。規格已寫明要同時看 AD F-score 和四類矩陣的 branch 列。這也表示：如果 C4（read pair 證據）主要改善的是分支判斷，用 sc3 會看不太出效果。

## 還沒確認的兩件事

- **sc1C 的 CP 單位**（是 CCF，還是 purity×CCF）要看官方 truth 檔才能確定。確認前 sc1C 記為 `NA`。
- **sc1B 的 clone 數要不要算進 clonal node**，同樣要用 truth 檔對齊。

兩件事都要下載 Synapse 上的 SMC-Het 資料才能確認。官方程式我只 clone 到暫存目錄，沒有放進 repo。

要不要接著寫評分程式？我可以先寫一個 Python 3 版本，用官方的測試資料做一致性驗收。


######## USER: 先下載 Synapse 上的 SMC-Het 資料看看

--- ASSISTANT:
下載資料需要登入 Synapse，所以要請你先建立 token。這個專案沒有使用條款或審核流程，任何 Synapse 帳號都能下載。

## 目前查到的內容

我用匿名方式列出了專案 `syn2813581` 的目錄。匿名可以看目錄和檔名，但下載會被拒絕（HTTP 403）。

| Synapse ID | 檔案 | 用途 |
|---|---|---|
| syn15654766 | `truthFiles.tar.gz` | 真值檔：樹、SNV 指派、CP |
| syn23585101 | `battenberg_files.tar.gz` | CN 和 purity 輸入 |
| syn21609786 | `downsampled_vcfs.tar.gz` | SNV VCF（downsampled 版） |
| syn21609785 | `downsampled_battenberg.tar.gz` | downsampled 版的 Battenberg 檔 |
| syn21609908 | `truthfilesDownsampled.tar.gz` | downsampled 版的真值檔 |
| syn15663340 | `Tumour_metadata_final`（Synapse 表格） | 每個腫瘤的特徵 |
| syn18694229–34 | `Tumour1–7.tar.gz`（沒有 Tumour5） | Galaxy 測試用的腫瘤，內容不明 |

還不清楚的地方：
- 根目錄只看到 downsampled 版的 VCF。完整的 51 個腫瘤 VCF 在哪裡、是否在 `Tumour*.tar.gz` 裡，要登入後才能確認。
- 匿名查不到檔案大小。存放位置 `/big8_disk` 還有 9.7 TB 空間，應該夠用。

## 請你做的事

1. 到 synapse.org 登入或註冊帳號。
2. 進入 **Account Settings → Personal Access Tokens**，建立一個 token，權限勾選 **View** 和 **Download** 即可。
3. **在你自己的終端機**（不要在這個對話裡）建立設定檔：
   ```bash
   cat > ~/.synapseConfig <<'EOF'
   [authentication]
   authtoken = 你的token
   EOF
   chmod 600 ~/.synapseConfig
   ```
   不要把 token 貼到對話裡，也不要用 `!` 執行這段指令，否則 token 會留在對話紀錄中。

完成後告訴我，我會依序執行：

1. **只列檔案大小和 MD5，不下載。** 我會把總大小回報給你。
2. 你確認後，下載到 `/big8_disk/boyu114/smchet_dataset/`，和現有的 `phyclone_dataset/` 放在同一層。每個檔案下載完都會核對 MD5。
3. 解壓縮後，檢查第一個 SMC-Het 腫瘤的真值檔格式，回答上一輪留下的兩個問題：sc1C 的 CP 是哪種單位、sc1B 的 clone 數是否包含 clonal node。

下載腳本放在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/5908f3a1-0d50-4a7e-be9e-2cf05fa90c32/scratchpad/syn_get.py`。它只用 Python 標準函式庫，從 `~/.synapseConfig` 讀取 token，不會把 token 印出來。


######## USER: token 設定好了，先列檔案大小，如果正常下載到/big8_disk/boyu114/smchet_dataset/

--- ASSISTANT:
The metadata table is saved. The download is still running in the background, and I'll continue once it finishes.

Two points from the table:
- It lists **49 Scoring tumors** (25 P, 16 T, 8 S) and 8 Training tumors (Tumour1–8). The paper says 10 special cases, but the table has only 8 (no S1 or S9). I'll check this against the truth files.
- The `Tumour1–7.tar.gz` files are the **training tumors**, not part of the 51 scored tumors.

--- ASSISTANT:
The Battenberg archive is extracted and readable. The rest of the download is still running.

**Results so far:**
- **51 tumors:** 25 P, 17 T (T0–T16) and 9 S (S2–S10). The paper's count of 51 checks out.
  - The metadata table has no rows for **T7 or S9**, but Battenberg files exist for both.
  - S1 is missing everywhere I have looked so far. I'll check the truth files.
- **Battenberg format:**
  - Each segment has a clonal state (`nMaj1_A / nMin1_A / frac1_A`) and, for subclonal segments, a second state (`nMaj2_A / nMin2_A / frac2_A`). A segment is subclonal when `frac1_A < 1`.
  - Each tumor also has a `cellularity_ploidy.txt` file. For example, T2 has cellularity 0.534 and ploidy 1.86.
- **T2 already contains subclonal CN:** 6 of its 26 segments have `frac1_A < 1`.
  - PhyClone accepts only one `major_cn/minor_cn` per SNV, so the conversion script must choose how to handle these segments.
  - I'll mark these SNVs so the results can be split into clonal-CN and subclonal-CN groups.


######## USER: 翻譯中文

--- ASSISTANT:
Battenberg 壓縮檔已解開，內容可以正常讀取。其餘檔案還在背景下載。

**目前結果：**
- **51 個腫瘤：** 25 個 P、17 個 T（T0–T16）、9 個 S（S2–S10），和論文的 51 個相符。
  - metadata 表格沒有 **T7 和 S9** 的資料列，但這兩個都有 Battenberg 檔。
  - 到目前為止，所有地方都找不到 S1。我會再用真值檔核對。
- **Battenberg 格式：**
  - 每個區段有一組 clonal 狀態（`nMaj1_A / nMin1_A / frac1_A`）。subclonal 區段另有第二組狀態（`nMaj2_A / nMin2_A / frac2_A`）。`frac1_A < 1` 就表示這個區段是 subclonal。
  - 每個腫瘤另有一個 `cellularity_ploidy.txt`。例如 T2 的 cellularity 是 0.534，ploidy 是 1.86。
- **T2 已經有 subclonal CN：** 26 個區段中有 6 個的 `frac1_A < 1`。
  - PhyClone 每個 SNV 只接受一組 `major_cn/minor_cn`，所以轉換腳本必須決定這些區段要怎麼處理。
  - 我會標記這些區段裡的 SNV，之後的結果就能分成 clonal CN 和 subclonal CN 兩組比較。
