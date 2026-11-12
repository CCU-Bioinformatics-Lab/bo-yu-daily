# P12 PRCGAP 主文深讀筆記

- 論文：Sakamoto Y, …, Shiraishi Y. "Personalized reference genome-based pipeline reveals comprehensive haplotype-resolved views of cancer genomes." bioRxiv 2026.05.28.728591 v2（預印本，未同儕審查）。
- 讀取範圍：`fulltext.md` 全部（Abstract、Introduction、Results 10 節、Discussion、Methods、Data／Code availability、Footnotes）。補充圖表未讀。
- 讀取日期：2026-11-12。起點是同資料夾 `summary.md`（11-11），每項已回原文核對；差異見 §6。

## 白話總結

這篇是一篇**方法論文**。作者用每個病人自己正常細胞的 diploid 組裝當參考，取代 GRCh38／T2T-CHM13，讓 SNV、SV、拷貝數、甲基化都能標上 haplotype，並找回標準參考漏掉的著絲點、端粒、segmental duplication 區域的變異。

**它沒有回答「somatic SNV 落在 HP1 或 HP2 的比例」。** 主文沒有比較任何一株兩條 haplotype 的 SNV 數量，也沒有檢定相鄰 SNV 是否獨立。主文唯一把 SNV 和特定 haplotype 連起來的結果，是 HCC1954 的局部 kataegis，而且是定性描述。

它仍值得讀，理由有三：（1）它定義了我們再分析時用的 hap1／hap2 標籤怎麼來（組裝編號，不是父母源）；（2）它公開了 8 株的 haplotype 層級 SNV 與 CN 結果；（3）TP53／KRAS 的例子提醒我們：最後看到的 haplotype 分布是突變加 CN／LOH 的累積結果。

---

## 1. 作者要解決什麼問題

**結論：** 作者要補的缺口是「沒有一條整合流程，能在同一個 personalized diploid reference 上同時做 point mutation、SV、CN、甲基化的 haplotype 解析，而且還沒有人系統性地用在臨床樣本」。〔論文〕Introduction 第 3 段

- 標準參考（GRCh38、T2T-CHM13）在高度重複區與個人特有序列上很難呼叫變異。作者把這些區域稱為 genomic "dark matter"：著絲點、segmental duplication、端粒序列、族群或個人差異區。〔論文〕Introduction 第 1 段
- Long read（HiFi、ONT-UL）加上 trio、Hi-C 或 Pore-C 定相，已能用 hifiasm、Verkko 做出近乎完整的 diploid 組裝。〔論文〕Introduction 第 2 段
- 前人已用正常樣本的 de novo 組裝當參考，改善 somatic 呼叫，也減少 SV 假陽性。但前人的缺點是：只分析單一樣本、沒有提供流程，或流程只處理一類變異（例如 SV）。〔論文〕Introduction 第 3 段
- 作者原話：這樣的整合流程 "has not yet been established"。〔論文〕Introduction 第 3 段
- Discussion 重申同一缺口：前人只處理 "a single sample or a single class"。〔論文〕Discussion 第 1 段
- 作者的動機**不是**演化、克隆結構或 haplotype 偏向。全文搜尋 phylogen、timing、purity 沒找到；evolution 只出現在參考文獻標題。〔論文〕全文關鍵字搜尋

## 2. 作者怎麼解決（流程）

下表照流程順序寫。〔論文〕Results「Personalized reference genome-based cancer genome analysis pipeline (PRCGAP)」；Methods 各節

