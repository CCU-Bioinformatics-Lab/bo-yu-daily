# P13 深讀：補充資料與程式（sSNV 呼叫、haplotype 指定、公開 VCF）

查核日期：2026-11-12。範圍：Methods、補充圖、作者 GitHub 程式、本機公開 VCF。主文結論見同資料夾 `summary.md`。

## 白話總結

- 作者沒有在主文、補充圖或程式裡比較 hap1、hap2 的 sSNV 數量或比例。這篇論文沒有回答「SNV 落在哪條 HP 的機率」。
- hap1、hap2 是 Verkko 組裝的標籤，沒有親代資料。唯一能對上親源的是性染色體：hap1 帶 chrX（男性的 X 來自母親），hap2 帶 chrY。
- 作者的流程會刪掉「整條 haplotype 已流失」區段（DEL）裡的 SNV。所以公開 VCF 裡，流失的那條在這些區段一定是 0 個 SNV。算兩條比例前，要先扣掉 DEL 區段和性染色體。
- Cell 版的補充資料（Document S1）沒拿到：PMC 下載頁有機器人檢查。改拿預印本（bioRxiv v1）的補充圖。預印本 Figure S3 就是 Cell 版的 Figure S5（sSNV 流程）。Cell 版 Figure S6（chr1q 時序）在預印本裡找不到對應的圖。
- 程式和 Methods 大致一致。不一致的地方有三處：DEL 門檻的數字、Fisher 步驟多一條規則、231 對沒解決的重複 SNV 兩邊都保留。

---

## 1. 補充資料：拿到什麼、沒拿到什麼

### 1.1 Cell 版（PMC13722029）：沒拿到

PMC 上的 Cell 版是作者稿（NIHMS2217201）。補充資料只有一個檔：`NIHMS2217201-supplement-1.pdf`（Document S1，Supplemental methods and Figures S1–S12）。〔論文〕efetch JATS `<supplementary-material id="SD1">`

| 試過的網址 | 回應 |
|---|---|
| `https://pmc.ncbi.nlm.nih.gov/articles/instance/13722029/bin/NIHMS2217201-supplement-1.pdf` | HTTP 200，但內容是 1,817 bytes 的 HTML「Preparing to download ...」，要瀏覽器做 proof-of-work 檢查。沒有繞過。 |
| `https://pmc.ncbi.nlm.nih.gov/articles/PMC13722029/bin/NIHMS2217201-supplement-1.pdf` | 404 |
| `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13722029/bin/NIHMS2217201-supplement-1.pdf` | 404 |
| `https://europepmc.org/articles/PMC13722029/bin/NIHMS2217201-supplement-1.pdf` | 403 |
| Europe PMC `.../rest/PMC13722029/supplementaryFiles` | 200，內容是錯誤訊息：`Article with id PMC13722029 is not open access one` |
| NCBI OA service `oa.fcgi?id=PMC13722029` | 404 |
| PMC OA S3 `pmc-oa-opendata/PMC13722029.1/` | 只有 json、txt、xml，沒有補充檔。json 寫 `is_pmc_openaccess: false`、`license_code: TDM` |
| Cell 網站 `cell.com/cell/fulltext/...` | 403（Cloudflare 檢查） |

授權補充：Crossref 寫 Cell 正式版（VoR）是 CC BY 4.0。PMC 上的作者稿是 TDM 授權，所以 Europe PMC 不給補充檔。〔實測〕Crossref API、PMC S3 json。`source.md` 寫「CC BY」對正式版成立，對 PMC 作者稿不成立。

**下一步（給使用者）：** 用瀏覽器開 PMC 頁面，手動下載 Document S1，放進 `supp/`。

### 1.2 預印本（bioRxiv 2025.10.10.681725 v1，PMC12632929，CC BY）：拿到

來源：PMC OA S3 `https://pmc-oa-opendata.s3.amazonaws.com/PMC12632929.1/media-{1..9}.pdf`。9 個檔的 md5 都和 S3 json 列的一致。〔實測〕

存放：`supp/biorxiv_v1_media-1.pdf` … `media-9.pdf`。`.gitignore` 的 `research/**/*.pdf` 已擋（`git check-ignore` 確認）。`supp/` 裡沒有其他格式。

**預印本和 Cell 版的圖號不同。** 對照如下（依圖說內容判斷）：〔補充〕〔推論〕

