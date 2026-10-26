# 03 Long read 與 haplotype-aware 模擬器調查

調查日期：2026-10-24。範圍：能從「haplotype 分開、clone 混合」的腫瘤基因組產生 ONT／PacBio read，並留下每條 read 的 haplotype 真值的程式。

證據標記：〔論文〕論文或文件的描述；〔程式〕讀過原始碼；〔推論〕本調查的推論，沒有實際執行。所有程式只讀不跑。

## 結論

> **2026-10-24 範圍更正：VISOR 已移出。** 篩選標準是「輸出最終能當 PhyClone 這類 bulk 建樹軟體的輸入，而且真值能直接對應 clone tree」。VISOR 沒有樹，只能當 read 模擬的零件。 下文保留原始調查內容，排名只作紀錄。見 [README「範圍更正」](README.md)。〔程式〕

1. **沒有任何公開工具能一次完成「clone tree → haplotype-specific SNV／CN → long read BAM → per-read 真值」。** 每個工具只做其中一段。〔推論〕
2. **VISOR（HACk + LASeR）最接近需求。** 它能混合多個 clone，並在 BAM 寫入 `CL`（clone）與 `HP`（haplotype）tag。但它沒有樹、沒有 seed、purity 用 reference read 補，CN 只能用 haplotype 內的 tandem duplication／deletion 表示。〔程式〕
3. **HeteroGenesis 是唯一能依 clone tree 產生 haplotype-specific SNV 與 CN FASTA 的現成程式。** 但它原本是給 short read（w-Wessim）用，而且沒有 seed。〔程式〕
4. **建議：自己寫 tree + haplotype 基因組產生器，再接 Badread 或 PBSIM3（都有 `--seed`）。** VISOR 的 LASeR 只當作參考實作，用來學它的 tag 與 merge 做法。〔推論〕
5. LongPhase-S、ClairS 的 purity 資料是「真實 read 混合」，不是模擬。它們沒有 clone tree。〔論文〕〔程式〕

### 排名表（依對本研究的用處）

| 排名 | 工具 | 角色 | clone／tree | haplotype SNV | CN | purity < 1 | per-read 真值 | seed | 授權 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | VISOR（HACk＋LASeR） | 基因組編輯＋long read BAM | 多 clone 混合，無樹 | 有（每條 haplotype 分開 BED） | tandem dup／deletion | 有，但補 reference read | `CL`、`HP` tag；read 名稱 `c{clone}h{hap}` | 無 | LGPL-3.0 |
| 2 | HeteroGenesis | tree-aware 基因組產生器 | 有（`structure` 參數寫親代） | 有 | 有（segment、aneuploidy、WGD） | 有（`freqcalc`） | 無 read | 無 | GPL-3.0 |
| 3 | Badread | read 引擎 | 無 | 無 | 無 | 無 | header 有 contig、strand、起訖 | 有 | GPL-3.0 |
| 4 | PBSIM3 | read 引擎（ONT／CLR／HiFi） | 無 | 無 | 無 | 無 | MAF 對位檔 | 有 | GPL-2.0 |
| 5 | NanoSim（metagenome mode） | read 引擎，多基因組依比例 | 用「物種」當 clone-haplotype | 無 | 無 | 用 abundance 表示 | read 名稱帶來源位置 | 有 | NOASSERTION |
| 6 | ClairS synthetic sample 流程 | 真實 BAM 混合 | 無 | 用另一個體的 germline 當 somatic | 無 | 有 | 無 | 未確認 | ClairS：BSD-3；訓練 repo：無授權 |
| 7 | smrest `simulation.rs` | pileup 層模擬 | 無（只有 CCF 分布） | 有 | 無 | 有 | 無 read | 無 | MIT |
| 8 | Sim-it | SV＋long read | 無 | 無（只有 SV heterozygosity） | 有限（dup） | 無 | 未確認 | 無 | Apache-2.0 |
| 9 | Squigulator／seq2squiggle | raw signal | 無 | 無 | 無 | 無 | read ID 帶真實位置（Squigulator） | 未確認 | MIT |
| 10 | SURVIVOR simreads、DeepSimulator、pysubsimtree、tHapMix | 不適用或過舊 | — | — | — | — | — | — | 見各節 |

## 各工具

### VISOR（HACk、SHORtS、LASeR、XENIA）（已移出，見上方更正）

