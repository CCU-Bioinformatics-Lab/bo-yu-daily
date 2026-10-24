# OncoSim 同名工具調查

調查日期：2026-10-24。目的：補完 02 組因 GitHub rate limit 沒查完的「OncoSim」。

證據標記：〔論文〕論文或 README 的描述；〔程式〕讀過原始碼（只讀，沒有執行）；〔推論〕分析推論，沒有實測。程式 clone 在 `/tmp/claude-1024/-bip8-disk-boyu114-main-work/18fc1cc2-ffb5-4afb-8a48-a15890b40de5/scratchpad/clones2/`（暫存，會消失）。

## 結論

- **沒有一個叫 OncoSim 的工具符合需求。** 沒有工具同時輸出可用的真值 clone tree 檔案與 read 或標準格式的 SNV 計數。
- **唯一相關的是 `ciarajudge/OncoSim`。** 這是一個 R／Shiny 小專案，沒有論文。它模擬 SNV、allele-specific CN、cluster 結構、purity，並抽 ref／alt 計數。但它不寫任何檔案，沒有 seed，CN 模型有 bug。只適合當教學參考。〔程式〕
- **「OncoSim」這個名稱主要指加拿大的人口層級癌症 microsimulation。** 它和基因體、定序無關。〔論文〕
- **OncoSimulR 沒有新發現。** 04 報告的描述仍成立。〔程式〕

| 候選 | 類型 | 真值樹 | SNV 資料層 | 符合需求？ |
|---|---|---|---|---|
| `ciarajudge/OncoSim` | R 函式＋Shiny app | 隱含（cluster 的 lineage 字串＋CCF），只畫圖，不寫檔 | 每個 SNV 的 total／variant count、VAF（R data.frame） | **部分**：有 count、purity、mat/pat allele；沒有檔案輸出、沒有 seed、沒有 read |
| OncoSim（CPAC／Statistics Canada） | 人口 microsimulation（Modgen） | 無 | 無 | 否：不是基因體模擬 |
| `JeanatCPAC/OncoSim` | 空 repo（只有 README 標題） | 無 | 無 | 否 |
| OncoSimulR（`rdiaz02/OncoSimul`） | fitness landscape 演化模擬 | genotype genealogy | genotype 頻率，無 read | 否（04 已收錄） |
| OncoSimulator（ICCS／ACGT、p-medicine） | 臨床 in silico 腫瘤療效模擬 | 無 | 無 | 否 |
| 其他同名 repo（`HassDhia/oncosim`、`Shaimaa8/OncoSim`、`Anas-Mohamed-Abdelghany/OncoSim`、`Iamnamanpanday/oncosim_ai_tumor_predictor-`） | 放療 RL、影像、雷射消融、AI 預測 | 無 | 無 | 否 |

## 候選 1：`ciarajudge/OncoSim`

- Repo：https://github.com/ciarajudge/OncoSim 。commit `5f8d223`（2021-10-19）。建立於 2021-04-04。0 star、0 fork。〔程式〕
- License：CC0-1.0（`LICENSE`）。〔程式〕
- 論文：沒找到。README 只有一句 "SNV and CNA profile simulation of a tumour with multiple subclones. Capability also for metastasis simulation."〔論文〕
- 檔案：`main.R`（508 行）、`helpers.R`（1332 行）、`app.R`（Shiny）。生成器是 `bigcancersimulator(num_generations, generationmetastasis, num_metastasis, purity)`（`main.R:1`、`helpers.R:1`）。`helpers.R:584` 另有 `evofreezesimulator`，介面相同。〔程式〕
- 生成流程：每個 generation 放一個 SNV。SNV 隨機選 mat 或 pat allele、chr1–22、位置（`main.R:216-219`）。〔程式〕
- Clone 結構：新 cluster 依機率產生，再隨機決定是 sister 或 daughter。每個 cluster 有一個 `tau`（CCF），daughter 的 tau 不超過 parent（`main.R:141-183` 的同型程式碼）。〔程式〕
- 真值樹：沒有樹檔案。每個 SNV 列有 cluster 編號（第 9 欄）與 lineage 字串（第 10 欄，例如 `ABD` 表示祖先路徑）。樹只用 `treeplotter`／`treeplotterwithmeta` 畫圖。〔程式〕要自己從 lineage 字串重建樹。〔推論〕
- 輸出表欄位（`app.R` 的 `colnames`）：ID、Chromosome、Locus、Mat/Pat、Maternal Copies、Paternal Copies、Multiplicity、CCF、Clone Number、Genotype、Total Counts、Variant Counts、VAF。函式回傳 R list，不寫任何檔案。〔程式〕
- CN 模型：allele-specific。每次 CNA 用 `rpois(1,3)` 抽 maternal 與 paternal copy（`generateCNA`，`main.R:13-27`）。長度約 250 kb。〔程式〕
- CN 不在樹邊上。CNA 發生時，區域內**所有**先前 SNV 都乘上新 CN，不論 SNV 屬於哪個 clone（`main.R:110-130` 的同型程式碼）。所以 CN 是全域的，不是 clone-specific。〔程式〕
- CN bug：`abberatedchrs <- append(aberratedchrs, chromosome)`（`main.R:133`）寫入拼錯的變數（同樣錯誤也在 `main.R:260` 與 `helpers.R:139,295,720,866`）。所以 `aberratedchrs` 一直是空的。之後的新 SNV 永遠拿到 CN (1,1)，不會繼承已發生的 CNA。〔程式〕〔推論：依變數名推得，未執行〕
- 計數模型（`addcountsandvaf`，`helpers.R:380-400`）：total = `(purity*(maternal+paternal) + (1-purity)*2)*50`，再加 `rnorm(sd=25)`。variant 用 `rbinom` 抽，機率含 purity、CCF、multiplicity 與 0.001 定序錯誤率。`evofreezesimulator` 的深度因子是 500（`helpers.R:941`）。〔程式〕
- purity<1：支援，單一純量 `purity`。〔程式〕
- Multi-sample：只有 primary＋一個 metastasis 兩個樣本。〔程式〕
- Haplotype：每個 SNV 標 mat/pat，等於 SNV 所在 haplotype 的真值。但沒有 read，所以沒有共現資訊。〔程式〕
- Read：沒有 FASTQ／BAM。只有 count 層。〔程式〕
- Seed：程式沒有呼叫 `set.seed`，也沒有 seed 參數。呼叫端可自己先 `set.seed`。〔程式〕〔推論：外部 set.seed 可重現，未測〕
- Standalone：要 source R 檔或跑 Shiny app。沒有 CLI。函式開頭 `par(new)` 會觸發繪圖。〔程式〕
- 能否接 PhyClone：要自己從 data.frame 轉 `mutation_id／ref_counts／alt_counts／major_cn／minor_cn／normal_cn`。〔推論〕

