# HCC1395 LongPhase-Clone 模型設計

> [!WARNING]
> **文件依賴警告：請勿單獨刪除或改名本文件、[`data.md`](data.md) 或 [`longphase-clone.md`](longphase-clone.md)。**
> 三者分別記錄模型定義、資料來源與研究／實作進度；缺少任何一份都會使結果失去可追溯性。若必須改名或搬移，請同步更新三份文件的連結。

## 0. 文件節點與關係

```yaml
document_id: model
document_type: model_specification
model_name: LongPhase-Clone
sample: HCC1395
updated: 2026-08-19
links:
  - relation: uses_data_from
    target: data.md
  - relation: implemented_and_tracked_by
    target: longphase-clone.md
  - relation: output_retention_policy
    target: convergence_cleanup_20260816.md
```

這三份 Markdown 共同構成一個輕量的文件關係圖：

```text
data.md ──provides_inputs_to──> model.md
   ^                                  |
   |                                  | specified_by
   |                                  v
   └──records_artifacts_from── longphase-clone.md
                   implements ────────^
```

- [`data.md`](data.md)：輸入檔案、路徑、資料狀態與 provenance。
- [`longphase-clone.md`](longphase-clone.md)：完整研究計畫、數學擴充、實作階段與結果。
- 本文件：收斂目前實際模型的公式、輸入、推導參數與限制。

## 1. 一頁結論

本文件記錄有限節點 **haplotype-aware clone-tree posterior** 的模型設計。先前 M3 sampler 的舊中間表已於 2026-08-13 移除；2026-08-15 以普通 Binomial bulk-count likelihood 重建新版 Stage 6 table，並保留 `multiplicity_posteriors` 作為輸入摘要。Beta-Binomial concentration 不再是輸入欄位，也不在目前模型中估計。

目前正式 purity input 已改為 ASCAT 的 HCC1395 5-kHz 輸出：`rho = rho_ASCAT = 0.99`，來源為 `output/cnv_callers/ascat_hcc1395_5khz_t4/purity_ploidy.txt`。LongPhase-S 報告的 tumor DNA fraction `0.958936` 僅保留作 reference/provenance，不再進入目前 M3 likelihood。

必須區分兩個層次：

1. **歷史 M3 實作**：有限節點、Binomial/Multinomial observation、CN/LOH moment summary；相關直接輸入已移除，只保留方法與歷史結果供稽核。
2. **目前 M3**：讀取新版 Stage 6 table，以普通 Binomial bulk counts、HP1-1/HP2-1 conditional allocation、CN 與固定的 `multiplicity_posteriors` 計算 candidate posterior。
3. **未來擴充**：正式 allele-specific CNV/LOH、haplotype-specific copy genotype 與 joint multiplicity；不預設加入 Beta-Binomial concentration。

因此現存 M3 圖與 posterior 輸出只能視為舊資料的歷史結果，不能代表新版 `data.md` 的 candidate posterior tree，更不是已完全校正並收斂的 lineage truth。

> [!CAUTION]
> 2026-08-13 以前產生的 M3 trees 與中間表來自舊資料流程，部分輸出另使用舊的 PS-wide `o_PS` 與包含 `1-2/2-2` 的 collapsed tag likelihood。這些輸出只保留作歷史比較，**不代表新版資料或本文件矯正後的模型**。正式候選樹必須由 `data.md` 的 canonical inputs 重建，並只使用 `1-1/2-1` 的新 likelihood 重跑。

## 2. 目前實作模型的整體公式

```text
P(T, z, eta, pi | D, H, C, Mpost, rho_ASCAT, PS)
  proportional to
P(T) × P(eta | T) × P(pi) × P(z | pi)
     × product_i sum_m Mpost_i(m)
         P_bulk(D_i | phi_z(i), C_i, m, rho_ASCAT)
         P_HP(H_i | z_i, PS_i)
```

本文件後續所有公式中的 purity 參數均明確寫作 `rho_ASCAT`，目前固定為 ASCAT tumor purity `0.99`；不再把 LongPhase-S tumor DNA fraction 當作模型輸入。

簡化成一句話：

```text
後驗機率
= 樹的先驗
× clone 比例先驗
× mutation 分群先驗
× 每個 SNV 的 REF/ALT likelihood
× 每個 SNV 的 HP1-1/HP2-1 likelihood
```

