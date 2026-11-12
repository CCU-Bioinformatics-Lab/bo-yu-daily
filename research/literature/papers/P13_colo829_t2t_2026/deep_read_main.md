# P13 深讀（主文）｜COLO829 近 T2T：somatic 變異的完整地圖，不是 HP 比例研究

- 論文：Sohn MH, …, Stergachis AB. *A telomere-to-telomere map of somatic mutation burden and functional impact in a cancer.* Cell 189(21):6630 (2026). DOI 10.1016/j.cell.2026.09.033，PMC13722029。
- 讀的範圍：本機 `fulltext.md` 全文（SUMMARY、INTRODUCTION、RESULTS 10 節、Discussion、Limitations、STAR Methods）。
- 沒讀到的：補充資料（Figure S1–S12、Supplemental methods）、主文圖說、Table 1。`fulltext.md` 只有正文，沒有圖說與表格內容。凡是「見 Figure X」的細節，本筆記都沒有看到。
- 寫作日期：2026-11-12。
- 來源標記：〔論文〕附章節名；〔推論〕是本筆記自己的判斷或算術。

## 白話總結

1. 這篇要解決的是「參考基因組看不到的區域」：著絲點、端粒、衛星重複等區域在 GRCh38 裡缺少或對不準，所以過去的 somatic 變異清單漏了這些區域。〔論文〕SUMMARY、INTRODUCTION
2. 作者的做法是：用配對正常的 COLO829BL 做出同一個人的近 T2T diploid 組裝，再把黑色素瘤 COLO829 的 read 對到這份組裝上找 somatic 變異。〔論文〕Results 第一節
3. **這篇沒有回答「somatic SNV 落在 HP1 或 HP2 的比例」。** 主文沒有比較兩條 haplotype 的 sSNV 數量，也沒有親代資料，所以沒有 parent-of-origin；chrX 也沒分析。〔論文〕全文搜尋 maternal／paternal 各 0 筆、chrX 0 筆；〔推論〕
4. 和我們間接相關的有三點：(a) 它的 sSNV 呼叫流程怎麼把每個 SNV 放到一條 haplotype；(b) chr1q 的 hVAF 時序示範「SNV 先發生、CN 後改變」會怎麼改變累積的 VAF；(c) 公開的 DSA 座標 VCF 可以拿來再分析。〔推論〕
5. 值得讀，但只讀方法與 chr1q 那段即可；衛星、著絲點、端粒、染色質的結果和 HP 比例無關。〔推論〕

## 1. 作者要解決什麼問題

- **缺口一：參考基因組不完整。** 現有的 somatic 變異地圖建在不完整的 haploid 參考上，缺少癌症中最容易變異的區域（著絲點、端粒等）。〔論文〕INTRODUCTION
- **缺口二：只有 long read 不夠。** COLO829 的 long read 對到 GRCh38 或 T2T-CHM13 時，在著絲點、亞端粒、片段重複、衛星區出現明顯 mapping artifact。作者說這代表「只靠 long read」無法把變異清單延伸到這些區域。〔論文〕Results「Telomere-to-telomere mapping…」
- **原因：** 這些區域在個體之間序列與結構差很多，所以通用參考對不準。人類基因組超過 10% 屬於這類區域，現有 somatic 清單一律把它們排除。〔論文〕同上
- **作者的主張：** 用同一個人的 diploid donor-specific assembly（DSA）當參考，能在「幾乎整個 diploid 基因組」上做 nucleotide 解析度的 somatic 分析。〔論文〕INTRODUCTION
- **Discussion 的定位：** 作者把這套框架稱為 somatic 突變特徵分析的新標準，並當作未來 T2T 癌症與 mosaicism 研究的藍圖。〔論文〕Discussion 第一、最後一段

## 2. 作者怎麼解決（流程）

```
COLO829BL（正常 LCL）                     COLO829（黑色素瘤，兩個 passage A/B）
  HiFi(Fiber-seq) 60x + ONT 60x(最長 read) + Hi-C 30x      HiFi/Fiber-seq、UL-ONT、ONT、Illumina、Element
        │ Verkko v2.12 phased assembly                           │
        ▼                                                        │
  DSA（hap1 + hap2）→ 去污染 → Flagger/NucFlag 標出可疑區並排除  │
        │                                                        │
        ├─ Minigraph-Cactus：DSA 兩條 + GRCh38 + CHM13 → DSG（圖）│
        ▼                                                        ▼
  兩邊 read 都對到 diploid DSA（MAPQ 一律改成 60，原值存 mq tag）
        │
        ├─ hCN：100 kb window 覆蓋度比值 → CBS 分段 → 每條 haplotype 的 haploid CN
        ├─ sSNV：DeepVariant（Fiber-seq）→ 多層過濾（見 2.4）→ UL-ONT 驗證
        ├─ sSV（著絲點）、CDR（CpG 甲基化 + CENP-A DiMeLo-seq）
        ├─ 端粒：跨端粒單分子 + TVR
        └─ Fiber-seq FIRE：haplotype-selective 染色質開放
```
〔論文〕STAR Methods 各節；圖為本筆記整理〔推論〕