- Repo：https://github.com/davidebolo1993/VISOR，HEAD `a889e59`（2024-10-21），LGPL-3.0。論文：Bolognini et al., *Bioinformatics* 2020。〔程式〕〔論文〕
- HACk 把 BED 列出的變異寫進每條 haplotype FASTA。支援 `SNP`、`MNP`、`deletion`、`tandem duplication`、`inversion`、translocation 等 15 種。〔程式〕`VISOR/HACk/HACk.py:330`
- HACk 會**跳過同一 haplotype 上重疊的變異**，只保留第一個。所以不能在一次執行中，把 SNV 放進一段被複製的區域。〔程式〕`HACk.py:134-149`
- 推論：要表達「SNV 在 CN 前發生」，要跑兩次 HACk：第一次放 SNV，第二次以第一次的 FASTA 當 genome 放 duplication。座標會偏移，要自己換算。〔推論〕
- LASeR 的 `-s` 可給多個資料夾。每個資料夾是一個 subclone，`--clonefraction` 給各 clone 百分比，總和必須是 100。〔程式〕`VISOR/VISOR.py:113,136`；`LASeR.py:555-571`
- LASeR 把 clone 的百分比**平均分給資料夾內每個 `.fa`**（`c.fperc=c.cperc/len(c.ffiles)`）。若某 clone 用多一個 FASTA 表示整條染色體增加，覆蓋度會被錯誤稀釋。〔程式〕`LASeR.py:595-615`
- BED 第 5 欄是 purity。purity < 100 時，剩下的覆蓋度從 **reference FASTA** 取 read，不是從 normal haplotype 取。這些 read 沒有 germline het SNP，會干擾 phasing。〔程式〕`LASeR.py:191-206`
- 推論：要模擬 normal 汙染，應另建一個「只有 germline SNP 的 normal clone 資料夾」，用 `--clonefraction` 給比例，BED 的 purity 欄設 100。〔推論〕
- read 由 Badread 產生，再用 minimap2（`map-ont`／`map-pb`）對回 reference。〔程式〕`LASeR.py:153,342`
- `--tag` 會在 BAM 加 `CL`（clone 編號）與 `HP`（haplotype 編號）。read 名稱前綴是 `c{clone}h{hap}`。〔程式〕`LASeR.py:138-139,244`
- Badread 指令**沒有傳 `--seed`**。結果不能重現。SHORtS 的 wgsim 則寫死 `seed=0`。〔程式〕`LASeR.py:153`；`SHORtS.py:296`
- 先例：SVCFit（KarchinLab，HEAD `1d3488a`，2026-10-07）用 VISOR 做多 clone SV 模擬，真值是每個 clone 一個 BED（`c1.bed`、`c2.bed`、`c3.bed`）。看起來是 short read 用途。〔程式〕https://github.com/KarchinLab/SVCFit/tree/main/inst/extdata/examples

### HeteroGenesis

- Repo：https://github.com/GeorgetteTanner/HeteroGenesis，HEAD `4c9a142`（2021-08-25），GPL-3.0。論文：Tanner et al., *Bioinformatics* 2019。〔程式〕〔論文〕
- 參數 `structure` 用「clone, 出現時間, 親代」描述樹，例如 `"clone1,0.2,germline,clone2,0.8,clone1"`。〔程式〕`example.json`
- 每個 SNV、indel、CNV、aneuploidy 事件都有 `hap` 欄位。CN 增加時，haplotype 會分裂成 `A`、`A1`、`A2`…，後續變異跟著複製。〔程式〕`heterogenesis_vargen.py:285-383,533-547`
- 每個 clone、每條染色體、每個 haplotype copy 各寫一個 FASTA（`prefix+clone+chrom+hap.fasta`）。〔程式〕`heterogenesis_varincorp.py:517`
- `freqcalc.py` 依 clone 比例與 purity 算 bulk VAF。輸入格式見 `example_clones.txt`（germline 0.2、clone1 0.65、clone2 0.15）。〔程式〕〔論文〕
- 沒有 seed 設定（grep 不到 `seed`）。〔程式〕
- 推論：它的 FASTA 輸出可直接餵 Badread／PBSIM3，但不能直接餵 LASeR（一條染色體一個檔，與 LASeR 的平均分配假設衝突）。〔推論〕

### Badread

- Repo：https://github.com/rrwick/Badread，HEAD `e2ccccc`（2026-07-24），GPL-3.0。〔程式〕
- 有 `--seed`。〔程式〕`README.md:170,194`
- read header 寫入 contig、strand、起訖位置、`length`、`read_identity`。read 名稱本身是隨機 UUID。〔程式〕`badread/simulate.py:73-99`
- 有 `nanopore2023` error／qscore model，也可自訓 model。〔程式〕

### PBSIM3

- Repo：https://github.com/yukiteruono/pbsim3，HEAD `35ce0de`（2025-04-22），GPL-2.0。PBSIM2 repo 最後 push 2023-07-22。〔程式〕
- 有 `--seed`。〔程式〕`src/pbsim.cpp:268,5747`
- 每次輸出 `*.maf.gz`，記錄每條 read 與來源序列的對位。這可當 per-read 真值。〔程式〕`README.md:47`
- `--strategy templ` 可對自己給的模板序列產生 read。〔程式〕`README.md:152-168`

