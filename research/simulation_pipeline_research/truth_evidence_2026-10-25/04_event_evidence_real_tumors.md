# 真值樹 7 類事件的真實腫瘤證據（2026-10-25）

對象：`lab_report/2026-10-24_hp_truth_tree_phyclone/` 的手動 HP-aware 真值樹（圖：`figures/hp_truth_tree.png`）。
範圍：只查真實腫瘤的一手證據。T2T-Q100、GIAB、SEQC2／COLO829／HCC1395 細胞株基準由其他同事負責，本檔不重查。
排除：M03、B06、B08、B02、M02 不列入。查詢時看到的 Donmez AACR 2026 摘要（CASTLE H2009／H1437 long-read pair 定相）就是 M03，所以不引用。

等級標記：〔論文實測〕＝論文報告的量測數字；〔論文主張〕＝作者的解讀或沒有直接數字；〔推論〕＝本檔的推論。
數字來源：PubMed metadata 或 PMC／期刊全文，查詢日期 2026-10-25。

## 1. 結論

- **7 類事件在真實腫瘤中都有大型 cohort 或 single-cell 證據。** 審查者若說「這些事件是編的」，可以逐類反駁。各類的最強證據見第 2 節。
- **事件本身真實，但這棵樹把 7 類事件放在 100 個 SNV、4 個 clone 裡，密度遠高於真實腫瘤。** 這是壓力測試設計，不是「典型腫瘤」。文件裡要明寫這一點。〔推論〕
- **大部分參數落在真實範圍內。** purity 0.40、4 個 clone、分岔加直線、單拷貝 subclonal gain、subclonal cnLOH、20% SNV 受遺失影響，都有對應數字（第 3 節）。
- **有 3 個參數偏樂觀，要另外說明或做敏感度分析。**
  1. depth 200×：PCAWG 中位約 46×。現有 ONT 腫瘤 WGS 多在 30–60×。
  2. C3 的 CCF 0.10（cell prevalence 0.04，期望 VAF 約 0.02）：PCAWG 只保證 CCF ≥ 0.30 的 subclone 可偵測。AML31 要約 850× 才能找回最低頻的 cluster。
  3. 每對指定 SNV 有 80 條跨越 read：真實 long read 能同時蓋到兩個 somatic SNV 的 pair 很少（B04 每例平均 69 對可排序 pair）。
- **「模擬可信」的業界做法是：樹與參數取自真實 cohort 的重建結果，再把突變 spike-in 到真實 read。** 例如 SMC-Het 的 51 棵樹中有 25 棵來自 PCAWG 重建，並用 BAMSurgeon 把突變放進 GIAB 的真實 read。我們可以照做：用 HCC1395 等細胞株的 ONT read 當底，把設計樹 spike-in 進去。〔論文實測＋推論〕
- **具已知真值的實體資料很少，而且都不完整。** 細胞株混合（Farahani 2017）只知道混合比例，不知道樹。單細胞衍生 sublines（B01）和單細胞參考樹（R01、B04、B09）可提供部分真值。目前沒有公開的「ONT bulk ＋ 完整 single-cell 真值樹」病人資料（未查到）。

## 2. 7 類事件 × 證據

