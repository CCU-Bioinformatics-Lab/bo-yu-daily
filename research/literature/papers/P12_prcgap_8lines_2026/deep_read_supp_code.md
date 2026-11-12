# P12 PRCGAP 深讀：補充資料、程式、Zenodo 結果檔（2026-11-12）

## 白話總結

- 這篇論文沒有比較兩條 haplotype 的 SNV 數量。補充資料、程式 README、Zenodo 說明都沒有。最接近的是 HCC1954 兩個染色體臂的 APOBEC 簽名比例，那是局部、定性的。
- SNV 的 hap1／hap2 標籤，實際上等於「這個 SNV call 落在哪一條 haplotype 的 contig 上」。條件是至少 1 條 alt read 在比對時被 k-mer 判定為 haplotype-resolved。沒有 read 數門檻。
- hap1／hap2 是組裝編號。8 株細胞株用 Hi-C 或 Pore-C 定相，沒有親代資料。跨染色體的編號是隨機的，所以跨染色體加總不能稱為父源／母源。
- Zenodo 的 SNV 表是「未過濾」的。要重現論文的數字，要自己套過濾條件，而且無法完全重現。本 repo 先前的再分析用的欄位和定義大致一致，只有幾點要補註（見 §4.3）。
- 補充資料（Supplementary Figures PDF、Supplementary Tables xlsx）已下載成功。

標記：〔論文〕bioRxiv v2 主文 `fulltext.md`；〔補充〕v2 補充資料；〔程式〕GitHub 原始碼（附 commit 與行號）；〔Zenodo〕Zenodo README 或 metadata；〔實測〕本次跑指令看到的；〔推論〕本檔推論；〔外部文件〕第三方工具文件。

---

## 1. 補充資料

### 1.1 取得結果

成功。bioRxiv 這次沒有擋。

| 檔案 | 本機路徑 | 大小 | 內容 |
|---|---|---:|---|
| `media-1.pdf` | `supp/media-1.pdf` | 6.4 MB，23 頁 | Supplementary Figures 1–21 |
| `media-2.xlsx` | `supp/media-2.xlsx` | 150 KB，15 個 sheet | Supplementary Tables 1–15 |

- 補充資料頁：`https://www.biorxiv.org/content/10.64898/2026.05.28.728591v2.supplementary-material`，HTTP 200。頁面列出兩個檔：`.../early/2026/07/09/2026.05.28.728591/DC1/embed/media-1.pdf?download=true`、`.../DC2/embed/media-2.xlsx?download=true`。帶瀏覽器 User-Agent 與 Referer 下載，兩個都 HTTP 200。〔實測〕
- 兩個檔都被 `.gitignore` 擋住（`research/**/*.pdf`、`research/**/*.xlsx`）。〔實測〕`git check-ignore`
- 沒有其他格式的檔案。

### 1.2 Supplementary Fig. 11（各株 haplotype 全基因組概觀）

- 內容：7 株（COLO829、H1437、H209、H2126、HCC1937、HCC1954、HG008；H2009 在主文 Fig. 3b）。每條染色體分 haplotype 1（左）、haplotype 2（右）。顏色是拷貝數狀態（gain、neutral、loss、Unassigned），加上 Cen/Sat、SV breakpoint。〔補充〕Supp. Fig. 11 legend
- **點突變只畫 cancer-associated 那幾個**（紫色叉，標基因名），不是全部 SNV。〔補充〕同上
- Zenodo 的 `genomic_overview/{sample}.point_mutations.txt` 就是這張圖畫的點：8 株合計只有 48 列（每株 3–13 個）。〔實測〕`wc -l`
- 結論：這張圖不能拿來看兩條 haplotype 的 SNV 數量。

### 1.3 Supplementary Fig. 12（HCC1954 kataegis）

- 內容：HCC1954 chr5、chr8 兩條 haplotype 的拷貝數、IMD 圖、kataegis 候選（橘色三角形）、SV circos 圖、chr5q 與 chr8q 的 96 型突變光譜。〔補充〕Supp. Fig. 12 legend
- 圖中每條 haplotype 的 SBS2+SBS13 占比（我讀圖上的數字）〔補充〕Supp. Fig. 12d、e：

