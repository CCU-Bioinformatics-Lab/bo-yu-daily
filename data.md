# HCC1395 腫瘤演化樹資料輸入契約

更新日期：2026-08-22

本文件只描述目前 repo 的 active data boundary：

1. 上游資料如何轉成 canonical SNV-level table。
2. 哪些欄位會被 model／C++ inference 讀取。
3. 哪些資料只作 provenance、QC 或 holdout。
4. 哪些舊介面目前禁止使用。

相關文件：

- [model.md](model.md)：模型、likelihood、prior 與 latent quantity。
- [inference_algo.md](inference_algo.md)：推理演算法與 posterior artifact。
- [experiment_workflow.md](experiment_workflow.md)：正式 workflow、holdout 與可追溯 run records。
- [tumor_tree_pipeline/README.md](tumor_tree_pipeline/README.md)：資料建表與 workflow module。
- [inference/README.md](inference/README.md)：目前 C++ inference backend。
- [legacy_data.md](legacy_data.md)：可能含舊資料或錯誤資料的低權重歷史邊界。

---

## 1. 一頁版 active data contract

目前資料流：

~~~text
upstream biological sources
        ↓
derived builder artifacts
        ↓
canonical likelihood_input.tsv.gz
        ↓
eligible SNV rows
        ↓
C++ Site
        ↓
model likelihood
~~~

C++ sampler 不直接讀取 raw BAM、raw VCF 或 ASCAT 原始 segment 檔；這些來源先經過資料整理流程，產生 derived artifacts，再由 tumor_tree_pipeline 建立 canonical table。

目前 canonical schema version（由 manifest／validation manifest 宣告，並非 TSV 內的欄位）：

~~~text
hcc1395_tumor_tree_input/v2
~~~

基本規則：

- 每一列代表一個 SNV。
- chrom、pos、ref、alt 定義 site identity。
- table 同時保留 eligible 與 excluded rows，方便 QA。
- 只有 model_include=yes 且 model_status=eligible 的 rows 可以進入 sampler。
- chain-specific holdout 會再從 eligible rows 排除指定 mutation_id。
- excluded rows 不會進入 sampler，但保留排除原因。
- mutation_id 必須唯一。
- canonical table 不得包含已禁止的 legacy columns。

正式 primary purity：

~~~text
rho_ASCAT = 0.99
~~~

---

## 2. 目前資料分層

### 2.1 Upstream biological sources

這些來源提供建立 derived artifacts 所需的原始證據：

| 來源 | 提供內容 | 是否直接進 C++ sampler |
|---|---|---|
| Reference FASTA | reference build、contig、座標基準 | 否 |
| Tumor BAM | tumor reads、REF/ALT 與 depth 原始證據 | 否 |
| Normal BAM | matched-normal、germline 與 CN 分析原始證據 | 否 |
| Somatic SNV VCF | SNV site universe 與 allele identity | 否 |
| Phased germline VCF | germline phase backbone | 否 |
| Phase-tagged tumor BAM | HP／PS read-level evidence | 否 |
| ASCAT segment output | segment-level major/minor/total CN、LOH context | 否 |
| ASCAT purity output | rho_ASCAT 的數值與 provenance | 否，builder 會讀取 |

目前指定的 phase-tagged tumor BAM：

~~~text
/bip8_disk/boyu114/longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam
/bip8_disk/boyu114/longphase-s-origin/output/hcc1395_old_tagging_rerun/hcc1395_old_tagging.bam.bai
~~~

這是未啟用 two-site split 的 LongPhase-S old-tagging 產物；不使用
`hcc1395_new_split_tagging.bam`。它的 read-level HP 來源以 `1`、`2`、
`1-1`、`2-1` 為主，舊版流程也可能保留 `HP3`；`1-2`／`2-2` 不屬於本次
tagged tumor BAM 的選擇目標。

注意：既有 `canonical_counts_20260814/site_counts_manifest.json` 仍記錄先前
new-split BAM 的來源，因此切換來源後，既有 counts bundle 必須重新建立並重新
驗證，不能只修改 manifest 的路徑或直接把舊 counts 當成新來源結果。

