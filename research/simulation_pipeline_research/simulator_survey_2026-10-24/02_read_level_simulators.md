# Read 層級（FASTQ／BAM）腫瘤基因體模擬器調查

調查日期：2026-10-24。範圍：會產生 clonal mixture read，而且帶已知真值的程式與 benchmark。Pairtree（`pearsim`）與 CONIPHER（`TRACERx_simulation_tool`）已在 `../notes/05_OTHER_SIMULATORS.md` 處理，這裡不重做。

證據標記：〔論文〕論文或 README 的主張；〔程式〕已讀原始碼（只讀，沒有執行）；〔推論〕我們的推論，沒有實測。程式 clone 在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones/`（暫存，會消失）。

## 結論

> **2026-10-24 範圍更正：PSiTE、VISOR 已移出。** 篩選標準是「輸出最終能當 PhyClone 這類 bulk 建樹軟體的輸入，而且真值能直接對應 clone tree」。PSiTE 有樹，但只輸出 FASTA／FASTQ（ART short read），要自己做 alignment、variant calling 與 CN calling 才能得到 PhyClone 輸入。VISOR 沒有樹，只能當 read 模擬的零件。 下文保留原始調查內容，排名只作紀錄。見 [README「範圍更正」](README.md)。〔程式〕

- **最接近需求的是 PSiTE。** 它沿 tree 放 SNV 與 allele-specific CN，每個 SNV 指定在某一條 parental haplotype 上。它為每個 clone × haplotype 寫一個 FASTA，然後逐一呼叫 ART。read 名稱帶 `{tipnode}_prt{parental}` 前綴，所以每條 read 的 clone 與 haplotype 來源都可追。限制：只接 ART（short read）。
- **唯一原生輸出 long read 且逐 read 標 haplotype 的是 VISOR（LASeR）。** 它用 Badread 產生 ONT／PacBio read，用 minimap2 比對，並可在 BAM 寫 `CL`（clone）與 `HP`（haplotype）tag。限制：它不建 tree，clone 基因體要自己用 HACk 做。
- **建議組合（〔推論〕，未實測）：** 用 PSiTE（或 HeteroGenesis）產生 tree、allele-specific CN 與每個 clone 的 haplotype FASTA，再把 FASTA 交給 VISOR LASeR 或 Badread／PBSIM3 產生 long read。這樣可得到 HP1/HP2 與 SNV 共現的 read 層級真值。
- **用真實 phased read 的工具（tHapMix、SMC-Het 管線）** 的 read 帶真實 haplotype。但 tHapMix 對每條 read、每個 SNV 獨立抽 Bernoulli，所以同一條 read 上多個 SNV 的共現**不符合** clone 結構。SMC-Het 管線是逐 tree node 切 sub-BAM 再 spike-in，共現有保留，但程式是 2016 年的 Perl，資料在 EGA 受控。

| 排名 | 工具 | tree | haplotype-resolved 基因體 | allele-specific CN | purity<1 | 逐 read 的 clone／HP 真值 | long read |
|---|---|---|---|---|---|---|---|
| 1 | PSiTE | 輸入 Newick（ms 產生）＋沿 branch 放變異 | 是（parental 0/1，SNV 指定 hap） | 是（每 parental 的 CN profile） | 是（多 sector 各自 purity） | **有**：read 名前綴 `{tipnode}_prt{parental}` | 否（只 ART）；FASTA 可外接 |
| 2 | VISOR（HACk＋LASeR） | 無 | 是（使用者給 BED 指定 hap） | 部分（haplotype 上的 SV／CNV） | 是（BED 每區 purity 欄、`--clonefraction`） | **有**：BAM `CL`、`HP` tag | **是**（Badread，ONT／PacBio 模型） |
| 3 | SMC-Het 管線（NGS-Tools-BAMSurgeon＋BAMSurgeon） | 是（YAML 巢狀 tree） | 是（GIAB 真實 phased read 切成兩個 parental BAM） | 是（論文：allele-specific CN、WGD） | 是 | 隱含：sub-BAM 依 node 與 phase 分開，合併後未標 tag | 否 |
| 4 | tHapMix | 是（random_binary、random_single_level、自訂） | 是（Platinum NA12882 真實 phased read） | 是（每 clone 每 haplotype CN 的 truth BED） | 是 | 只有 haplotype 來源；**SNV 共現不符合 clone** | 否 |
| 5 | HeteroGenesis | 是（`structure` 參數） | 是（每條染色體 copy 一個 FASTA） | 是（`cnv.txt` 含 phased major/minor） | 是（`freqcalc`） | 不產生 read；外接 read simulator 時可自己保留 | 可外接 |
| 6 | MOV&RSim | 是（`tree.txt`） | 是（每 clone 每 haploid 一個 FASTA） | README 未提 CNV | 是（clone proportion） | 未說明 | 否（Synggen short read） |
| 7 | SimuSCoP | 否（clone 各自列變異） | 部分（het／homo） | 可能（CNV 欄有兩個數字，未驗證） | 是（`normal` 群體＋abundance） | 未說明 | 否 |
| 8 | Xome-Blender | Linear／Branched | 否（混合不同真實 BAM） | 否（總 CN Del／Dup） | 是 | 否 | README 宣稱支援 |
| 9 | VarSim | 否（單一 tumor） | 是（diploid） | 否 | 需自己混 | 有 read 位置真值，無 clone | 否 |
| 10 | BAMSurgeon（單獨） | 否 | 否 | 否 | 以 VAF 近似 | 否 | 否（主要 short read 比對器） |

其他（Pysim-sv、CNV-Sim、SVEngine、VarBen、Mutation-Simulator、NEAT／rneat、SCSsim、SInC）的用處更低，見下方各節。

## 各工具

### PSiTE（Phylogeny guided Simulator for Tumor Evolution）（已移出，見上方更正）

- repo：<https://github.com/hchyang/PSiTE>，commit `b752cd1`（2021-04-25），GPL-3.0。論文：Yang et al. 2019, *Bioinformatics* 35(17):3148, doi:10.1093/bioinformatics/btz028。〔程式〕
- 流程分六個 module：`vcf2fa`（phased germline VCF → 兩個 parental FASTA）、`phylovar`（沿 tree 放 SNV／CNV）、`chain2fa`（建每個 clone 的基因體）、`fa2wgs`／`fa2wes`（呼叫 ART）、`allinone`。〔程式〕`README.md` §2
- tree 是 Newick 格式的 cell lineage tree，建議用 `ms -T` 產生。這是 coalescent 的細胞樹，不是 clone tree。clone 要靠 prune 與 CCF 檔整理。〔論文〕README §2.2.1；〔推論〕
- 每個變異有 `hap` 欄，指定在哪一條 parental haplotype copy 上。CNV 也綁 haplotype。〔程式〕README §2.2.1 trunk_vars 格式
- 真值輸出：每 sector 的 `.snv`（含 `rcount`、`rfreq`）、`.cnv`、`--snv_genotype`（每細胞 `M:N`）、`--ind_cnvs`（每 parental 的 CNV）、`cnv_prof`（`parental0_cn`、`parental1_cn`）、NHX variant tree（變異放在哪條 branch，含 hap）、每 node 的 CCF、chain file。〔程式〕README §2.2.2
- purity：`--purity`；多 sector 時每個 sector 有自己的 purity 與 depth。〔程式〕README §2.2.3、§2.4.1
- 種子：`--random_seed`，也傳給 ART 的 `--rndSeed`。〔程式〕`psite/fa2wgs.py` L390–396
- **逐 read 真值：** `fa2wgs` 對每個 tipnode × parental 各呼叫一次 ART，`--id` 設成 `'{tipnode}_prt{parental}'`；normal 是 `'nm_prt{parental}'`。所以 read 名稱直接告訴我們它來自哪個 clone、哪條 haplotype。〔程式〕`psite/fa2wgs.py` L216–226、L278–286
- read simulator 寫死是 `art_illumina`（`--art` 可改參數字串，但程式會再加 ART 專用參數 `--len --fcov --in --id --out --rndSeed`）。換 long read 要改程式或直接拿 FASTA 外接。〔程式〕`psite/fa2wgs.py` L81、L390；〔推論〕
- 對我們：最接近理想。可產生 SNV 在 haplotype 上的真值，以及 allele-specific CN 在 branch 上。缺 long read，但 haplotype FASTA 已備好。〔推論〕

### VISOR（HACk＋LASeR）（已移出，見上方更正）

- repo：<https://github.com/davidebolo1993/VISOR>，commit `a889e59`（2024-10-21），LGPL-3.0，`setup.py` version 1.1.3。論文：Bolognini et al. 2019, *Bioinformatics*, doi:10.1093/bioinformatics/btz719。〔程式〕
- HACk 把使用者 BED 指定的變異（SNV、indel、SV、CNV）放進各 haplotype FASTA。它不建 tree。〔程式〕`VISOR/VISOR/HACk/HACk.py`；〔論文〕README
- LASeR：long read 用 Badread（error model 可選 `nanopore2023`、`nanopore2020`、`pacbio2016`），再用 minimap2 比對。〔程式〕`VISOR/VISOR.py` L104–142、`LASeR/LASeR.py` L342
- 多 clone：`-s` 可給多個資料夾，每個資料夾是一個 subclone；`--clonefraction` 給比例，總和要 100。〔程式〕`VISOR.py` L113、L136；`LASeR.py` L558–574
- purity：模擬區域 BED 的第 5 欄是 purity 百分比。〔程式〕`LASeR.py` L500
- **逐 read 真值：** `--tag` 時，每條 read 寫入 `CL`（clone 編號）與 `HP`（haplotype 編號）tag。〔程式〕`LASeR.py` L124–139、L628–636
- 種子：VISOR 本身沒有 seed 參數。〔程式〕grep `seed` 無結果
- 對我們：可直接產生帶 HP tag 的 ONT BAM，和 longphase 的 HP 標記可直接對照。但 tree、CN timing、SNV 指派都要自己產生。建議當 PSiTE／HeteroGenesis 的下游。〔推論〕

### ICGC-TCGA DREAM SMC-Het 模擬管線（Salcedo et al. 2020）

- 論文：Salcedo et al. 2020, *Nat Biotechnol* 38:97–107, PMC6956735。〔論文〕
- 基底是 GIAB GM24385（300x PE＋16x mate-pair），用 PhaseTools 依 trio 做 phasing，phase set 中位長約 85 kbp。結果是「每條染色體兩個 BAM，各代表一個 parental copy」。〔論文〕Methods
- 論文說 phasing 是必要的，否則 allele-specific CN 會模擬錯。〔論文〕
- 做法：依每個 tree node 的 cellular prevalence 與局部 CN，把 phased read 分成 sub-BAM；每 1000 對 read 一個 window 隨機抽。再對每個 sub-BAM、每個 phase 跑 BAMSurgeon spike-in。最後合併。〔論文〕Methods
- 對 BAMSurgeon 的擴充：variant phasing、allele-specific CN（含 WGD）、translocation、三核苷酸 signature、replication timing。〔論文〕
- 程式：CPAN `NGS-Tools-BAMSurgeon-v1.0.0`（2016-05-25，Perl 5 授權，作者 BOUTROSLB）。內有 `share/template.yaml`：巢狀 tree，每個 node 有 `percent` 與 SNV／Indel／SV 數；pipeline 有 `splitsubclones`、`makevcf`、`mergephases` 階段。〔程式〕<https://cpan.metacpan.org/authors/id/B/BO/BOUTROSLB/NGS-Tools-BAMSurgeon-v1.0.0.tar.gz>，`lib/NGS/Tools/BAMSurgeon.pm` L122–133、L564–628
- 真值：論文說用 BAMSurgeon 的 perfect call 當 gold standard，並有真實 lineage 指派。檔名未在正文列出。〔論文〕
- 資料：EGA `EGAS00001002092`（受控）。計分程式：`asalcedo31/SMC-Het_Scoring`。`morrislab/smchet-challenge`（commit `736acf0`）只有驗證與報告腳本，不是模擬器。〔論文〕〔程式〕
- **逐 read 真值：** 每條 read 在切分時已知 node 與 phase。合併後是否保留 tag，論文沒說。〔推論〕
- 對我們：設計理念最接近（真實 read、phased、tree 上 allele-specific CN）。但只支援 short read，依賴 GIAB 300x 資料與 2016 年 Perl 環境，重跑成本高。〔推論〕

### tHapMix（Illumina）

- repo：<https://github.com/Illumina/tHapMix>，commit `e665040`（2026-04-20），PolyForm Strict 1.0.0（限制多，不能改作再散布）。論文：Ivakhno et al. 2017, *Bioinformatics*, doi:10.1093/bioinformatics/btw589。〔程式〕
- 輸入是 Platinum Genomes NA12882（200x HiSeq）依 haplotype 切好的 48 個 BAM（約 300 GB，BaseSpace 下載）。可用 `scripts/haplobams/split_by_haplotype.py` 自己做。hg19。Python 2。〔程式〕README
- tree：`tree_format` 可選 `random_binary`、`random_single_level` 或自訂巢狀 list；參數有 `num_clones`、`perc_majority_clone`、`purity`。〔程式〕README Usage
- CN：依 haplotype 抽樣 read 來產生 CN；每個 clone 有 truth BED（每 haplotype 的 CN）。〔程式〕`bin/HapMixWorkflow.py` L78–107
- SNV：從 Strelka VCF 讀入，每個 SNV 隨機指定到第一或第二 haplotype。〔程式〕`bin/simulate_copy_number_changes.py` L372–430
- **逐 read 真值的問題：** 每條 read、每個 SNV 都獨立擲一次 `random.random() < freq` 決定是否改 base。所以同一條 read 上兩個 SNV 的共現是獨立的，不符合 clone 結構。read 的 haplotype 來源是真的，但沒寫成 tag。〔程式〕`simulate_copy_number_changes.py` L432–457
- 種子：`--seed`。〔程式〕
- 對我們：不適合研究 read 上 SNV 共現。〔推論〕

### HeteroGenesis

- repo：<https://github.com/GeorgetteTanner/HeteroGenesis>，commit `4c9a142`（2021-08-25），GPL-3.0。論文：Tanner et al. 2019, *Bioinformatics*, doi:10.1093/bioinformatics/bty1063。〔程式〕
- `structure` 參數定義 clone tree（clone、與 parent 距離、parent）。〔程式〕README
- `heterogenesis_varincorp` 為每個 clone 輸出每條染色體 copy 的 FASTA、VCF（每個 copy 上的出現次數、VAF）、`cnv.txt`（含 phased major/minor allele）。〔程式〕README Outputs
- 有 aneuploidy 與 WGD（`wgdprob`）。〔程式〕
- `freqcalc` 依 clone 比例與 purity 合成 bulk 真值。〔程式〕
- 不產生 read。使用者要自己對每個 FASTA 跑 read simulator。〔程式〕
- 沒有 seed 參數（grep 無結果）。〔程式〕
- 對我們：可當 PSiTE 的替代上游；chromosome copy 層級的 FASTA 可直接交給 long-read simulator。〔推論〕

### MOV&RSim

- repo：<https://gitlab.com/sysbiobig/movarsim>，commit `5e87143`（2026-06-16），GPL-3.0。論文：Longhin et al. 2025, *BMC Bioinformatics* 26, doi:10.1186/s12859-025-06292-0。〔程式〕
- 可選 `tree.txt`（child、distance、parent，格式與 HeteroGenesis 相似）。〔程式〕README L209–214
- 每個 clone 輸出每個 haploid 的 `.fa`、座標對照 `.pkl`、真值 `.vcf`。〔程式〕README L254–257
- read 由 Synggen 產生（short read）；clone 比例在 shell 腳本設定（例如 `PROPORTIONS=(0.4 0.3 0.2 0.1)`）。〔程式〕README L852–927
- README 沒有提到 CNV。種子：`--chooseSeed`。〔程式〕
- 對我們：有 haplotype FASTA 與 tree，但沒有 CN，用處有限。〔推論〕

### SimuSCoP

- repo：<https://github.com/qasimyu/simuscop>，commit `590bff1`（2020-12-18），GPL-3.0。〔程式〕
- tumor 範例：`name = clone1, clone2, clone3, normal`＋abundance 檔。變異檔逐 clone 列出 SNV／indel／CNV；共享變異要在每個 clone 重複列。沒有 tree 物件。〔程式〕`configFiles/config_test_tumor.txt`、`testData/variations_tumor.txt`
- CNV 行有兩個數字（例如 `3 2`），可能是總 CN 與 major CN，未驗證。〔程式〕〔推論〕
- short read，依真實資料學 error profile。〔論文〕

### Xome-Blender

- repo：<https://github.com/rsemeraro/XomeBlender>，commit `fefc35c`（2020-09-21），GPL-3.0。〔程式〕
- 混合不同真實 BAM，「不加入任何合成元素」。`-sa Linear|Branched`、`-scn` 子 clone 數、CNV 檔（Del／Dup、CN、所屬 subclone）。〔程式〕README
- v3.1 README 宣稱支援 long read，未驗證。〔論文〕
- 沒有 haplotype 指派；CN 不分 allele。〔推論〕

### VarSim

- repo：<https://github.com/bioinform/varsim>，commit `aa1b70d`（2022-01-28），BSD-2-Clause。〔程式〕
- `varsim_somatic.py`：在 normal VCF 上加 somatic 變異，用 vcf2diploid 建 diploid 基因體，再呼叫 ART 或 DWGSIM；有 `--seed`。〔程式〕L20–72
- 只有一個 tumor 基因體，沒有 clone 或 tree。read 名稱帶真實位置（VarSim 的設計）。〔程式〕〔推論〕

### BAMSurgeon（單獨使用）

- repo：<https://github.com/adamewing/bamsurgeon>，commit `d9448a5`（2026-08-06），MIT。〔程式〕
- 把 SNV／indel／SV spike-in 到現有 BAM；`-z/--haplosize` 讓相近位點一起改；`--seed` 可固定。〔程式〕`bin/addsnv.py` L32–59
- 本身沒有 tree 與 clone。SMC-Het 論文指出它「不產生代表性的 subclonal population，也不 phase 變異」。〔論文〕〔程式〕
- `scripts/` 有 `bamsplit_proportion.py` 等，可手動做混合。〔程式〕

### 其他（用處低）

- **Pysim-sv**：<https://github.com/xyc0813/pysim>，commit `6002572`（2017-06-29），無授權檔。有 aneuploidy 與 `mixture_v0.5.py`（按比例混合 FASTQ），呼叫 ART。沒有 tree。〔程式〕
- **CNV-Sim**：<https://github.com/NabaviLab/CNV-Sim>，commit `7c3eec7`（2018-07-30），無授權檔。只做 CNV，呼叫 ART／Wessim。沒有 clone。〔程式〕
- **SVEngine**：<https://bitbucket.org/charade/svengine>，BSD3。接受 Newick tree 做 clonal evolution，以 SV 為主；用改過的 wgsim（xwgsim）；有 locus-specific ploidy，但論文沒說 allele-specific CN。〔論文〕PMC6057526；程式未讀
- **VarBen**：<https://github.com/nccl-jmli/VarBen>，commit `0f66e35`（2021-03-16）。BAM spike-in，有 `--haplosize`，沒有 clone。〔程式〕
- **Mutation-Simulator**：<https://github.com/mkpython3/Mutation-Simulator>，commit `3493697`（2024-02-07），GPL-3.0。README 寫「只支援 haploid mutation」。〔程式〕
- **NEAT**：<https://github.com/ncsa/NEAT>，commit `0b44d36`（2026-10-17）。沒有 clone tree。姊妹工具 `rneat`（<https://github.com/ncsa/rusty-neat>）宣稱支援 tumor/normal 混合、purity、origin-tagged truth VCF；未驗證。〔論文〕README L861
- **SCSsim**：<https://github.com/qasimyu/scssim>，commit `52d2d94`（2019-12-16），BSD-3。single-cell read 模擬，給完整性；屬另一份調查（05）的範圍。〔程式〕
- **SInC**：Pattnaik et al. 2014, *BMC Bioinformatics* 15:40。germline 取向的 SNV／indel／CNV＋short read 模擬，沒有 tumor clone 功能。〔論文〕PMC3926339；程式未讀

## 沒找到程式或不屬於 read 層級的工具

- **PCAWG Evolution & Heterogeneity（Dentro et al. 2021 Cell）**：模擬資料由 `galder-max/SimClone1000`（commit `909395c`，2018-08-31）產生，呼叫 R 套件 `simclone`。這是 VAF／read count 層級，不是 FASTQ／BAM。`sdentro/simclone` 在 GitHub 已不存在（`git ls-remote` 回 not found）。〔程式〕
- **OncoSim、CancerSim、TumorSim／tumor-sim、"Moonshot" 模擬器**：沒找到對應 read 層級腫瘤模擬的公開 repo（GitHub repo search 在調查中途觸發 rate limit，搜尋不完整）。〔未驗證〕 補查結果見 [07](07_oncosim.md)、[08](08_cancersim.md)、[09](09_tumorsim.md)、[10](10_moonshot.md)。
- **2023–2026「tumor evolution read simulator」**：只找到 Lai et al. 2024 arXiv:2402.09599（模擬方法回顧，無程式），以及 Springer Nature「Behind the Paper」一文提到需要把 read phase 到 parental haplotype 才能模擬 allele-specific CN（應指 SMC-Het 系列，未確認）。沒找到新的、同時支援 long read 與 clone tree 的工具。〔論文〕〔未驗證〕

## 搜尋範圍（2026-10-24）

- GitHub：`gh api repos/...` 查 metadata；`gh search repos` 查 HeteroGenesis、pysim-sv、Mutation-Simulator、SMC-Het、smchet、MOV&RSim、Varben、SInC、tumor long read simulator 等；之後 search API rate limit 用完，Moonshot、TumorSim、OncoSim 沒有查完。
- 讀過的程式（shallow clone，只讀）：PSiTE、VISOR、tHapMix、HeteroGenesis、BAMSurgeon、Xome-Blender、SimuSCoP、VarSim、VarBen、Mutation-Simulator、NEAT、pysim、MOV&RSim、CNV-Sim、SCSsim、SimClone1000、smchet-challenge、smchet_utils、CPAN NGS-Tools-BAMSurgeon v1.0.0。
- 網頁：Salcedo 2020 PMC6956735 全文前 100k 字元；SVEngine PMC6057526；arXiv 2402.09599 摘要；MetaCPAN API；WebSearch（SMC-Het、tumor read simulator long read、MOV&RSim、SInC／Pysim-sv）。
- 沒有執行任何模擬器。