| 區域 | hap1 | hap2 |
|---|---:|---:|
| chr5 q arm | 46% | 13% |
| chr8 q arm | 0% | 22% |

- kataegis 候選：chr5 在 hap1 約 115 Mb；chr8 在 hap1 約 45 Mb 一處、hap2 多處（約 100–130 Mb）。〔補充〕Supp. Fig. 12a、b（讀圖）
- 這是**簽名占比**，不是 SNV 數量；只有兩個染色體臂，和 chromothripsis 樣重排同區。不能推廣成「SNV 偏向某條 haplotype」。〔推論〕
- 圖上沒有寫 hap1、hap2 的 SNV 總數。〔補充〕

### 1.4 Supplementary Table 9（每株定相比例）

標題：「Haplotype assignment and liftability of somatic mutations」。SNV 部分〔補充〕Supp. Table 9：

| 細胞株 | SNV 總數 | Haplotype assigned | % assigned |
|---|---:|---:|---:|
| COLO829 | 39,877 | 39,187 | 98.3% |
| H1437 | 58,913 | 57,298 | 97.3% |
| H2009 | 144,968 | 138,606 | 95.6% |
| H209 | 30,625 | 29,767 | 97.2% |
| H2126 | 131,697 | 128,184 | 97.3% |
| HCC1937 | 17,744 | 17,430 | 98.2% |
| HCC1954 | 17,358 | 17,244 | 99.3% |
| HG008 | 10,180 | 9,860 | 96.9% |

- **只有「已定相／總數」，沒有拆成 hap1、hap2。** 〔補充〕表的欄位：Sample、Mutation type、Total、Haplotype assigned、% of Haplotype assigned、Liftable to T2T-CHM13、%、Liftable to GRCh38、%。
- 同表也有 indel（定相 ≥99.4%）與 SV（定相 76.0–93.8%）。〔補充〕
- 「Haplotype assigned」有沒有把 homozygous 算進去，表上沒寫。〔補充〕

### 1.5 其他和 haplotype 有關的補充圖表

| 圖表 | 和 haplotype 的關係 | 有沒有 SNV 的 hap1／hap2 數量 |
|---|---|---|
| Supp. Fig. 1c、Table 2 | 組裝的 Hamming／switch error。Pore-C 樣本（BL1437、BL2009、HCC1937BL）是 N/A。HG008N Verkko：Hamming 2.11%、switch 0.59%；其他 Hi-C 樣本 Verkko Hamming 0.19–0.77% | 沒有 |
| Supp. Fig. 3、Table 7 | read 層級：haplotype-resolved、position-only、multi-mapped 的比例 | 沒有 |
| Supp. Fig. 10 | 各株兩條 haplotype 的拷貝數圖 | 沒有 |
| Supp. Table 11 | cancer-associated 突變清單，有 `PRCGAP Contig`（contig 名含 haplotype1／haplotype2） | 只有幾十個 driver，不是全體 |
| Supp. Table 12、13、Fig. 14–16 | SV 的 haplotype（著絲點、端粒） | 沒有 SNV |
| Supp. Table 15 | 組裝工具與定相模式（見 §3） | — |
| Supp. Fig. 18、19 | B-ALL 臨床樣本的 paternal／maternal 拷貝數 | 沒有 SNV 比例 |

搜尋：在 Supp. PDF 文字（`pdftotext`）與 15 個 sheet 裡，用 `bias`、`imbalanc`、`balanced`、`per haplotype`、`between haplotypes`、`proportion`、`equal` 搜尋，沒有找到比較兩條 haplotype SNV 數量的段落。`each haplotype` 只出現在 Supp. Fig. 12 legend。〔實測〕

---

## 2. SNV 怎麼指定 haplotype（程式）

### 2.1 結論