上游 raw source 只作 provenance；目前 builder manifest 主要記錄 derived counts、HP、site-CNV、purity 檔案及其 hash。若上游 manifest 另外提供 sample 或 reference build，才由上游 provenance 保存；這些 raw source 不會直接變成 sampler input。

### 2.2 Derived builder artifacts(上游資料整理後的中間輸入檔)

目前建表介面需要：

~~~text
snv_bulk_counts.tsv.gz
snv_hp_counts.tsv.gz
snv_hp_qc.tsv.gz
site_cnv_qc.tsv.gz
site_counts_manifest.json
ASCAT purity file
~~~

這些檔案是已整理成 single-site 或 site-CNV 格式的中間資料。

### 2.3 Canonical input bundle(模型輸入資料包)

builder 產生：

~~~text
likelihood_input.tsv.gz
input_qa.json
manifest.json
~~~

likelihood_input.tsv.gz 是 model 與 inference backend 之間的資料介面；input_qa.json 和 manifest.json 是驗證與 provenance artifacts，不是 likelihood observation。

---

## 3. Canonical required columns

目前 required columns 共 20 個：

~~~text
mutation_id
chrom
pos
ref
alt
bulk_ref
bulk_alt
bulk_depth
hp1_1_ref
hp1_1_alt
hp2_1_ref
hp2_1_alt
major_cn
minor_cn
total_cn
rho_ASCAT
multiplicity_candidates
multiplicity_prior
model_include
model_status
~~~

欄位意義：

| 欄位 | 來源／產生方式 | 目前作用 |
|---|---|---|
| mutation_id | chrom:pos:ref>alt | SNV 唯一識別與 output 對應 |
| chrom | SNV key | genomic identity |
| pos | SNV key | genomic identity |
| ref | SNV key | reference allele identity |
| alt | SNV key | alternate allele identity |
| bulk_ref | bulk count artifact | bulk REF observation |
| bulk_alt | bulk count artifact | bulk ALT observation |
| bulk_depth | bulk_ref + bulk_alt | bulk depth observation |
| hp1_1_ref | HP count artifact 的 1-1 類別 | HP1-1 REF observation |
| hp1_1_alt | HP count artifact 的 1-1 類別 | HP1-1 ALT observation |
| hp2_1_ref | HP count artifact 的 2-1 類別 | HP2-1 REF observation |
| hp2_1_alt | HP count artifact 的 2-1 類別 | HP2-1 ALT observation |
| major_cn | ASCAT site-CNV projection | allele-specific CN |
| minor_cn | ASCAT site-CNV projection | allele-specific CN |
| total_cn | major_cn + minor_cn | total CN |
| rho_ASCAT | ASCAT purity output | fixed global purity |
| multiplicity_candidates | major/minor CN deterministic derivation | 可行 mutated-copy 數 |
| multiplicity_prior | major/minor CN deterministic derivation | multiplicity marginalization prior |
| model_include | builder eligibility gate | 是否允許進 sampler |
| model_status | builder eligibility gate | eligible 或 exclusion reason |

對 C++ Site 而言，identity 欄位會保留用於追蹤；真正的 observation 主要是 bulk counts、HP counts、ASCAT CN、purity 與 multiplicity support/prior。

---

## 4. Optional audit columns

builder output 會固定保留下列欄位；它們對 model 是 optional audit columns：

| 欄位 | 用途 | 是否進 C++ likelihood state |
|---|---|---|
| phased_gt | genotype／phase provenance | 否 |
| cnv_status | CN mapping、CN zero、unmapped、overlap 狀態 | 否 |
| segment_id | ASCAT segment identity 與 holdout grouping | 否 |
| loh_state | LOH compatibility context | 否 |
| cnv_confidence | site-CNV projection confidence | 否 |
| somatic_hp_evidence_status | HP read evidence QC 摘要 | 否 |

這些欄位可以存在於 builder output，但不代表它們是 sampled state、clone prior 或 likelihood parameter。

PS 不應作為 canonical likelihood column；PS audit、read-level evidence 與 holdout grouping 應保存在獨立的 workflow metadata／audit artifacts。

---

## 5. Derived artifact 的格式

### 5.1 Bulk counts

檔案：

