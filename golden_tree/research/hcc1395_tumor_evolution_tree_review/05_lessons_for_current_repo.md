# 05. 對目前 tumor-tree repo 的啟示

這一章只把論文的可移植原則，對照目前 repo 的 ASCAT + long-read/HP-count 架構；不把論文的資料介面假設成目前模型已經使用的介面。

目前 repo 對 PhyloWGS 原始模型的補充整理可參考 [`research/phylowgs_model_review.md`](../phylowgs_model_review.md)；本章只保留這篇 HCC1395 resource paper 對資料可信度與驗證層級的啟示。

## 1. 可直接借用的研究原則

### 1.1 先固定可信的 site-level evidence，再談 tree

論文先用多 replicate、caller、aligner、深度與 orthogonal assay 固定 somatic call set，再做 clonality analysis。對目前 repo，對應做法是先確認 canonical site-level table 的 provenance、bulk REF/ALT counts、ASCAT total/major/minor CN、ASCAT purity 與 long-read HP counts，再把它交給 model。

### 1.2 VAF 不能只看 ALT / depth

論文明確用 local copy number 修正 clonality，並用 tumor-normal titration 檢查 VAF 隨 purity 的行為。這支持目前 model 將 bulk counts、`rho_ASCAT`、local CN 與 multiplicity 放在同一個 likelihood context，而不是把簡單 VAF 當成獨立真值。

### 1.3 long read 的角色要標清楚

在這篇 HCC1395 resource paper 裡，PacBio long-read 主要用於 mutation call-set 的 orthogonal validation 與 challenging-region filter；它不是 high-confidence candidate branching tree topology 的 PS/HP read-level lineage input。這和目前 repo 想把 long-read HP1/HP2 counts 放進 emission likelihood 的方向不同，因此不能直接說「目前模型重現了論文的 long-read tree」。

### 1.4 topology 與 evidence validation 分開

論文把 mutation validation、CNA validation、single-cell heterogeneity support 與 tree inference 放在不同證據層級。現在的 repo 也應分開記錄：

```text
canonical data table
        ↓
model likelihood
        ↓
inference algorithm
        ↓
candidate topology + CCF + SNV assignment
        ↓
independent QC / holdout / biological interpretation
```

不能因為輸入 call set 很可靠，就宣稱 topology 自動成為 truth。

## 2. 目前 repo 與論文的關鍵差異

| 論文 HCC1395 tree | 目前 repo |
|---|---|
| PhyloWGS / SuperFreq 的 bulk clonality analysis | 目前 active inference 是 finite-K、PhyloWGS-inspired 的 C++ MCMC backend |
| 以 VAF accounting for local CN 的 bulk evidence 為主 | 額外保留 ASCAT purity、major/minor CN、multiplicity 與 long-read HP1/HP2 counts |
| PacBio 是 orthogonal validation | long-read HP counts 在目前方向中是 likelihood observation |
| high-confidence candidate branching tree topology 沒有公開完整 input table/command | 目前 repo 應保存 canonical site-level input contract 與每次 run 的 provenance |
| single-cell 只提供 CNV heatmap support | 目前不能把 PS block 或 HP label 直接當成 clone ancestry；需由 model likelihood/assignment 決定 |

## 3. 目前文件中應保留的說法

建議在研究文件中使用：

> 本研究參考 HCC1395/PhyloWGS 的 copy-number-aware clonal evolution 思路，將 ASCAT purity、local CN、bulk allele counts 與 long-read haplotype observations 放入可替換的 tumor-tree model。輸出是由 inference algorithm 推導的 candidate topology、CCF 與 SNV assignment；它不是 single-cell lineage truth。

不要寫成「用 high-confidence candidate branching tree topology 當作每個 SNV 的 golden label」。比較準確的是把這篇論文當作高品質 benchmark 的方法背景與 biological plausibility reference。

## 4. 對實驗驗證的直接建議

若要讓目前模型的結果接近這篇論文的可信度層級，至少要分開報告：

1. site-level input 是否通過 provenance、CN、purity 與 count QC；
2. likelihood/inference chain 是否收斂，topology 是否在不同 seed/chain 重現；
3. CCF 與 SNV assignment 是否在 holdout 或 perturbation 下穩定；
4. long-read HP evidence 與 bulk evidence 是否一致；
5. 哪些結論只是 candidate tree 的 posterior support，哪些有外部 truth 或 orthogonal assay 支持。