### 2.1 COLO829BL 組裝

- 資料：60x PacBio HiFi、60x ONT（挑最長的 read 降到 60x，以 3.1 Gb 計）、30x Hi-C。〔論文〕Methods「Building COLO829BL diploid genome assembly」
- 工具：Verkko v2.12 產生 phased assembly。再用 NCBI FCS 與 BLAST 去掉外來 DNA、adapter、粒線體、EBV、rDNA。〔論文〕同上
- Results 寫的總資料量：Fiber-seq HiFi 186.24 Gb（N50 19.15 kb）、UL-ONT 186.00 Gb（N50 130.85 kb）、Hi-C 126.07 Gb。〔論文〕Results 第一節
- 品質：5.92 Gb，N50 135 Mb，估計 QV 62.16，98.6% 看起來組裝正確；12 條染色體 T2T；46 個著絲點都有序列。〔論文〕Results 第一節
- QC：QV 用 Meryl／Merqury（COLO829BL Illumina k-mer），基因完整度用 compleasm。Flagger 與 NucFlag 標出的區域稱為「potentially misassembled regions」，後續分析一律排除。〔論文〕Methods「Evaluating quality of COLO829BL DSA」
- 染色體歸屬：contig 對 CHM13（minimap2 asm20），取對上比例最高的染色體。〔論文〕同上

### 2.2 定相

- 主文只寫「Phased assembly was generated using Verkko」，輸入包含 Hi-C。〔論文〕Methods「Building…」
- Hi-C 在 Verkko 中負責定相，這是一般工具知識，主文沒有明講 Hi-C 的角色。〔推論〕
- **沒有親代資料。** hap1／hap2 是組裝的編號，不是父源／母源。全文搜尋 maternal、paternal 各 0 筆。〔論文〕全文搜尋；〔推論〕
- 跨染色體的 hap1 是否同一親源：主文沒有說明。全文搜尋 parent 只找到 CDR 遺傳穩定性與 fibroblast 母細胞株兩處，和定相無關。〔論文〕全文搜尋
- 每個 SNV 的 haplotype 歸屬來自「read 對到 DSA 的哪一條」，不是 read-backed phasing。WhatsHap 只用在確認 sDNV 的兩個鹼基在同一分子上。〔論文〕Methods「Diploid variant calling」、「Generating SBS-96 and DBS-78…」

### 2.3 COLO829 read 對到組裝

- Fiber-seq：pbmm2（HiFi preset）。ONT／UL-ONT：minimap2 map-ont。Illumina／Element：bwa mem + samblaster。〔論文〕Methods「Alignment and post-processing of reads」
- **MAPQ 一律改成 60。** 原因：兩條 haplotype 在長於 read 的同型合子區段完全相同，aligner 會隨機放到其中一條並給 MAPQ 0。作者把原值存在 `mq` tag。〔論文〕同上
- 這一步的後果：同型合子長區段內，read 的 haplotype 歸屬是隨機的。作者後面用「兩條都被呼叫」的過濾處理這個問題（見 2.4）。〔論文〕同上；〔推論〕兩者的關聯
- DSG：Minigraph-Cactus 建四個組裝的圖（DSA 兩條、CHM13、GRCh38），用 vg inject／surject 在兩條 haplotype 或 GRCh38 之間搬移 read 與區間。〔論文〕Methods「Donor-specific graph (DSG) construction…」
- 對齊品質：DSA 讓全基因組 mapping 品質明顯變好，包括著絲點。〔論文〕Results 第一節（細節在 Figure S1，沒讀到）

### 2.4 sSNV 呼叫與過濾（Methods「Diploid variant calling」）

順序如下，全部〔論文〕Methods「Diploid variant calling」：