~~~text
snv_bulk_counts.tsv.gz
~~~

每個 SNV 至少提供：

~~~text
chrom
pos
ref
alt
bulk_ref
bulk_alt
bulk_usable_depth
~~~

builder 會將 bulk_usable_depth 寫成 canonical table 的 bulk_depth，並檢查：

~~~text
bulk_depth = bulk_ref + bulk_alt
~~~

上游可能另有 bulk_vaf、vcf_af、vcf_dp、vcf_ad_ref、vcf_ad_alt 等摘要欄位，但它們不是 canonical active columns。

目前不是先計算一個獨立 VAF parameter 再交給模型；model likelihood 直接使用 REF/ALT counts，並在 purity、CN、multiplicity 與 latent clone fraction 的共同條件下計算 observation probability。bulk_alt/bulk_depth 只在 holdout predictive coverage 中作為觀察摘要，不是 canonical 欄位，也不是 likelihood 的獨立輸入。模型公式請見 model.md。

### 5.2 HP counts

檔案：

~~~text
snv_hp_counts.tsv.gz
~~~

每個 SNV 依照完整 HP tag domain 保存 REF/ALT counts：

~~~text
.
1
2
3
4
1-1
2-1
1-2
2-2
other
~~~

對任一 HP tag 類別：

- *_ref 是該類別 reads 中觀察到 reference allele 的數量。
- *_alt 是該類別 reads 中觀察到 alternate allele 的數量。

因此 hp1_1_ref 不是「HP1 本身是 reference」，而是「被標記為 1-1 的 reads 中，支持 reference allele 的數量」。

canonical table 只保留 downstream model 使用的兩組：

~~~text
hp1_1_ref
hp1_1_alt
hp2_1_ref
hp2_1_alt
~~~

其他 HP 類別仍用於完整 count conservation 和 QC。C++ likelihood 不另存 untagged 欄位；untagged REF/ALT counts 由 bulk counts 減去四個 active HP counts 推導，再和 HP-tagged counts 一起形成 emission。

### 5.3 HP QC

檔案：

~~~text
snv_hp_qc.tsv.gz
~~~

用途：

- 確認 site key 與 bulk table 完全一致。
- 檢查 upstream HP-QC delta 是否為零。
- 保存 HP read evidence 的品質狀態。

完整 HP domain 是由 snv_hp_counts.tsv.gz 的 loader 驗證；所有 HP categories 的 REF/ALT conservation 則由 builder 在產生 QA 前檢查，失敗時直接停止。active table 的四個 HP 欄位只是 model 使用的 primary HP evidence。

### 5.4 Site-CNV QC

檔案：

~~~text
site_cnv_qc.tsv.gz
~~~

必要欄位：

~~~text
chrom
pos
ref
alt
cnv_status
~~~

cnv_status 為 mapped_nonzero_cn 或 cn_zero 時，還必須提供：

~~~text
major_cn
minor_cn
total_cn
~~~

可選的 audit 欄位：

~~~text
segment_id
loh_state
cnv_confidence
~~~

用途：

- ASCAT segment → site-CNV projection 必須在 canonical builder 之前完成；build_model_table() 讀取並驗證已投影的 site_cnv_qc.tsv.gz。
- 提供 major、minor、total CN。
- 判定 site 是否有可用 CN。
- 排除 CN zero、unmapped segment 或 segment overlap。
- 保存 CNV／LOH 的 provenance 與 audit context。

其中只有 major_cn、minor_cn、total_cn 是 active likelihood input；segment_id、loh_state 和 confidence 欄位目前只作 audit／holdout context。

### 5.5 ASCAT purity

builder 從 ASCAT purity output 讀取：

~~~text
sample
purity
~~~

並寫入 canonical field：

~~~text
rho_ASCAT
~~~

primary value 是 0.99。ASCAT output 中可能還有 ploidy 或 goodness-of-fit，但目前不會作為 sampler 的 active input。

---

## 6. Source 到 canonical table

完整轉換流程：

