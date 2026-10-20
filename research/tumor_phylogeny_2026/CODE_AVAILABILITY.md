# 程式碼與 GitHub 星星數

13 篇論文是否公開程式碼，以及對應 GitHub repo 的星星數。

- **連結來源**：各篇 `papers/*/paper.txt` 的 Code availability 段落（A01 的 duplex 連結被 PDF 雙欄切斷，改用 `pdftotext -raw` 重新抽取）。
- **星星數**：2026-10-16 以 `gh api repos/<owner>/<repo>` 查詢的快照，會隨時間變動，引用前要重新查。
- **分類**：「方法本體」指論文提出的方法實作；「pipeline／分析腳本」指資料處理或重現圖表的程式；「未發布」指論文只引用第三方工具。

| ID | 論文（簡稱） | 程式碼類型 | GitHub repo | ⭐ |
|---|---|---|---|---|
| A01 | Ovarian cfDNA clonal tracking (Nature 2025) | pipeline／分析腳本 | `mondrian-scwgs` org（主 repo `mondrian`）<br>`msk-access/nucleo`（duplex cfDNA pipeline） | 8<br>3 |
| A02 | SPRINTER (Nat Genet 2025) | **方法本體** | `zaccaria-lab/SPRINTER` | 7 |
| A03 | Pancreatic snDNA-seq (Nat Commun 2023) | 第三方套件的 fork | `haochenz96/mosaic`（fork 自 `MissionBio/mosaic`，18⭐）<br>`haochenz96/scg` | 0<br>0 |
| A04 | AML Strand-seq multiomics (Nat Genet 2024) | 作者實驗室自有工具 | `jeongdo801/scNOVA`<br>`friendsofstrandseq/mosaicatcher-pipeline`<br>`daewoooo/StrandPhaseR`<br>`jeongdo801/NO_based_HSPC_classifier`<br>`lysfyg/PloidyAssignR` | 12<br>26<br>11<br>2<br>0 |
| A05 | MPAL multiome (Nat Commun 2024) | 下游分析腳本 | `SmithLabUCSF/MPAL` | 1 |
| B01 | Melanoma sublines long-read (Nat Commun 2026) | **方法本體** | `KolmogorovLab/TreeHarmonizer` | 1 |
| B03 | Single-cell mutational processes (Nature 2022) | **方法本體**＋pipeline | `shahcompbio/MultiModalMuSig.jl`（MMCTM）<br>`shahcompbio/signals`<br>`shahcompbio/single_cell_pipeline`<br>`shahcompbio/wgs`<br>`marcjwilliams1/hscn_pipeline` | 20<br>14<br>28<br>13<br>2 |
| B04 | Lung cancer long-read phasing (Nat Commun 2022) | **未發布** | 只引用第三方工具，例如 `friend1ws/nanomonsv`（99⭐）；資料在 JGA（JGAS000349），需申請 | — |
| B05 | MEDICC2 (Genome Biol 2022) | **方法本體** | `schwarzlab-ccb/medicc2`（論文寫 Bitbucket `schwarzlab/medicc2`） | 10 |
| B07 | Numbat (Nat Biotechnol 2022) | **方法本體** | `kharchenkolab/numbat`<br>`kharchenkolab/NumbatAnalysis`（重現論文結果） | **231**<br>10 |

## 重點

- **有方法本體的只有 5 篇**：A02 SPRINTER、B01 TreeHarmonizer、B03 MMCTM、B05 MEDICC2、B07 Numbat。
- 社群使用度最高的是 **Numbat（231⭐）**，其餘都在 30⭐ 以下。要參考 haplotype 感知推理的實作，Numbat 最值得看。
- 與本 repo long-read／haplotype 方向最接近的 **B01 TreeHarmonizer（1⭐）** 是 2026 年的新 repo，尚未有社群使用。

## 與論文文字不一致之處

- 論文寫 `shahcompbio/MultiModal-MuSig.jl`，該網址 404；實際 repo 是 `shahcompbio/MultiModalMuSig.jl`。
- `ICCB-Cologne/medicc2` 會轉址到 `schwarzlab-ccb/medicc2`。