1. **呼叫：** DeepVariant v1.6.1 分別跑 COLO829BL Fiber-seq 與兩個 COLO829 生物重複的 Fiber-seq。
2. **排除可疑組裝區：** 落在 potentially misassembled regions 的刪掉。
3. **兩個 passage 都有、COLO829BL 沒有：** 只留兩個 COLO829 重複都有、COLO829BL 沒有的 SNV。
4. **COLO829BL pileup 過濾：** COLO829BL 最多只能有 1 條 alt read。作者發現 alt read ≥ 2 時開始出現假的突變特徵，所以用這個門檻去掉定序錯誤與長期培養造成的變異。
5. **刪掉 haploid deletion 區段的呼叫：** 和 hCN 判定為 deletion 的區段重疊的 SNV 刪掉。作者的理由：這些呼叫來自「對應的完整 haplotype 的同型合子區段」。
   - 解讀：deletion 的那條 haplotype 在癌細胞裡沒有 DNA，上面的呼叫只能是另一條 haplotype 的 read 錯放過來。因此刪掉的應是「deleted haplotype 座標上」的呼叫；同一區段另一條完整 haplotype 上的 SNV 應該保留。〔推論〕主文沒有逐字說明刪的是哪一條的座標，Figure S5A 沒讀到。
6. **兩條都被呼叫時指定一條：** 作者認為兩條 haplotype 出現相同 sSNV「highly unlikely」，所以這種成對呼叫多半是同型合子區或片段重複造成的錯放。
   - 找配對：用 DSG 把 sSNV 搬到另一條 haplotype，找重疊的配對。
   - 指定：先用 UL-ONT 跑 bcftools mpileup，算兩條 haplotype 上支持 alt 與 ref 的 read 數，做 Fisher's exact test；p < 0.01 就指定給一條。剩下的改用一般 ONT 重做一次。
   - 仍不確定的標記起來，「certain analyses」排除，其餘分析保留。主文沒有寫有幾個。
7. **密度過濾：** 1 kb window、500 bp 滑動。≥ 3 個 sSNV 的 window 合併；若 window 內 ≥ 3 個 sSNV 的 VAF < 0.75，或中位覆蓋度低於 61.5 − 3σ（σ 為 μ = 61.5 的 Poisson 標準差；61.5 是 COLO829 Fiber-seq hCN = 1 的覆蓋度），就刪掉。理由：假陽性多集中在 SV（尤其 deletion）附近的對齊 artifact。
8. **正交驗證：** 用其他平台資料做 bcftools mpileup 驗證。

- 結果：44,795 個 sSNV、828 個 sDNV；held-out 的 UL-ONT 驗證 99.9%，估計 FDR 約 0.1%。〔論文〕Results「Genome-wide map of COLO829 sSNVs…」
- 作者的目標是「fixed cancer variants」。〔論文〕Methods「Diploid variant calling」
- 這套流程只留兩個 passage 都有的變異，再加上 VAF < 0.75 的密度過濾，會偏向 clonal 變異；低頻 subclonal SNV 不是本篇的目標。〔推論〕全文搜尋 subclon 0 筆。
- sDNV：相距 1 bp 的 sSNV；兩個都是 1/1 直接算 DBS；兩個都是 het 時用 WhatsHap 確認同一分子，再用 IGV 人工確認。〔論文〕Methods「Generating SBS-96 and DBS-78…」

### 2.5 haploid VAF（hVAF）

- 主文只在 Results 用到 hVAF：多數 sSNV 的 hVAF ≈ 1.0，代表「fixed along one of the two haplotypes」。〔論文〕Results「Genome-wide map…」
- **hVAF 的計算方式主文沒寫。** 全文搜尋 hVAF 只在 Results 第 3 節出現；Methods 沒有 hVAF 的定義。〔論文〕全文搜尋
- 依上下文，hVAF 應是「該 haplotype 座標上 alt read ÷ 該 haplotype 的 read」，也就是單一 haplotype 內所有拷貝中帶突變的比例。〔推論〕
- 因為每個 SNV 都對到其中一條 haplotype 的座標，hVAF 不受另一條 haplotype 拷貝數影響；這是 diploid DSA 的好處。〔推論〕

### 2.6 拷貝數（hCN）

全部〔論文〕Methods「Determining somatic haploid copy number (hCN) in COLO829」，除非另註：

