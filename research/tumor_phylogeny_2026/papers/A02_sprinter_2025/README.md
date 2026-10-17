# A02 — SPRINTER：病人單細胞樹、細胞週期與轉移

Lucas, O. et al. **Characterizing the evolutionary dynamics of cancer proliferation in single-cell clones with SPRINTER.** *Nature Genetics* **57**, 103–114 (2025). DOI: [10.1038/s41588-024-01989-z](https://doi.org/10.1038/s41588-024-01989-z)。2024-11-29 online，2025 年卷期；目錄使用卷期年份。保存官方正式期刊 PDF。

[官方正文](https://www.nature.com/articles/s41588-024-01989-z) · [官方 PDF](https://www.nature.com/articles/s41588-024-01989-z.pdf) · [本機 PDF](paper.pdf) · [完整文字](paper.txt)

## 收錄與閱讀定位

第一類 A：直接病人 scDNA genetic phylogeny。主要新病人資料為 **1 名 NSCLC 病人 CRUKP9145**，10 個腫瘤樣本、14,994 顆細胞：5 個原發區域共 9,532 cells，5 個轉移部位共 5,462 cells。另重分析 7 個 TNBC 與 15 個 HGSC tumors 的 61,914 顆細胞；這些不是 22 名新招募且全數獨立驗證的病人。DLP+ scWGS 使用 short reads，本文不是 long-read 或 linked-read 演化樹方法。

PDF 實體頁從 1 起算：p.1 為印刷頁 103；p.2 方法概覽；p.5（印刷 107）病人/部位與 clone phenotype；p.7 Fig.4 的 single-cell clone tree 與 metastatic migration；p.15 Methods「Phylogenetic and metastatic seeding analysis」；p.16 Data/Code availability。PDF 後段 Extended Data Fig.5/6 補充 clone distribution、影像與時間證據。不能把本文的 FACS **cell-cycle ground truth** 叫作 patient-tree ground truth。

## 推樹流程與相依性

SPRINTER 的核心先辨識 S/G2 cells，修正 replication 對 read-depth ratio 的擾動，再指派 clones 及 CNAs。S-phase 的局部 depth 上升若直接當 CN gain，會製造假 clone，因此對 CNA-based tree 的上游 QC 很重要。以細胞週期分選與 EdU 標記建立的實驗真值檢查的是此部分。

病人演化樹在後續三步建立：先對每 clone 合併 reads，透過 pseudobulk 與 probabilistic SNV cellular-frequency 模型判斷 SNV presence；其次使用 **HUNTRESS** 重建 SNV evolution；最後用 **MEDICC2** 重建 CNA evolution，但**固定與 SNV tree 相同的 topology**。因此不能說 SNV tree 和 CN tree 各自獨立建出相同答案。再以 MACHINA 推 metastasis seeding 與 migration，這也依賴前述樹和解剖取樣位置。

Fig.4 顯示不同 metastatic clades 的增殖差異，較高增殖 clones 的 seeding potential 與 ctDNA shedding 較高。Ki-67、nuclear imaging 和 clinical imaging 是 phenotype/生長的正交佐證，並沒有逐條確認所有 ancestral edges。單一新 NSCLC 病人的泛化能力與失落/未取樣 clones 仍有限。

## 與使用者關鍵字的關係

single cell、CNV/copy number、SNV cellular frequency 與 ctDNA CCF 均實際參與分析；cell-cycle/ploidy 是避免誤判 CN 的重要變數。allele/haplotype-aware 方法出現在相關背景，但本文主要的新增 SPRINTER clone identification 並非 LongPhase `HP`/`PS` 感知模型，沒有同 molecule 的 `n00/n01/n10/n11` linkage factor。LOH、purity 不是本文核心準確度終點。

ctDNA shedding index 可用 ctDNA SNV frequency 減去組織 SNV frequency，也可比較扣除祖先共享訊號後的 clone proportions。兩種定義依賴不同測量與樹，不能把血中 read fraction 直接當成組織 cellular purity；亦不能因高 ctDNA VAF 就推斷該 clone 的細胞比例一定最高。

## 資料與軟體

主要病人 raw scDNA：EGA **EGAD00001015411**（TRACERx/PEACE DAC 受控）；cell-cycle 實驗 raw：SRA **PRJNA1158752**。Processed：Zenodo [10.5281/zenodo.13754278](https://doi.org/10.5281/zenodo.13754278) 為概念記錄；論文 reference 73 指向版本 [13754279](https://doi.org/10.5281/zenodo.13754279)。既有 TNBC/HGSC：Zenodo 6998936 與 7718917。重現時應固定具體版本。

[SPRINTER code](https://github.com/zaccaria-lab/sprinter) · [EGA dataset](https://ega-archive.org/datasets/EGAD00001015411) · [CodeOcean capsule](https://doi.org/10.24433/CO.4888914.v1)。本次只下載論文，不取得病人 raw reads。

## 對 C0–C6 的改進與最小驗證（尚未實作）

C0 的 CN extractor 不應無條件收所有 cells/read-depth profiles；若未來加入 scDNA calibration，需標記 S-phase、QC、coverage、sample location。對 bulk long reads 雖無 single-cell cycle 標籤，仍應以 noisy CN segments 作敏感性分析。C1 schema 儲存 CN reference 及參考樹建法，明示 SNV/CNA tree 的相依性。C2/C3 測 multiplicity、CN-aware likelihood 時，固定 cell cycle filtering 後的 CN；C4 無本文長讀 linkage 真值；C5 可量化是否把 replication artifact 分成新 clone；C6 輸出 unidentifiable edges 與 clone 內 subclonal SNVs，避免假定一個 CNA clone 內所有 SNV 都完全共享。

最小 benchmark：以同一病人的 primary/metastasis 組合作 holdout，將 reference clone cells pseudobulk，比較 total-CN baseline、移除或納入 S-phase、再加 C2/C3。評估 cluster stability、SNV carrier-fraction error、參考 ancestral-pair 關係與按部位的 clone recovery；cell-cycle ground truth 另列結果，不與 topology correctness 合併成一個 accuracy。若要測 C4，必須另找同病人 matched long-read BAM 或以真細胞 genotype 模擬分子；後者需明標 synthetic molecules。