| 內容 | 預印本 | Cell 版 |
|---|---|---|
| 組裝流程、品質 | S1 | S2 |
| hCN、染色體重排 | S2 | S3 |
| **sSNV 呼叫、過濾、驗證、chr1q 斷點 IGV、hVAF 直方圖** | **S3（A–E）** | **S5（A–E）**：Cell 主文引用 S5A–C（流程、驗證）、S5D–E（chr1q 斷點） |
| **hVAF 分布：依染色體、重複序列、hCN** | **S4（A–C）** | Cell 主文沒引用；可能在 S6 或被移除，未確認 |
| chr1q 時序（S6A–C） | 找不到對應圖 | S6（主文引用「Figure 2E and Figure S6A–C」） |

所以 Cell 版 Figure S6（chr1q 時序）沒看到。預印本主文只有 Figure 2E 示意圖。〔論文〕預印本 JATS

### 1.3 預印本 Figure S3（= Cell S5）：sSNV 流程

〔補充〕`supp/biorxiv_v1_media-3.pdf`（圖與圖說）

- **A 流程：** Passage B 和 Passage A 的 sSNV 候選做 Venn（B 獨有 11,053，14.98%；共有 56,160，76.16%；A 獨有 6,528，8.86%）→「Filter out sSNVs using hCN information」→「Resolve sSNVs using DSG」（Minigraph-Cactus 圖：CHM13、COLO829BL hap1、hap2、GRCh38）→「Apply density-based filtration method」→ 44,795 sSNV、828 sDNV。
- **B：** COLO829BL 有 1–4 條 read 帶腫瘤 allele 時的 SBS 組成。只有 1 條時以 UV 簽名（SBS7a/7b）為主；2 條以上換成 SBS5 等。作者據此只容許 COLO829BL 有 1 條 alt read。
- **C：** 用 ONT、UL-ONT（含 MAPQ1 版本）、Illumina、Element 驗證，依 read 支持數分層，驗證率多在 90–100%。
- **D、E：** chr1 hap1 q12 的 IGV 與 hVAF 直方圖。q 臂（4 份拷貝）有 hVAF 約 0.5 和約 1.0 兩群；chr1 p 臂與 chr3 p 臂只有約 1.0。
- **小差異：** 圖說寫「lime green = chr1 p-arm、salmon = chr3 p-arm」。程式裡顏色是 p-arm-side = salmon、chr3_hap2 = limegreen。〔程式〕`sSNV/_EDA_on_SNVs_main.py:5062-5071,5079,5123` 圖說或程式其中一個標錯，不影響結論。

### 1.4 預印本 Figure S4：hVAF 分布

〔補充〕`supp/biorxiv_v1_media-4.pdf`

- A：每條染色體一格（chr1–22、chrX）。B：依重複序列類別。C：每條染色體 × hCN 1–4。
- 幾乎每格都是 hVAF ≈ 1.0 的單峰。chr1 有明顯的 0.5 峰。
- **分組是「染色體」，不是「haplotype」。** 圖上沒有 hap1、hap2 分開的計數或比例。hCN 欄可以間接區分兩條，但圖沒有標哪條是哪條。〔補充〕〔推論〕

### 1.5 補充資料裡 hap1／hap2 的數量、比例、偏向

- 在預印本 S1–S9 圖說（JATS）、S3、S4 圖面，用 hap1、hap2、haplotype 1、haplotype 2、both haplotypes、ratio 找：**沒有 hap1 對 hap2 的 sSNV 數或比例。**〔補充〕
- 唯一和「兩條都在」有關的數字在主文：位在兩條都保留區域的 sSNV＋sDNV 有 29,189 個。這是總數，沒分 hap1、hap2。〔論文〕Cell 主文「Functional impact」節；預印本相同

---

## 2. sSNV 呼叫與 haplotype 指定的程式

**程式位置：** GitHub `StergachisLab/T2T-COLO829BLT-Manuscript`，commit `4a9a42e`（2026-10-20）。主要檔：`sSNV/_EDA_on_SNVs_main.py`（5,786 行，VS Code `# %%` cell 格式，路徑寫死在作者的叢集上）。只讀不執行。

Permalink 前綴：`https://github.com/StergachisLab/T2T-COLO829BLT-Manuscript/blob/4a9a42eeca00a58295b6627ccd5d01fd38db961b/`

**DeepVariant 本身不在這個 repo。** README 指向 `mrvollger/k-mer-variant-phasing`。〔程式〕`README.md`「Short variants Calling」該 repo（commit `48b34fd`）的規則用 `--model_type=PACBIO`，沒有 haploid 選項；預設版本 1.9.0，可由 config 改。〔程式〕`k-mer-variant-phasing/workflow/rules/vcf.smk:1-35`、`workflow/Snakefile:43` 版本不一致：論文寫 v1.6.1，公開 VCF header 寫 `DeepVariant_version=1.6.0`。〔論文〕〔實測〕