- 資料：COLO829BL 與 COLO829 passage B 的 Fiber-seq 對到 DSA；COLO829BL 視為正常核型。
- 100 kb window，排除可疑組裝區；mosdepth 算中位覆蓋度。
- 正規化：COLO829BL 覆蓋度單峰（mode 176x）。COLO829 passage B 雙峰（主峰 123x）。作者依「COLO829 經歷多次 whole-genome duplication」的既有觀察，把第二峰當作 haploid（1n）覆蓋度。
- log2 比值 → 低於 −1.5 截斷 → DNAcopy CBS 分段。
- 門檻：log2(n + 0.5)。≤ log2(0.5) 為 haploid deletion（DEL）；之後依序 hCN = 1、2、3、4、> 4。
- 跨 haplotype：用 DSG 把一條 haplotype 的 read 搬到另一條，再用同樣方法算。
- 結果：COLO829 基因組 78.05% 有 sCNV。〔論文〕Results「Somatic copy number variants…」
- 染色體層級：15 條 haploid 染色體整條加倍、6 條整條缺失、6 條染色體臂缺失或加倍。〔論文〕Results「Kinetochore binding regions are hotspots for somatic translocations…」
- 主文沒有用 LOH 這個詞。全文搜尋 LOH、loss of heterozygosity 各 0 筆。「haploid deletion」在功能上等於該區段 LOH。〔推論〕

### 2.7 甲基化、Fiber-seq、CENP-A

- CDR：α-satellite array 內 1 kb bin 的 CpG 甲基化 z-score，低於門檻（COLO829 組 −1.25，其他 −1.75）、距 array 邊界 ≥ 50 kb 的低甲基化段。單分子 UL-ONT 用 −1.5。〔論文〕Methods「Identifying CDRs…」
- CENP-A DiMeLo-seq：nanobody-Hia5，ONT R10 ultralong，m6A 訊號在 CDR 與 α-satellite 之間比較。〔論文〕Methods「Validation of functional kinetochore…」
- FIRE：Fiber-seq 的染色質開放峰。把每條 read 也搬到另一條 haplotype，讓每條 haplotype 有 diploid 覆蓋度來呼叫峰；再用兩條的相對覆蓋度找 haplotype-selective 峰。〔論文〕Methods「FIRE calling using the donor specific assembly」

### 2.8 端粒

- seqtk telo 找端粒；fibertools center 把單分子對齊到端粒／亞端粒邊界。要求亞端粒錨定 > 5 kb、端粒 > 500 bp。〔論文〕Methods「Detecting somatic restructuring of telomeres」
- TVR：不屬於 canonical CCCTAA／TTAGGG 的鹼基。每個端粒做 consensus，找 COLO829BL 有、COLO829 沒有的 TVR 峰，推算被「啃掉」的最少與最多長度。每端要求兩邊各 ≥ 5 分子，再人工檢查。〔論文〕同上

## 3. Results 逐節

相關性分三級：**直接相關**（回答 SNV 在兩條 HP 的比例、獨立性、parent-of-origin、chrX）、**間接相關**（方法前提、可用資料、SNV 與 CN 的時序）、**無關**。

### 3.1 Telomere-to-telomere mapping of COLO829 cancer somatic variants

- 問題：long read 或組裝能不能把 somatic 清單延伸到複雜區域？〔論文〕
- 數字：COLO829 long read 對 GRCh38／CHM13 有 artifact；DSA 5.92 Gb、N50 135 Mb、QV 62.16、98.6% 正確、12 條 T2T、46 個著絲點。DSA 有 342.87 Mb（5.87%）不在 GRCh38。〔論文〕
- 另外：定序了 COLO829 兩個 passage，用來區分癌細胞變異與培養中產生的變異。〔論文〕
- 結論：COLO829BL DSA 是 COLO829 germline 基因組準確、近乎完整的代表。〔論文〕
- **相關性：間接相關（方法前提）。** 我們若用 COLO829 資料，haplotype 座標系統就是這份 DSA；但本節沒有任何 HP 比例。〔推論〕

### 3.2 Kinetochore binding regions are hotspots for somatic translocations in COLO829

- 問題：染色體臂異常的斷點和 kinetochore 結合區有什麼關係？〔論文〕
- 數字：15 整條加倍、6 整條缺失、6 臂缺失／加倍。三個重排：t(1;3)(q12;p21) 斷點在 1q 的 HSat2 與 3p 的 RARB；i(4)(q10) 與 t(14;16)(p10;p10) 的四個斷點都在 α-satellite HOR，位置在 GRCh38、CHM13 都不存在。〔論文〕
- 修復特徵：兩個接點只有 1 bp microhomology，i(4)(q10) 沒有。三個斷點都有 kataegis，推測涉及 1–5 kb ssDNA。t(1;3) 接點上游 5 kb 有 20 個、下游 1 kb 有 3 個群聚突變，17/23（73.91%）在 TpC，符合 APOBEC。〔論文〕
- 作者推論：符合 MMBIR，但也可能是不依賴複製的修復。i(4) 與 t(14;16) 各有一個斷點在 CENP-A 陽性 CDR（permutation p = 0.0048）。〔論文〕
- **相關性：間接相關（弱）。** kataegis 是一種局部群聚的 SNV，和我們「cis 聚集、相鄰 SNV 不獨立」的假說有關。但作者沒有寫這 23 個群聚突變落在哪條 haplotype，也沒做 haplotype 層級的群聚分析。〔論文〕本節只報數量與 TpC 比例；〔推論〕相關性判斷
- 本節也提供 CN 事件清單，可對照 hVAF 時序；但事件的 haplotype 細節在 Figure 1C（沒讀到）。〔推論〕