1. **marker 是 haplotype-specific 21-mer。** 只在一條 haplotype 出現一次、另一條沒有的 21-mer。〔論文〕Methods「Haplotype-aware read mapping refinement」；〔程式〕bam_refiner README Step 1
2. **read 先定相，SNV 再看 read。** bam_refiner 把每條 read 放到 k-mer 支持較多的那條 haplotype contig，並寫入 `HP` tag。mutation_postprocess 再看支持 alt 的 read 的 `HP` tag，決定 SNV 的標籤。〔程式〕
3. **`HP` 值等於 read 最後所在 contig 的 haplotype。** 1＝在 hap1 contig、2＝在 hap2 contig、0＝無法判定。〔程式〕bam_refiner `src/refine/write_bam.rs`（v0.3.6 L221–233；HEAD L226–240）
4. 所以一個在 hap1 contig 上的 SNV call，支持 read 只會是 `HP=1` 或 `HP=0`。**標籤實際上等於「SNV 所在 contig 的 haplotype」，前提是至少 1 條 alt read 是 HP=1/2。** 〔程式〕＋〔實測〕：Zenodo 8 株全部 SNV 列，`haplotype1` 標籤只出現在 `haplotype1-*` contig，`haplotype2` 只在 `haplotype2-*`，沒有交叉。
5. **門檻：** read 層級有（見 2.3）；SNV 層級只要 ≥1 條 HP=1 read 就標 hap1，沒有最少 read 數或比例門檻。〔程式〕

### 2.2 程式位置與版本

論文寫的版本：bam_refiner v0.3.6、mutation_postprocess v0.1.3、DeepSomatic v1.8.0。〔論文〕Methods

| 工具 | 論文寫的版本 | 和 Zenodo 檔吻合的版本 | 程式位置 |
|---|---|---|---|
| bam_refiner | v0.3.6 | v0.3.6（`7c38b71`，2026-04-01） | `src/refine.rs`、`src/refine/write_bam.rs` |
| mutation_postprocess | **v0.1.3** | **v0.1.2**（`acf833e`，2026-05-14） | `src/haplotype.rs` |
| PRCGAP 註解步驟 | — | `d6fc851`（2026-07-03）含 `check_homozygous_snv.py` | `workflow/scripts/annotate/` |

**版本不一致要注意：** 〔程式〕〔Zenodo〕
- mutation_postprocess 的 tag v0.1.3 是 2026-07-30（`fad1551`），晚於論文 v2（2026-07-09）與 Zenodo v1.1（2026-07-09）。
- 同一天 PRCGAP 的 `images/pull_images.sh`（`d6fc851`）拉的是 `mutation_postprocess:v0.1.2`。
- v0.1.3 已經不輸出 `homozygous`；PRCGAP 在 2026-08-27（`049a1df`）也把 `check_homozygous` 換成 `check_unassigned`。
- Zenodo 檔有 `homozygous` 標籤，所以它是舊邏輯（v0.1.2＋`check_homozygous`）產生的。〔實測〕＋〔推論〕
- 論文說「PRCGAP-paper」的參考腳本，公開 PRCGAP 註解說是「mirror」它（`workflow/rules/annotate_mut.smk:4–6`）。PRCGAP-paper 本身不在 `yos-sk` 的公開 repo 清單裡（GitHub API `users/yos-sk/repos`，2026-11-12）。所以 Zenodo 確切用的腳本，我看到的是公開鏡像，不是原件。〔程式〕〔推論〕

### 2.3 read 層級：bam_refiner

- 流程：minimap2（HiFi `asm5`、ONT `asm10`）比到 hap1+hap2 串接的參考 → 依 read name 排序 → `bam_refiner refine`。〔論文〕Methods；〔程式〕bam_refiner README Step 2–3
- 每個候選位置（primary／secondary／supplementary）數 read 上符合的 haplotype-specific k-mer。v0.3.6 取數量較多的位置當 primary，`flag=1`（haplotype-resolved）；平手是 `flag=0`（position-only）。〔程式〕bam_refiner v0.3.6 `src/refine.rs:430–628`（例：L463 `if prim_cnt < info.kmer_cnt`）
- v0.3.6 **沒有** 0.8 比例門檻。README：v0.4.0 起才預設 `--ratio-threshold 0.8`、`--min-markers 3`；「Lowering it to 0.5 restores the pre-0.4.0 behaviour, where the winner only had to beat the runner-up」。〔程式〕bam_refiner README「Counting markers and calling a haplotype」
- 沒有 marker 的片段，v0.3.6 有「1 primary + 1 secondary 都是 0 個 k-mer 時，換到 hap1」的特例（`src/refine.rs:407–423`）。這種 read 的 `HP` 是 0。〔程式〕
- `HP` 寫入：`flag==0` → `HP=0`；否則依 contig 屬於 hap1 或 hap2 清單 → `HP=1` 或 `2`。〔程式〕`src/refine/write_bam.rs` v0.3.6 L221–233
- 另產出每條 read 的 k-mer ratio（`kmer-ratio` 子命令）：read 可觀察到的 haplotype-specific 位點中，實際符合的比例。〔程式〕bam_refiner README Step 5