~~~text
SNV site universe
        │
        ├── bulk counts
        │       └── bulk_ref / bulk_alt / bulk_depth
        │
        ├── HP counts
        │       └── hp1_1_* / hp2_1_*
        │
        ├── HP QC
        │       └── complete-domain count conservation
        │
        ├── ASCAT site-CNV projection
        │       └── major_cn / minor_cn / total_cn
        │
        └── ASCAT purity output
                └── rho_ASCAT
                        │
                        ▼
              multiplicity_candidates
              multiplicity_prior
                        │
                        ▼
             likelihood_input.tsv.gz
                        │
                ┌───────┴───────┐
                ▼               ▼
           input_qa.json    manifest.json
~~~

### 6.1 Canonical CSV-like example

canonical table 是 TSV；下面用 CSV-like 格式展示一列：

~~~csv
mutation_id,chrom,pos,ref,alt,bulk_ref,bulk_alt,bulk_depth,hp1_1_ref,hp1_1_alt,hp2_1_ref,hp2_1_alt,major_cn,minor_cn,total_cn,rho_ASCAT,multiplicity_candidates,multiplicity_prior,model_include,model_status
chr1:100:A>G,chr1,100,A,G,34,11,45,8,6,10,2,3,1,4,0.99,"1;2;3","1=0.666667;2=0.166667;3=0.166667",yes,eligible
~~~

這列表示：

~~~text
bulk counts:
  REF=34, ALT=11, depth=45

HP 1-1:
  REF=8, ALT=6

HP 2-1:
  REF=10, ALT=2

ASCAT:
  major=3, minor=1, total=4

purity:
  rho_ASCAT=0.99

multiplicity:
  candidates=1,2,3
  prior=1=0.666667, 2=0.166667, 3=0.166667

eligibility:
  model_include=yes
  model_status=eligible
~~~

excluded row 也保留在 table，例如：

~~~csv
chr2:200:C>T,chr2,200,C,T,0,0,0,0,0,0,0,2,1,3,0.99,,,no,excluded_zero_depth
~~~

excluded row 的用途是保留完整 site universe 和排除原因；它不會進入 sampler。

---

## 7. PS 與 HP 的資料邊界

### 7.1 PS 的正確角色

PS 是上游 phase provenance。它可以協助：

- 在同一 PS block 內維持 HP label 的局部一致性。
- 產生 HP1-1／HP2-1 read counts。
- 進行 read-level phase audit。
- 建立 PS-grouped holdout，避免同一 block 被拆到不同 partition。

不同 PS block 之間，不假設 HP1／HP2 方向具有全球一致性。

### 7.2 PS 不直接進 model likelihood

PS block 本身不是：

- C++ Site field。
- downstream likelihood column。
- clone-assignment prior。
- eta 或 phi parameter。
- topology edge constraint。
- clone label。

資料關係是：

~~~text
phase-tagged reads
        ↓
PS block / HP label consistency
        ↓
HP read counts + read-level QC
        ↓
hp1_1_* / hp2_1_* in canonical table
~~~

所以 PS 可能透過產生 HP counts 間接影響 observation，但 PS label 本身不作為模型參數。

### 7.3 Holdout 的位置

PS grouped holdout 是 workflow evaluation design，不是 biological likelihood constraint。它用來評估模型對整個 phase block 的預測，不能解讀成模型把 PS block 當成 clone 或 topology。

---

## 8. ASCAT CN、LOH 與 purity

### 8.1 Active CN fields

active CN 欄位：

~~~text
major_cn
minor_cn
total_cn
~~~

必要條件：

~~~text
major_cn >= minor_cn >= 0
total_cn = major_cn + minor_cn
~~~

要進入 sampler 的 eligible row 還必須滿足：

~~~text
total_cn > 0
~~~

這些欄位支援：

- allele-specific copy-number context。
- purity-aware alternate fraction emission。
- multiplicity candidate construction。
- multiplicity prior marginalization。

### 8.2 LOH 的定位

loh_state 是 optional audit／provenance annotation，不是目前 C++ Site 的 active likelihood field；目前也沒有使用它計算 likelihood 或已實作的 compatibility score。

LOH 的判讀要結合：

~~~text
major_cn
minor_cn
total_cn
BAF / allele-specific evidence
segment boundary
normal heterozygous context
caller provenance
~~~