符號定義：

| 符號 | 定義 |
|---|---|
| `T` | clone 之間的 rooted parent–child tree |
| `z_i` | mutation `i` 被分配到的 clone node |
| `eta_v` | clone `v` 自身獨占的 cellular fraction |
| `phi_v` | clone `v` 與其所有 descendants 的 cumulative prevalence／CCF |
| `q_i` | mutation `i` 的 HP1/HP2 side；目前在每個 site 的 HP likelihood 中邊際化 |
| `pi_v` | mutation 被分配到各 clone 的混合權重 |
| `C_i` | locus `i` 的 total copy number 摘要 |
| `M_i` | locus `i` 的 mutated-copy multiplicity；由輸入的 `multiplicity_posteriors` 邊際化 |
| `Mpost_i(m)` | 位點 `i` 的固定 `multiplicity_posteriors` 輸入；目前只作權重，不由 sampler 重新抽樣 |
| `rho_ASCAT` | **ASCAT tumor purity**；正式 input 固定為 `0.99`，來源是 `output/cnv_callers/ascat_hcc1395_5khz_t4/purity_ploidy.txt`。LongPhase-S 的 `tumor DNA fraction=0.958936` 只作 reference，不再進目前 likelihood。這個正式 purity input 與歷史 Beta-Binomial 版本曾使用的 `rho=0.03` overdispersion shorthand 無關。 |
| `D_i`, `H_i` | locus `i` 的 bulk REF/ALT counts 與 HP1-1/HP2-1 counts |

### 2.1 Exclusive fraction 與 CCF

```text
phi_v = eta_v + sum(eta_w for w in descendants(v))
```

`eta_v` 只計算該 clone 本身；`phi_v` 則包含該 clone 以及所有後代，所以目前圖上的 CCF 是 cumulative prevalence。

### 2.2 預期 VAF

位點 `i` 若被分配到 clone `z_i`，其預期 ALT fraction 為：

```text
theta_i = rho_ASCAT × phi_z(i) × m_i
          / [2 × (1-rho_ASCAT) + rho_ASCAT × C_i]
```

加入定序錯誤率 `e_i` 後，將 read-level ALT probability 記為 `r_i`，避免和 mutation haplotype assignment `q_i` 混淆：

```text
r_i = e_i + (1 - 2e_i) × theta_i
```

沒有 HP-tag evidence 時，模型使用：

```text
ALT_i ~ Binomial(REF_i + ALT_i, r_i)
```

有正式 HP-tag evidence 時，同一批 reads 被拆成六個互斥類別共同建模，避免把 bulk counts 與 HP counts 重複算兩次：

```text
HP1-1_REF, HP1-1_ALT,
HP2-1_REF, HP2-1_ALT,
untagged_REF, untagged_ALT
```

這六類使用 Multinomial likelihood。`HP:Z:1-1` 已表示 somatic ALT read 可追溯到 germline HP1，`HP:Z:2-1` 已表示可追溯到 germline HP2；模型以每個 mutation 的 `q_i` 表達其 haplotype side，不再建立 PS-wide `o_PS` 重新猜方向。

> [!IMPORTANT]
> `HP:Z:1-2/2-2` 來自目前本地 `somatic-two-site-split` 實驗流程，暫不納入 likelihood；germline-only `HP:Z:1/2` 也不能冒充 somatic ALT haplotype evidence。PS 只保留 phase-block provenance、資料切分與局部一致性檢查，不是需要重新推導的 mutation-side direction。

## 3. 完整目標模型

[`longphase-clone.md`](longphase-clone.md) 規劃的完整 posterior 為：

```text
p(T, z, q, eta, C, M, E | D, PS, rho_ASCAT)
  proportional to
    p_TSSB(T,z)
  × p(eta | T)
  × p(C,M | CNV/LOH,T)
  × p(q | PS,phased_GT)
  × p(E)
  × L_bulk × L_HP
```

其中完整目標會再加入：

- `q`：mutation-to-haplotype latent assignment；
- `C, M`：haplotype-specific copy number 與 mutated copy number；
- `E`：真實 haplotype 到 observed HP tag 的 emission matrix；
- 正式 segment-aware allele-specific CNV/LOH likelihood。

