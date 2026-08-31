# HCC1395 腫瘤演化樹 module

更新日期：2026-08-31；狀態：本文件整理研究模組的邊界、資料流與 inference 目的；完整 model 與 inference 規格以參考文件為準。

> [!IMPORTANT]
> 這是為了目前研究架構下的html視覺化文字說明參考，避免產生混淆。
> 本文件摘要 data input、model、inference 的模組邊界與輸入輸出，供模組規格與 HTML 視覺化對照使用。
> 完整的 likelihood、prior、posterior 與推理實作細節，請以參考文件為準。

## 研究模組主線架構

![HCC1395 tumor evolution tree module](assets/png_to_svg/full_arch.svg)

## 1. Data input

### 一句話功能

`data input` 把 BAM、VCF、ASCAT 的資訊整理成一列一個 SNV 的基本資料，供 model
讀取。

### 從哪裡取得資料

| 上游來源 | 提供的資訊 |
|---|---|
| BAM | REF/ALT read counts |
| VCF | SNV identity：`mutation_id、chrom、pos、ref、alt` |
| ASCAT | tumor purity `rho_ASCAT`、site-level `major_cn/minor_cn/total_cn` 與 CN/LOH context |

### raw data轉換model基本輸入資料

| 類別 | 欄位 | 意義 |
|---|---|---|
| Identity | `mutation_id、chrom、pos、ref、alt` | 哪一顆 SNV |
| Read counts | `ref_reads、alt_reads、total_reads` | 觀察到的 REF/ALT read counts；`total_reads = ref_reads + alt_reads` |
| Purity | `rho_ASCAT` | 固定的 sample-level tumor purity；目前主分析為 `0.99` |
| Copy number | `major_cn、minor_cn、total_cn` | SNV 所在位置的 CN context；`total_cn = major_cn + minor_cn` |

## 2. Model

Model 的主要目的是讀取 data input 整理出的 canonical SNV table。它把表中的 read counts、purity 和 copy number，連同候選 tree 的 clone fraction 及模型內部建立的 multiplicity，計算成候選 tree 的分數，讓 inference 模組負責探索不同候選樹並根據分數更新參數。

假設有一顆腫瘤演化樹

```text
Root
  │
  ├── Clone A
  │      └── Clone B
  │
  └── Clone C
```


之後必須讓電腦了解這個腫瘤演化樹故事，就必須寫成數學模型。

### 數學模型

```text
posterior ∝ prior × likelihood
```

候選腫瘤樹最後有多可信 = 原本的假設有多合理 × 它和真實資料有多吻合。

### Prior:

還沒看sequencing data 之前，哪些演化樹演化狀態比較合理。
例如:某演化樹中某一個clone的ccf 最高都是100%,不會出現超過100%的情況。

### Likelihood

假設這棵樹是真的，觀察到的sequencing data的機率有多高？

### Posterior

看到真實sequencing data後，模型猜測出來的腫瘤演化樹可信度有多高

### model輸出參數

| 參數 | 參數意義 |
|---|---|
| Tree topology `T` | 哪些 clone 是 parent／descendant？ |
| clone-specific local fraction $\eta_v$ | 每個 clone 自己獨有、且不包含 descendants 的 tumor-cell fraction 是多少？ |
| CCF／`phi` | 某 clone 加上 descendants 的累積比例是多少？ |
| Clone assignment `z` | 一顆 SNV 比較支持哪個 clone？ |

## 3. inference

### 目的

`inference` 按照 model 定義的 posterior、likelihood、prior 與結構限制，持續探索不同的腫瘤演化樹拓樸與各 clone 的比例，反覆評估哪些參數組合最能解釋目前的 sequencing data，並保留多個具有 posterior 支持的候選腫瘤演化樹結果。




## 4. 參考文件

- [data.md](data.md)：canonical data contract 與 target/spec boundary。
- [model.md](model.md)：模型語意、target posterior 與限制。
- [inference_algo.md](inference_algo.md)：目前 SMC implementation、annealing 與 output。
- [output.md](output.md)：topology、CCF 與 SNV assignment 的結果語意。
- [validation.md](validation.md)：posterior output 後的獨立 validation。

<!-- spec-paged-html:visual-feedback:start -->
## HTML 視覺化回饋

此區塊記錄 [`module_format.html`](module_format.html) 的 inline SVG／元件基礎與文字來源；重新生成時只更新本區塊。

### slide-1-module-flow（updated）

![研究模組主線](assets/png_to_svg/full_arch.svg)

