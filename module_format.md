# Tumor-tree module

更新日期：2026-08-27
狀態：簡化版；本文件只先說明 `data input` 和 `model`。

## 一條主線

```text
BAM / VCF / ASCAT
        ↓
data input：建立每顆 SNV 的 data row
        ↓
model：用 data row 評分候選解釋
        ↓
candidate tree topology / CCF / SNV-to-clone assignment
```

這裡的 BAM、VCF、ASCAT 是上游資料來源。實際 runtime 不把 raw BAM、raw VCF
或 ASCAT 原始 segment 直接交給 C++ sampler；`data input` 先建立 canonical
SNV-level table，再交給 model。

## 1. Data input

### 一句話功能

`data input` 把 BAM、VCF、ASCAT 的資訊整理成一列一個 SNV 的基本資料，供
model 讀取。

### 從哪裡取得資料

| 上游來源 | 提供的資訊 |
|---|---|
| BAM | REF/ALT read counts |
| VCF | SNV identity：`mutation_id、chrom、pos、ref、alt` |
| ASCAT | sample purity `rho_ASCAT`、site-level `major_cn/minor_cn/total_cn` 與 CN/LOH context |

### 交給 model 的 SNV data row

| 類別 | 欄位 | 意義 |
|---|---|---|
| Identity | `mutation_id、chrom、pos、ref、alt` | 哪一顆 SNV |
| Read counts | `ref_reads、alt_reads、total_reads` | REF/ALT read 支持；`total_reads = ref_reads + alt_reads` |
| Purity | `rho_ASCAT` | 整個樣本的 tumor purity |
| Copy number | `major_cn、minor_cn、total_cn` | SNV 所在位置的 CN context；`total_cn = major_cn + minor_cn` |

### Data input 做的三件事

1. 依 SNV identity 對齊 VCF、read counts 和 ASCAT site-CNV。
2. 檢查 read count、purity 和 copy number 資訊是否一致。
3. 產生標準 SNV 資料輸入表。


## 2. Model

### 一句話功能

Model 像裁判：用 reads、purity 和 CN，替每個候選樹及其 CCF、SNV 歸屬打分。

### Model 使用的主要 features

- `ref_reads、alt_reads、total_reads`：觀察到的 REF/ALT read counts。
- `rho_ASCAT`：sample-level purity。
- `major_cn、minor_cn、total_cn`：site-level copy-number context。
- `loh_state`：可作 compatibility context；目前不是 active C++ likelihood 欄位。

### Model 評分的候選結果

| 候選結果 | Model 要回答的問題 | 之後呈現的結果 |
|---|---|---|
| Tree topology | 哪些 clone 是 parent／descendant？ | candidate branching topology |
| CCF / `phi` | 在這個 topology 下，每個 clone 及其 descendants 的累積比例是多少？ | clone CCF summary |
| SNV-to-clone assignment | 一顆 SNV 比較支持哪個 clone？ | SNV assignment probability/summary |
| Multiplicity | 在 CN context 下，ALT 可能有幾份 mutated copies？ | multiplicity posterior |

Model 會把 observed REF/ALT counts 和候選結果所對應的 expected ALT probability 比較，
再對由 CN context 產生的 multiplicity candidates 做邊際化。`multiplicity` 是
model 內部的 candidate，不是 ASCAT 直接量到的 input 欄位。

Model 是評分規則，不是搜尋器。它不直接讀 raw BAM、VCF 或 ASCAT，也不單獨在
整個 tree space 中搜尋。

### Current C++ baseline likelihood

以下是目前 active C++ runtime 實際使用的簡化 baseline；它不是 `model.md` 中尚未
同步的 PhyClone-compatible `xi` target/spec。

對第 `i` 顆 SNV 和第 `v` 個 clone，runtime 使用：

```text
N_i = ref_reads_i + alt_reads_i
d_i = (1 - rho_ASCAT) * 2 + rho_ASCAT * total_cn_i
q_i(phi_v, m) = clamp(
    rho_ASCAT * phi_v * m / d_i,
    1e-12,
    1 - 1e-12
)

L_i(phi_v) = sum over m in M_i of:
    pi_i(m) * Binomial(alt_reads_i | N_i, q_i(phi_v, m))

log_L(D | T, eta) = sum over i of:
    log( sum over v of eta_v * L_i(phi_v) )
```