### 3.3 Genome-wide map of COLO829 sSNVs and their mutational timing（重點）

- 問題：全基因組 sSNV 有多少？它們何時發生？〔論文〕
- 數字：44,795 sSNV、828 sDNV；UL-ONT 驗證 99.9%（FDR 約 0.1%）。突變譜大多符合 UV，作者解讀為成癌前皮膚前驅細胞一生累積，不是培養 artifact。15.6% 的 sSNV 落在 GRCh38 沒有的區域，其中 599 個在 DSA 特有的非重複區。〔論文〕
- **作者沒有報告 hap1 與 hap2 的 sSNV 數量或比例。** 本節只說多數 sSNV 固定在「兩條 haplotype 其中一條」。〔論文〕；全文搜尋 hap2 只有 1 筆（CDR 段落），haplotype 2 只有 1 筆（不在本節）

**chr1q hVAF 時序（逐句整理）**〔論文〕本節第二段：

1. 多數 sSNV 的 hVAF ≈ 1.0，表示固定在一條 haplotype 的所有拷貝上。
2. 例外：chr1q haplotype 1（chr1qhap1）有 38% 的 sSNV hVAF ≈ 0.5。
3. chr1qhap1 在 COLO829 有 4 份：2 份在完整 chr1 的整條加倍上，2 份在 t(1;3)(q12;p21) 的加倍上。
4. 對到 t(1;3) 斷點旁 HSat2 array 的 long read 顯示：hVAF ≈ 0.5 的 sSNV「exclusively」只在 t(1;3) 上，或只在完整 chr1 上。
5. 推論時序：hVAF ≈ 1.0 的發生在 t(1;3) 形成之前（early clonal）；≈ 0.5 的發生在之後（late clonal）。
6. 作者因此把 t(1;3) 定為產生 COLO829 的細胞一生中「first retained chromosome gain aneuploidy」。
7. 兩組突變譜都以 UV 為主；只有 hVAF ≈ 0.5 的一組多了符合 SBS38 的 C>A，作者認為支持 SBS38 只出現在黑色素瘤演化晚期。

示意圖〔推論〕依上述文字畫；拷貝怎麼加倍的細節在 Figure 2E、S6（沒讀到）：

```
時間 →
chr1q hap1（1 份）── SNV_early 累積 ──┬─ t(1;3) 形成 → 衍生染色體 der ── SNV_late_A ── der 加倍 → der ×2
                                      └─ 完整 chr1               ── SNV_late_B ── chr1 加倍 → chr1 ×2
結果：4 份 hap1
  SNV_early：4/4 份帶 → hVAF ≈ 1.0
  SNV_late_A：只有 der ×2 帶 → hVAF ≈ 2/4 = 0.5
  SNV_late_B：只有 chr1 ×2 帶 → hVAF ≈ 2/4 = 0.5
```

我們的解讀〔推論〕：

- 這是「累積比例會被 CN 改變」的實例。同一條 haplotype 上，hVAF 分成 1.0 與 0.5 兩群，兩群對應 CN 事件前後。
- 「late」SNV 必須發生在 t(1;3) 之後、各自加倍之前，才會剛好在 2/4 份上。作者只寫「after the formation of t(1;3)」。
- 38% 是 chr1qhap1 的局部數字；作者沒有給全基因組有多少 sSNV 晚於 CN 事件。
- 全基因組「多數 hVAF ≈ 1.0」是作者的定性描述，主文沒有給比例數字（在 Figure 2B，沒讀到）。
- 對 HP 比例的意義：若某條 haplotype 在 SNV 累積後加倍，**SNV 數量**不變，改變的是 VAF；若某條 haplotype 被刪除，該條上已累積的 SNV 會整批消失，累積 HP 比例才會偏。主文沒有直接做這個計算。

- **相關性：間接相關（SNV 與 CN 的時序）。** 本節是全文最接近我們問題的段落，但它回答的是「何時」，不是「落在哪條」。〔推論〕

### 3.4 Satellite repeats act as genomic sinks for UV-associated sSNVs