| 步驟 | 做什麼 | 工具 | 資料 |
|---|---|---|---|
| 1. 組裝 | 用 matched normal 做 diploid 組裝；刪除 < 100 kb 的 contig | hifiasm、Verkko；下游採用 Verkko | HiFi、ONT-UL |
| 2. 定相 | 組裝時直接分出兩條 haplotype | Hi-C：HCC1954BL、NH-ALL-001、BL209、BL2126；trio（yak／merqury）：UTPT2T-02、UTPT2T-04；Pore-C（只 Verkko）：BL1437、BL2009、HCC1937BL | Hi-C、Pore-C、親代短讀 |
| 3. 組裝評估 | contiguity、QV、BUSCO、misassembly、switch error | yak、Flagger、Inspector、NucFlag、compleasm、yak trioeval、pstools | HiFi、ONT |
| 4. 註解 | 基因、重複、segdup、著絲點／satellite | liftoff、RepeatMasker、SEDEF、alphaAnnotation | 組裝本身 |
| 5. 座標轉換 | 個人參考 ↔ GRCh38／T2T-CHM13，分 liftable／non-liftable | minimap2 asm5、transanno、coordconv | 組裝 |
| 6. haplotype-aware mapping | 每條 read 分成 haplotype-resolved、position-only、multi-mapped | minimap2（asm5／asm10）、bam_refiner；marker 是每條 haplotype 只出現一次、另一條沒有的 21-mer | 腫瘤與正常 long read |
| 7. point mutation | 呼叫 somatic SNV／indel，再指定 haplotype | DeepSomatic v1.8.0（PACBIO model）、mutation_postprocess | HiFi |
| 8. SV | 呼叫 somatic SV，每個 breakpoint 各自定相 | nanomonsv、nanomonsv_postprocess | ONT |
| 9. CN | 50 kb bin 的腫瘤／正常 depth ratio，分 haplotype | samtools depth（-Q 40） | HiFi |
| 10. 甲基化 | CpG 甲基化 | pb-CpG-tools、modkit | HiFi、ONT |
| 11. parent-of-origin | trio 樣本組裝時就有親源；非 trio 用 iDMR 甲基化把每個 contig 指給父或母 | iDMR catalog + chain file | 正常樣本甲基化 |

### SNV 怎麼指定 haplotype（和我們最相關的一步）

〔論文〕Methods「Point mutation calling」、「Filtering and annotation of point mutations」

1. 每個 SNV 取 ±100 bp 序列，在兩條 haplotype 間比對，找出對應位置（相似度門檻 0.98）。
2. 用 21-mer marker 篩掉支持 read 的 k-mer coverage ratio < 0.8 的 SNV，避免 mismapping。
3. 看支持 read 在 mapping 時被指定到哪條 haplotype：
   - 只來自一條 → 指定 haplotype1 或 haplotype2。
   - 兩條都有 → 記為 homozygous（兩條都有）。
   - 都沒有被指定 haplotype → 才記 unphased。
4. 過濾：腫瘤與正常 depth 都 ≥ 10、VAF ≥ 0.05、排除 misassembly 區；用 DeepVariant 的 germline 呼叫去掉參考差異造成的假變異。
5. liftover 後兩條 haplotype 落在同一位置的 SNV，也標為 homozygous。

- 〔推論〕hap1／hap2 是組裝輸出的 haplotype 編號。只有 trio 樣本的編號等於父／母。Fig. 1f 圖說寫 "hap1)/paternal (pat)"，這只適用 trio 樣本。8 株細胞株都不是 trio。
- 〔推論〕作者沒有說明 Hi-C／Pore-C 定相的 hap1 是否跨染色體指同一位親代。主文沒寫。依 hifiasm／Verkko 的一般行為，跨染色體一致性不保證。repo 的 HG008 比對（23 條中 14 條編號和 GIAB 相反，`lab_report/2026-11-07_hg008_giab_hap_concordance/`，本筆記未重新核對）也支持這點。
- 〔推論〕「兩條都有 → homozygous」這條規則，會把真正的 cn-LOH 後雙份突變，和少數 read 被錯指 haplotype 的情況，都歸到同一類。主文沒有拆開討論。

## 3. Results 逐節

### 3.1 Personalized reference genome-based cancer genome analysis pipeline (PRCGAP)

- **問題：** 流程長什麼樣。
- **內容：** read 分三類；somatic 呼叫用 haplotype-resolved 與 position-only read；定相只用 haplotype-resolved read；position-only read 會在另一條 haplotype 產生重複的 unphased call，流程用兩條 haplotype 的側翼序列比對合併。〔論文〕本節
- **結論：** 每個變異自動標 haplotype、基因組特徵、liftover 座標。
- **和 HP 比例：間接相關。** 它定義了 SNV 的 haplotype 標籤怎麼產生，是我們用 Zenodo 資料再分析的前提。