目前不能只用高 VAF、ALT count 或 HP label 宣稱某個 SNV 發生 LOH，也不能僅由 loh_state 自動產生：

~~~text
CNA event → clone node
LOH event → evolutionary branch
~~~

### 8.3 Purity 的定位

rho_ASCAT 是固定的 global purity input：

- 參與 purity-aware observation emission。
- 寫入 table、manifest 和 validation result。
- 目前分析固定使用 0.99。

rho_ASCAT 不等於：

~~~text
eta
phi
某一個 clone 的 CCF
某一條 topology edge 的 support
~~~

目前沒有舊 purity interface；canonical table 只接受 rho_ASCAT。

---

## 9. CN-only multiplicity

### 9.1 產生方式

資料流：

~~~text
major_cn + minor_cn
        ↓
multiplicity_candidates
        ↓
multiplicity_prior
        ↓
likelihood 對 multiplicity 做 marginalization
~~~

目前規則：

1. major/minor homolog side 各分配相等總權重。
2. CN=0 的 side 不分配權重。
3. 每一側在 m=1..side_CN 間均分。
4. 兩側相同的 multiplicity 合併其機率。
5. 最終 prior 必須正規化為 1。

例如：

~~~text
major_cn=3, minor_cn=1

major side:
  m=1,2,3 各 1/6

minor side:
  m=1 為 1/2

combined:
  m=1: 2/3
  m=2: 1/6
  m=3: 1/6
~~~

### 9.2 不使用的資料

multiplicity_prior 不使用：

~~~text
bulk_ref
bulk_alt
bulk_depth
bulk_vaf
vcf_af
rho_ASCAT
HP counts
PS block
~~~

因此 bulk counts 不會先被拿來建立 multiplicity prior，再在 likelihood 中重複使用。

multiplicity_prior 是固定的 CN-only prior，不是獨立的 MCMC latent state；模型在 observation likelihood 中對候選 multiplicity 做 marginalization。exact construction 由 Python builder 負責，C++ loader 不重新推導 prior，只驗證 candidates、prior keys、正規化與 CN 邊界。詳細定義見 model.md。

---

## 10. Eligibility 與 holdout

### 10.1 Site eligibility

builder 為每個 site 產生：

~~~text
model_include
model_status
~~~

常見結果：

~~~text
model_include=yes
model_status=eligible
~~~

或：

~~~text
model_include=no
model_status=excluded_zero_depth
~~~

可能的 exclusion reason 還包括：

~~~text
excluded_unmapped_segment
excluded_segment_overlap
excluded_cn_zero
~~~

eligible row 必須通過：

- site key 一致。
- bulk counts 存在且 depth 守恆。
- 完整 HP domain 與 count conservation 通過。
- site-CNV projection 可用。
- CN arithmetic 正確。
- purity 一致。
- multiplicity candidates 非空、排序且唯一。
- multiplicity_prior keys 與 candidates 完全一致，所有 probability 大於零且總和為 1。
- 最大 multiplicity 不超過可用 CN，且 eligible row 的 total_cn 大於零。

### 10.2 Chain-specific holdout

即使 row 是 eligible，只要 mutation_id 在某條 chain 的 holdout list 中，就不會被 C++ loader 放入該 chain 的 Site collection。

因此：

~~~text
fitted sites
=
eligible sites
-
該 chain 的 holdout sites
~~~

holdout site 用於 predictive evaluation，不要求該 chain 為它產生 clone assignment。

目前 workflow 的 grouped holdout 類型：

~~~text
PS grouped
chromosome grouped
ASCAT-segment grouped
~~~

holdout metadata 至少需要：

~~~text
mutation_id
chrom
ps
ascat_segment_id
~~~

若沒有 ascat_segment_id，則必須有 segment_start 與 segment_end。metadata 的 mutation_id 必須與 canonical eligible mutation IDs 完全一致。有有效 PS 的 SNV 以 chromosome + PS 分組；缺少 PS 的 SNV 目前退回該 SNV 自己的 singleton block。這些 grouped holdout 都是 workflow control，不是新的 biological model parameter。

---

## 11. Manifest 與 QA

### 11.1 manifest.json