## 候選 2：OncoSim（CPAC／Statistics Canada）

- 這是加拿大 Canadian Partnership Against Cancer 與 Statistics Canada 的人口 microsimulation。它模擬個人從出生到死亡，輸出發生率、死亡率、篩檢與成本。〔論文〕
- 模組有 OncoSim-Breast、OncoSim-Cervical、OncoSim-Colorectal、OncoSim-Lung 與一般 25 種癌症模組。〔論文〕
- PubMed `OncoSim[Title/Abstract]` 共 35 筆。抽查 4 筆，全是這個模型：
  - Alagoz et al., Health Rep 2026, DOI [10.25318/82-003-x202600500002-eng](https://doi.org/10.25318/82-003-x202600500002-eng)。
  - Alagoz et al., Health Rep 2025, DOI [10.25318/82-003-x202500600001-eng](https://doi.org/10.25318/82-003-x202500600001-eng)。
  - Pataky et al., CMAJ 2024, DOI [10.1503/cmaj.231682](https://doi.org/10.1503/cmaj.231682)。
  - Murphy et al., Front Oncol 2022, DOI [10.3389/fonc.2022.872765](https://doi.org/10.3389/fonc.2022.872765)。
- 與 clone tree、SNV、定序都無關。〔論文〕
- `JeanatCPAC/OncoSim`（https://github.com/JeanatCPAC/OncoSim ，最後 push 2019-12-17）只有一個 README，內容只有標題 `# OncoSim`。repo 大小 0。〔程式〕作者名可能與 CPAC 有關，未驗證。〔推論〕

## 候選 3：OncoSimulR（補充）

- `rdiaz02/OncoSimul` 最新 commit 仍是 `26d96c7`（2026-04-16），與 04 報告相同。〔程式〕
- 本次沒有找到 read 層或 VAF 計數的新功能。沒有新事實可補。〔論文：Bioconductor vignette 搜尋結果〕

## 候選 4：OncoSimulator（不同名但易混淆）

- EU ACGT／p-medicine 計畫的 in silico oncology 模擬器，模擬腫瘤對治療的反應（arXiv 1009.2186）。〔論文〕
- 沒有 SNV、clone tree 或定序資料。〔論文〕

## 搜尋範圍（2026-10-24）

- GitHub：`gh search repos oncosim`（30 筆上限，回傳 19 筆，這次沒有 rate limit）。逐一看描述。clone 並讀 `ciarajudge/OncoSim` 全部 R 檔。用 `gh api` 查 `JeanatCPAC/OncoSim` 內容與 `rdiaz02/OncoSimul` 最新 commit。
- PubMed：`OncoSim[Title/Abstract]`（35 筆，前 20 筆 PMID，抽查 4 筆 metadata）。
- Web search：「OncoSim simulator tumor sequencing reads clonal」、「"OncoSim" cancer genome simulator SNV copy number subclones github OR bioRxiv」、「"OncoSim" Ciara Judge tumour simulation」。三次都沒有找到名為 OncoSim 的 read 層腫瘤模擬器，也沒有找到 `ciarajudge/OncoSim` 的論文。
- 沒有查：GitLab、Bitbucket、Zenodo、PyPI、CRAN 的同名套件。