- 問題：sSNV 在不同重複元件的密度？為什麼衛星特別高？〔論文〕
- 數字：重複元件是非重複區的 1.4 倍；衛星 3.79 倍；不同衛星類別差 5.05 倍；HSat2 最高，6.1×10⁻⁵ /bp（7.78 倍）。〔論文〕
- 機制：重複與非重複區的 k-mer 正規化突變譜相近，都以 UV 為主。衛星的突變量和序列的預測可突變性高度相關（R² = 0.91，p = 0.01），但控制可突變性後仍偏高。衛星占此 donor 基因組 4.27%。〔論文〕
- Discussion 補充：控制可突變性後衛星仍約 3 倍；作者認為是 UV 損傷發生率較高或修復較差，不是衛星特有的突變過程；可能符合「Bodyguard hypothesis」。〔論文〕Discussion
- **相關性：無關。** 這是位置（區域）造成的突變密度差異，和突變落在哪條 haplotype 無關。〔推論〕
- 補充〔推論〕：若模擬器未來要讓突變密度隨區域變化，這是證據之一；但這不在 SNV-only 第一階段的 HP 問題內。

### 3.5 Kinetochore binding regions are hotspots for sSNVs in COLO829

- 問題：kinetochore 結合區（CDR）的 sSNV 負擔是否較高？〔論文〕
- 數字：DSA 有 43/46 條 haploid 染色體的完整 CDR；CHM13 沒有一個 CDR 被正確涵蓋。CDR 4.20×10⁻⁵ vs 其他 α-satellite HOR 2.32×10⁻⁵（two-proportion Z-test p = 3.05×10⁻³¹）。〔論文〕
- 結論：突變譜和 k-mer 組成與其他 HOR 相似，所以較高的負擔不是另一種突變過程。〔論文〕
- **相關性：無關。** 同 3.4，是位置效應。〔推論〕

### 3.6 Kinetochore binding regions are hotspots for sSVs in COLO829

- 問題：著絲點 sSV 的特徵能不能指出機制？〔論文〕
- BIR 模型預測：sSV 長度是 ~171 bp 的倍數，插入是相鄰 HOR 的完美複製。〔論文〕
- COLO829：長度大多是 ~171 bp 倍數；插入大多是相鄰 HOR 的完美複製；CDR 的 sSV 負擔較高（p = 4.08×10⁻¹¹）。sSV 周圍也有 TpC sSNV 富集，但比兩個 α-satellite 易位低很多。〔論文〕
- COLO829BL（HiFi 171.35x haploid、ONT 17.59x haploid）：同樣特徵，CDR 富集 p = 5.10×10⁻³。SMaHT 組織：長度與插入特徵相同，但檢定力不足以量化 CDR 富集。〔論文〕
- 結論：著絲點 sSV 在正常發育與成癌中都以 BIR 方式產生。〔論文〕
- **相關性：無關。** 主題是 SV，不是 SNV 的 haplotype 分配。〔推論〕

### 3.7 Focal kinetochore occupancy is marked by somatic epigenetic variation in COLO829

- 問題：CDR 是否也是表觀遺傳變異的熱點？〔論文〕
- 數字：COLO829 的 CDR 比 COLO829BL 大 51%，位置平均移動約 65 kb（Discussion 寫 ~64.5 kb）；每個著絲點從約 4 個 CDR 變成約 1 個；兩個 passage 之間穩定。最極端：t(14;16) 上原本的 chr14-hap1 CDR 被關閉，改用 1.7 Mb 外的 CDR。〔論文〕
- 三組對照：
  - 細胞類型：SMaHT ST001（肺、肝）、ST002（肺、結腸）兩組織間 CDR 穩定。〔論文〕
  - 細胞培養：兩位 donor（2 歲男、18 歲女）的 LCL 與皮膚 fibroblast，只有小幅移動。〔論文〕
  - 克隆擴增：LB-LA2 fibroblast 衍生的 5 株 iPSC，CDR 低甲基化減弱，位置異質移動（中位 ~30 kb）。〔論文〕
- 結論：這三種因素都沒有 COLO829 那麼極端，作者認為成癌可能獨特地重組 CDR。作者也承認 COLO829BL 不是 COLO829 的前驅細胞。〔論文〕
- **相關性：無關。** 甲基化與著絲點位置，不涉及 SNV 分配。〔推論〕

### 3.8 Mutational mechanisms within COLO829 telomere arrays

