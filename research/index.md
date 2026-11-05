# 研究知識庫索引

這是研究知識庫的唯一索引。先在這裡找路徑，再照下面的順序讀。論文用關鍵字搜尋：`grep -i <關鍵字> research/index.md`。

## 檢索順序

1. 讀 `summary.md`（重點摘要）。資訊夠，就回答。
2. 不夠，讀 `fulltext.md`（全文）。用 `grep` 找關鍵字，讀相關段落。
3. 發現錯誤或缺漏，讀 `source.md` 列出的第一手資料（PDF、URL、程式 commit）。接著修正 `fulltext.md` 和 `summary.md`，必要時更新本檔那一列。

回答時標來源，也寫明讀到第幾層。

## 論文

每篇目錄都有 `summary.md`、`fulltext.md`、`source.md`，另有本機 PDF。`fulltext.md` 和 PDF 只留本機，新 clone 的 repo 沒有這兩種檔；要重建時看 `source.md`。R01 例外：主文 closed access，沒有 `fulltext.md`。

**文獻空缺：** 在本目錄收錄的論文中，沒找到用 long-read 特徵重建完整 SNV／CN clone tree，再以完整 single-cell 真值樹量化評估的研究。這是本 repo 的空缺。最接近的是 B04，它的 scDNA 只做局部驗證，且與 long-read topology 篩選不在同一病人。〔repo〕B04 `summary.md`

