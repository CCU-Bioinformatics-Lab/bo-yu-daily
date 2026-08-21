# 06. Evolutionary-model support：high-confidence candidate branching tree topology 的證據檢查架構

> **文件狀態：review draft。**
>
> 本章不是重新推導 high-confidence candidate branching tree topology，也不是宣稱已證明 S1–S10 的 lineage；它把「哪些資料能支持候選 branching model、支持到哪一層、還缺什麼」整理成可檢查的架構。

## 1. 先定義要檢查的 claim

本章真正要問的是：

```text
high-confidence candidate branching tree topology
        是否與獨立的
        CNA / ploidy / LOH / single-cell CNV evidence 相容？
```

不是直接問：

```text
single-cell data 是否畫出了 S1–S10？
```

因為論文沒有公開每個 single cell 的 SNV genotype、S1–S10 label，或 SNV-CNV joint matrix。因此本章的結論上限是：

> **support / compatibility，而不是 branch-level proof。**

## 2. 整體架構

```text
┌────────────────────────────────────────┐
│ 原始觀測與外部驗證                      │
│                                        │
│ bulk SNV/VAF      ASCAT / WGS CNA       │
│ WES clonality     ploidy / LOH          │
│ karyotype/CytoScan  subHMM              │
│ 10x single-cell CNV  call-set validation│
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ source-specific processing              │
│                                        │
│ copy-number-aware CCF / clonality       │
│ clonal/subclonal CNA states             │
│ cell-level CNV clusters                 │
│ mutation call confidence                │
└────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────┐     ┌──────────────────────────┐
│ PhyloWGS              │     │ support evaluator          │
│ candidate topology    │────▶│ compatibility / stability  │
│ S1–S10 + CCF          │     │ evidence matrix           │
└───────────────────────┘     └──────────────────────────┘
                                      │
                                      ▼
                          claim grade / confidence ceiling
```

重要分工：

- `PhyloWGS` 產生候選樹；
- `ASCAT`、`subHMM`、karyotype、CytoScan 與 single-cell CNV 提供不同層級的 genomic support；
- `support evaluator` 檢查相容性，不把所有資料自動當成同一個 likelihood input；
- 只有在有 branch-specific evidence 時，才可以把結論從「heterogeneity support」提升到「topology support」。

## 3. 先固定待檢查的 candidate topology

```text
Normal cells
    │
   S1 = MRCA
    ├── S2: 60% ── S4: 51% ──┬── S5: 14%
    │                         └── S7: 29%
    └── S8: 34% ── S9: 27% ── S10: 25%
```

`S3` 與 `S6` 因 CCF < 10% 未在圖中顯示。

檢查表中的每個 node 至少應有：

| 欄位 | 意義 |
|---|---|
| `node` | S1、S2、S4、S8 等 node 名稱 |
| `parent` | 候選祖先 node |
| `CCF` | 模型推導的 cancer cell fraction |
| `SNV/driver annotation` | 樹上標示的 mutation，不等於 branch truth |
| `expected CNA state` | 若有公開資料，記錄預期 CN/LOH pattern |
| `evidence_source` | PhyloWGS、SuperFreq、subHMM、single-cell 等 |
| `support_status` | supported / partial / not reported |

## 4. 每種證據實際測量什麼

| 證據 | 實際觀察 | 可以支持 | 不能單獨支持 |
|---|---|---|---|
| PhyloWGS | bulk SSM/CNV 與 clonal prevalence 下的模型輸出 | candidate topology、CCF、CNV-to-node assignment | single-cell lineage truth |
| SuperFreq | WES VAF、local CN、replicate uncertainty | 多個 bulk clone/subclone | 每個 SNV 的 cell-level assignment |
| ASCATNgs | purity、ploidy、allele-specific CN、LOH 背景 | copy-number-aware 解讀 | branch identity、事件時間順序 |
| subHMM | clonal/subclonal CNA genotype 與 proportion | CNA state compatibility | SNV-to-clone assignment |
| karyotype/CytoScan | 大尺度 chromosome state | genome complexity / aneuploidy | S2、S8 的 exact branch |
| 10x single-cell CNV | 每個 cell 的 integer-scaled CNV profile 與 clusters | cell-level CNV heterogeneity | S1–S10 的 SNV lineage |
| AmpliSeq/WES/PacBio | mutation call 是否存在、是否可重現 | mutation input quality | tree edge correctness |
| tumor-normal titration | VAF 對 nominal DNA mixture 的反應 | purity/VAF behavior | branching topology |

## 5. 分層檢查流程

### Level 1：確認 HCC1395 確實具有 genomic heterogeneity

要檢查：

```text
ploidy abnormality
+ chromosome gains/losses
+ LOH / NLOH
+ clonal CNA
+ subclonal CNA
+ non-identical single-cell CNV profiles
```