### 2.4 SNV 層級：mutation_postprocess v0.1.2（Zenodo 用的版本）

permalink 基準：`https://github.com/yos-sk/mutation_postprocess/blob/acf833ea28c9c1dfa7d1da41cb78d70273eabdae/src/haplotype.rs`

步驟：
1. DeepSomatic PASS 的 call → 取每個 call 前後 ±100 bp → bwa mem 自我比對（`-a -k 50 -c 1000000`）。〔論文〕Methods「Point mutation calling」
2. identity ≥0.98（`-d 0.98`）且 alt 相同（或互補）的兩個 call 視為同一事件在兩條 haplotype 的重複 call，用 union-find 分群。〔程式〕`haplotype.rs` L130–141（`filter_pair_candidates`、`identical_pair_db`）、L476（`grouping`）
3. `samtools mpileup --output-QNAME` 找出帶 alt 的 read。〔程式〕`collect_mutation_read_id` L200–
4. 在 BAM 上數這些 read 的 `HP`：`cnt_hap1`、`cnt_hap2`、`cnt_unassign`；跳過 secondary。〔程式〕L555–595
5. 判定（**沒有成對的 call**）〔程式〕L855–910：
   - `cnt_hap1 > 0` → 輸出一列 `haplotype1`
   - `cnt_hap2 > 0` → 輸出一列 `haplotype2`（兩者都 >0 會輸出兩列）
   - 兩者都 0、`cnt_unassign > 0` → `unassigned`
6. 判定（**成對／成群的 call**）〔程式〕L633–781：
   - 群內有 call 有 HP1 read、也有 call 有 HP2 read → 兩個 call 各輸出一列，都標 `homozygous`
   - 只有 HP1 → 取 HP1 read 最多的 call，標 `haplotype1`；只有 HP2 同理
   - 都沒有 → 取 unassigned read 最多的那個，標 `unassigned`
7. 每列附上支持 read 的平均 k-mer ratio（`Kmer_ratio` 欄）。沒有 reference k-mer 的 read，ratio 直接設成 `-m 0.8`。〔程式〕`load_kmer_ratio` L161–197（v0.1.2）；HEAD L192–220
   - 〔實測〕HG008 的 677 個 `unassigned` SNV 中，343 個 `Kmer_ratio` 恰為 0.8。〔推論〕這些多半是所有支持 read 都沒有 marker 的位置；它們會通過 `Kmer_ratio ≥ 0.8` 過濾。
8. 註解階段再跑一次 `check_homozygous_snv.py`：兩列 lift 到同一個 GRCh38（或 CHM13）位置、alt 相同、都已定相 → 兩列都改成 `homozygous`；一列定相、一列 unassigned → 留定相那列；兩列都 unassigned → 留 VAF 高的。〔程式〕PRCGAP `049a1df^:workflow/scripts/annotate/check_homozygous_snv.py:112–187`；呼叫順序 `d6fc851:workflow/scripts/annotate/annotate_mut.sh:132–150`（GRCh38 `update` → CHM13 `preserve`）

〔實測〕Zenodo 的 `homozygous` 列，在 hap1 與 hap2 contig 上的數量每株都完全相等（例：COLO829 286／286、HG008 227／227），符合「成對輸出兩列」。

### 2.5 和論文 Methods 對照