### 3.2 Construction and evaluation of personalized reference genomes

- **問題：** 組裝品質夠不夠當參考。
- **數字：**〔論文〕本節
  - 總長約 3 Gb；N50 中位數 hifiasm 110.9 Mb、Verkko 145.7 Mb。
  - QV 中位數 60.5（hifiasm）、60.7（Verkko）。
  - T2T 染色體中位數 9（4–15，hifiasm）、16（7–23，Verkko）。
  - switch error 中位數 0.17%（hifiasm 0.04–0.72%；Verkko 0.06–0.63%）；Hamming error 中位數 0.59%（hifiasm 0.15–1.26%；Verkko 0.19–2.11%）。
  - 每條 haplotype 中位數 99.7%（98.4–99.9%）組裝正確；正確組裝的著絲點中位數 35 個。
- **結論：** 兩個組裝器都夠好；Verkko 連續性較高，下游用 Verkko。
- **注意：** Methods 說 pstools（Hi-C 樣本用）會低估 switch error。〔論文〕Methods「Evaluation of genome assembly」
- **和 HP 比例：間接相關。** switch error 決定 hap 標籤在一條染色體內有多可靠；Hamming error 0.59% 代表少量位置的 hap 標籤可能對調。〔推論〕

### 3.3 Haplotype-aware mapping to the personalized reference genomes

- **問題：** 多少 read 能定 haplotype。
- **數字：** 中位數 78.1% haplotype-resolved、19.9% position-only、1.9% multi-mapped；對 T2T-CHM13 時 multi-mapped 是 7.1%。rDNA 與高相似 segdup 仍多 multi-mapped。〔論文〕本節
- **結論：** 個人參考加 marker 能降低 multi-mapping。
- **和 HP 比例：間接相關。** 約兩成 read 沒有 marker。SNV 只要有一條 haplotype-resolved 支持 read 就能定相，所以 SNV 層級的定相率比 read 層級高。〔推論〕

### 3.4 Somatic variant detection in cancer cell lines

- **問題：** PRCGAP 能找回多少標準參考找到的變異，又多找了什麼。
- **數字：**〔論文〕本節
  - SNV 中位數 35,251（10,180–144,968）；indel 中位數 4,635（916–8,252）；SV 中位數 382（61–1,106）。
  - **> 95% 的 SNV 與 indel 可定相（phasable）**；> 74% 可 liftover。SV 可定相 76.0–93.8%。
  - 和 GRCh38／T2T-CHM13 重疊率中位數：SNV 96.4%、indel 91.8%、SV 86.7%。
  - Illumina k-mer 驗證：SNV 支持率中位數 99.1%（89.4–99.6%）、SV 97.0%；只有 PRCGAP 找到的 SNV 為 93.3%。
  - PRCGAP 獨有：SNV 中位數 23.4%、SV 32.6%，集中在著絲點與 segdup。
- **結論：** PRCGAP 找回多數標準變異，獨有變異大多可信。
- **和 HP 比例：間接相關。** 本節只報「可不可定相」，**沒有**報 hap1 與 hap2 各多少。逐株 hap1／hap2 數量可能在 Supplementary Table 9（主文只說它是 phasability 統計，未讀）。
- 〔推論〕驗證只用 VAF ≥ 0.15 的 SNV（Methods「Validation of somatic variants」，作者說是為了排除 subclonal）。低 VAF SNV 的可信度沒有被同一方法檢驗。

### 3.5 Genomic overview of cancer cell lines

- **問題：** haplotype 層級整合 CN、SV、驅動突變能看到什麼。
- **數字與結論：**〔論文〕本節
  - 找回 56 個已知驅動突變中的 46 個（82.1%）；漏掉的 10 個中 8 個 GRCh38 也漏。
  - TP53：8 株中 7 株有突變，野生型那條都失活。5 株（H1437、H209、H2009、H2126、HCC1937）是突變那條增加、野生型丟失；HG008 是野生型丟失、突變那條單份（hemizygous LOH）；HCC1954 兩條都有 TP53 突變。
  - KRAS：H2009（G12A）、HG008（G12V）突變那條拷貝數增加，增加區邊界有 SV breakpoint。
  - HCC1954：chr5 hap1 與 chr8 hap2 有 chromothripsis 樣的 CN 振盪與密集 breakpoint；同區有 kataegis 候選，C>T、C>G 集中在 chr5 hap1 q 臂與 chr8 hap2 q 臂；signature 為 SBS2、SBS13（APOBEC）。