目前論文提供的證據：

- karyotype / cytogenetic analysis：大型 chromosome gains、losses 與 rearrangements；
- CytoScan：copy-number background；
- ASCATNgs：WGS 層級 CNA、LOH 與約 99% 的 CNA-based purity；
- subHMM：clonal/subclonal CNA genotype 與 proportion；
- 10x single-cell CNV：638 個 HCC1395BL cells 與 1,270 個 HCC1395 cells 的 CNV profiles。

這一層可以宣稱：

> HCC1395 是具有複雜 ploidy、LOH、clonal/subclonal CNA 與 cell-level CNV heterogeneity 的異質性細胞株。

這一層不能宣稱：

> S2 與 S8 已被 single-cell 資料證明是兩條 branch。

### Level 2：確認存在多個 clone/subclone prevalence

先把 bulk observation 做 copy-number-aware 解讀：

```text
bulk REF/ALT counts
    + purity
    + total/major/minor CN
    + multiplicity
    + measurement uncertainty
            ↓
copy-number-aware CCF / clonality
            ↓
multiple stable prevalence groups
```

檢查項目：

- 不同 SNV 是否形成穩定的 CCF groups？
- CCF groups 是否在 replicate 或不同 bulk assay 中重現？
- VAF peak 是否可能只是 CN 或 multiplicity 差異？
- purity/ploidy 誤差是否足以解釋該分群？
- SuperFreq 與 PhyloWGS 是否共享同一 bulk bias？

這一層可以支持：

> HCC1395 不是單一 homogeneous clone，而是存在多個 clonal/subclonal populations。

但多個 CCF peaks 本身還不能區分 linear、branching 或 polytomy。

### Level 3：檢查 CCF 與候選 parent-child 關係是否相容

若 `A` 是 `B` 的候選祖先，至少要檢查：

```text
CCF(A) ≥ CCF(B)
```

例如：

```text
S1 ≈ 100%
├── S2 ≈ 60%
└── S8 ≈ 34%
```

但這只是必要條件，不是充分條件。因為相同的 CCF 排序可能被多種 topology 解釋。

必須保存一張 event-level table：

| event | candidate node | CCF interval | CNA proportion | parent constraint | result |
|---|---|---:|---:|---|---|
| `event-A` | S1/S2? | published / inferred | published / absent | pass / fail | supported / unknown |

如果論文沒有公開 event-to-node mapping，就填 `not reported`，不能自行補成 `pass`。

### Level 4：PhyloWGS 方法層級的 CNV-to-node 與 branch-specific CNA pattern

這裡要先分開「PhyloWGS 方法能力」與「HCC1395 論文實際公開的結果」。PhyloWGS 本身確實可以把外部 CNV event 加入樹模型：CNV 先由外部工具估計，再轉成 CNV pseudo-SSM，與 somatic SSM 一起進入 TSSB tree。每個 CNV datum 可以被配置到某個 inferred clone / tree node；若 CNV 與 SSM 重疊，CNV 的 copy number、allele-specific state、事件順序與 node placement 會共同影響 SSM 的 expected VAF likelihood。

```text
外部 CNV preprocessing
    ↓
CNV segment + copy number + cellular prevalence
    ↓
CNV pseudo-SSM + bulk SSM
    ↓
PhyloWGS tree inference
    ↓
CNV event → inferred clone / tree node
```

因此，`branch-specific CNA pattern` 不是憑空假設，而是建立在 PhyloWGS 的事件配置語意上：若某個 CNA 被配置到 `S2`，它應該與 `S2` 及其 descendant populations 的 CCF、CNV prevalence 和相關 SNV group 相容；配置到 `S1` 的 CNA 則比較像 trunk/MRCA event。PhyloWGS 方法與輸入轉換的整理見 [`research/phylowgs_model_review.md`](../phylowgs_model_review.md)。

但這個方法層級事實不能反推 HCC1395 論文已公開完整的 CNA-to-node 結果。HCC1395 論文沒有提供本次 PhyloWGS 的完整 `cnv_data`、CNV event assignment、`CNA event → S1–S10 node` 表或 edge-level posterior；因此以下是「若取得 CNV-to-node output，應如何檢查」的 framework，不是已完成的 HCC1395 branch validation。

要支持 `S1 → S2` 與 `S1 → S8`，CNA 不能只是在全基因組「存在」，而應具有 branch-compatible pattern：

```text
MRCA / trunk CNA
       │
       ├── Branch-A CNA pattern + Branch-A SNV group
       │
       └── Branch-B CNA pattern + Branch-B SNV group
```

需要檢查：