| Methods 寫的 | 程式行為 | 一致？ |
|---|---|---|
| marker：21-mer，一條出現一次、另一條沒有 | 同（meryl difference + count==1） | 一致 |
| 「k-mer coverage ratio 門檻 0.8」過濾假陽性 | mutation_postprocess 的 `-m 0.8` 只是「無 marker read 的預設值」，不是過濾。過濾在下游，靠 `Kmer_ratio ≥ 0.8` | 意思一致，但位置不同；Zenodo 檔**沒有**套這個過濾 |
| 只有一條 haplotype 的 read 支持 → 指定那條 | 同；且門檻是 ≥1 條 read | 一致；Methods 沒寫「≥1 條就算」 |
| 兩條都有支持 → homozygous | 對**單一 call**，程式會輸出 hap1、hap2 各一列，不叫 homozygous；只有**成對 call** 或 lift 到同位置時才標 homozygous | 部分不一致 |
| 都沒有才 unphased | 程式標籤叫 `unassigned` | 一致（用詞不同） |
| mutation_postprocess v0.1.3 | Zenodo 對應 v0.1.2 行為 | 版本號不一致 |
| bam_refiner v0.3.6 的 read 定相 | v0.3.6 只要求 k-mer 數最多，沒有 0.8 比例門檻 | Methods 沒寫 read 層級門檻 |

〔推論〕在單一 call 上「hap1、hap2 都有 HP read」實際很難發生，因為 `HP` 跟著 contig 走（§2.1 第 4 點）。

---

## 3. hap1／hap2 編號怎麼來

### 3.1 結論

- **8 株細胞株的 hap1／hap2 是組裝工具的任意編號，跨染色體沒有一致的親源。** 跨染色體加總 hap1 不能稱為父源或母源。（O1）
- 證據有三層：外部文件明講（hifiasm）、論文的定相方式、本 repo 實測。程式和作者文件沒有直接說明。

### 3.2 組裝與定相方式

- Zenodo 檔用的參考：8 株都是 **Verkko** 組裝（COLO829BL v2.1、HCC1954BL v2.0、HG008N v2.2 由 GIAB 組裝、其餘 v2.2.1）。〔Zenodo〕README「Samples」
- 定相模式〔補充〕Supp. Table 15：
  - Hi-C：COLO829BL、BL209、BL2126、HCC1954BL、HG008N
  - Pore-C：BL1437、BL2009、HCC1937BL（只用 Verkko）
  - Trio：只有 B-ALL 的 UTPT2T-02、UTPT2T-04
- 論文 Methods 說 hifiasm 與 Verkko 都跑了；Zenodo 結果用 Verkko。〔論文〕Methods「De novo assemblies」；〔Zenodo〕README
- 主文提到 paternal／maternal 的地方，只在 B-ALL（NH-ALL-001 用 iDMR 甲基化指定，UTPT2T 用 trio）。〔論文〕Results「Application of PRCGAP to clinical sequencing data」、Methods「Parent-of-origin analysis」。在 `fulltext.md` 用 `paternal` 搜尋，只有 L111、L113、L158 三處，都是 B-ALL。〔實測〕

### 3.3 編號是否每條染色體各自決定

- 〔外部文件〕hifiasm README（Hi-C 模式）：「contigs from different parental chromosomes are randomly mixed as it is just not possible to phase across chromosomes with Hi-C」，另說「phasing across centromeres is challenging」。來源：`https://github.com/chhylp123/hifiasm` README（2026-11-12 取得）。
- Verkko README 只寫 Hi-C／Pore-C 模式用 rukki 定相，沒有提到跨染色體編號。〔外部文件〕`https://github.com/marbl/verkko` README，用 `paternal`、`chromosome`、`arbitrar`、`consistent` 搜尋，只找到 trio 段落。
- 〔推論〕Hi-C／Pore-C 的接觸訊號只能把同一條染色體的片段連在一起，Verkko 也一樣不能跨染色體決定親源。
- 〔實測〕本 repo 的 HG008 對照：PRCGAP 和 GIAB 的 haplotype，23 條染色體有 14 條編號相反、9 條相同；容許整條對調後 97.4% 一致。`lab_report/2026-11-07_hg008_giab_hap_concordance/`。注意 GIAB 用的是另一份正常組裝（HG008-N v6.3），所以這是兩份組裝互相比，不是和親源比。
- 在 PRCGAP、bam_refiner、mutation_postprocess、assembly_workflow、prcgapdoc 的 README 與程式，用 `paternal`、`maternal`、`parent`、`arbitrar`、`random`、`swap`、`consistent across` 搜尋，沒有找到關於細胞株 hap1／hap2 親源的說明（只有 trio 模式的參數）。〔實測〕
- 安全的分析單位：**contig 或同一條染色體內**。著絲點兩側也可能斷開（hifiasm README 的說法）。〔推論〕