- HTML：[`module_format.html#slide-1`](module_format.html#slide-1)
- 保留強度：`anchored`
- 視覺槽位：`module-flow`（1／1）
- SVG：inline SVG；`assets/png_to_svg/full_arch.svg`
- 對應來源：`## 研究模組主線架構`
- 涵蓋文字：raw data、data input、model、inference、output 的既有順序與目的。

### slide-2-source-to-row（updated）

![BAM、VCF、ASCAT 匯入 canonical SNV row](assets/components/source_to_input.svg)

- HTML：[`module_format.html#slide-2`](module_format.html#slide-2)
- 保留強度：`anchored`
- 視覺槽位：`source-to-row`（1／1）
- SVG：inline SVG；組裝基礎 `assets/components/source_to_input.svg`
- 對應來源：`## 1. Data input` → `### 一句話功能`、`### 從哪裡取得資料`
- 涵蓋文字：BAM、VCF、ASCAT 整理為一列一個 SNV 的基本資料。

### slide-3-canonical-fields（updated）

![Identity](assets/components/snv_identity_igv_reads.svg)

![Read counts](assets/components/read_pileup.svg)

- HTML：[`module_format.html#slide-3`](module_format.html#slide-3)
- 保留強度：`anchored`
- 視覺槽位：`canonical-fields`（1／1）
- SVG：inline SVG；組裝基礎 `assets/components/snv_identity_igv_reads.svg`、`assets/components/read_pileup.svg`、`assets/components/cn_segment_context.svg`、`assets/components/purity_mixture.svg`
- 對應來源：`## 1. Data input` → `### raw data轉換model基本輸入資料`
- 涵蓋文字：Identity 元件以已核准示例 `mutation_id = 1`、`chr1:123,456,789`、`G → A` 表達 `mutation_id, chrom, pos, ref, alt`，並以 IGV-style reads 呈現共享基因座與示意 read pileup；read pileup 上方也以 `ref = G · alt = A` 標示該示例鹼基。圖中同時表達 read counts、`rho_ASCAT` 與 copy number；CN 圖以已核准的示例 `major_cn = 3`、`minor_cn = 1` 表達重複 copy，並標示 `total_cn = 4`，不是由本文件推得的資料值。

### slide-4-candidate-tree（updated）

![候選 clone tree](assets/components/clone_tree.svg)

- HTML：[`module_format.html#slide-4`](module_format.html#slide-4)
- 保留強度：`anchored`
- 視覺槽位：`candidate-tree-evidence`（1／1）
- SVG：inline SVG；組裝基礎 `assets/components/clone_tree.svg`、`assets/components/read_pileup.svg`；clone 標籤依來源改為 Root、Clone A、Clone B、Clone C，示例 read counts 已移除
- 對應來源：`## 2. Model` 的候選腫瘤演化樹與兩項假設
- 涵蓋文字：Root、Clone A、Clone B、Clone C 與祖先／後代、clone fraction 假設；一顆 SNV 指派至一個 clone。

### slide-6-output-parameters（removed）

- HTML：[`module_format.html#slide-6`](module_format.html#slide-6)
- 保留強度：`replaceable`
- 視覺槽位：`output-parameters-combined`（removed）
- 原 SVG：`assets/components/eta_phi_tree.svg`、`assets/components/snv_assignment.svg`
- 替代 visual ID：`slide-6-topology`、`slide-6-local-eta`、`slide-6-cumulative-phi`、`slide-6-clone-assignment`
- 變更：`split`；依使用者指示將四個平行參數拆成四個獨立槽位。

### slide-6-topology（new）

![Tree topology](assets/components/clone_tree.svg)

- HTML：[`module_format.html#slide-6`](module_format.html#slide-6)
- 保留強度：`anchored`
- 視覺槽位：`tree-topology`（1／4）
- SVG：inline SVG；`assets/components/clone_tree.svg`
- 對應來源：`## 2. Model` → `### model輸出參數`
- 涵蓋文字：Tree topology `T` 表示哪些 clone 是 parent／descendant。

### slide-6-local-eta（new）

![local fraction eta](assets/components/eta_phi_tree.svg)

- HTML：[`module_format.html#slide-6`](module_format.html#slide-6)
- 保留強度：`anchored`
- 視覺槽位：`local-eta`（2／4）
- SVG：inline SVG；聚焦 `assets/components/eta_phi_tree.svg` 的 local `eta_v` 結構
- 對應來源：`## 2. Model` → `### model輸出參數`
- 涵蓋文字：`eta_v` 是每個 clone 自己獨有、且不包含 descendants 的 tumor-cell fraction。

### slide-6-cumulative-phi（new）

![CCF phi](assets/components/eta_phi_tree.svg)

- HTML：[`module_format.html#slide-6`](module_format.html#slide-6)
- 保留強度：`anchored`
- 視覺槽位：`cumulative-phi`（3／4）
- SVG：inline SVG；聚焦 `assets/components/eta_phi_tree.svg` 的 cumulative `phi` 結構
- 對應來源：`## 2. Model` → `### model輸出參數`
- 涵蓋文字：CCF／`phi` 是某 clone 加上 descendants 的累積比例。

### slide-6-clone-assignment（new）

![Clone assignment](assets/components/snv_assignment.svg)

- HTML：[`module_format.html#slide-6`](module_format.html#slide-6)
- 保留強度：`anchored`
- 視覺槽位：`clone-assignment`（4／4）
- SVG：inline SVG；`assets/components/snv_assignment.svg`
- 對應來源：`## 2. Model` → `### model輸出參數`
- 涵蓋文字：Clone assignment `z` 表示一顆 SNV 比較支持哪個 clone。

### slide-7-inference-module（new）

![Inference 探索、評估與候選結果](assets/png_to_svg/inference_module.svg)

- HTML：[`module_format.html#slide-7`](module_format.html#slide-7)
- 保留強度：`anchored`
- 視覺槽位：`inference-module-overview`（1／1）
- SVG：inline SVG；`assets/png_to_svg/inference_module.svg`
- 對應來源：`## 3. inference` → `### 目的`
- 涵蓋文字：inference 探索不同腫瘤演化樹拓樸與 clone 比例，反覆評估候選狀態，並保留具有 posterior 支持的候選結果。
<!-- spec-paged-html:visual-feedback:end -->