- 問題：端粒酶重新活化後，COLO829 的端粒經歷了什麼？〔論文〕
- 數字：TERT promoter 有 chr5:1295113_4GG>AA DNV，產生 ETS 結合 motif。COLO829 端粒比 COLO829BL 短約 2.4 kb（ONT，Mann-Whitney p = 2.41×10⁻⁸⁶）。5,853 條跨端粒分子（ONT R10 1,825、HiFi 4,028），76 個端粒。13.6% 的端粒遠端 TVR 被 canonical TTAGGG 取代。〔論文〕
- 重建：成癌前端粒縮短到距端粒／亞端粒交界 1.2 kb 內（ONT），之後端粒酶延長約 2.5 kb，然後維持穩態。chr22q-hap1 端粒有內部 35 個 TTAGGG 的缺失，兩側有共同 TVR，作者判定不是末端侵蝕。〔論文〕
- **相關性：無關。** 端粒序列重構，不涉及 SNV 的 haplotype 分配。〔推論〕

### 3.9 Functional impact of sSNVs and sDNVs on the COLO829 gene regulatory landscape

- 問題：sSNV／sDNV 對染色質開放有沒有影響？〔論文〕
- 方法前提：作者寫「一個 somatic 變異只會在一條 haplotype 上」，所以若兩條 haplotype 都保留，另一條可當內部對照。〔論文〕
- 數字：29,189 個 sSNV＋sDNV 落在兩條 haplotype 都保留的區域；其中 280 個和 COLO829 開放的調控元件重疊（低於預期，chi-squared p = 1.091×10⁻¹⁴）；只有 11 個（3.9%）有顯著 haplotype-selective 開放，9 個降低、2 個增加。例子：chr2 片段重複中的 CTCF 位點被一個 sSNV 消除。〔論文〕
- 結論：只有極少數 sSNV／sDNV 有可觀察的染色質功能影響。〔論文〕
- 算術：44,795 + 828 = 45,623；29,189 / 45,623 ≈ 64%。也就是約 36% 的 sSNV＋sDNV 落在「只剩一條 haplotype」或其他被排除的區域。〔推論〕作者沒有寫這個比例，也沒有拆成 hap1、hap2。
- **相關性：間接相關（方法前提）。** 「每個 somatic 變異只在一條 haplotype」和我們模擬器「每個 SNV 只選一條 HP」的前提一致；但作者把它當前提使用，沒有檢驗。〔推論〕

### 3.10 Somatic copy number variants (sCNVs) provide a canvas for somatic epimutations in COLO829

- 問題：sSNV 解釋不了的 haplotype-selective 開放，是不是 sCNV 造成的？〔論文〕
- 數字：另有 253 個 haplotype-selective 元件，sSNV、sDNV、印記、germline het 都解釋不了。基因組 78.05% 有 sCNV。CN 增加帶來成比例的開放增加（Pearson R = 0.92），即多數是加成效應。253 個元件富集在 sCNV 邊界附近，延伸到 9 Mb，超過 TAD 範圍，作者推測是重複的調控程式上出現 somatic epimutation（細節在 companion paper）。例子：DDX43 在 hap1 啟動子去抑制而活化。〔論文〕
- 結論：sCNV 主要是加成效應，但也提供 epimutation 出現的「畫布」；epimutation 影響的調控元件比 sSNV／sDNV 多。〔論文〕
- **相關性：無關。** 主題是染色質與 CN 的關係，沒有 SNV 的 haplotype 分配。〔推論〕

## 4. 作者自己的限制與 Discussion

**Limitations（作者自述）**〔論文〕Limitations of the study：

- 需要更多癌症與正常組織，才能確定這些突變過程能不能推廣。
- 要看非 UV 主導的癌症，才知道衛星是普遍高突變，還是只對 UV 敏感。
- 要更多正常組織 mosaicism 資料，才能分開「正常老化」與「成癌特有」的過程。
- DSA 不是完全完整，部分重複或結構複雜區域仍未解出，某些變異可能仍漏掉。

**Discussion 主要論點**〔論文〕Discussion：

- 框架：long read + diploid 組裝 + 單分子染色質 + graph genome，克服 GRCh38、CHM13 與 pangenome 的限制。
- 衛星是 somatic 突變熱點；控制可突變性後約 3 倍；成因是 UV 損傷或修復，不是衛星特有機制。這和 germline、早期胚胎突變偏好重複區不同（後者是 clock-like 與 gene conversion）。
- Kinetochore 結合區：染色體臂異常斷點符合 MMBIR + kataegis；CDR 內的 sSV 符合 BIR、kataegis 較弱。非癌樣本也有 CDR 的 sSV 富集。
- CDR 表觀改變：變大約 51%、移動約 64.5 kb、合併成一個；可能和染色體錯誤分離有關。
- 端粒：TERT 活化前端粒縮短到交界 1.2 kb 內；端粒縮短到交界可能無法存活。
- Epimutation 影響的開放調控元件比 sSNV／sDNV 多，例如 DDX43。