---

## 4. Zenodo 結果檔的欄位定義

### 4.1 版本

- 論文引用的 DOI `10.5281/zenodo.21231495` 是 v1（2026-07-08，單一 tarball）。本機下載的是 `21271691` = v1.1（2026-07-09，每株一個 tarball）。兩者同一個 concept record `21231494`。〔Zenodo〕API metadata；〔實測〕`manifest.tsv`
- Zenodo README 只列 `copynumber`、`genomic_overview` 的欄位，**沒有** `point_mutation` SNV 表的欄位定義。〔Zenodo〕README「Contents by analysis type」

### 4.2 SNV 表 `{sample}.deepsomatic.snv.annotated_checked_gnomad.txt`（33 欄）

欄位意義主要由程式推回，因為 Zenodo README 沒寫。

| # | 欄位 | 意義 | 來源 |
|---:|---|---|---|
| 1–3 | `Contig`、`Start`、`End` | 正常組裝上的位置（0-based BED）。contig 名 `haplotype1-*`／`haplotype2-*` 即所屬 haplotype | 〔程式〕`add_lift_coords.py`；〔實測〕 |
| 4–5 | `Ref`、`Alt` | 組裝座標上的鹼基 | 〔程式〕 |
| 6–8 | `GRCh38_contig`、`_pos`、`_status` | coordconv lift 結果；status = Match／Gap／Overlap／No_chain_info／Unspecified | 〔程式〕`add_lift_coords.py:82–110`；〔實測〕 |
| 9–11 | `chm13_*` | 同上，T2T-CHM13 | 同上 |
| 12–13 | `GRCh38_flag`、`chm13_flag` | 同一個變異是否也被 GRCh38／CHM13 版 DeepSomatic 叫到。公開 PRCGAP 在 Zenodo 當時尚未實作，輸出 `-`；Zenodo 檔是 True／False，所以來自原版 PRCGAP-paper 腳本 | 〔程式〕`d6fc851:add_lift_coords.py:1–16`；〔論文〕Methods「matched against GRCh38- and T2T-CHM13-based DeepSomatic calls」 |
| 14–15 | `VAF`、`Depth` | 腫瘤 VAF 與深度（DeepSomatic） | 〔程式〕 |
| 16–17 | `Normal_VAF`、`Normal_depth` | 正常樣本的 VAF／深度。**Zenodo 檔全是 0**，正常深度過濾無法重建 | 〔實測〕HG008 28,267 列全為 0 |
| 18 | `ID` | call 的 ID；homozygous 的兩列 ID 不同 | 〔實測〕 |
| 19 | **`Haplotype`** | `haplotype1`、`haplotype2`、`homozygous`、`unassigned`。規則見 §2.4 | 〔程式〕 |
| 20 | `Kmer_ratio` | 支持 alt 的 read 的平均 k-mer ratio；無 marker 的 read 記 0.8 | 〔程式〕§2.4 第 7 點 |
| 21–24 | `liftoff_gene`、`liftoff_gene_info`、`cgc`、`cmrg` | 基因註解 | 〔程式〕`add_annotation_mut.py` |
| 25–26 | `rmsk_class`、`rmsk_type` | RepeatMasker | 〔程式〕 |
| 27 | `contig_size` | contig 長度 | 〔程式〕 |
| 28 | `misassembly` | 是否落在 hap1 或 hap2 misassembly BED | 〔程式〕`add_annotation_mut.py:236` |
| 29 | `centromere` | cenSat 類別 | 〔程式〕 |
| 30–31 | `segdup`、`segdup_similarity` | segmental duplication | 〔程式〕 |
| 32 | `point_mutation_other` | 另一個 caller（ClairS）在同 contig、同位置、同 alt 也有 call → True | 〔程式〕`d6fc851:add_annotation_mut.py:312–345` |
| 33 | `gnomAD` | gnomAD v4.1＋ToMMo 註記；`-` = 沒有 | 〔程式〕`add_annotation_mut.py:404–440`；〔論文〕Methods |