### 2.1 低 purity

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Aran 2015, Nat Commun | TCGA，>10,000 樣本，21 種癌 | ABSOLUTE purity 平均 62.3% ± 19.9%（11 種癌）。consensus（CPE）平均 75.3% ± 18.9%。LUAD、LUSC、HNSC 等 purity < 70%。SKCM 以 ABSOLUTE 計有 40.3% 樣本 < 60%。TCGA 收案門檻原本 80% tumour nuclei，後來降到 60% | 〔論文實測〕 | [10.1038/ncomms9971](https://doi.org/10.1038/ncomms9971) |
| TCGA PDAC 2017, Cancer Cell | TCGA PDAC，150 例 WES | ABSOLUTE purity 範圍 9–89%，中位 33%，第一四分位 20%。74／150 例 purity < 33% | 〔論文實測〕 | [10.1016/j.ccell.2017.07.007](https://doi.org/10.1016/j.ccell.2017.07.007) |
| Dentro 2021, Cell（PCAWG） | 2,658 例 WGS | consensus purity 與 TCGA purity 相關 R = 0.76。WGS 中位 depth 約 46×。全文前段沒有報 purity 分佈數字 | 〔論文實測〕 | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) |

要點：TCGA 有收案門檻，所以 purity 分佈偏高。不設門檻的 PDAC 中位只有 0.33。〔論文實測＋推論〕

### 2.2 subclonal、haplotype-specific CN gain

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Jamal-Hanjani 2017, NEJM（TRACERx 100） | 多區域 WES，100 例 NSCLC | 92 例有 CN 資料，其中 62% 有 mirrored subclonal allelic imbalance（MSAI，不同 subclone 的不同 parental allele 各自 gain／loss）。共 375 個 MSAI 事件，佔受影響基因組 1–43% | 〔論文實測〕 | [10.1056/NEJMoa1616288](https://doi.org/10.1056/NEJMoa1616288) |
| Watkins 2020, Nature | 394 個腫瘤、1,421 個樣本、22 種癌，多樣本 phasing | 基因組中位 18% 有 subclonal SCNA（clonal 是 26%）。45% 腫瘤有 > 20% 基因組是 subclonal SCNA。37% 腫瘤有 parallel 事件 | 〔論文實測〕 | [10.1038/s41586-020-2698-6](https://doi.org/10.1038/s41586-020-2698-6) |
| Dentro 2021, Cell（PCAWG） | 2,658 例 WGS | arm-level CNA 中 subclonal 的比例依癌別為 13.3%（chRCC）到 53.8%（前列腺癌） | 〔論文實測〕 | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) |
| Zaccaria & Raphael 2021, Nat Biotechnol（CHISEL） | 單細胞 DNA，2 位乳癌病人，約 2,000 個細胞 | 找到 total CN 看不到的 cnLOH、mirrored-subclonal CNA，涉及 TP53、BRCA2、PTEN | 〔論文實測〕 | [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6) |
| Wu 2021, Nat Biotechnol（Alleloscope） | scDNA（8 個胃腸腫瘤、乳癌）＋ scATAC；用 10x linked-read WGS 驗證 phasing | P5931 chr7 有 MMm／Mmm 兩個 mirrored subclone（total CN 都是 3）。P6198 chr9 有 7 種 allele 組合。和 linked-read 比較的 sensitivity 0.86–0.97，specificity 0.97–1.00 | 〔論文實測〕 | [10.1038/s41587-021-00911-w](https://doi.org/10.1038/s41587-021-00911-w) |
| Funnell 2022, Nature（SIGNALS；本地 B03） | DLP+ scDNA，HGSC／TNBC 病人與 PDX；ONT 只做驗證 | 細胞層級 haplotype-specific CN、cnLOH、parallel 事件 | 〔論文實測〕 | [10.1038/s41586-022-05249-0](https://doi.org/10.1038/s41586-022-05249-0) |

### 2.3 deletion 造成突變遺失（違反 infinite sites）

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Jamal-Hanjani 2017, NEJM（TRACERx 100） | 多區域 WES | 每個樣本的 subclonal 突變中，中位 13%（範圍 0–56%）可能是 CN loss 造成的「看似 subclonal」 | 〔論文實測〕 | [10.1056/NEJMoa1616288](https://doi.org/10.1056/NEJMoa1616288) |
| Kuipers 2017, Genome Res | 12 個人類癌症 single-cell 資料集 | 11／12 資料集有同位點重複突變。7 例有突變遺失，其中 5 個位點沒有大段 deletion | 〔論文實測〕 | [10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117) |
| Satas 2020, Cell Systems（SCARLET） | 轉移性大腸癌單細胞（141 primary＋45 metastasis） | 推出 FHIT、LRP1B、LINGO2 三個 mutation loss。每個都有 read depth 顯著下降支持 | 〔論文實測〕 | [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001) |
| McPherson 2016, Nat Genet（本地 R01） | HGSOC 多區域 WGS＋單核 targeted PCR | 用 infinite sites with loss 模型，以 LRT 檢定 loss。PhyClone 的 p3 truth 帶 `lost_snvs` | 〔論文實測〕 | [10.1038/ng.3573](https://doi.org/10.1038/ng.3573) |
| Wintersinger 2022, Blood Cancer Discov（Pairtree） | 14 例 B-ALL 多樣本 | 作者說 Pairtree 可以推出 infinite sites 的違反 | 〔論文主張〕 | [10.1158/2643-3230.BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092) |

PCAWG 的 Dentro 2021 全文前 20 萬字沒有討論 mutation loss 的頻率（未查到）。

### 2.4 低 CCF clone

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Dentro 2021, Cell（PCAWG） | 2,658 例 WGS | 1,705 例符合 NRPCC ≥ 10，這時只保證 CCF ≥ 30% 的 subclone 可偵測。95.1%（1,621／1,705）至少有 1 個 subclone。CCF < 30% 的 subclone 約 21% SNV 被漏掉。單一樣本約 26% subclonal 突變被誤判為 clonal | 〔論文實測〕 | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) |
| Griffith 2015, Cell Systems（AML31） | 單一病人，primary WGS 312× | 30× 只找到 4／6 個 cluster。第 5 個 cluster 要約 200× 才穩定出現。6 個全部要約 850×。TP53 在 primary 的 VAF 約 0.01%，復發時升到 17.65%。作者建議 subclonal 推論用 500–1,000× | 〔論文實測〕 | [10.1016/j.cels.2015.08.015](https://doi.org/10.1016/j.cels.2015.08.015) |
| Minussi 2021, Nature | 單細胞 CN，8 例 TNBC＋4 株細胞株，16,178 個細胞 | 每個腫瘤 7–22 個 subclone，歸成 3–5 個 superclone。許多 subclone 很小 | 〔論文實測〕 | [10.1038/s41586-021-03357-x](https://doi.org/10.1038/s41586-021-03357-x) |
| Salcedo 2025, Nat Biotechnol（SMC-Het；本地 M07） | 51 個模擬腫瘤 | NRPCC 解釋 sc2A 分數 19.8% 的變異。建議單樣本 NRPCC ≥ 32。subclonal gain 有 25／48 被 Battenberg 漏掉 | 〔論文實測（模擬）〕 | [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y) |

### 2.5 HP 拆分與 read 層級 SNV 共現

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Dentro 2021, Cell（PCAWG） | 短讀 read-pair 定相 | 1,537 例中 245 例有 cis 的 SNV pair，其中 95.1%（233）符合 clone→subclone 關係。995 例中 51 例有 trans pair（sibling 證據）。兩個 subclone 是 sibling 的機率是 parent-child 的 3.11 倍（95% CI 1.71–7.50） | 〔論文實測〕 | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) |
| Sakamoto 2022, Nat Commun（本地 B04） | 20 例 NSCLC，ONT＋Illumina；2 例有 10x scDNA | 每例平均 69 對可排序 pair（範圍 0–649）。S14 靠 long read 從 branched／linear 候選中選出 linear。scDNA 只能局部驗證（S8、S20 各 2、13 對） | 〔論文實測〕 | [10.1038/s41467-022-31133-6](https://doi.org/10.1038/s41467-022-31133-6) |
| Keskus 2025, Nat Biotechnol（Severus） | ONT／PacBio 腫瘤-正常配對，細胞株面板與兒童白血病／淋巴瘤 | 產出 haplotype-specific somatic SV，建 phased breakpoint graph | 〔論文主張〕 | [10.1038/s41587-025-02618-8](https://doi.org/10.1038/s41587-025-02618-8) |
| Ho 2025, bioRxiv（LongPhase-S） | 8 組 ONT 資料，6 株細胞株 | somatic haplotyping 後重新校正 variant。ClairS 的 SNV F1 平均升 4.5%，indel 升 7.1%。purity 估計「優於現有方法」，摘要沒有數字 | 〔論文實測＋主張〕，未同儕審查 | [10.1101/2025.11.20.689492](https://doi.org/10.1101/2025.11.20.689492) |
| B01 黑色素瘤 sublines（本地） | 小鼠單細胞衍生 sublines，ONT | 用 ONT SNV 建樹，SV／甲基化事後放上樹；沒有用共現約束 topology | 〔論文實測〕 | 見本地 `papers/B01_melanoma_longread_2026/README.md` |

病人層級「long read 共現建樹＋完整 single-cell 真值」的論文：除 B04 外未查到。

### 2.6 cnLOH

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Sivakumar 2021, Genetics | TCGA，11,074 對腫瘤-正常，33 種癌 | 94% 腫瘤有 allelic imbalance，基因組中位負擔 32%。5,222 例（約 47%）共有 20,454 個 arm-level cnLOH。17p cnLOH：LGG 21.6%、ESCA 22%、LUSC 20.1%、OV 18.5% | 〔論文實測〕 | [10.1093/genetics/iyaa021](https://doi.org/10.1093/genetics/iyaa021) |
| Ciani 2022, Cell Systems | TCGA，4,950 例，27 種癌 | 每樣本 CN-LOH 負擔中位 2%（IQR 0–9%）。9.2% 看似 wild-type 的基因其實是 CN-LOH | 〔論文實測〕 | [10.1016/j.cels.2021.10.001](https://doi.org/10.1016/j.cels.2021.10.001) |
| Wu 2021（Alleloscope） | scATAC，基底細胞癌 SU008 | chr4 的 cnLOH 只在 clone-2，是 subclonal。P6198 的 cnLOH 用 linked-read WGS 全部驗證 | 〔論文實測〕 | [10.1038/s41587-021-00911-w](https://doi.org/10.1038/s41587-021-00911-w) |
| Zaccaria & Raphael 2021（CHISEL） | 單細胞乳癌 | 找到 total CN 看不到的 cnLOH | 〔論文實測〕 | [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6) |

### 2.7 CN timing／multiplicity

| 論文 | 資料類型 | 數字 | 等級 | DOI |
|---|---|---|---|---|
| Gerstung 2020, Nature（PCAWG，MutationTimeR） | 2,658 例 WGS；2,116 例有可定時的 gain | gain 的 molecular time 中位 0.60（IQR 0.10–0.87）。arm-level gain 有 80–90% 只讓 allele-specific CN 加 1。57%（468／815）near-diploid 腫瘤的 gain 同步發生。4,700 萬個點突變中 22% early clonal（multiplicity > 1）、7% late clonal、53% 無法定時、17% subclonal | 〔論文實測〕 | [10.1038/s41586-019-1907-7](https://doi.org/10.1038/s41586-019-1907-7) |
| Nik-Zainal 2012, Cell | 21 例乳癌 WGS | multiplicity 定時法的早期示範 | 〔論文主張〕，本次未重查數字 | [10.1016/j.cell.2012.04.023](https://doi.org/10.1016/j.cell.2012.04.023) |
| Zaccaria & Raphael 2021（CHISEL） | 單細胞 | 用 haplotype-specific CN 把 allele 事件排在 WGD 之前或之後 | 〔論文主張〕 | [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6) |

## 3. 使用者設計參數是否落在真實範圍

設計值取自 README 與圖：purity 0.40；C1 CCF 1.00、C2 0.80、C4 0.45、C3 0.10；depth 200×；100 個 SNV（10 種角色 × 10）。

| 設計 | 設計值 | 真實範圍 | 判定 |
|---|---|---|---|
| purity | 0.40 | TCGA ABSOLUTE 平均 0.62 ± 0.20；PDAC 中位 0.33 | **在範圍內**，約平均減 1 SD〔論文實測＋推論〕 |
| depth | 200× | PCAWG WGS 中位約 46×；TRACERx WES 中位 413×；Griffith 建議 200–300× | **短讀 WGS 中偏高；ONT 腫瘤 WGS 更是偏高**。要加 40–60× 的敏感度組〔推論〕 |
| NRPCC | 0.4·200／(0.4·2＋2·0.6) ≈ 40（ψ≈2） | SMC-Het 建議 ≥ 32；PCAWG 門檻 10 | 達標。若 depth 降到 60×，NRPCC ≈ 12，低於 32〔推論〕 |
| clone 數與形狀 | 4 個 clone，C1→{C2, C3}、C2→C4 | PCAWG 95.1% 有 subclone；sibling 比 parent-child 多 3.11 倍；Minussi 7–22 個 subclone | **在範圍內**〔論文實測＋推論〕 |
| C3 低 CCF | CCF 0.10，cell prev 0.04，期望 VAF ≈ 0.02，200× 時約 4 條 alt read | PCAWG 只保證 CCF ≥ 0.30；AML31 最低頻 cluster 需要約 850× | **生物上存在，但在 200× 低於可靠偵測下限**。模擬沒有 caller 與 error，所以 PhyClone 仍找到 C3。真實 ONT error 率接近 0.02，這群 SNV 多半不會被 call 出來〔推論〕 |
| subclonal HP1 gain | seg A 在 C2 加 1 copy | Gerstung：80–90% gain 只加 1；Watkins：中位 18% 基因組 subclonal；TRACERx：62% 有 MSAI | **在範圍內**〔論文實測〕 |
| cnLOH | seg D 在 C2（CCF 0.80），subclonal | 約 47% TCGA 腫瘤有 arm-level cnLOH；Alleloscope 有 subclonal cnLOH | **在範圍內**〔論文實測〕 |
| 突變遺失比例 | s2＋s10 共 20／100 個 SNV 受影響 | TRACERx：subclonal 突變中位 13%（0–56%）來自 loss；CONIPHER 生成器 `prop_mut_lost` 0.02–0.25 | **在範圍內，偏高端**〔論文實測＋實測〕 |
| multiplicity | s1、s9 multiplicity 2；s8 為 1 | PCAWG 22% 點突變是 early clonal（multiplicity > 1） | **在範圍內**〔論文實測〕 |
| read 共現 | 指定 pair 各有 80 條跨越 read | B04 每例平均只有 69 對可排序 pair；PCAWG 短讀只有 245／1,537 例有 cis pair | **偏樂觀**。要依 SNV 間距與 read 長度分佈抽跨越 read，大部分 pair 應為 0〔推論〕 |
| 事件密度 | 100 個 SNV 中 7 類事件 | 真實 WGS 有數千到數萬個 SNV，事件分散 | **刻意加密的壓力測試**，不是典型腫瘤〔推論〕 |

## 4. 模擬可信度的業界標準（問題 8）

| 做法 | 例子 | 怎麼用真實資料校準 | DOI |
|---|---|---|---|
| 樹取自真實 cohort 的重建 | SMC-Het（Salcedo 2025） | 51 棵樹中 25 棵來自 PCAWG 的 DPClust＋Battenberg 重建，16 棵來自文獻，10 棵是 PD4120 的邊界案例。有 titration 系列（8×–128×）〔論文實測〕 | [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y) |
| spike-in 到真實 read | BAMSurgeon（Ewing 2015）；SMC-Het | 用 GIAB HG002 300× 真實 read，先定相，再依 CP 與 CN 調 read pool，把 SNV／SV spike-in。除了 deletion 以外，子 clone 帶有父 clone 的突變，所以 SMC-Het 本身也模擬了 deletion 造成的遺失〔論文實測〕 | [10.1038/nmeth.3407](https://doi.org/10.1038/nmeth.3407) |
| 評分標準 | Salcedo 2020 | 定義 purity、clone 數、CCF、co-clustering、ancestor-descendant 等指標；跑 580 個重建，改變 depth、癌別與 caller〔論文實測〕 | [10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z) |
| CN 取自真實樣本 | PCAWG-11（Dentro 2021） | PhylogicSim500：500 個樣本，CN profile 從 PCAWG 樣本抽。SimClone1000：965 個樣本，用網格涵蓋 PCAWG 看到的情境〔論文實測〕 | [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009) |
| 參數範圍取自 cohort | CONIPHER（Grigoriadis 2024）；TRACERx 421 | 150 份模擬，依樣本數分組。生成器有 mutation loss、WGD、noise，預設 coverage 400、purity 0.7–0.9〔論文實測＋本 repo 程式〕 | [10.1038/s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9) |
| 只模擬 VAF | Pairtree（Wintersinger 2022） | 沒有 CN、沒有 loss。真實資料驗證靠 14 例 B-ALL 專家樹〔論文實測＋本 repo 筆記〕 | [10.1158/2643-3230.BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092) |
| 實務指引 | Tarabichi 2021, Nat Methods | 列出每一步的假設與不確定性，建議 QC 做法〔論文主張；本次沒有逐條查核建議內容〕 | [10.1038/s41592-020-01013-2](https://doi.org/10.1038/s41592-020-01013-2) |
| 模擬器綜述 | Lai 2024, arXiv | 評估 51 個模擬方法，指出假設差異大〔論文主張〕 | [10.48550/arXiv.2402.09599](https://doi.org/10.48550/arXiv.2402.09599) |
| 實體細胞株混合 | Farahani 2017 | 見第 5 節 | [10.1038/s41598-017-13338-8](https://doi.org/10.1038/s41598-017-13338-8) |

建議給本研究的做法〔推論〕：

1. 每個事件參數附一個真實數字來源（第 3 節表格可直接引用）。
2. 加一組「典型腫瘤」設定：depth 40–60×、C3 CCF ≥ 0.30、跨越 read 數依 SNV 間距抽。
3. 用 SMC-Het 的方式升級到 read 層級：以 ONT 細胞株的真實 read 當底，依 HP（longphase haplotag）切 read pool，再 spike-in 設計樹的 SNV 與 CN。這樣 ONT error、phasing 斷點、跨越 read 數都來自真實資料。
4. 回報 NRPCC，並區分 nominal 與實際 purity。

## 5. 已知真值的實體資料（問題 9）

| 資料 | 真值內容 | 平台 | 可取得性 | 限制 | DOI |
|---|---|---|---|---|---|
| Farahani 2017 細胞株混合 | 已知混合比例（0.9／0.1 到 0.1／0.9），每組 14 個樣本；兩組：近二倍體（184-hTERT-L2＋HCT116）、非整倍體（同一病人來的 DAH55＋DAH56）；另有 PDX SA494 | Illumina MiSeq 深度 amplicon（中位 5,488× 與 11,754×） | ENA PRJEB18801 | 只有兩個 clone，沒有樹；是 amplicon，不是 WGS〔論文實測〕 | [10.1038/s41598-017-13338-8](https://doi.org/10.1038/s41598-017-13338-8) |
| Marass 2016（Ann Appl Stat） | 作者說用「受控生物資料」驗證（單細胞稀釋的癌細胞株與正常株混合） | exome | 未查 | 混合細節未從摘要確認〔論文主張〕 | [10.1214/16-AOAS986](https://doi.org/10.1214/16-AOAS986) |
| Salehi 2021, Nature | DLP+ 單細胞時間序列，共 42,000 個細胞基因組；TNBC PDX 做了實驗強制的 clone 競爭 | DLP+ scWGS | EGA 受控 | 真值是 CN 定義的 clone 與比例，不是 SNV 樹〔論文主張〕 | [10.1038/s41586-021-03648-3](https://doi.org/10.1038/s41586-021-03648-3) |
| B01 小鼠黑色素瘤 sublines（本地） | 單細胞衍生 sublines，各自 ONT bulk | ONT R10.4 | 見本地筆記 | 沒有單細胞定序的真值樹；小鼠 | 見本地 README |
| R01 McPherson 2016（本地） | 單核 targeted PCR 參考樹 | Illumina | PhyClone benchmark 已收錄 | 只有 3 位病人有單核資料；真值是模型樹 | [10.1038/ng.3573](https://doi.org/10.1038/ng.3573) |
| B04 Sakamoto 2022（本地） | ONT bulk＋同病人 10x scDNA（S8、S20） | ONT＋Illumina | JGA 受控 | 只能局部驗證 | [10.1038/s41467-022-31133-6](https://doi.org/10.1038/s41467-022-31133-6) |
| B09 PCDH 甲基化 barcode（本地） | 同病人 colony WGS 樹 | ONT 約 280× | 見本地筆記 | read dendrogram，不是 SNV clone tree | 見本地 README |

結論〔推論〕：沒有一套公開資料同時具備「病人 ONT bulk＋HP phasing＋完整 single-cell SNV 真值樹」。最接近的是 B04（局部）。可行的替代是自己做 in silico mixing：把不同 ONT 細胞株（或同一株不同 purity subsample）的 read 依已知比例混合。混合比例是真值，但樹只有「各株為 sibling」這一種形狀。

## 6. 參考文獻

1. Aran D, Sirota M, Butte AJ. Systematic pan-cancer analysis of tumour purity. *Nat Commun* 6:8971 (2015). [10.1038/ncomms9971](https://doi.org/10.1038/ncomms9971)
2. TCGA Research Network (Raphael BJ et al.). Integrated genomic characterization of pancreatic ductal adenocarcinoma. *Cancer Cell* 32:185–203 (2017). [10.1016/j.ccell.2017.07.007](https://doi.org/10.1016/j.ccell.2017.07.007)
3. Dentro SC et al. Characterizing genetic intra-tumor heterogeneity across 2,658 human cancer genomes. *Cell* 184:2239–2254 (2021). [10.1016/j.cell.2021.03.009](https://doi.org/10.1016/j.cell.2021.03.009)
4. Jamal-Hanjani M et al. Tracking the evolution of non-small-cell lung cancer. *NEJM* 376:2109–2121 (2017). [10.1056/NEJMoa1616288](https://doi.org/10.1056/NEJMoa1616288)
5. Watkins TBK et al. Pervasive chromosomal instability and karyotype order in tumour evolution. *Nature* 587:126–132 (2020). [10.1038/s41586-020-2698-6](https://doi.org/10.1038/s41586-020-2698-6)
6. Zaccaria S, Raphael BJ. Characterizing allele- and haplotype-specific copy numbers in single cells with CHISEL. *Nat Biotechnol* 39:207–214 (2021). [10.1038/s41587-020-0661-6](https://doi.org/10.1038/s41587-020-0661-6)
7. Wu CY et al. Integrative single-cell analysis of allele-specific copy number alterations and chromatin accessibility in cancer. *Nat Biotechnol* 39:1259–1269 (2021). [10.1038/s41587-021-00911-w](https://doi.org/10.1038/s41587-021-00911-w)
8. Funnell T et al. Single-cell genomic variation induced by mutational processes in cancer. *Nature* 612:106–115 (2022). [10.1038/s41586-022-05249-0](https://doi.org/10.1038/s41586-022-05249-0)
9. Kuipers J, Jahn K, Raphael BJ, Beerenwinkel N. Single-cell sequencing data reveal widespread recurrence and loss of mutational hits in the life histories of tumors. *Genome Res* 27:1885–1894 (2017). [10.1101/gr.220707.117](https://doi.org/10.1101/gr.220707.117)
10. Satas G, Zaccaria S, Mon G, Raphael BJ. SCARLET: single-cell tumor phylogeny inference with copy-number constrained mutation losses. *Cell Systems* 10:323–332 (2020). [10.1016/j.cels.2020.04.001](https://doi.org/10.1016/j.cels.2020.04.001)
11. McPherson A et al. Divergent modes of clonal spread and intraperitoneal mixing in high-grade serous ovarian cancer. *Nat Genet* 48:758–767 (2016). [10.1038/ng.3573](https://doi.org/10.1038/ng.3573)
12. Wintersinger JA et al. Reconstructing complex cancer evolutionary histories from multiple bulk DNA samples using Pairtree. *Blood Cancer Discov* 3:208–219 (2022). [10.1158/2643-3230.BCD-21-0092](https://doi.org/10.1158/2643-3230.BCD-21-0092)
13. Griffith M et al. Optimizing cancer genome sequencing and analysis. *Cell Systems* 1:210–223 (2015). [10.1016/j.cels.2015.08.015](https://doi.org/10.1016/j.cels.2015.08.015)
14. Minussi DC et al. Breast tumours maintain a reservoir of subclonal diversity during expansion. *Nature* 592:302–308 (2021). [10.1038/s41586-021-03357-x](https://doi.org/10.1038/s41586-021-03357-x)
15. Salcedo A et al. Crowd-sourced benchmarking of single-sample tumor subclonal reconstruction. *Nat Biotechnol* 43:581–592 (2025). [10.1038/s41587-024-02250-y](https://doi.org/10.1038/s41587-024-02250-y)
16. Salcedo A et al. A community effort to create standards for evaluating tumor subclonal reconstruction. *Nat Biotechnol* 38:97–107 (2020). [10.1038/s41587-019-0364-z](https://doi.org/10.1038/s41587-019-0364-z)
17. Sakamoto Y et al. Phasing analysis of lung cancer genomes using a long read sequencer. *Nat Commun* 13:3464 (2022). [10.1038/s41467-022-31133-6](https://doi.org/10.1038/s41467-022-31133-6)
18. Keskus AG et al. Severus detects somatic structural variation and complex rearrangements in cancer genomes using long-read sequencing. *Nat Biotechnol* (2025). [10.1038/s41587-025-02618-8](https://doi.org/10.1038/s41587-025-02618-8)
19. Ho ME et al. LongPhase-S: purity estimation and variant recalibration with somatic haplotying for long-read sequencing. *bioRxiv* (2025). [10.1101/2025.11.20.689492](https://doi.org/10.1101/2025.11.20.689492)
20. Sivakumar S et al. Pan cancer patterns of allelic imbalance from chromosomal alterations in 33 tumor types. *Genetics* 217:iyaa021 (2021). [10.1093/genetics/iyaa021](https://doi.org/10.1093/genetics/iyaa021)
21. Ciani Y et al. Allele-specific genomic data elucidate the role of somatic gain and copy-number neutral loss of heterozygosity in cancer. *Cell Systems* 13:183–193 (2022). [10.1016/j.cels.2021.10.001](https://doi.org/10.1016/j.cels.2021.10.001)
22. Gerstung M et al. The evolutionary history of 2,658 cancers. *Nature* 578:122–128 (2020). [10.1038/s41586-019-1907-7](https://doi.org/10.1038/s41586-019-1907-7)
23. Nik-Zainal S et al. The life history of 21 breast cancers. *Cell* 149:994–1007 (2012). [10.1016/j.cell.2012.04.023](https://doi.org/10.1016/j.cell.2012.04.023)
24. Ewing AD et al. Combining tumor genome simulation with crowdsourcing to benchmark somatic single-nucleotide-variant detection. *Nat Methods* 12:623–630 (2015). [10.1038/nmeth.3407](https://doi.org/10.1038/nmeth.3407)
25. Grigoriadis K et al. CONIPHER: a computational framework for scalable phylogenetic reconstruction with error correction. *Nat Protoc* 19:159–183 (2024). [10.1038/s41596-023-00913-9](https://doi.org/10.1038/s41596-023-00913-9)
26. Frankell AM et al. The evolution of lung cancer and impact of subclonal selection in TRACERx. *Nature* 616:525–533 (2023). [10.1038/s41586-023-05783-5](https://doi.org/10.1038/s41586-023-05783-5)
27. Tarabichi M et al. A practical guide to cancer subclonal reconstruction from DNA sequencing. *Nat Methods* 18:144–155 (2021). [10.1038/s41592-020-01013-2](https://doi.org/10.1038/s41592-020-01013-2)
28. Lai J, Liu Y, Scharpf RB, Karchin R. Evaluation of simulation methods for tumor subclonal reconstruction. *arXiv* 2402.09599 (2024). [10.48550/arXiv.2402.09599](https://doi.org/10.48550/arXiv.2402.09599)
29. Farahani H et al. Engineered in-vitro cell line mixtures and robust evaluation of computational methods for clonal decomposition and longitudinal dynamics in cancer. *Sci Rep* 7:13467 (2017). [10.1038/s41598-017-13338-8](https://doi.org/10.1038/s41598-017-13338-8)
30. Marass F et al. A phylogenetic latent feature model for clonal deconvolution. *Ann Appl Stat* 10:2377–2404 (2016). [10.1214/16-AOAS986](https://doi.org/10.1214/16-AOAS986)
31. Salehi S et al. Clonal fitness inferred from time-series modelling of single-cell cancer genomes. *Nature* 595:585–590 (2021). [10.1038/s41586-021-03648-3](https://doi.org/10.1038/s41586-021-03648-3)

查核備註：Kuipers 2017、SCARLET、CHISEL、Alleloscope、Nik-Zainal、Marass 的 DOI 來自搜尋結果或既有知識，沒有逐一打開 DOI 頁面確認。Frankell 2023 只用來引用 WGD 與模擬驗證規模（WGD 77%、subclonal WGD 19%、150 份模擬），正文未另列表。