- **和 HP 比例：**
  - TP53／KRAS 部分：**間接相關。** 這是選擇後的驅動基因，不是中性 SNV。它示範 CN／LOH 會決定最後看到哪條 haplotype 帶突變（突變那條被放大、另一條丟失）。這支持「觀察到的 haplotype 比例是累積結果」的說法（O4）。〔推論〕
  - HCC1954 kataegis 部分：**直接相關，但只是局部、定性。** 它顯示一串 APOBEC SNV 集中在同一條 haplotype 的一段（cis 聚集），表示這類局部 SNV 彼此不獨立。主文沒有給叢集大小、SNV 數或 hap 比例（細節在 Supplementary Fig. 12，未讀）。〔論文〕本節；〔推論〕
  - 〔推論〕kataegis 的偵測方法是**先分 haplotype**再算 inter-mutation distance（Methods「Kataegis and mutational signature analysis」：每條 haplotype、每個臂各自的 VCF）。所以「叢集落在單一 haplotype」有一部分是方法設計決定的，不是獨立檢定兩條 haplotype 混雜的叢集後得到的結果。

### 3.6 Variants involving centromere regions in cancer cell lines

- **問題：** 著絲點裡的 somatic 變異有什麼特徵。
- **數字：** 6 株（排除 HCC1954、HG008，因為可用著絲點 < 30／46）。CDR 的 somatic SNV 速率是著絲點側翼 unique 區的 4.3 倍。〔論文〕本節；Methods「Somatic SNV rate analysis in centromere regions」
- **SV 例子：** H2009 chr20 hap1 active HOR 內 496 bp 的 solo L1 插入；H209 chr5 hap1 isochromosome 5p，保留 CDR；H2126 chr10 hap2、chr8 hap1、chr19 hap2 的複雜重排，CDR 往 q 臂移。〔論文〕本節
- **結論：** PRCGAP 能偵測與解讀著絲點相關 SV；多數這些 SV 標準參考測不到。
- **和 HP 比例：無關。** 這是「位置」對突變速率的影響，不是「哪條 haplotype」。Methods 說每條 haplotype 分開算 class，但主文只報兩條合併後的倍數。〔論文〕Methods；〔推論〕

### 3.7 SVs involving telomere sequences in cancer cell lines

- **問題：** 端粒相關 SV。
- **數字：** 8 株共 13 個：端粒相關易位 4、subtelomeric SV 7、含端粒的 single breakend 2；其中 11 個只有 PRCGAP 找到。H2009 有 chr14 hap2 端粒和 chrX hap2 q 臂的易位，接點保留 282 bp 端粒重複。H2126 chr14 q 臂端粒有約 75 kb 的 haplotype 間重組，hap1 是模板，作者認為像 break-induced replication。〔論文〕本節
- **和 HP 比例：無關。** SV 不是 SNV。〔推論〕唯一延伸：腫瘤內 haplotype 間重組會讓一段序列的 hap 標籤和組裝不一致；這屬於 LOH 類事件，不在 SNV-only 範圍。

### 3.8 L1 source site detection in cancer cell lines

- **問題：** 用個人參考找 L1 插入的來源位點。
- **數字：** 427 個 solo L1、142 個 partnered TD、52 個 orphan TD；190 個（44.5%）solo L1 找到來源；共 63 個 active source site，其中 17 個 GRCh38 與 T2T-CHM13 都沒有。H2009 已知來源的 48 個 TD 中 45 個（93.8%）指對。〔論文〕本節
- **和 HP 比例：無關。** 對象是 retrotransposition，不是 SNV。

### 3.9 Application of PRCGAP to clinical sequencing data