### 2.1 步驟對照（程式 vs Methods）

| # | 步驟 | 程式（`sSNV/_EDA_on_SNVs_main.py`） | 門檻 | 和 Methods 一致嗎 |
|---|---|---|---|---|
| 0 | DeepVariant 分別呼叫 BL、Passage A、Passage B（Fiber-seq，對到二倍體組裝），只留 PASS SNV | 讀入 `:668-678` | PASS | 一致 |
| 1 | 去掉可能組裝錯誤區 | `:720-733` | `Flagger == "Hap"` 且沒有 NucFlag 註記 | 一致（Methods：potentially misassembled regions） |
| 2 | 去掉 BL 有呼叫的；BL pileup 容許 1 條 alt read | `:977-987`、`:1234-1243` | 刪 BL DeepVariant 有呼叫的；刪 BL bcftools mpileup `AD > 1`（2025-06 改成「lenient」版） | 一致（Methods：allow only single alternate allele） |
| 3 | 只留兩個 passage 都有的 | `:1244-1246` | 交集 | 一致 |
| 4 | **刪 DEL 區段的 SNV** | `:1739-1752`（SNV 自身位置 hCN == "DEL"）；DSG 投影後落在 DEL 的：`:1754-1789`、`:1792-1845`；callable BED 名稱就是 `..._100kb-DEL_removed.bed.gz`（`:524-525`） | DEL＝該 haplotype 的 hCN 為 0 | 一致，但門檻數字有誤，見 2.2 |
| 5 | **兩條 haplotype 都被呼叫（DSG 投影後座標重疊）→ Fisher 指定一條** | 找重疊對：`:1848-1874`；UL-ONT：`:1883-1941`；ONT（新馬達蛋白）：`:1949-2013`；未解的：`:2015-2028` | 見 2.3 | 大致一致，程式多一條規則，見 2.3 |
| 6 | 合併：刪 DEL 清單＋Fisher 判輸的 | `:2035-2040` | — | — |
| 7 | 密度過濾 | `:2209-2309`、`:2351-2355` | 1 kb 視窗、每 500 bp 滑動；≥ 3 個 SNV 的視窗合併；視窗內 ≥ 3 個 SNV 的 VAF < 0.75，或 DP 中位數 < 61.5 − 3×√61.5（約 38.0），整窗刪掉 | 一致 |
| 8 | 輸出 Passage B 的紀錄 | `:2363-2390`，檔名 `...shared.scna.dsg.density.filtered.vcf` | — | 公開 VCF 的樣本欄確實是 `COLO829T_PassageB_DSA`〔實測〕 |

### 2.2 DEL 門檻：程式和 Methods 的數字不同

- Methods 寫：分界是 log2(n + 0.5)，DEL 是「≤ –0.415 (log2(0.5))」；後面的分界寫 0.585、1.322、1.848、2.263。〔論文〕Methods「Determining somatic haploid copy number」
- 但 log2(0.5) = –1，不是 –0.415（–0.415 是 log2(0.75)）。log2(3.5) = 1.807，log2(4.5) = 2.170，也和 Methods 的 1.848、2.263 不同。
- 程式用公式算：`breakpoints <- log2((0:4 + 0.5) / 1)`，註解寫 `-1 0.585 1.322 1.807 2.170`。〔程式〕`hCN/CBS_DNAcopy.qmd:281-292`
- **結論：程式符合 Methods 的公式，Methods 的數字寫錯。** 〔推論〕
- **手動指定 DEL：** 程式把 `haplotype2-0000059`（chr1 hap2）整條、`haplotype2-0000068` 前 53 Mb、`haplotype2-0000070`（chr14 hap2）10 Mb 之後設成 DEL，不管 CBS 結果。三段都在 hap2。〔程式〕`hCN/CBS_DNAcopy.qmd:294-312` contig 對染色體：chr1、chr14 來自作者 `hCN/plot_log2hcn.py`（本 repo 11-06 已引用）。Methods 沒提到手動指定。

### 2.3 Fisher 步驟的實際規則

〔程式〕`sSNV/_EDA_on_SNVs_main.py:1883-2028`