**`Haplotype` 欄的實際分布**〔實測〕（未過濾，列數）：

| 細胞株 | haplotype1 | haplotype2 | homozygous | unassigned |
|---|---:|---:|---:|---:|
| COLO829 | 33,629 | 24,666 | 572 | 1,009 |
| H1437 | 39,324 | 48,704 | 1,672 | 1,980 |
| H2009 | 94,703 | 99,065 | 4,500 | 6,958 |
| H209 | 32,468 | 27,052 | 1,050 | 1,269 |
| H2126 | 94,267 | 81,569 | 2,376 | 3,863 |
| HCC1937 | 15,055 | 49,057 | 1,980 | 900 |
| HCC1954 | 15,812 | 19,232 | 574 | 347 |
| HG008 | 13,951 | 13,185 | 454 | 677 |

這張表是未過濾、跨染色體加總，**不能**解讀成偏向，理由見 §3。

**Zenodo 檔是未過濾的。** 用可重建的條件（`Depth ≥ 10`、`VAF ≥ 0.05`、`misassembly = False`、`Kmer_ratio ≥ 0.8`、`gnomAD = -`），HG008 得 10,677、COLO829 41,463、HCC1954 18,594、H2009 150,671。Supp. Table 9 是 10,180、39,877、17,358、144,968。接近但不相等，差在正常深度與 normal DeepVariant germline 過濾無法重建。〔實測〕

### 4.3 和本 repo 再分析的欄位是否一致

對照 `tools/prcgap_hap_snv_ratio.py:44–54`、`tools/prcgap_snv_vs_hap_depth.py:86`：

| 項目 | 再分析的做法 | 和作者定義比 |
|---|---|---|
| 用 `Haplotype` 欄、只取 `haplotype1`／`haplotype2` | 排除 `homozygous`、`unassigned` | 一致。排除 homozygous 合理：它們是同一位置兩條 contig 各一列 |
| 用 contig 名判斷 haplotype（`snv_vs_hap_depth.py` 要求 contig hap = `Haplotype`） | 同時檢查兩者 | 一致；實測兩者永遠相同 |
| `Kmer_ratio ≥ 0.8` | 有用 | 一致。但「無 marker read 記 0.8」會讓 marker-poor 區的 call 通過，README 沒提 |
| `Depth`、`VAF`、`misassembly`、`gnomAD` | 有用 | 一致 |
| `Normal_depth ≥ 10` | 無法用（全 0） | 已在 README 註明 |
| `point_mutation_other = True`、`GRCh38_flag = True` | 額外要求 | 作者論文的過濾沒有這兩條。定義已確認：前者是 ClairS 也叫到，後者是 GRCh38 版 DeepSomatic 也叫到。後者會排除 GRCh38 無法 lift 的 SNV（著絲點、segdup 等），所以再分析的樣本偏向 standard-reference 可及區 |
| hap1／hap2 跨染色體 | 用 20 Mb 平衡區段，兩條各自比較 | 合理，沒有跨染色體加總成親源 |

需要補到再分析 README 的一句〔推論〕：「`GRCh38_flag = True` 會排除 PRCGAP-unique 的 SNV（約 23%，集中在著絲點與 segdup），結果只代表兩套參考都叫得到的區域。」

`copynumber/{sample}.hap{1,2}.copynumber.txt` 欄位 `chrom, contig, index, tumor_depth, normal_depth`，Zenodo README 有寫。〔Zenodo〕`tumor_depth` 是 50 kb bin 的深度總和（再分析除以 50,000 當平均深度），README 沒寫單位；這是再分析的解讀。〔實測〕數值量級（例：18,059,629）符合總和。〔推論〕

