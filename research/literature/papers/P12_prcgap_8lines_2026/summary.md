# P12｜PRCGAP：8 株癌細胞株在正常細胞自身組裝上做 haplotype 解析的體細胞變異；作者沒有比較兩條 haplotype 的 SNV 數量

## 論文與結論

Sakamoto Y, Ochi Y, Kogure Y, …, Kato M, Shiraishi Y. **Personalized reference genome-based pipeline reveals comprehensive haplotype-resolved views of cancer genomes.** *bioRxiv* 2026.05.28.728591（v2，2026-07-09）. DOI：[10.64898/2026.05.28.728591](https://doi.org/10.64898/2026.05.28.728591)。作者 24 位（依 citation_author meta 計數）。

- 同儕審查：否（bioRxiv preprint）。預印本也是論文，先讀作者的問題與結論，再用它的資料（O2）。
- 讀取層級：全文（bioRxiv v2 HTML 轉文字）；補充資料未下載，Supplementary Fig. 11、12 與 Table 9 沒看到。
- 查核日期：2026-11-11。

**作者回答的問題：** 用每位病人「正常細胞的 diploid 組裝」當參考，能不能一次做完 SNV、SV、拷貝數、甲基化的 haplotype 解析，並找回標準參考漏掉的變異。〔論文〕Abstract、Introduction

**作者的主要結論：**〔論文〕

1. 和 GRCh38／T2T-CHM13 的結果重疊率中位數：SNV 96.4%、indel 91.8%、SV 86.7%。另有 23.4% 的 SNV、32.6% 的 SV 只有 PRCGAP 找到，集中在著絲點與 segmental duplication。（Results「Somatic variant detection」）
2. 著絲點的 CDR（推定的 kinetochore 位置）體細胞 SNV 速率是旁邊 unique 區的 4.3 倍。只用 6 株；HCC1954、HG008 因可用著絲點太少而排除。（Results「Variants involving centromere regions」）
3. haplotype 層級看抑癌基因與致癌基因：7/8 株 TP53 突變都伴隨野生型那條失活（5 株是突變那條增加、野生型丟失；HG008 是 hemizygous LOH；HCC1954 兩條都有突變）；H2009、HG008 的 KRAS 突變那條拷貝數增加。（Results「Genomic overview」）
4. HCC1954 的 chr5 hap1 q 臂、chr8 hap2 q 臂有 chromothripsis 樣重排，同區有 kataegis（APOBEC，SBS2／SBS13）。**這是全文唯一一處把 SNV 和特定 haplotype 連起來的結果，而且是局部、定性的。**
5. Parent-of-origin 只做在小兒 B-ALL 臨床樣本，對象是**整條染色體的丟失與增加**，不是 SNV：NH-ALL-001 用 imprinted DMR 甲基化指定每個 contig 的親源，丟失的染色體親源隨染色體不同；UTPT2T-04 用 trio 組裝，增加的染色體爸媽都有。作者據此支持「親源隨機、imprinting 不是主因」的既有說法。（Results「Application of PRCGAP to clinical sequencing data」；Methods「Parent-of-origin analysis」）

| 查核軸 | 結果 |
|---|---|
| 樣本 | 8 對腫瘤／正常細胞株：H1437、H2009、HCC1937（CASTLE）、COLO829（SMaHT）、HG008（GIAB）、H209、H2126、HCC1954（新定序）；另 3 例小兒 B-ALL |
| 定序資料 | long read：PacBio HiFi、ONT-UL；phasing 用 Hi-C、Pore-C 或 trio；Illumina 只做驗證 |
| 親代資料與定相方法 | 8 株細胞株**沒有親代資料**，用 Hi-C 或 Pore-C 定相；hap1／hap2 是組裝編號。Fig. 1f 圖說的「hap1/paternal、hap2/maternal」只適用 trio 樣本。只有 B-ALL 有親源（trio 或 iDMR 甲基化） |
| SNV 怎麼放到 haplotype | DeepSomatic 呼叫後，看支持 read 的 haplotype（21-mer marker）：只來自一條就指定那條；兩條都有記為 homozygous；都沒有才 unphased。>95% SNV 可定相 |
| 突變類型 | SNV、indel、SV、haplotype CN、甲基化 |
| 對本問題（SNV 落哪條）的方向 | 作者**沒有**比較每株兩條 haplotype 的 SNV 數量，也沒有檢定（主文；補充資料未讀）。只有 HCC1954 的局部 kataegis |
| 證據類型 | 資料可用（Zenodo 每株結果），結論要自己再分析 |

## 對本研究的意義

- **作者沒有回答「SNV 偏向哪條 HP」。** 本 repo 的 8 株比例是再分析，不是作者結論。〔repo〕`lab_report/2026-11-06_prcgap_hap_snv_ratio/`、`lab_report/2026-11-10_prcgap_snv_vs_hap_depth/`
- **hap1／hap2 不能跨染色體加總成父源／母源（O1）。** 沒有親代資料，編號在每條染色體各自決定。HG008 和 GIAB 比對，23 條有 14 條編號相反。〔實測〕`lab_report/2026-11-07_hg008_giab_hap_concordance/`
- **SNV 的 haplotype 是累積結果（O4）。** 作者只看細胞株最後的狀態，不能直接推每次突變發生時選哪條的機率。拷貝數變化、LOH 會改變一條 haplotype 上能看到的 SNV 數。〔推論〕
- **作者的 iDMR 甲基化方法可以替 contig 指定親源**，正常樣本也有甲基化資料。理論上可用在細胞株，把 hap1／hap2 換成爸／媽。作者沒有對細胞株做，可行性未查。〔論文〕Methods；〔推論〕
- 著絲點 CDR 的 SNV 富集是位置效應，和 HP 選擇無關；第一階段 SNV-only 模擬不需要。〔推論〕

## 深讀結果（2026-11-12）

詳細筆記：`deep_read_main.md`（主文逐節）、`deep_read_supp_code.md`（補充資料、程式、Zenodo 欄位）。補充資料已下載到本機 `supp/`（不進 repo）。

**作者在解決什麼問題：** 標準參考（GRCh38、T2T-CHM13）和病人的基因組不同，著絲點、segdup 區的變異會漏掉或錯放，也無法替變異標上 haplotype。作者的解法是用病人正常細胞的 diploid 組裝當參考。這是**方法論文**，問的是「能不能完整、haplotype 解析地看到體細胞變異」，**不是**「SNV 偏向哪一條 haplotype」。〔論文〕Introduction、Discussion

**和 HP 比例的關係：**
- **直接回答：沒有。** 主文、補充圖 1–21、補充表 1–15、程式 README、Zenodo 說明都沒有比較兩條 haplotype 的 SNV 數或比例。〔論文〕〔補充〕〔程式〕關鍵字 bias、imbalanc、per haplotype、between haplotypes
- **最接近的一處：** HCC1954 的 kataegis 落在 chr5 hap1 q 臂、chr8 hap2 q 臂（補充圖 12）。但叢集是在每條 haplotype 的 VCF 上分開找的，所以「落在單一 haplotype」有一部分是方法造成的。〔論文〕Methods「Kataegis」
- **間接有用（方法前提）：**
  - hap1／hap2 是組裝編號。8 株都用 Hi-C 或 Pore-C 定相，沒有親代資料。〔補充〕表 15（COLO829BL、HG008N 是 Hi-C 模式）
  - SNV 的 hap 標籤＝ call 落在哪條 haplotype 的 contig；至少 1 條 alt read 被 k-mer 判定即可，沒有 read 數門檻。〔程式〕`mutation_postprocess src/haplotype.rs`、`bam_refiner src/refine/write_bam.rs`
  - 沒有 marker 的 read，`Kmer_ratio` 直接記成門檻值 0.8，所以會自動通過 ≥ 0.8 的過濾。〔程式〕`mutation_postprocess/src/haplotype.rs:54、210-211`
  - 補充表 9 只有「已定相／總數」（95.6–99.3%），沒有拆成 hap1 和 hap2。〔補充〕
  - parent-of-origin 只做在兒童 B-ALL 的整條染色體 CN，不是 SNV。〔論文〕

**對本 repo 再分析的影響：**
- 再分析用的 Zenodo 欄位，和作者程式的定義一致。〔程式〕
- 再分析多加了 `GRCh38_flag=True`，所以排除了只有 PRCGAP 找到的 SNV（約 23%，集中在著絲點和 segdup）。這要在 `lab_report/2026-11-06_prcgap_hap_snv_ratio/` 註明。〔推論〕
- Zenodo 檔可能由 `mutation_postprocess` v0.1.2 產生（有 `homozygous` 標籤），Methods 寫的是 v0.1.3。〔程式〕〔推論〕