1. 用 DSG（vg inject／surject）把每個 sSNV 投到另一條 haplotype 的座標。投影後座標重疊的兩筆視為一對。4,660 對，去重後 2,327 對（`:1873-1874` 註解）。重疊可以是 hap1 對 hap2，也可以是同一條 haplotype 內（segmental duplication）。
2. 每對取 UL-ONT 的 bcftools mpileup 結果，2×2 表 `[[AD₁, AD_REF₁], [AD₂, AD_REF₂]]`，做雙尾 Fisher（scipy 預設）。
3. p < 0.01：odds ratio > 1 → 刪第二筆；< 1 → 刪第一筆。也就是留 alt 比例較高的那筆。
4. **Methods 沒寫的規則：** 如果 pileup 只有其中一筆有紀錄，而且那筆 `AD ≥ 3`，就留那筆、刪另一筆（`:1928-1938`、`:1996-2010`）。
5. 沒解決的，用 ONT（新馬達蛋白）資料重做同樣步驟（`:1949-2013`）。
6. **兩種資料都解決不了的 231 對：兩筆都保留**（`:2015-2016` 註解：「These SNV pairs will be kept in the final filtered set」），之後可能被密度過濾刪掉。這和 Methods「flagged and excluded from certain analyses but retained if not stated」一致。作者畫 hCN 別 hVAF 圖時有排除它們（`:2477`）。
7. mpileup 的指令不在 repo 裡（`:1522` 只有註解「Run bcftools mpileup on this sitelist」）。所以 mpileup 的 MAPQ、base quality 門檻無法確認。repo 另有 `_MAPQ1` 版的 pileup 檔，但 Fisher 步驟用的是非 MAPQ1 版（`:1539-1547`）。

---

## 3. hap1／hap2 的編號

- **組裝方法是 Verkko，不是 hifiasm。** 材料：60× PacBio（Fiber-seq）HiFi、60× ONT（最長的 read 優先）、30× Hi-C。〔論文〕Methods「Building COLO829BL diploid genome assembly」寫 Verkko v2.12；預印本 Table 1 寫 Verkko v2.1。hifiasm 只用在其他捐贈者的 HiFi-only 組裝（ST001–ST004 等）。〔論文〕Methods「Haplotype-resolved genome assembly using PacBio HiFi data」
- **沒有親代資料。** 全文、預印本 JATS、程式 repo 用 maternal、paternal、parent、trio 搜尋：程式裡的命中都是無關字串（例如 `hCN/utils.R:192` 的 `transparent`），沒有親代資料的用法。〔論文〕〔程式〕
- **定相靠 Hi-C。** Verkko 用 Hi-C 定相時，同一條染色體內的 hap 標籤一致，但不同染色體之間的 hap1／hap2 沒有對應關係，等於每條染色體各自決定。〔推論〕根據 Verkko 的 Hi-C 定相設計；論文沒寫，程式也沒有重新命名 haplotype 的步驟（在 repo 用 `haplotype1-`、`rename` 搜尋，沒找到改名步驟）。
- **唯一的親源線索：性染色體。** 預印本 Table 1：hap1 的性染色體是 chrX，hap2 是 chrY。病人是男性，所以 hap1 的 chrX 來自母親、hap2 的 chrY 來自父親。〔補充〕預印本 Table 1；〔推論〕親源 這只對性染色體成立，不能推到體染色體。hap2 的 BUSCO missing 3.14% 偏高，原因就是 hap2 沒有 chrX（Table 1 註腳）。
- **contig 名稱：** `haplotype1-00000NN`、`haplotype2-00000NN`，共 91 條 contig。〔實測〕VCF header 名稱本身沒有染色體編號。作者用 DSA 對 CHM13 的比對來指定染色體（`sSNV/_EDA_on_SNVs_main.py:587-611`），但對照表檔案不在 repo 裡。

---

## 4. 公開 VCF：欄位與座標

**檔案：** `/big8_disk/boyu114/benchmark_data/colo829_t2t_sohn2026/somatic_snvs.vcf.gz`（注意是 `big8_disk`，不是任務寫的 `bip8_disk`）。44,810 筆，比論文的 44,795 多 15 筆，原因未查。〔實測〕

**座標：** COLO829BL DSA v3.0.0（`DSA_COLO829BL_v3.0.0.fasta`），hap1、hap2 contig 放在同一份 FASTA。不是 GRCh38，也不是 CHM13。〔實測〕header 的 `bcftools norm -f .../DSA_COLO829BL_v3.0.0.fasta`

**樣本欄：** `COLO829T_PassageB_DSA`，也就是 Passage B 的 read 數。〔實測〕