---

## 5. 作者有沒有算過兩條 haplotype 的 SNV 數或比例

**沒有找到。** 查過的地方與關鍵字：

| 來源 | 查法 | 結果 |
|---|---|---|
| 主文 `fulltext.md` | `bias`、`imbalanc`、`per haplotype`、`each haplotype`、`between haplotypes`、`proportion` | 只有 kataegis、iDMR 方法、B-ALL 親源（整條染色體增減，不是 SNV），以及一篇引用文獻（Bielski 2018）的標題 |
| Supp. PDF（21 張圖） | 同上，加讀 Fig. 11、12 legend 與 Fig. 12 圖面 | 只有 Fig. 12 的兩個染色體臂的 SBS2/13 占比 |
| Supp. xlsx（15 個表） | 逐表看欄名 | Table 9 只有「已定相／總數」 |
| PRCGAP、mutation_postprocess、bam_refiner、prcgapdoc README 與程式 | 讀 README；`grep` haplotype 相關 | 只有定相方法，沒有統計 |
| Zenodo README 與 metadata | 全文讀過 | 只有目錄與欄位，沒有統計 |

〔推論〕作者的問題是「personalized reference 能不能做 haplotype 解析的體細胞變異偵測」，不是「SNV 偏向哪條 haplotype」。本 repo 的 8 株比例是再分析，不是作者結論（O2）。

---

## 6. 對本研究的意義

- 這篇論文不能直接給「每個 SNV 落在 HP1 的機率」。它給的是：一套可以把 SNV 放到 contig 層級 haplotype 的方法、8 株的未過濾結果、和 97% 左右的定相率。〔推論〕
- 再分析要守的三條：只在同一條染色體（或 contig）內比兩條；控制拷貝數；把它當「累積結果」，不是每次突變的發生機率（O4）。〔推論〕
- 若要回答父／母源，需要另外的親源指定（例如論文用在 B-ALL 的 iDMR 甲基化），細胞株作者沒做。這是一個可能的方向，帶到週會前要先問：結果能不能改變模擬器的決定。〔推論〕

## 7. 不確定的地方

1. Zenodo 檔確切由哪一版腳本產生。我根據 `homozygous` 標籤、日期、`pull_images.sh` 推斷是 mutation_postprocess v0.1.2＋`check_homozygous`。原版 PRCGAP-paper 腳本沒有公開，無法逐行核對。
2. `GRCh38_flag`、`chm13_flag` 的確切比對規則（位置容差、alt 比對）。公開程式在當時沒有實作，只能依 Methods 一句話解讀。
3. Supp. Table 9 的「Haplotype assigned」是否把 `homozygous` 算一次或兩次；表上沒寫。
4. Verkko Hi-C／Pore-C 模式下，同一條染色體的兩臂是否保證同一編號。只有 hifiasm README 的間接說法，和 HG008 一株的實測。
5. Supp. Fig. 12 的百分比是我讀圖得到的；kataegis 位置是目視估計。
6. bam_refiner v0.3.6 的 read 層級判定，我讀了關鍵段落（`refine.rs:407–628`），沒有逐行追完所有分支。

## 8. 下載的程式碼（只讀，未執行）

放在 scratchpad，不進 repo：`/tmp/claude-1024/-bip8-disk-boyu114-main-work/1df43c96-c6de-4089-8e4a-e2268cdbfecf/scratchpad/gh/`

| repo | HEAD（2026-11-12） |
|---|---|
| `yos-sk/PRCGAP` | `9f0fd86c915bc9905ef2551179c9331f7cc244c9` |
| `yos-sk/mutation_postprocess` | `fad155168874dd7b15ed76599e8a257e487c0fce`（v0.1.2 = `acf833ea28c9c1dfa7d1da41cb78d70273eabdae`） |
| `yos-sk/bam_refiner` | `3249b80792efdb5cf67bcd49f9dbd91560ba97cb`（v0.3.6 = `7c38b7141a08bc38dc6f151bef6624b9e7215fd9`） |
| `yos-sk/prcgapdoc`、`yos-sk/assembly_workflow` | 只用來搜尋說明 |