目前明確不加入 Beta-Binomial concentration 或其他 bulk overdispersion
參數；bulk observation 使用普通 Binomial，HP tag allocation 使用條件式
Multinomial。

注意：sampler 命令列仍可能出現 `eta_concentration` 或
`assignment_concentration`；它們是 η proposal／mutation-assignment prior 的
取樣設定，不是 allele-count overdispersion，也不是被移除的
`beta_binomial_concentration`。

這些項目尚未全部落實在目前 M3 sampler，不能把完整公式直接當成目前已完成的計算結果。

### 3.1 Dynamic multiplicity posterior 設計

`M_i` 表示 mutation `i` 在一個 tumor cell 中有幾份 copy 攜帶 ALT；它不是 clone 數，也不是 CCF。`M_i` 必須依該位點的 allele-specific CN 動態建立候選集合，不能對所有 SNV 固定為 1–2。

對 ASCAT 的 segment：

```text
C_major = major_cn
C_minor = minor_cn
C_total = major_cn + minor_cn
```

若突變只發生在單一 haplotype，候選範圍為：

```text
mutation on major side: M_i ∈ {1, ..., C_major}
mutation on minor side: M_i ∈ {1, ..., C_minor}
```

因 ASCAT 的 major/minor 是 copy-number 大小排序，通常不能直接對應 HP1/HP2；若 retained-allele direction 尚未解決，模型對 major-side/minor-side orientation 邊際化，候選集合取兩側聯集。除非有獨立證據，不加入「同一 SNV 同時突變於兩條 homolog」的 biallelic state。

對候選 `m`，使用 raw REF/ALT counts 的 Binomial likelihood：

```text
theta_i(phi,m,C,rho_ASCAT)
  = rho_ASCAT × phi × m
    / [2(1-rho_ASCAT) + rho_ASCAT × C_total]

P(M_i=m | D_i,C_i)
  ∝ P(M_i=m | C_i,q_i)
    × Σ_phi P(D_i | theta_i(phi,m,C_i,rho_ASCAT))
            P(phi)
```

目前 Stage 6 builder 對 major/minor direction 未知的位點使用 **side-marginalized neutral prior**：major side 與 minor side 各先分到等量先驗，再在該 side 可容許的 `m` 值中均分。例如 `major/minor=3/1` 時，`P(M=1)=0.5`、`P(M=2)=0.25`、`P(M=3)=0.25`。這使 candidate support 由實際 CN 動態決定，不會把 minor-side possibility 遺失，也不會把 major/minor 誤命名為 HP1/HP2。

未來 joint sampler 可另加入偏向單一突變 copy 的敏感度 prior（例如 `exp[-lambda × (m-1)]`）；`lambda` 不視為生物學真值，須以 simulation/held-out calibration 比較。未通過 calibration 前，不把任何單一 `M` 當作確定答案。

每個 SNV 的 observation table 應保存完整分布，而不是只保存一個 mode：

```text
multiplicity_candidates = 1,2,...,M_max
multiplicity_posteriors = 1=0.70;2=0.25;3=0.05
multiplicity_map         = 1
multiplicity_map_prob    = 0.70
multiplicity_expected    = 1.35
multiplicity_entropy_bits
multiplicity_status      = identified|ambiguous|cn_underidentified|truncated
```

其中：

- `M_max` 由 `major_cn/minor_cn` 動態決定，不由全域常數 2 決定；
- `cn_underidentified` 表示沒有可靠 CN segment，不能默認 `M=1`；
- `truncated` 只在為了計算資源設定上限時使用，並必須報告被截斷的 CN；
- posterior 很分散本身是結果，代表該位點的 multiplicity 不可由目前資料唯一決定。

目前 `multiplicity_posteriors` 保持為 Stage 6 的固定輸入，sampler 對其做邊際化；它不是目前 sampler 重新估計的輸出。未來若改為 joint multiplicity sampler，應另開版本，不得把目前輸入 posterior 誤稱為新的 MCMC posterior。

## 4. 模型輸入

### 4.1 M3 sampler 中間表目前狀態

舊 M3 sampler 曾直接讀取下列五個檔案；它們已確認不是依新版 `data.md` 建立，並已於 2026-08-13 刪除：