目前 manifest 會記錄：

- schema version。
- build time、builder command、software version。
- derived source file path 和 hash。
- ASCAT purity value、source 和 hash。
- multiplicity construction rule。
- PS 的 upstream／QC／holdout role。
- canonical output hash。
- expected、observed、eligible site count。
- model status counts。
- active、optional、forbidden columns。

schema version 存在 manifest／validation manifest，不是 TSV 的欄位。raw source 的 sample、reference build 等資訊若要保存，須由上游 provenance manifest 提供；目前 builder 不會自行補造這些欄位。manifest 是 provenance artifact，不是 likelihood input。

### 11.2 input_qa.json

builder 在產生 QA 前會檢查：

- total、eligible、excluded rows。
- model_status counts。
- bulk depth conservation。
- complete HP count conservation。
- active HP subset 不超過 bulk counts。
- CN arithmetic。
- purity consistency。
- multiplicity candidates/prior consistency。
- forbidden columns。
input_qa.json 保存上述檢查的 summary、status、counts、issues preview，以及 active／optional／forbidden columns；部分 conservation、CN arithmetic 與 purity check 若失敗會在 QA 寫出前直接停止。

input QA 沒有通過時，不應把 bundle 交給正式 workflow。

### 11.3 Workflow validation

正式 workflow 進一步確認：

- schema version。
- canonical table hash。
- validation manifest hash。
- table 內 rho_ASCAT 是否符合本次 run。
- required columns 與 forbidden columns。
- table 的 input QA status。
- holdout metadata 與 input bundle 對應。

---

## 12. 目前執行邊界

目前 Python 入口：

~~~text
python3 -m tumor_tree_pipeline
~~~

主要操作：

~~~text
python3 -m tumor_tree_pipeline plan --config <experiment-config>
python3 -m tumor_tree_pipeline run --config <experiment-config>
~~~

責任分工：

- input_table.build_model_table(...)：建立 canonical input bundle。
- workflow：執行 input validation、holdout、chain orchestration 與 diagnostics。
- inference/：提供目前 C++17 inference backend。
- C++ loader：只讀 canonical table、chain config 和 holdout exclusion control。
- raw BAM、VCF、ASCAT segment output：不直接傳給 C++ sampler。

workflow run 會在 experiment output 下保存 input bundle、validation、holdout metadata、chain output、logs 和 status markers；實際 artifact 位置以 run 的 manifest 為準。

推理演算法不在本文件重複描述，請見 inference_algo.md。

---

## 13. 明確不屬於 active data input 的項目

| 項目 | 目前定位 |
|---|---|
| tumor_dna_fraction | 已停用的 purity interface，不可出現在 canonical table |
| multiplicity_posteriors | 已停用的 multiplicity interface，不可出現在 canonical table |
| bulk_vaf | 上游摘要，不是獨立 model parameter |
| vcf_af、vcf_dp、VCF AD | caller/provenance 欄位，不是 active model columns |
| PS block | phase provenance、HP 建立、read audit、grouped holdout |
| ploidy | purity output 的額外資訊，目前不是 sampler input |
| goodness-of-fit | ASCAT provenance，目前不是 sampler input |
| segment_id、loh_state | optional audit／compatibility context |
| driver annotation | 目前不是 model input |
| CNA/LOH event-to-node mapping | 目前不是既有 canonical input |
| HP1/HP2 label | read-level evidence，不是 clone label |
| normal cells | tree presentation 的 root concept，不是 canonical table row |
| output 後 external validation | support evaluation，不是 active likelihood input |

歷史資料和舊結果不在 active data contract 中；統一參照 [legacy_data.md](legacy_data.md)，但該文件內容只具低參考權重。

---

## 14. Active data flow

~~~text
reference / tumor / normal / SNV / phase / ASCAT sources
                         │
                         ▼
          bulk / HP / HP-QC / site-CNV artifacts
                         │
                         ▼
          hcc1395_tumor_tree_input/v2
             likelihood_input.tsv.gz
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
      input_qa.json                 manifest.json
          │
          ▼
 eligible rows:
 model_include=yes
 model_status=eligible
          │
          ├── remove chain-specific holdout IDs
          ▼
      C++ Site collection
          │
          ▼
      model likelihood
