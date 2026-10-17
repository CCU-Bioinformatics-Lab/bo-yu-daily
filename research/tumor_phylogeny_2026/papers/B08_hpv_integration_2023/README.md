# B08｜HPV heterocateny：long reads 重建局部 SV molecular history

## 論文、版本與定位

Akagi K, Symer DE, Mahmoud M, et al. **Intratumoral Heterogeneity and Clonal Evolution Induced by HPV Integration.** *Cancer Discovery* 13(4), 910–927 (2023). DOI：[10.1158/2159-8290.CD-22-0900](https://doi.org/10.1158/2159-8290.CD-22-0900)，online 2023-01-30，issue 2023-04。查核日期 2026-10-15。

本地 PDF 是 **CSHL 作者機構保存的 accepted-manuscript／online-before-typesetting 版本**：46 physical pages，含逐行編號、獨立 figure legends 與後置圖；不是正式排版的 18 頁期刊 PDF。以下頁碼均指這份本地 PDF，從 1 起算。

**定位：真正使用 ONT／PacBio long reads 推導局部 SV ancestry、amplification／excision 次序的延伸研究；不是 de novo 完整 tumor clone tree，也沒有 single-cell sequencing。** 不能把文中 molecular ancestor 自動當作 cancer-cell MRCA。

## 樣本與真正使用的訊號

p4 明確確認 **5 個 HPV-positive primary oropharyngeal cancers＋4 cell lines**，從先前 105 病人的 WGS 篩選；入選條件為 integration 周圍 CN≥4n 或 SV breakpoints 距離<60 kb。四株為 VU147、GUMC-395、HeLa、HTEC；HTEC 為 HPV16 轉染後 immortalized epithelial model，不能把四株全稱病人原發癌，也不能將富集樣本的結果外推為所有 HPV 癌盛行率。

Illumina 提供 CN／initial breakpoints，PacBio HiFi 提供高準確度 junction sequence，ONT 提供跨數萬鹼基、多個病毒與 host segments 的連續分子連接。p21–23 Methods：對 hybrid GRCh37＋HPV reference alignment；breakpoints 需跨平台支持（≥20 Illumina 或≥5 PacBio／ONT，至少兩平台），再 local realign。演化重建限 **≥20-kb informative ONT reads**；segment／breakpoint pattern 至少三 reads 支持，依 pattern 分組，人工以最少新增 segments／breakpoints 排序。

它的模型假設 unique breakpoint 只發生一次且由後代保留，除非 deletion；新 deletion 應產生新 breakpoint。作者再以最少 deletion、insertion、inversion、ecDNA excision、rolling-circle amplification、recombination、translocation 解釋組間差異，必要時引入未觀察到的 intermediate。這是可核對的 mechanistic reconstruction，沒有全樹 likelihood／posterior 或唯一性保證。

## Fig. 4、5、7 的關鍵讀法

- **Fig. 4（圖 p43，legend p36–37，結果 p7–8）**：Tumor 2 的 EP300／chr22 區域有多種 virus-host concatemers；相同 viral breakpoint 17 亦出現在 chr4 integrant，支持共同 molecular origin。它證明跨位點結構有關聯，未證明兩種 structures 位於同一 cell。
- **Fig. 5（圖 p44，legend p37–38，結果 p9–11）**：GUMC-395 的 MYC 區域最高約225n，774 條≥20-kb virus-host ONT reads 多數帶 breakpoint 7；共享 V–F–B–C pattern 與 D／E deletion 支持早期共同結構，再經 ecDNA amplification、recombination、deletion 分化。Fig. 5C 的虛括號是推測 intermediate，5D 為插入、duplication、inversion、translocation 的順序模型；FISH 提供 chromosome-level 佐證。
- **Fig. 7（圖 p46、legend p39）**：跨樣本綜合的 HPV replication→integration→host capture／excision→ecDNA amplification／recombination→再插入模型。它不是某病人抽樣 cells 的 lineage tree。

最重要限制是作者自己在 **p18 lines 454–466** 說：沒有 longitudinal specimens 驗證事件序列；目前 LR-seq 不能分辨不同 structures 是接在同一個>100-kb molecule、共存於同 cell，或分布於 distinct subclones。因此不能從 molecule counts 算確定 CCF，也不能用「不同 read pattern」直接當不同 clone。

## 對本 repo 的用途與最小 ablation

以下為**分析推論**，未修改模型。`plan.md` C0／C1 可增 junction／segment-pattern provenance、molecule IDs、ecDNA／high-CN flags；C2／C3 應把這些超高 CN、未知 subclonal copy mixtures 標成 multiplicity／CCF 不可辨識，本文沒有測 purity／CCF，也沒有可沿用的 HP／PS 校準。

**C4 最值得借鏡的是限制條件**：同 read 跨 SNV／SV 是物理連接證據；在多 copy、ecDNA、recombination 場景，不能直接套 `C_h=1` 的 cell-ancestry 規則。C5 可用 shared unique junction 檢查 CN-induced clusters；C6 應分「直接觀察 junction」「模型推定順序」「未知 cell assignment」。breakpoint loss 的處理也提醒 CNV timing 模型不能一律採不允許 loss 的 infinite sites。

最小 ablation：先在 published junction patterns 建 fixture，比較純 SNV ancestry、加入 shared-junction constraints、再允許 deletion／ecDNA event 的結果；以 held-out junction／跨平台確認作評估。超高 CN 區域另報排除組。只能報 local-event consistency 與可辨識關係，不能宣稱改善 patient full-tree accuracy。

## 資料與驗真

p25 Data availability：Illumina／PacBio／ONT 資料 **EGAD00001009630、EGAD00001009631、EGAD00001009632**，研究 **EGAS00001006652**；HeLa 為 **phs000640** substudy。raw data 受控，本文不等於可免申請取得同病人資料。已閱讀 main Results、Methods、limitations、data statement，並渲染核對 Fig. 4／5／7。

- [paper.pdf](paper.pdf)：[CSHL 機構來源](https://repository.cshl.edu/40840/1/2023-Goodwin-Intratumoral-heterogeneity-and-clonal-evolution-induced-by-HPV-integration.pdf)，`file`／`pdfinfo` 均確認 46 頁真 PDF。
- SHA256：`f5aeab2885a2244c4d458346b822855eb81690b53fa92e5148c85b41ed8e4a1f`。
- [paper.txt](paper.txt)：`pdftotext -layout`，保留 page breaks 與 manuscript line numbers。