- **問題：** 流程能不能用在臨床樣本；兒童 B-ALL 染色體丟失／增加有沒有親源偏向。
- **數字：** 3 例 B-ALL：SNV 1,071–1,542、indel 260–494、SV 19–30；染色體數 26（NH-ALL-001，near-haploid）、46（UTPT2T-02，DUX4 重排）、65（UTPT2T-04，hyperdiploid）。〔論文〕本節
- **parent-of-origin：**〔論文〕本節
  - NH-ALL-001（Hi-C 定相 + iDMR 指定親源）：除 chr6、10、21、X 外每條都丟失一份；丟失哪個親源**隨染色體不同**。1q gain 在母源 haplotype，breakpoint 落在 HSat 區。
  - UTPT2T-04（trio）：除 chr1、7、9、13、15、19、X 外都增加；chr10、21 兩個親源都增加；三體染色體中父源、母源都有。另有父源 1q gain。
  - 作者結論：和 "random parental origin" 的既有報告一致，imprinting 不是主因。〔論文〕Discussion 第 2 段
- **和 HP 比例：間接相關。**
  - 對象是**整條染色體的 CN**，不是 SNV；病種是兒童 B-ALL，不是我們的固態腫瘤細胞株（O3）。只有 2 例，沒有統計檢定。
  - 它提供兩樣可用的東西：iDMR 甲基化指定 contig 親源的方法；以及「染色體層級親源丟失是隨機的」的小樣本例子。
  - chrX：兩例的 chrX 都沒有變化（NH-ALL-001 保留、UTPT2T-04 未增加）。主文沒有任何 chrX 上 SNV 的分析。全文搜尋 chrX／chromosome X 只出現在 H2009 端粒易位與這兩句。

### 3.10 IGH::DUX4 fusion gene structure in a pediatric B-ALL sample

- **問題：** UTPT2T-02 的 IGH::DUX4 融合中，DUX4 片段來自哪個 D4Z4 單位。
- **數字：** 來自母源 chr4 27 個 D4Z4 單位中的第 4 個（identity > 0.999），是內部 pseudogene，不是遠端完整 DUX4。這組變異在 235 個組裝中只見於東亞（10/54）。T2T-CHM13 沒有 identity > 0.995 的對應單位。〔論文〕本節
- **和 HP 比例：無關。**

## 4. 作者承認的限制與未來方向

〔論文〕Discussion 第 4–5 段

**限制（作者原文列三點）：**
1. 腫瘤與正常都要深度 long read，通常要 HiFi + ONT-UL + Hi-C／Pore-C／trio。成本、操作、計算量高，還要新鮮冷凍樣本的高分子量 DNA。
2. 組裝的 haplotype switch error 雖少，但會影響受影響區域的 haplotype 解析。
3. 缺 haplotype marker 的區域（rDNA、高相似 segdup）仍難解。

**未來方向：**
- 用 pangenome reference 取代逐人組裝，降低負擔。
- ONT-only 的 diploid 組裝（hifiasm、加 read correction 的 Verkko）可減少資料種類。
- 作者把 PRCGAP 看成走向「完整 diploid 基因組臨床定序」的早期例子，要從細胞株延伸到臨床。

**作者沒有列、但對我們重要的限制：**〔推論〕
- 沒有討論 hap1／hap2 在非 trio 樣本跨染色體不等於親源。
- 沒有討論兩條 haplotype 的 SNV 數量差異，也沒有考慮 CN 對「可觀察 SNV 數」的影響。
- 8 株都是細胞株，經長期培養；全文搜尋 purity 沒找到。

## 5. 對我們的總結

### 能提供