```text
output/longphase_clone/snv_bulk_counts.tsv.gz
output/longphase_clone/snv_hp_counts.tsv.gz
output/longphase_clone/m3_latent_cn_site_posterior.tsv.gz
output/longphase_clone/m3_bam_sensitivity_site_ccf_proxy.tsv.gz
output/longphase_clone/m3_bam_sensitivity_candidate_tree.json
```

目前狀態為 **Stage 6 Binomial input available / sampler adapter connected / I6 production-like rerun completed but not converged**。最新 I6 結果位於 [`run_20260816_002_longchain_eta1`](output/longphase_clone/i6_automation_tmp/run_20260816_002_longchain_eta1)：最大 label-invariant R-hat=24.983、最低 ESS/chain=3.1，因此尚不能把其 tree sample 當作正式 lineage posterior。新版 canonical input 為 [`likelihood_input.tsv.gz`](output/longphase_clone/stage_06_likelihood_20260815_binomial/likelihood_input.tsv.gz)，其 QA 與 manifest 分別為 [`stage_06_likelihood_input_qa.json`](output/longphase_clone/stage_06_likelihood_20260815_binomial/stage_06_likelihood_input_qa.json) 與 [`stage_06_likelihood_manifest.json`](output/longphase_clone/stage_06_likelihood_20260815_binomial/stage_06_likelihood_manifest.json)。表中有 30,490 個 TP SNV，30,006 個 `eligible`；其餘 399 個 CN=0 與 85 個 unmapped 位點保留 QC 狀態而不進 likelihood。

`tools/run_longphase_clone_m3_tssb_mcmc.py` 現在會優先讀取這張新表，並在 observation layer 使用普通 Binomial、固定的 `multiplicity_posteriors` 邊際化與 HP1-1/HP2-1 conditional allocation；舊 Beta-Binomial table 與 production output 僅保留作歷史比較。K=2 smoke 與 I6 production-like run 均可執行，但 I6 的 R-hat/ESS、simulation recovery 與 strict VAF calibration gate 尚未通過；收斂導向的輸出保留策略見 [`convergence_cleanup_20260816.md`](convergence_cleanup_20260816.md)。

### 4.2 上游原始資料類型

```text
Reference FASTA
Tumor BAM + index
Matched-normal BAM + index
Somatic TP VCF + PS + index
Phased germline VCF + index
LongPhase-S HP/PS-tagged tumor BAM + index
Allele-specific CNV/LOH segments
ASCAT tumor purity (`rho_ASCAT=0.99`)
```

實際 canonical path、版本、筆數與缺件狀態統一由 [`data.md`](data.md) 管理，本文件不重複宣告為唯一來源。特別是：

- 目前可用的 somatic PS VCF 為 [`data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz`](data/hcc1395_clairs_v041_tp_with_bam_ps.vcf.gz)。
- Stage 6 目前採用已正規化的 ASCAT major/minor/total CN schema；retained-allele direction 仍未識別，major/minor 不冒充 HP1/HP2。
- 歷史 latent CN 表的上游 proxy 不再是 canonical provenance；新表的 source/command/checksum 見 Stage 6 manifest。

## 5. 模型會自動推導的參數

| 自動推導項目 | 意義 |
|---|---|
| `T` | clone tree topology 與每個 clone 的 parent |
| `z_i` | 每個 SNV 屬於哪個 clone |
| `eta_v` | clone 自身獨占的 cellular fraction |
| `phi_v`／CCF | clone 與所有 descendants 的 cumulative prevalence |
| `pi_v` | mutation 分配到各 clone 的混合比例 |
| `q_i` | 每個 mutation 位於 HP1/HP2/unknown 的 latent state；目前在 likelihood 中逐位點邊際化，尚未輸出獨立 posterior 表 |
| `M_i` | 每個 mutation 的 mutated-copy multiplicity；目前依輸入的 `multiplicity_posteriors` 邊際化 |
| `multiplicity_posteriors` | Stage 6 固定輸入的 `M_i` 候選機率；目前不是 sampler 新推導的參數 |
| edge posterior | parent→child edge 在 retained samples 中出現的機率 |
| topology posterior | 不同候選樹的 posterior mass |
| assignment posterior | mutation 屬於各 node 的後驗機率 |
| CCF credible interval | clone CCF 的後驗可信區間 |

圖上的 node VAF 是依 mutation assignment 加權彙整的 observed VAF，不是獨立 latent clone parameter。