| ID | 路徑 | 一句話 | 關鍵字 |
|---|---|---|---|
| [A01](literature/papers/A01_ovarian_cfDNA_2025/summary.md) | `literature/papers/A01_ovarian_cfDNA_2025/` | 病人 scWGS 建 MEDICC2 樹；cfDNA 追蹤抗藥 clone。 | 卵巢癌、游離DNA、單細胞DNA、等位基因特異拷貝數、縱向追蹤、結構變異、hgsoc、ovarian cancer、cfdna、scwgs、dlp+、medicc2、signals、allele-specific copy number、structural variants、ccf calibration、longitudinal、wgd |
| [A02](literature/papers/A02_sprinter_2025/summary.md) | `literature/papers/A02_sprinter_2025/` | SPRINTER 校正 S 期 CN；病人 scDNA 樹連結增殖與轉移。 | 單細胞DNA、細胞週期、肺癌、轉移播種、拷貝數、循環腫瘤DNA、sprinter、nsclc、scwgs、dlp+、cell cycle、s-phase、huntress、medicc2、machina、metastatic seeding、ctdna shedding、copy number |
| [A03](literature/papers/A03_pancreatic_snDNA_2023/summary.md) | `literature/papers/A03_pancreatic_snDNA_2023/` | Tapestri snDNA 建 PA04 的 SNV+SMAD4 刪除 clone 樹。 | 胰臟癌、單核DNA定序、擴增子面板、互斥變異、等位基因脫落、克隆樹、pdac、pancreatic cancer、sndna-seq、tapestri、amplicon panel、scg、smad4 deletion、kras、allelic dropout、doublet、mutual exclusivity、clone phylogeny |
| [A04](literature/papers/A04_aml_strandseq_2024/summary.md) | `literature/papers/A04_aml_strandseq_2024/` | Strand-seq 單細胞 SV+單倍型建 CK-AML 人工 clone 樹。 | 急性骨髓性白血病、複雜核型、單細胞結構變異、染色體長度單倍型、染色體碎裂、人工整理樹、ck-aml、acute myeloid leukemia、strand-seq、sctrip、chromosome-length haplotype、structural variants、chromothripsis、bfb、optical genome mapping、pdx、haplotype-aware copy number |
| [A05](literature/papers/A05_mpal_multiome_2024/summary.md) | `literature/papers/A05_mpal_multiome_2024/` | DAb-seq 單細胞 DNA 以 SCITE 建 MPAL 突變樹。 | 混合表型急性白血病、單細胞DNA、突變樹、表面蛋白、克隆表型、基因面板、mpal、mixed phenotype acute leukemia、dab-seq、tapestri、scdna、scite、mutation tree、cite-seq、surface protein、flt3 itd、leukemia gene panel |
| [B01](literature/papers/B01_melanoma_longread_2026/summary.md) | `literature/papers/B01_melanoma_longread_2026/` | ONT SNV 建樹；SV／甲基化只事後放上固定樹。 | 長讀定序、單細胞衍生亞株、小鼠黑色素瘤、結構變異、甲基化、變異放置、scistree、treeharmonizer、oxford nanopore、long-read wgs、single cell-derived sublines、mouse melanoma、b2905、structural variants、severus、wakhan、methylation dmr、variant placement |
| [B03](literature/papers/B03_singlecell_mutational_processes_2022/summary.md) | `literature/papers/B03_singlecell_mutational_processes_2022/` | scDNA total-CN 建細胞樹；ONT 只驗證 SV。 | 單細胞DNA、單倍型特異拷貝數、卵巢癌、三陰性乳癌、平行演化、長讀驗證、signals、dlp+、scdna-seq、sitka、haplotype-specific copy number、hgsc、tnbc、pdx、184-htert、parallel evolution、cnloh、hlamp、oxford nanopore validation、mutational processes |
| [B04](literature/papers/B04_lung_longread_phasing_2022/summary.md) | `literature/papers/B04_lung_longread_phasing_2022/` | long read 同 read 排序選出 S14 線性樹；scDNA 局部驗證。 | 肺癌、長讀定序、單倍型定相、突變先後順序、單細胞DNA驗證、拓樸篩選、nsclc、lung cancer、oxford nanopore、promethion、whatshap、haplotype phasing、mutation pair order、read co-occurrence、clonevol、pyclone-vi、facets、scdna-seq、10x chromium、topology selection |
| [B05](literature/papers/B05_medicc2_2022/summary.md) | `literature/papers/B05_medicc2_2022/` | haplotype CN+WGD 改變 topology；單細胞樹仍是推論。 | 單倍型特異拷貝數、全基因組加倍、最小事件距離、拷貝數演化樹、單細胞DNA、medicc2、haplotype-specific copy number、minimum event distance、whole-genome doubling、loh、mirrored subclonal allelic imbalance、neighbor joining、copy-number phylogeny、pcawg、prostate cancer、triple-negative breast cancer、single-cell dna |
| [B07](literature/papers/B07_numbat_2022/summary.md) | `literature/papers/B07_numbat_2022/` | scRNA 加族群 phasing 推 CNV 細胞樹；不是 long read。 | 單細胞轉錄體、單倍型感知、拷貝數變異、族群相位、中性拷貝數LOH、細胞演化樹、numbat、scrna-seq、haplotype-aware hmm、allele-specific copy number、cnloh、eagle2 population phasing、perfect phylogeny、scistree、multiple myeloma、anaplastic thyroid cancer、single-cell cnv、clonal architecture |
| [M01](literature/papers/M01_phyclone_2025/summary.md) | `literature/papers/M01_phyclone_2025/` | bulk SNV+CN 的貝氏 clone tree；HGSOC 真值樹來自單細胞。 | 腫瘤演化樹、bulk 定序、貝氏推論、粒子吉布斯、卵巢癌、單細胞真值樹、phyclone、bulk snv、copy number、fs-crp、particle gibbs、smc、pyclone emission、outlier mutation loss、multi-sample、hgsoc、mcpherson 2016、ancestor-descendant f-score、clone tree |
| [M04](literature/papers/M04_pharming_2026/summary.md) | `literature/papers/M04_pharming_2026/` | 單細胞 SNV+CNA 聯合 clone tree；只有模擬真值。 | 單細胞 DNA 定序、SNV 與 CNA 聯合演化樹、haplotype 特異 CN、三陰性乳癌、卵巢癌細胞株、pharming、scdna-seq、low-pass single-cell、act、dlp+、joint snv cna tree、haplotype-specific copy number、cnrein、dollo snv loss、infinite alleles cna、triple-negative breast cancer、ovarian cancer cell lines |
| [M05](literature/papers/M05_tusv_ext_2022/summary.md) | `literature/papers/M05_tusv_ext_2022/` | ILP 聯合 SNV/SV/CNA 建樹；phasing 是潛變數。 | 整數線性規劃、結構變異、等位基因特異拷貝數、多區域取樣、潛在定相、tusv-ext、ilp、gurobi、multi-region bulk、snv、structural variation、sv breakpoint、allele-specific copy number、latent allele phasing、dollo、deconvolution、prostate cancer |
| [M06](literature/papers/M06_phylex_2023/summary.md) | `literature/papers/M06_phylex_2023/` | bulk+scRNA 共現建樹；以 DLP scDNA 樹為真值。 | 單細胞轉錄體、共現、克隆樹、卵巢癌、貝氏推論、phylex、tssb、slice sampler、bulk plus scrna、cell-level snv co-occurrence、smart-seq3、10x、dlp、pyclone likelihood、high-grade serous ovarian cancer、her2 breast cancer |
| [M07](literature/papers/M07_smchet_benchmark_2024/summary.md) | `literature/papers/M07_smchet_benchmark_2024/` | 短讀模擬的單樣本 benchmark，比較 31 個方法。 | 社群基準測試、模擬腫瘤、單樣本、次克隆重建、拷貝數、smc-het、dream challenge、bamsurgeon、battenberg、mutect、single-sample bulk、subclonal reconstruction、nrpcc、phylowgs、dpclust、simulated tumors、co-clustering、ancestor-descendant matrix |
| [M08](literature/papers/M08_bitphylogeny_2015/summary.md) | `literature/papers/M08_bitphylogeny_2015/` | 每條 read 的多位點 pattern 當一次抽樣，用 TSSB 聯合推 clone 與樹；沒有 CN。 | 樹狀 stick-breaking、read 層級 pattern、共現、甲基化、clone 與樹聯合推論、大腸癌、骨髓增生性腫瘤、bitphylogeny、tssb、tree-structured stick-breaking、read-level pattern、methyltype、co-occurrence、joint clustering and tree inference、clones at inner nodes、bisulfite sequencing、colon cancer、myeloproliferative neoplasm、single-cell exome、mcmc、mpear |
| [R01](literature/papers/R01_mcpherson_hgsoc_2016/summary.md) | `literature/papers/R01_mcpherson_hgsoc_2016/` | 病人單核 PCR 建樹；是 PhyClone HGSOC 真值樹來源。 | 卵巢癌、單核定序、真值樹、多區域取樣、突變流失、high-grade serous ovarian cancer、single-nucleus sequencing、targeted deep sequencing、scg、pyclone、stochastic dollo、infinite sites with loss、multi-region wgs、clone tree、phyclone truth tree、intraperitoneal spread |