### 4.1 欄位意思

| 欄位 | header 定義 | 實際意思 | 本機實測 |
|---|---|---|---|
| CHROM | — | 這個 SNV 在哪條 haplotype 的哪條 contig。**haplotype 就是由 contig 名稱決定。** | hap1 27,410、hap2 17,400 |
| FORMAT/GT | Genotype | DeepVariant 二倍體模型的輸出。read 已分到單條 haplotype，所以 `1/1` 代表 hVAF ≈ 1，`0/1` 代表 hVAF 明顯小於 1（例如 gain 後才發生，或 subclonal）。**不是「兩條 haplotype 的異型合子」。**〔推論〕 | 1/1 38,339；0/1 6,469；1/0 2 |
| FORMAT/DP | Read depth | 這條 haplotype 的深度（read 對到二倍體組裝，只算該 haplotype 的 read） | 11-10 報告：CN1 約 63、CN2 約 120、CN4 約 230 |
| FORMAT/AD | Read depth for each allele | ref、alt 的 read 數 | — |
| FORMAT/VAF | Variant allele fractions | **就是 hVAF**。作者畫 hVAF 圖直接用這欄（`sSNV/_EDA_on_SNVs_main.py:2448,5060`）〔程式〕 | VAF < 0.75：4,926；0.4–0.6：2,820 |
| FORMAT/GQ、PL | DeepVariant 標準 | — | — |
| INFO/Flagger | Flagger Annotation | 組裝品質；`Hap` 代表正常 | 全部是 `Hap` |
| INFO/NucFlag | NucFlag Annotation | 組裝錯誤註記 | 全部沒有（已在步驟 1 刪掉） |
| INFO/CN | 「SCNA identified by CBS algorithm. Only applies to Tumor data」 | **這條 haplotype 在該位置的 hCN**（每條 haplotype 各自算）。來源 `merged_cov_callable_100kb_log2ratio_CBS_wCN_simple.bed.gz` | CN1 11,477；CN2 29,384；CN3 1,914；CN4 1,218；>CN4 817；**DEL 0 筆** |
| INFO/RM、DM、TRF、CpGi | RepeatMasker、DupMasker、TRF、CpG island | 位置註記 | — |

hap × CN 交叉：〔實測〕

| | CN1 | CN2 | CN3 | CN4 | >CN4 |
|---|---:|---:|---:|---:|---:|
| hap1 | 5,368 | 18,748 | 1,304 | 1,218 | 772 |
| hap2 | 6,109 | 10,636 | 610 | 0 | 45 |

### 4.2 本 repo 再分析用的欄位和作者定義對不對得上

- **11-06**（`lab_report/2026-11-06_colo829_hap_snv_ratio/`）：用 CHROM 前綴分 haplotype、用 INFO/CN 標主要 CN。和作者定義一致。〔程式〕`tools/colo829_hap_snv_ratio.py:34-44,94-95`
- **11-10**（`lab_report/2026-11-10_colo829_hp_depth_snv/`）：用 DP 當單條 haplotype 深度，用 INFO/CN 切片段。和作者定義一致（DP、VAF 是 haplotype 層級，作者也這樣用）。
- **11-06 的 README 第一句**把兩條寫成「一條來自爸爸，一條來自媽媽」。生物上對，但檔案裡的 hap1／hap2 不能對到爸爸或媽媽；README 後面也寫了這點。

### 4.3 「刪 DEL 區段」等步驟對兩條比例的影響