## 6. 目前不會可靠自動推導的項目

- 正式 segment/per-site major CN 與 minor CN。
- 可靠的 LOH retained-allele direction。
- mutation multiplicity 的完整 joint posterior；目前只使用輸入的 `multiplicity_posteriors`。
- HP1/HP2 跨 PS 的全基因組 homolog identity。
- 真正不固定 clone 數的 non-parametric TSSB；目前 `K=2–8` 是設定值。
- ASCAT tumor purity 是固定的外部 input，不由 sampler 自動推導；目前不把 LongPhase-S tumor DNA fraction 作為替代輸入。sequencing error rate、MAPQ/baseQ 門檻也不是 sampler 自動推導項目。
- 由資料校準的 overdispersion 參數與完整 HP emission matrix `E`；目前不輸入、不估計任何 Beta-Binomial concentration。

因此 CN/multiplicity 現階段主要是輸入摘要或 proxy，而不是目前 sampler 已經從正式 CNV/LOH segments 完整推導出的結果。

## 7.1 目前的 topology / assignment / prevalence proposals

目前 M3 的目標 posterior 沒有因 proposal 改變；改變的是 MCMC 如何探索它：

```text
Pairtree-style pairwise relation guide
        + topology parent move (forward/reverse q)
        + assignment Gibbs sweep
        + eta pairwise prevalence move
        + restricted split–merge / full-occupancy exchange block
        -> MH accept/reject under the same posterior
```

Pairwise relation guide 只用 assignment 的 observed CCF/VAF、HP1-1/HP2-1 summary 與 node `phi` 產生 soft parent-edge proposal；它不是把 pairwise relation 當作真實 lineage constraint。Split–merge 有空 leaf 時會同時改變一個 assignment、sibling topology 與兩個 `eta`，並使用明確的 move-type、選擇率與 prevalence-coordinate Hastings/Jacobian。若 K 個 node 都已 occupied，則使用 CCF-similar site-pair 的 assignment/prevalence exchange fallback；其中 `split_merge_topology_probability=0.20` 的 branch 會再提出 Pairtree-guided parent reattachment，未抽到該 branch 時才由獨立 topology proposal 探索 parent edge。

這些 proposal 仍不引入 exactly-two-SNV PS、RR/RA/AR/AA 或新的 HP orientation latent variable；PS 仍是所有 TP site 的 provenance、grouped holdout 與局部 QC。

## 8. 實作邊界與解讀警告

目前程式是 finite-truncation、TSSB-inspired Metropolis–Hastings sampler，不是原始 PhyloWGS TSSB 程式的完整重作。它目前可以提供：

```text
候選 topology posterior
+ mutation-to-node posterior
+ clone CCF posterior
+ HP1-1/HP2-1-aware mutation likelihood（`q_i` 已邊際化；逐位點 posterior 輸出仍待補）
```

但仍有以下限制：

1. retained-allele direction 尚未識別；major/minor CN 不能轉稱 HP1/HP2 CN。
2. Stage 6 是 site-level CN/multiplicity observation summary；完整 joint CN/LOH event ordering 與 segment graph 尚未進入 sampler。
3. posterior convergence gate 尚未通過。
4. 實驗性 `HP:Z:1-2/2-2` 與 RR/RA/AR/AA joint-read evidence 明確排除。
5. `HP:Z:1-1/2-1` 是 somatic mutation side 的 read-level observations，不是 clone labels 或 lineage truth。

研究設計、階段狀態與改善歷史請以 [`longphase-clone.md`](longphase-clone.md) 為準；檔案 provenance 與 canonical input 選擇請以 [`data.md`](data.md) 為準。

## 9. 維護規則

修改這個文件關係圖時，必須遵守：

1. 新增或替換 canonical input：更新 `data.md`，並檢查本文件第 4 節。
2. 修改 likelihood、latent variables 或 sampler：更新本文件及 `longphase-clone.md`。
3. 實驗階段或結果改變：更新 `longphase-clone.md`，必要時回寫本文件的限制。
4. 刪除、改名或搬移任一文件前，以 `rg` 搜尋其 `document_id` 與檔名並同步修正所有 inbound links。
5. 三份文件的角色不可合併：資料 provenance、模型 specification、研究進度需要保持獨立但互相連結。