| 項目 | 內容 | 用途 | 來源 |
|---|---|---|---|
| hap 標籤定義 | SNV 依支持 read 的 21-mer haplotype 指定；hap1／hap2 是組裝編號 | 再分析 Zenodo 前必須知道的前提 | 〔論文〕Methods「Point mutation calling」 |
| 資料 | 8 株的 haplotype 層級 SNV／indel、SV、CN、overview，放在 Zenodo 10.5281/zenodo.21231495 | 自己算兩條 haplotype 的比例（標「再分析」） | 〔論文〕Data availability |
| 前提條件 | CN／LOH 會改變一條 haplotype 上能看到的 SNV（TP53、KRAS 例） | 再分析時要排除 LOH、CNA 區，或分層 | 〔論文〕Results「Genomic overview」；〔推論〕 |
| 局部 cis 例子 | HCC1954 的 APOBEC kataegis 集中在單一 haplotype 的一段 | 和 repo 11-07「< 1 kb 有局部 cis」方向一致，是定性旁證 | 〔論文〕Results「Genomic overview」 |
| 親源方法 | iDMR 甲基化可把 contig 指給父或母 | 理論上可把細胞株的 hap1／hap2 轉成父／母；作者沒對細胞株做 | 〔論文〕Methods「Parent-of-origin analysis」 |
| 定相品質 | switch error 中位數 0.17%、Hamming 0.59% | 估計 hap 標籤錯誤的上限量級 | 〔論文〕Results「Construction and evaluation」 |

### 不能提供

- **每株兩條 haplotype 的 SNV 比例。** 主文沒有。全文搜尋 "proportion"、"ratio"、"balance" 都沒有用在 hap1 對 hap2 的 SNV 比較。〔論文〕全文關鍵字搜尋
- **相鄰 SNV 是否獨立的檢定。** 主文沒有。kataegis 是先分 haplotype 再找叢集，不是獨立性檢定。
- **SNV 的 parent-of-origin。** 親源分析只做在 B-ALL 的整條染色體 CN。
- **chrX 上 SNV 的 haplotype。** 沒有。Methods 只說男性樣本的性染色體在 CN 分析時併到對應 haplotype。〔論文〕Methods「Copy-number analysis」
- **每次突變發生時選哪條的機率。** 細胞株只看最後狀態，觀察值是累積結果（O4）。〔推論〕
- **跨染色體加總成父源／母源。** 8 株都不是 trio，不能這樣做（O1）。〔推論〕

### 值不值得讀

**和 HP 比例的直接答案：無關。** 作者問的是「個人參考能不能做完整的 haplotype 解析、找回 dark matter 變異」，不是「SNV 偏向哪條 haplotype」。

**仍值得讀。** 我們的 8 株 hap 比例再分析（`lab_report/2026-11-06_prcgap_hap_snv_ratio/`、`lab_report/2026-11-10_prcgap_snv_vs_hap_depth/`）直接用它的輸出。不讀 Methods，就不知道 hap 標籤的來源、homozygous 標籤的意義、VAF ≥ 0.05 的過濾，也不知道結果只有 trio 樣本能當親源。週會報告時應寫：「作者沒有分析 SNV 的 haplotype 比例；我們的數字是再分析。」

## 6. 和 11-11 `summary.md` 的差異與不確定處

- `summary.md` 寫「8 株用 Hi-C 或 Pore-C 定相」。Methods 的組裝一節只列 7 個正常細胞株的定相法（Hi-C：HCC1954BL、BL209、BL2126；Pore-C：BL1437、BL2009、HCC1937BL；外加臨床的 NH-ALL-001）。**COLO829BL 與 HG008 沒有列在任何一類。** COLO829BL 的組裝取自 SMaHT，HG008 的正常組裝取自 GIAB（另有十二指腸 Hi-C）。主文沒說作者有沒有自己重組裝這兩株，也沒說它們的定相方法。〔論文〕Methods「Publicly available sequence data」、「De novo assemblies」
- Results 說下游用 Verkko 組裝。COLO829BL 與 HG008 若用聯盟提供的組裝，組裝器可能不同；主文沒寫。〔推論〕
- 定相品質的 switch error 只對「有 Hi-C 或 trio 資料」的樣本評估（"when applicable"）。Pore-C 樣本是否評估，主文沒說清楚。〔論文〕Results「Construction and evaluation」
- 著絲點 SNV 速率「每條 haplotype 分開算」，但主文只報合併倍數；Supplementary Fig. 13 是否有分 haplotype 的結果，未讀。
- 「兩條都有 → homozygous」的 SNV 比例，主文沒報。它可能來自 cn-LOH，也可能來自 read 錯指；兩者在再分析時都會影響 hap 比例的分母。〔推論〕
- 補充資料（Supplementary Table 9、Fig. 11、12、13）未讀；本筆記對它們的內容只依主文的一句引用推測。
