# PhyClone 是否使用 long-read 資訊？

更新日期：2026-08-25

## 結論

PhyClone 本身不是 long-read-aware 演算法。它可以接受由 ONT 或 PacBio BAM 上游計算出的 allele counts，但進入 PhyClone 後只使用每個 sample／mutation 的 aggregated `ref_counts` 與 `alt_counts`，以及 copy-number、normal CN、tumour content 和 error rate 等欄位。

因此要分開兩件事：

1. **long-read 可作為上游資料來源：可以。** 例如先從 ONT BAM 做 variant pileup，再把 REF／ALT read counts 寫入 PhyClone TSV。
2. **PhyClone 直接使用 long-read 特有資訊：沒有證據支持。** 官方 model、schema 與 source 沒有讀取 BAM／CRAM／FASTQ，也沒有使用 read length、CIGAR、同一 molecule 的多位點共現、HP／PS phase tag、haplotype sequence 或 methylation tag。

## 輸入格式證據

官方 README 將主要輸入定義為 tidy TSV，必要欄位是：

- `mutation_id`
- `sample_id`
- `ref_counts`
- `alt_counts`
- `major_cn`
- `minor_cn`
- `normal_cn`

可選欄位包括 `tumour_content`、`error_rate` 與 `chrom`。官方 schema 也只驗證這些 scalar／count 欄位：

- [官方 README 的 input format](https://github.com/Roth-Lab/PhyClone#main-input-format)
- [官方 input schema](</bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/validator/PhyClone_schema.json:21>)
- [local README:68-110](</bip8_disk/boyu114/main_work/research/phyclone/PhyClone/README.md:68>)

README 確實提到，如果某些 mutation 缺少資料，可以從該 sample 的 BAM 抽取 REF／ALT counts；但這是 **上游資料準備建議**，不是 PhyClone 內部讀 BAM。local README 的原文位置是 [81-82](</bip8_disk/boyu114/main_work/research/phyclone/PhyClone/README.md:81>)。

## 官方程式碼追蹤

PhyClone 的 loader 從每列讀取：

```python
ref_count = row_series["ref_counts"]
alt_count = row_series["alt_counts"]
major_cn = row_series["major_cn"]
minor_cn = row_series["minor_cn"]
normal_cn = row_series["normal_cn"]
tumour_content = row_series["tumour_content"]
```

來源：[pyclone.py:299-319](</bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/pyclone.py:299>)。

接著 likelihood 只使用 aggregated counts 與 expected VAF：

```text
ALT_count ~ Binomial(total_count, expected_VAF)
```

或使用 Beta-Binomial。來源：[math_utils.py:215-244](</bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/utils/math_utils.py:215>)。

對官方 clone 的 source、dependency 與 README 搜尋 `BAM`、`CRAM`、`FASTQ`、`pysam`、`samtools`、`HP`、`PS`、`haplotype`、`phasing`、`ONT`、`PacBio` 後，唯一的 BAM 命中是 README 中「由使用者自行抽取 counts」的說明；沒有發現 PhyClone 內部的 alignment/read parser 或 long-read-specific likelihood。

## 論文資料型態

PhyClone 論文把方法定位為從 **bulk sequencing** 重建 cancer phylogeny，模型輸入是 SNV allelic counts、CNV information 和 tumour content。官方 GitHub README 也將工具描述為 “from bulk sequencing”，並把 input 明確寫成 `ref_counts`／`alt_counts`。

- [PhyClone primary paper](https://academic.oup.com/bioinformatics/article/41/7/btaf344/8161563)
- [PhyClone GitHub README](https://github.com/Roth-Lab/PhyClone)

論文中的 HGSOC ground truth 使用 single-cell 與 targeted sequencing 來評估結果；這些資料是 benchmark／ground truth，不代表 PhyClone 的 likelihood 直接使用 single-cell 或 long-read molecule 資訊。

### 平台 provenance 的精確說法

PhyClone 主論文與 supplement 對 real-data experiment 的描述是 **WGS bulk data**、**WGS + targeted deep-sequencing counts**，沒有在 PhyClone 方法中指定單一測序儀器型號，也沒有把 ONT／PacBio 當作方法條件。因此目前能負責任地說：

- PhyClone paper 的 real-data benchmark 不是以 long-read-specific input 定義；
- exact instrument/platform 應追溯到被引用的原始 HGSOC data paper，而不是從 PhyClone 本身推定；
- PhyClone 的 TSV counts contract 對 Illumina、ONT、PacBio 都是平台中立的。

PhyClone 論文的 HGSOC provenance 來源是 [McPherson et al. 2016](https://www.nature.com/articles/ng.3573)；該文在公開摘要中只概括為 whole-genome 與 single-nucleus sequencing，未在 PhyClone paper 中提供可直接引用的單一 platform model。

## 與目前研究 repo 的差異

目前 `/bip8_disk/boyu114/main_work` 研究線使用 ONT long reads、HP／PS 與同一 molecule 上的多 SNV 共現來做 read-level clone evidence；local knowledge note 將此流程描述為：

```text
same-read multi-SNV genotype
→ pairwise co-occurrence
→ partial/full populations
→ candidate clone trees
```

來源：[InterSubMod methodology summary](</bip8_disk/boyu114/bip8_disk_boyu_database/multi-evol-tree/by_date/2026/2026-08-01_multi-evol-tree-hcc1395-topology-summary/notes/InterSubMod_methodology_research_summary_20260626_20260723.md:19>)。

這與 PhyClone 的輸入層級不同：

| 資訊層級 | PhyClone | 目前 long-read research 線 |
|---|---|---|
| 單點 REF／ALT counts | 使用 | 使用 |
| CN、purity／tumour content | 使用 | 可作輔助 context |
| 同一條 read 的多 SNV 共現 | 不使用 | 核心證據 |
| read length／alignment CIGAR | 不使用 | 可由上游流程使用 |
| HP／PS haplotype phase | 不使用 | 輔助分層／provenance |
| ONT methylation tags | 不使用 | 目前僅 bounded auxiliary |

## 最終判定

若問題是「PhyClone 能不能分析由 long-read 定序產生的 VAF counts？」答案是 **可以，因為輸入 counts 與平台無關**。

若問題是「PhyClone 的 clone inference 有沒有利用 long-read 的 molecule-level 資訊？」答案是 **沒有**。它使用的是 bulk allele-count model；long-read 的優勢必須在 PhyClone 之前由 pileup／variant caller／phasing pipeline 壓縮成 counts 或其他外部 annotation，原始 read-level 資訊不會進入 PhyClone likelihood。

因此，把 PhyClone 稱為「可使用 long-read counts 的 bulk VAF／clone-tree 方法」是準確的；把它稱為「long-read phasing 或 read-level clone reconstruction 方法」則不準確。