**作者沒有列、但和我們有關的限制**〔推論〕：

- 只有一位病人、一株細胞株、兩個 passage。
- 沒有親代資料，hap1／hap2 不能對應父源／母源。
- 呼叫流程偏向 fixed／clonal 變異，低頻變異不在分析內。
- hVAF 的計算方法主文沒有寫。
- 兩條都被呼叫、最後仍不確定的 sSNV 有多少，主文沒有寫。

## 5. 對我們的總結

### 和 HP 比例的關係

- **沒有一節直接相關。** 作者沒有計算兩條 haplotype 的 sSNV 數量或比例，沒有檢驗相鄰 SNV 的 haplotype 獨立性，沒有 parent-of-origin，沒有分析 chrX。〔論文〕全文搜尋 maternal、paternal、chrX、LOH 各 0 筆；hap2 只 1 筆（CDR）；〔推論〕
- 本筆記把「直接相關」定義為回答上述四件事之一；依此定義，Results 10 節都不是直接相關。〔推論〕

### 能提供什麼

1. **SNV → haplotype 的指定方法（間接，方法前提）：** read 對到 diploid DSA，SNV 就屬於它所在的 haplotype 座標；兩條都被呼叫時用 Fisher's exact test 指定一條；deletion 區段的錯放呼叫先刪掉。用它的 VCF 算比例時，要知道這些過濾已經做過。〔論文〕Methods「Diploid variant calling」；〔推論〕
2. **「SNV 只在一條 haplotype」的前提（間接）：** 作者在過濾與功能分析都採用這個前提，和我們每個 SNV 只選一條 HP 一致。但這是前提，不是檢驗結果。〔論文〕Methods「Diploid variant calling」、Results「Functional impact…」
3. **SNV 與 CN 的時序實例（間接）：** chr1q hap1 的 hVAF 1.0／0.5 兩群，示範 CN 增加會把 SNV 分成「事件前、事件後」。這支持「分析累積 HP 比例時，要先分開 CN 改變區段」。只有一個區域，不能推到全基因組。〔論文〕Results「Genome-wide map…」；〔推論〕
4. **可再分析的資料：** 程式在 GitHub `StergachisLab/T2T-COLO829BLT-Manuscript`（Zenodo 10.5281/zenodo.22774707），結果有 UCSC trackHub，資料在 SMaHT Data Portal 與 dbGaP。〔論文〕Data and code availability。主文沒有直接寫 sSNV VCF 的檔名或下載位置。〔論文〕全文搜尋
5. **局部群聚的例子：** t(1;3) 斷點旁 23 個 kataegis 突變，和 cis 聚集假說相關，但作者沒給 haplotype。〔論文〕Results「…somatic translocations…」

### 不能提供什麼

- 不能提供 HP1／HP2 的 sSNV 比例（主文沒算）。〔論文〕
- 不能提供父源／母源（沒有親代資料）。〔論文〕
- 不能提供相鄰 SNV haplotype 獨立性的檢驗。〔論文〕
- 不能提供 chrX 的資訊。〔論文〕全文搜尋 chrX 0 筆
- 不能提供「每次突變發生時選 HP 的機率」；作者的資料是累積結果，而且是一株細胞。〔推論〕

### 值不值得讀

- 值得讀方法（2.3、2.4、2.6）與 3.3 的 chr1q 段落：它們決定了「用 COLO829 DSA VCF 再分析 HP 比例」時，哪些偏差已被處理、哪些還在。〔推論〕
- 其餘結果（衛星、著絲點、端粒、染色質）和 HP 比例無關，週會報告可以一句帶過。〔推論〕
- 依 CLAUDE.md，COLO829 實驗已在 11-06 結束；本筆記只整理論文，不提議新實驗。

## 不確定之處

- `fulltext.md` 沒有圖說、Table 1 與補充資料。Figure 1C（CN 圖）、2B（全基因組 hVAF 分布）、2E、S5、S6 的內容沒有看到。
- hVAF 的計算公式主文沒寫；2.5 的定義是推論。
- 「刪掉 deletion 區段的 SNV」刪的是哪條 haplotype 座標上的呼叫，主文沒有逐字說明；2.4 第 5 點是推論。
- Hi-C 在 Verkko 中負責定相，是工具知識，主文沒寫。
- COLO829 donor 的性別主文沒寫（全文 male／female 只出現在其他 donor）。DSA 有「46 條 haploid 染色體」，但主文沒有說 X、Y 的組成。