- Branch-A CNA 是否只出現在 A-like population？
- Branch-B CNA 是否只出現在 B-like population？
- 兩種 CNA 是否互斥或呈 nested pattern？
- descendant 是否保留 ancestor CNA？
- CNA proportion 是否和 node CCF 大致相容？
- 是否有相反的 CNA pattern 可以同樣解釋資料？

如果某個 CNA 約 100% 存在，它比較像 trunk/MRCA candidate；它不能單獨區分 S2 與 S8。

目前論文沒有公開完整的 `CNA event → S node` 對應表，因此這一層只能標示為：

```text
biologically compatible / partially evaluated
```

而不能標示為：

```text
branch independently validated
```

### Level 5：檢查 single-cell CNV 是否真的連到候選 topology

論文目前能做的檢查是：

```text
single-cell DNA
    ↓
每個 cell 的 CNV profile
    ↓
CNV similarity clustering
    ↓
確認多個 cell-level genomic states
```

這可以支持 bulk 推導出的「多個 subclone 並存」具有細胞層級的生物學合理性。

但若要把 single-cell CNV 連到 S1–S10，最低需要：

```text
同一個 cell：SNV genotype + allele-specific CN
        ↓
cell cluster ↔ S node mapping
        ↓
cluster proportion ↔ CCF comparison
        ↓
branch-specific SNV/CNA co-occurrence
```

目前論文未提供：

- 每個 cell 的 SNV genotype；
- 每個 cell 的 S1–S10 label；
- S2/S8-defining SNV 出現在哪些 cells；
- single-cell SNV-CNV joint matrix；
- high-confidence candidate branching tree topology 的 branch 與 4b/4c CNV cluster 的正式 mapping。

所以目前 single-cell 結論只能是：

> single-cell CNV supports cell-level heterogeneity and CNA plausibility.

不是：

> single-cell data independently validated the S1–S10 SNV topology.

## 6. 需要同時檢查的替代解釋

| 觀察結果 | 可能的替代解釋 | 必須追加的檢查 |
|---|---|---|
| 多個 CCF peaks | multiplicity、CN、purity 或 mapping bias | posterior predictive check、CN/multiplicity sensitivity |
| subclonal CNA | 同一 clone 內不同 segment，不一定是不同 clone | segment co-occurrence、branch-specific mapping |
| LOH/NLOH | allele state，不代表事件先後 | allele-level phasing 或 joint event-order likelihood |
| CNV cell clusters | CNV-defined population，不一定是 SNV lineage | single-cell SNV+CN joint assay |
| branching tree | model prior 或 topology proposal 偏好 | linear/branching/polytomy model comparison |
| cell-line branching | culture evolution / genetic drift | 多時間點、獨立 culture、或 lineage assay |

## 7. Cross-validation 與穩定性，不等於 biological truth

即使要提高 topology reliability，也要把以下三種分數分開：

```text
Model fit
    候選樹能否解釋 bulk / CN / HP observations？

Inference reliability
    chains、ESS、K sensitivity、edge stability、holdout？

Biological support
    CNA/LOH、single-cell CNV、orthogonal assay 是否相容？
```

建議的 topology robustness checks：

1. 直接比較 `linear`、`branching`、`polytomy` 與 alternative branch order。
2. 對不同 topology 計算 posterior、marginal likelihood 或 held-out predictive likelihood。
3. 移除一組 replicate、某類 CNA、低 confidence sites 或某個 evidence source 後重新推理。
4. 檢查主要 branch 是否在不同 seed、chain、K 與 held-out data 中保留。
5. 對候選樹做 posterior predictive check，確認 observed CCF/VAF/CN pattern 可被重現。

這些結果能提高「計算穩定性」或「資料相容性」，仍不會自動變成 single-cell lineage truth。

## 8. Evidence matrix：最後要交付的檢查表

| Claim | Evidence | Direct / indirect | Published result | Missing artifact | Claim ceiling |
|---|---|---|---|---|---|
| HCC1395 非簡單 diploid | karyotype、CytoScan、ASCATNgs | direct background | supported | exact event harmonization | genome complexity |
| 存在 clonal/subclonal CNA | subHMM、ASCATNgs、single-cell CNV | direct/orthogonal | supported | full cell-to-CNA mapping | heterogeneity |
| 存在多個 clone prevalence | SuperFreq、bulk VAF/local CN | model-based | supported | raw full clonality table | multiple populations |
| high-confidence candidate branching tree topology | PhyloWGS | direct model output | reported | full input/parameters/posterior | candidate topology |
| CNA 與 branch CCF 相容 | event-to-node comparison | compatibility | not fully reported | CNA→S-node table | partial support |
| single-cell 支持 S1–S10 | single-cell SNV+CN joint data | absent | not demonstrated | cell SNV genotype/mapping | no edge claim |
| 每條 edge 真實存在 | independent lineage truth | absent | not demonstrated | edge-level truth set | no validated lineage claim |