實作在 log scale 使用 log-sum-exp。`M_i` 不是全 sample 共用的數值，而是第 `i`
顆 SNV 根據自己的 `major_cn/minor_cn` 建立的 multiplicity candidates；`pi_i(m)`
是對應的 CN-derived prior。`minor_cn > 0` 時，major/minor 兩個 copy-number
side 各分配一半權重，side 內的 `m = 1..side_cn` 均勻分配；重複的 `m` 再合併。
`minor_cn = 0` 時只使用 major side。

| 符號 | 目前 runtime 的定義 |
|---|---|
| `i` | 一顆 SNV 的索引；read counts 和 CN 都是 site-level input。 |
| `v` | 一個候選 tumor clone 的索引。 |
| `T` | clone 的 tree topology；決定 parent／descendant 關係。 |
| `eta_v` | clone `v` 自己獨有的 local mass；必須為正，且所有 clone 的 `eta` 總和為 1。 |
| `phi_v` | clone `v` 加上 descendants 的累積 mass；由 `T` 和 `eta` 推導，不是獨立輸入。 |
| `rho_ASCAT` | sample-level purity；目前主分析設定為 `0.99`，每列的值必須和 runtime 設定一致。 |
| `major_cn_i/minor_cn_i` | SNV `i` 所在位置的 allele-specific CN，用來建立 `M_i` 和 `pi_i(m)`。 |
| `total_cn_i` | SNV `i` 的 total CN，進入 DNA-copy denominator `d_i`。 |
| `M_i` | SNV `i` 的 multiplicity candidate set；由該 SNV 的 `major_cn_i/minor_cn_i` 建立。 |
| `pi_i(m)` | SNV `i` 對候選 multiplicity `m` 的 CN-derived prior weight；同一 SNV 的候選 prior 加總為 1。 |
| `m` | SNV `i` 的一個候選 mutated-copy 數；是 SNV-level latent candidate，不是 sample-level 參數。 |
| `ref_reads_i/alt_reads_i` | SNV `i` 的觀察到的 REF/ALT read counts；`N_i` 必須等於兩者總和。 |
| `N_i` | SNV `i` 的總觀察 reads；`N_i = ref_reads_i + alt_reads_i`。 |
| `d_i` | SNV `i` 的 expected total DNA-copy denominator；由 normal diploid `2` 和 tumor `total_cn_i` 組成。 |
| `q_i(phi_v,m)` | 在 clone `v` 與 multiplicity `m` 下，觀察到 ALT read 的 expected probability。 |
| `z_i` | SNV `i` 的 clone assignment；目前不放進 particle，而是由 `eta_v * L_i(phi_v)` 對所有 clone 邊際化。 |

其中 denominator 的 `2` 是 normal diploid copy number；`1e-12` 的 clamp 只是數值
安全限制，不是 sequencing error parameter。HP counts 只做讀取與 conservation check，
不進這個 primary likelihood。

### Current runtime boundary

目前 C++ runtime 使用較簡化的 baseline likelihood；文件中的 PhyClone-compatible
`xi`、`error_rate=0.001` 和完整 genotype/CN-timing model 仍是 target/spec，不在
這份簡化文件中展開。

## 3. 只保留的 downstream boundary

- `inference_algo` 搜尋 model 定義的 candidate states。
- `output` 把 posterior candidates 整理成 topology、CCF 和 SNV assignment。
- `validation` 只讀取結果與 evidence，檢查可靠性和 claim ceiling。

因此，candidate tree 是模型支持的候選結果，不是唯一真實演化歷史；bulk CN/LOH
相容性也不等於 branch-level proof。

## 4. 參考文件

- [data.md](data.md)：canonical data contract。
- [model.md](model.md)：likelihood、latent state 和 model semantics。
- [inference_algo.md](inference_algo.md)：目前 SMC implementation。
- [output.md](output.md)：topology、CCF 和 SNV assignment 的結果語意。