### NanoSim（metagenome mode）

- Repo：https://github.com/bcgsc/NanoSim（現轉到 `BirolLab/NanoSim`），HEAD `1ae603e`（2026-03-12），GitHub 授權欄為 NOASSERTION。〔程式〕
- metagenome mode 吃一個 genome list 與 abundance 表。abundance 表可有多個 sample 欄，每欄總和 100，首列是每個 sample 的 read 數。〔程式〕`README.md:515-585`
- 推論：把每個「clone × haplotype copy」當一個物種，就能用一張表產生多 sample bulk。但 abundance 以 read 數計，不是 DNA 量；要自己換算。〔推論〕
- 有 `--seed`。〔程式〕`src/simulator.py:2110,2200`
- read 名稱帶來源染色體與位置（例：chromosome XI、position 115406、strand R）。〔程式〕`README.md:692`
- 預訓練 model 多為 R9.4、Guppy 3.x，比我們的資料舊。〔程式〕`README.md:93-99`

### ClairS synthetic sample（真實 BAM 混合）

- ClairS repo：https://github.com/HKU-BAL/ClairS，BSD-3-Clause，push 2026-09-11。訓練流程：https://github.com/HKU-BAL/ClairS-series-model-training，無授權檔，push 2026-06-30。〔程式〕
- 流程用 `clairs.py split_bam` 與 `mix_chunk_bam`，把兩個 GIAB 個體（例如 HG003／HG004）的 BAM 依 `SYNTHETIC_COV` 與 purity 混合。另一個體獨有的 germline variant 當作 somatic 真值。〔程式〕`clairs/clairs_ss_model_training_workflow.sh:24,75-86,160-181`
- 沒有 clone tree，沒有 CN。所有「somatic」都是 clonal。〔推論〕
- 用處：可借它的切塊混合程式，做「真實 read 背景＋可控 purity」。〔推論〕

### smrest `simulation.rs`

- Repo：https://github.com/jts/smrest，MIT，最後 commit `eb49ad7`（2024-03-04）。〔程式〕
- 在一條染色體上產生兩條 germline haplotype，再在每條 haplotype 上放 somatic 變異。每個 somatic 位點抽 CCF，read 數按 purity × CCF 抽。輸出含 `haplotype` 與 `hvaf` 欄位。〔程式〕`src/simulation.rs:157-214`
- 每個位點獨立模擬，沒有 read 共現、沒有 CN、沒有樹。RNG 是 `ThreadRng`，沒有 seed。〔程式〕
- 用處：它的 phased／unphased likelihood 比較，可當 L1 計數層的對照。〔推論〕

### Sim-it

- Repo：https://github.com/ndierckx/Sim-it，HEAD `723754e`（2026-05-19），Apache-2.0。論文：Dierckxsens et al., *Genome Biology* 2021。〔程式〕〔論文〕
- 產生 SV 與 ONT／PacBio read。只有 SV 的 `Heterozygosity` 參數，有 `haplotype1`、`haplotype2` 變數。〔程式〕`Sim-it1.4.5.pl:96-101,462`
- 論文明說不模擬 clonal 結構。`srand()` 沒有固定 seed。〔論文〕〔程式〕`Sim-it1.4.5.pl:2361`

### Squigulator 與 seq2squiggle

- Squigulator：https://github.com/hasindu2008/squigulator，MIT，push 2026-03-04。輸入 FASTA，輸出 BLOW5 signal。read ID 編入真實位置，例 `S1_33!chr1!225258409!225267761!-`。〔程式〕README
- seq2squiggle：https://github.com/ZKI-PH-ImageAnalysis/seq2squiggle，MIT，push 2026-06-04。由 FASTA 產生 read 與 signal。〔程式〕README
- 推論：只有要測 basecaller 影響時才需要。對 PhyClone 輸入沒有額外好處。〔推論〕

### 其他（不適用或過舊）

- SURVIVOR `simreads`：https://github.com/fritzsedlazeck/SURVIVOR，MIT，push 2023-12-01。只吃單一 FASTA，沒有 haplotype 或 clone。〔程式〕README
- DeepSimulator：https://github.com/liyu95/DeepSimulator，無授權檔，push 2020-10-20。〔程式〕
- pysubsimtree：https://github.com/dustincys/pysubsimtree，無授權檔，push 2018-10-25。有樹（node `1`、`1.1`），但接 art_illumina（short read）。〔程式〕README
- tHapMix：https://github.com/Illumina/tHapMix，NOASSERTION，push 2026-04-20。用真實 Illumina read 做 haplotype 混合，有 purity、ploidy、多 clone。是 short read。〔論文〕
- LongPhase-S：https://github.com/CCU-Bioinformatics-Lab/longphase-s，GPL-3.0，push 2026-10-20。是分析工具，不是模擬器。preprint 用 `samtools view -s` 與 `samtools merge` 混合真實 tumor／normal ONT BAM，purity 1.0、0.8、0.6、0.4、0.2。資料是同樣 6 個細胞株。〔論文〕https://www.biorxiv.org/content/10.1101/2025.11.20.689492