1. **DEL 區段一定是 0。** 流失那條在 DEL 區的 SNV 全被刪，VCF 裡沒有任何 `CN=DEL`。生物上，流失那條的 SNV 本來也觀測不到。所以 DEL 區段必須從兩條都扣掉，不能算進比例。〔程式〕〔實測〕〔推論〕
2. **作者的 DEL 區段檔不公開。** VCF 只在有 SNV 的位置標 CN，看不到 DEL 區段的邊界。11-06 用「連續 > 5 Mb 沒有 SNV 就扣掉」近似。小於 5 Mb 的 DEL 會留在分母裡，讓帶小 DEL 的那條密度略低。〔推論〕手動 DEL 三段都在 hap2（2.2 節），11-06 觀察到「≥ 20 Mb 的零 SNV contig 有 7 條，全在 hap2」，兩者方向一致。至於為什麼流失的都標在 hap2，論文和程式都沒說明。
3. **性染色體要分開。** hap1 帶 chrX、hap2 帶 chrY。男性的 chrX 只有一份，SNV 只能落在 hap1。11-06 的全基因組合計包含所有 contig，沒有排除性染色體（`tools/colo829_hap_snv_ratio.py:107-120`）。〔程式〕〔推論〕依長度猜，`haplotype1-0000027`（155.6 Mb，1,730 個 SNV）可能是 chrX，但沒有驗證。成對比較（11-06 第 3 節）不受影響，因為 X 和 Y 長度差太多，不會被配對。
4. **231 對未解的重複 SNV 兩筆都保留。** 如果是 hap1 對 hap2 的對，兩條各多算 1 筆，比例會被拉向 1:1。上限約 462 筆（全部的 1%）。公開 VCF 沒有標記欄位，所以認不出是哪些。〔程式〕〔實測〕header 沒有對應 INFO
5. **Fisher 的勝負看 alt 比例，不看 hap 標籤。** 對 hap1、hap2 沒有系統性偏向。〔程式〕〔推論〕
6. **密度過濾會刪掉 hVAF 低的群聚。** 1 kb 內有 ≥ 3 個 VAF < 0.75 的 SNV 就整窗刪掉。hCN ≥ 2 的區段，gain 後才發生的 SNV hVAF 會小於 1，比較容易被刪。所以拷貝較多那條的「晚期 SNV」可能被少算一點。〔推論〕
7. **只留兩個 passage 共有的 SNV。** 單一 passage 的 subclonal SNV 不在檔案裡。〔程式〕`:1244-1246`

---

## 5. 作者有沒有算過兩條 haplotype 的 sSNV 數或比例

**沒有找到。** 查的範圍：

- 程式 repo 全部 42 個檔（`.py`、`.R`、`.qmd`、`.Rmd`、5 個 `.ipynb`）：用 `startswith("haplotype1`、`haplotype2`、`value_counts`、`groupby` 搜尋。haplotype 前綴只出現在 DEL、DSG 過濾的條件裡（`sSNV/_EDA_on_SNVs_main.py:1772-1833,2136-2201`），沒有用來計數或算比例。〔程式〕
- 唯一按 haplotype 畫的 sSNV 圖是 chr1 hap1 的 p 臂、q 臂和 chr3 hap2 的 hVAF 直方圖（`:5042-5130`）。這是時序分析，不是兩條比較。〔程式〕
- 預印本補充圖 S1–S9 圖說、S3、S4 圖面：沒有。〔補充〕
- Cell 主文：沒有（`summary.md` 已查）。〔論文〕
- **沒查到的：** Cell 版 Document S1（沒拿到）、`mrvollger/SMaHT-DSA-figures`（haplotype 選擇性染色質，README 有連結，沒 clone）、UCSC track hub 的其他軌。

---

## 6. 對本研究的意義

- 這篇不能用來定「SNV 落 HP1 或 HP2 的機率」。作者沒做這件事，也沒有親源。〔論文〕〔程式〕
- 本 repo 11-06、11-10 用的欄位定義正確。要改進的是兩點：全基因組數字要排除性染色體；DEL 區段只能近似。這是一位病人、一株細胞的再分析，COLO829 實驗已在 11-06 結束，不建議重開。〔推論〕
- 作者流程的設計本身，可以當「真實資料的觀測限制」參考：DEL 區段 SNV 全刪、只留共有 SNV、低 hVAF 群聚被刪。這些是觀測端的過濾，模擬器的真值不應該模仿它們（CLAUDE.md：真值和觀測分開）。〔推論〕

## 7. 不確定的地方

1. Cell 版 Document S1 沒拿到。預印本 S3 對應 Cell S5 是靠圖說內容判斷的。Cell S6（chr1q 時序）完全沒看到。
2. Verkko Hi-C 模式「每條染色體各自決定 hap 標籤」是根據工具設計推論，論文沒寫。
3. 公開 VCF 比論文多 15 筆，原因未查。
4. mpileup 的參數不在 repo 裡。
5. `haplotype1-0000027` 是否為 chrX 沒有驗證（要把 contig 比對到 CHM13）。
6. 預印本 Figure S4C 每格的 N 值解析度不夠，沒有逐格抄錄。

## 本次檔案

- 本筆記：`deep_read_supp_code.md`
- 補充 PDF：`supp/biorxiv_v1_media-1.pdf` … `media-9.pdf`（gitignore 已擋）
- 程式 clone（scratch，不進 repo）：`T2T-COLO829BLT-Manuscript` @ `4a9a42e`、`k-mer-variant-phasing` @ `48b34fd`