~~~

PS 的位置：

~~~text
phase provenance
        ↓
HP label / count construction
        ↓
HP counts in canonical table
~~~

PS 不直接進 C++ Site、clone prior、eta、phi 或 topology edge。

---

## 15. 交付前檢查清單

### Schema

- [ ] schema version 為 hcc1395_tumor_tree_input/v2。
- [ ] 每列是一個 SNV。
- [ ] mutation_id 唯一。
- [ ] 20 個 required columns 全部存在。
- [ ] forbidden columns 不存在。
- [ ] optional audit columns 已清楚標示。

### Counts 與 CN

- [ ] bulk_depth = bulk_ref + bulk_alt。
- [ ] HP domain 完整。
- [ ] 完整 HP REF/ALT 總和等於 bulk counts。
- [ ] active HP subset 不超過 bulk counts。
- [ ] major_cn >= minor_cn >= 0。
- [ ] total_cn = major_cn + minor_cn。
- [ ] CN zero、unmapped、overlap sites 有明確 exclusion status。

### Purity 與 multiplicity

- [ ] primary table 使用 rho_ASCAT=0.99。
- [ ] purity source 可追溯，table 與 source 一致。
- [ ] multiplicity_candidates 只由 major/minor CN 推導。
- [ ] multiplicity_candidates 非空、排序且唯一。
- [ ] multiplicity_prior keys 與 candidates 完全一致，且每個 probability 大於零。
- [ ] multiplicity_prior 機率總和為 1。
- [ ] 最大 multiplicity 不超過可用 CN；eligible row 的 total_cn 大於零。
- [ ] 沒有停用的 purity／multiplicity columns。

### Eligibility 與 holdout

- [ ] eligible row 是 model_include=yes、model_status=eligible。
- [ ] excluded row 保留排除原因。
- [ ] chain-specific holdout IDs 有 metadata。
- [ ] PS、chromosome、ASCAT-segment grouped holdout 的定義沒有混淆。
- [ ] holdout site 不要求該 chain 產生 clone assignment。

### Provenance

- [ ] source path、hash 已記錄。
- [ ] 若 sample 或 reference build 不在目前 builder manifest，已由上游 provenance manifest 保存。
- [ ] canonical table hash 已記錄。
- [ ] input QA status 為 pass。
- [ ] build command 與 software version 可追溯。

---

## 16. Repo source map

### Active contracts

- [model.md](model.md)
- [inference_algo.md](inference_algo.md)
- [experiment_workflow.md](experiment_workflow.md)

### Data builder

- [tumor_tree_pipeline/README.md](tumor_tree_pipeline/README.md)
- [tumor_tree_pipeline/contracts.py](tumor_tree_pipeline/contracts.py)
- [tumor_tree_pipeline/input_table.py](tumor_tree_pipeline/input_table.py)
- [tumor_tree_pipeline/provenance.py](tumor_tree_pipeline/provenance.py)
- [tumor_tree_pipeline/workflow.py](tumor_tree_pipeline/workflow.py)

### C++ model input

- [inference/include/tumor_tree_inference/model.hpp](inference/include/tumor_tree_inference/model.hpp)
- [inference/src/model.cpp](inference/src/model.cpp)

### Historical boundary

- [legacy_data.md](legacy_data.md)

---

## 17. 最終定義

目前 repo 的 active data input 可以濃縮成：

~~~text
bulk REF/ALT counts
+ HP1-1 / HP2-1 counts
+ ASCAT major/minor/total CN
+ ASCAT purity rho_ASCAT
+ CN-only multiplicity candidates/prior
+ site eligibility metadata
~~~

實際 downstream flow：

~~~text
derived artifacts
        ↓
likelihood_input.tsv.gz
        ↓
eligible, non-holdout SNV rows
        ↓
C++ Site
        ↓
tumor-tree model and inference backend
~~~

data layer 的責任是提供可追溯、可驗證的 canonical SNV-level observation table。模型公式由 model.md 定義，推理演算法由 inference_algo.md 定義，正式執行、holdout 與錯誤追蹤由 experiment_workflow.md 定義。