## 建議的串接流程

目標：產生同時有 clone tree、HP-specific SNV／CN、read 共現與 phasing 誤差的資料，最後轉成 PhyClone 輸入。

1. **產生樹與事件（自寫）。** 在樹的每條邊放 SNV 與 CN 事件，每個事件指定 haplotype（HP1／HP2）與 segment。germline het SNP 取自 GIAB HG002 phased VCF，或我們細胞株的 normal。可參考 HeteroGenesis 的 haplotype copy 分裂邏輯（`heterogenesis_vargen.py:533-547`）。
2. **寫 FASTA（自寫）。** 每個 clone（含 normal）、每條 haplotype copy 寫一個 FASTA。同時寫真值表：SNV 的 clone、HP、multiplicity、CN timing。
3. **算每個 FASTA 的 depth。** 令 sample 的 cell fraction 為 `f_c`（normal 也算一個 clone），平均 ploidy 為 `P = Σ f_c · ploidy_c`。每個 haplotype copy 的 depth 是 `D · f_c / P`。多 sample 只改 `f_c`，基因組不重做。〔推論〕
4. **產生 read。** 用 Badread（`--seed`）或 PBSIM3（`--seed`，有 MAF 真值）。每個 FASTA 一次。read 名稱加上 `c{clone}_h{hap}_copy{k}` 前綴。
5. **對位與加 tag。** minimap2 `-ax map-ont` 對到 GRCh38。依 read 名稱加 `CL`、`HP` 真值 tag（照 VISOR `LASeR.py:124-139` 的做法），但用不同 tag 名（例如 `XC`、`XH`），避免和 longphase 寫的 `HP` 衝突。最後 `samtools merge`。
6. **normal BAM。** 用只有 germline SNP 的兩條 haplotype，另跑一次第 4–5 步。
7. **phasing。** 對 normal 跑 longphase `phase`，再對 tumor 跑 `haplotag`。也可試 longphase-s `somatic_haplotag`。比對 longphase 的 `HP` 與真值 `XH`，就能量 phasing 錯誤率與 switch。
8. **轉 PhyClone 輸入。** 在真值 SNV 位點，依 `HP` 分開算 ref／alt read 數；major／minor CN 從真值或 Wakhan 推論。輸出 `data.tsv`＋`tree.json`，另加 HP 欄與 SNV pair 共現檔（見 `../notes/04_GAPS_FOR_LONGREAD.md`）。

捷徑：若只要 SV 或簡單 CN，可直接用 VISOR LASeR。條件是每個 clone 資料夾只放 `h1.fa`、`h2.fa`，CN 全寫成 haplotype 內的 dup／deletion，normal 用獨立資料夾，並自己在 `LASeR.py:153` 補 `--seed`。〔推論〕

## 沒找到模擬程式的工具

- Severus、SAVANA、Wakhan：repo 檔案樹中沒有 `sim`、`visor`、`benchmark` 的檔名。Severus preprint 只用真實細胞株與 COLO829 truthset。〔程式〕〔論文〕
- Sniffles2：mosaic 驗證用真實腦組織資料，沒找到模擬程式。〔論文〕
- nanomonsv、cuteSV、HiPhase、WhatsHap、HapCUT2：沒有查 repo 內是否附模擬腳本。〔未確認〕
- lrsomatic（IntGenomicsLab/lrsomatic，MIT，push 2026-10-14）：是 somatic 分析 workflow，沒查到模擬器。〔未確認〕
- SVEngine（Stanford，論文有 clonal Newick 輸入）：GitHub 上找不到官方 repo，可能在 Bitbucket。〔未確認〕
- TKSM（vpc-ccg/tksm）：是 long read transcriptome 模擬器，不適用。〔程式〕
- 名為「TumorSim long-read」的工具：沒找到。
- GitHub code search `clonefraction`：沒找到其他用 VISOR 做 clone 混合的公開腳本。

## 搜尋範圍

- 日期：2026-10-24。
- WebSearch：VISOR、HeteroGenesis、Sim-it、ClairS synthetic、LongPhase-S、Sniffles2 mosaic、Severus 模擬、2025 long read 腫瘤 subclone 模擬。
- `gh api`：上述各 repo 的 metadata、檔案樹、README。
- 淺層 clone（只讀）：VISOR、HeteroGenesis、Sim-it、pbsim3、Badread、NanoSim。
- 未讀：各工具論文的補充材料；Severus／SAVANA／Wakhan 論文全文中的模擬細節。