## 主題

每個目錄都有 `summary.md`（表內連結）和 `source.md`。全文層是 `fulltext.md`，或 `summary.md` 列出的編號筆記。

| 主題 | 路徑 | 一句話 | 關鍵字 |
|---|---|---|---|
| [方法調查](literature/surveys/methods_survey/summary.md) | `literature/surveys/methods_survey/` | 45 個推論 topology 的方法、novelty 邊界、評估指標 | 方法調查、novelty、評估指標；methods survey, phylogeny, Pairtree, Orchard, CONIPHER, Pharming, TUSV-ext, MEDICC2, ADM |
| [long-read 建樹補搜](literature/surveys/longread_tree_search_2026-10-19/summary.md) | `literature/surveys/longread_tree_search_2026-10-19/` | long-read 特徵建樹的搜尋結果與 phased feature 工具 | 同 read 共現、單倍型；long read, HP, PS, co-occurrence, longphase-s, Wakhan, Severus, SAVANA, TreeHarmonizer |
| [公開資料調查](literature/surveys/sc_longread_datasets_2026-10-26/summary.md) | `literature/surveys/sc_longread_datasets_2026-10-26/` | 同時有 bulk long read 和 single-cell 的公開資料 | 公開資料、單細胞、細胞株；HG008, HG009, COLO829, PTA, clonal line, GIAB, passage |
| [2026 文獻調查](literature/surveys/patient_sc_longread_2026/summary.md) | `literature/surveys/patient_sc_longread_2026/` | 病人 single-cell 與 long-read／haplotype 研究，含資料與程式可得性 | 病人、資料可得性、程式可得性；patient, single cell, ONT availability, code availability |
| [PhyClone 與 HP 設計](phyclone_research/summary.md) | `phyclone_research/` | PhyClone 模型與程式分析、HP 擴充設計、FSCRP prior 計畫 | HP 擴充、先驗、離群值；PhyClone, FS-CRP, FSCRP, PG-SMC, emission, A1, A2, outlier, multiplicity |
| [模擬流程](simulation_pipeline_research/summary.md) | `simulation_pipeline_research/` | PhyClone 生成器的實際行為；Pairtree、CONIPHER、SISTEM 比較 | 模擬器、生成器、真值格式；simulator, pearsim, Pairtree, CONIPHER, tx_simulation, SISTEM, benchmark format |
| [真值樹合理性](simulation_pipeline_research/truth_evidence_2026-10-25/summary.md) | `simulation_pipeline_research/truth_evidence_2026-10-25/` | 7 類事件的真實資料證據（歷史參考） | 真值樹、事件證據、壓力測試樹、典型樹；truth tree, T2T, HG002, HG008, SEQC2, COLO829, cnLOH, CN timing |
| [HCC1395 參考樹](hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/summary.md) | `hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/` | HCC1395 參考樹的證據邊界與 PhyloWGS 模型（暫停，只當歷史參考） | 參考樹、證據邊界；HCC1395, golden tree, Fang 2021, PhyloWGS, SuperFreq, ASCAT, single-cell CNV |

單檔文件：[`literature/SYNTHESIS_phyclone_longphase.md`](literature/SYNTHESIS_phyclone_longphase.md)：跨論文去重與 PhyClone × longphase-s 整合地圖。

## 不在本目錄

| 要找 | 先看 |
|---|---|
| 資料路徑 | `docs/index.md` |
| 實驗結論 | `lab_report/INDEX.md` |
| 會議需求、決議、待辦 | `meeting_record/index.md` |
| 模擬器 | `diplosim/DECISIONS.md` |
| 樹重建（HP 擴充） | `/bip8_disk/boyu114/haploclone/rust/docs/PORTING.md` |