## 9. HCC1395 論文的目前 evidence grade

```text
Level 0  mutation call-set quality             strong
Level 1  genomic / cell-level heterogeneity    strong
Level 2  multiple clone prevalence             moderate–strong
Level 3  candidate branching compatibility     moderate / incomplete
Level 4  held-out topology robustness          limited in published artifact
Level 5  single-cell SNV lineage truth          not available
```

最安全的總結：

> HCC1395 的 ploidy、allele-specific CN、LOH、clonal/subclonal CNA 與 10x single-cell CNV 結果，支持其具有複雜且異質的細胞族群，因此 branching evolution 是合理且比單一路徑模型更符合整體證據的候選模型。這個結果命名為 **high-confidence candidate branching tree topology**；目前沒有 single-cell SNV lineage 或逐 edge validation，因此不能宣稱 S1–S10 是唯一真實演化樹。

## 10. 對目前 repo 的模塊邊界

目前 repo 應維持：

```text
data input → model → inference_algo → output
                                      │
                                      ▼
                              support evaluator
```

`support evaluator` 可以讀取：

- candidate topology、CCF、SNV assignment；
- ASCAT site/segment table 與 LOH/QC；
- inference diagnostics、holdout 與 topology stability；
- optional single-cell CNV clusters；
- optional multi-SNV long-read linkage。

但 single-cell CNV 不應被假定為目前 model likelihood 的輸入；目前 repo 的 `Hᵢ` long-read HP counts 也只是 site-level allocation evidence，不能等同於 single-cell lineage evidence。

建議 output 分開保存：

```text
model_fit
inference_reliability
biological_support
claim_grade
```

## 11. 請檢查的問題

1. 是否同意把本章的主要動詞從「證明」改為「檢查相容性」？ **Yes。**
2. 是否同意把 `support evaluator` 視為 output 後的獨立評估層，而不是塞入現有 likelihood？ **Yes。**
3. 是否需要未來建立 `CNA event → candidate node → CCF interval` 的實際 evidence table？ **No，暫不建立。**
4. 是否要把 single-cell SNV+CN joint assay 列為 topology validation 的必要升級條件？ **No，不列為必要條件。**
5. 是否接受 HCC1395 候選樹的最終命名為 `high-confidence candidate branching tree topology`？ **Yes。**

### Decision record

使用者已確認接受 HCC1395 候選樹的正式命名：

```text
high-confidence candidate branching tree topology
```

使用者也已確認本章的主要動詞改為：

```text
檢查相容性
```

這表示本章評估候選 topology 是否與 CNA、ploidy、LOH、CCF 與 single-cell CNV evidence 相容，不把目前資料誇大成逐條 branch 的直接證明。

使用者也已確認 `support evaluator` 的定位：

```text
candidate topology / CCF / SNV assignment
        ↓
support evaluator
        ↓
evidence grade / claim grade
```

它是 output 後的獨立評估層，不直接修改目前 likelihood。其目的，是讓「高信心度」建立在可列出的 model fit、topology stability、CN/LOH compatibility 與外部 biological support 上，最後命名為：

```text
high-confidence candidate branching tree topology
```

目前不建立 `CNA event → candidate node → CCF interval` 的實際 evidence table。現階段只有 bulk sequencing，沒有 single-cell SNV+CN 或其他能直接把 CNA event 對應到 candidate node 的 joint evidence；因此先保留此表格為未來可選項，不把 bulk-level prevalence mapping 誤當成 clone-level proof。

目前也不把 `single-cell SNV+CN joint assay` 列為 topology validation 的必要升級條件。現階段研究範圍以 bulk sequencing、ASCAT/CN、long-read observations 與 inference stability 評估 candidate topology；single-cell joint assay 不是目前模型或驗證流程的必備輸入。

此命名表示：

- branching model 比單一路徑模型更符合目前公開的 bulk clonality、CNA、LOH、ploidy 與 single-cell CNV 證據；
- `high-confidence` 描述整合後的候選模型可信度，不代表每一條 edge 都有獨立 lineage truth；
- `candidate` 保留 PhyloWGS 輸入、posterior topology support 與 single-cell SNV validation 未完整公開的限制。

## 12. 來源

- [HCC1395 原始 PDF](../../hcc1395_golden_tree.pdf)：Fig. 4、Methods 的 CNA、clonality 與 single-cell CNV。
- [01_data_and_callset.md](01_data_and_callset.md)
- [02_tree_reconstruction.md](02_tree_reconstruction.md)
- [03_validation_evidence.md](03_validation_evidence.md)
- [04_confidence_and_limits.md](04_confidence_and_limits.md)
- [05_lessons_for_current_repo.md](05_lessons_for_current_repo.md)
