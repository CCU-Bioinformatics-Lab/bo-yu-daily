# 主論文圖表索引與證據用途

| Item | Page | What is encoded | Claim it can support | Important caution |
|---|---:|---|---|---|
| Fig.1 | 2 | Multi-sample bulk inputs（CN、ref/alt counts、optional clustering）→ PhyClone graphical model → reconstructed clone tree | Input/model/output architecture | Schematic，不是 runtime pipeline 的全部細節；圖內 formulas 應以正文/supplement為準 |
| Table 1 | 4 | 六方法的 year、loss inference、sequencing-error correction、clustering、clonal prevalence、multiple solutions | 作者對 baseline capabilities 的分類 | 部分能力是 preprocessing 而非 during tree building；footnotes a/b 必須保留 |
| Fig.2 | 6 | PC vs PC-N 在 lost fraction 0/0.1/0.2 下的 V-measure、AD F-score boxplots | Outlier state improves robustness to simulated loss | Self-generated FS-CRP data，作者承認偏向 PhyClone；無跨方法比較/精確數表 |
| Fig.3 | 7 | TSSB-Low V-measure/AD F-score 隨 samples 2/4/8/16/128 | Sample scalability and point accuracy | 顯著性與 posterior metrics/runtime 在 supplementary；圖本身不能支持全部文字主張 |
| Fig.4 | 8 | TSSB-High、Pairtree、CONIPHER-NN 的 V-measure/AD F-score by samples | Robustness across generators; sample benefit | Y-axis boxplots顯示 distributions，exact effects/P-values需 XLSX |
| Fig.5 | 8 | CONIPHER-noise V-measure/AD F-score by sample groups | Robustness to ISA violations | 主文只明確陳述 AD F-score significance；不可替 V-measure 自行宣告 pairwise significance |
| Fig.6 | 9 | Patient 3 ground truth vs five methods，WGS與WGS+Targeted；dashed nodes mark absence/lost-outlier | Qualitative topology/loss reconstruction | 圖中 node colors按 ground-truth assignment著色，屬 post-hoc comparison；需 Supplement Table 1 支持 quantitative claim |

## Table 1 feature claims（[STATED]）

主文 Table 1（p.4）把 PhyClone 列為同時能推斷 mutation loss、做 sequencing-error correction、cluster mutations、計算 clonal prevalence、提供 multiple solutions。CONIPHER 亦被列為五項皆可；PhyloWGS 不能 correction/compute clonal prevalence；Pairtree/Orchard 的 correction 與 clustering 依 footnotes 是 tree-building 前的 preprocessing，而非 tree-building 中；fastBE 五項皆列 No。

[INFERRED] 這張表是作者的高層功能分類，不能取代各工具版本與 code-level verification。

## Supplementary items cited by main paper

| Supplement item cited | Main-paper use |
|---|---|
| Methods S1.1–S1.2 | PyClone likelihood、allelic counts/CN details（§2.2, p.3） |
| Fig.1 | Single-sample model schematic（§2.2, p.3；注意與 main Fig.1 同號不同來源） |
| Fig.2 | Multi-region generalization（§2.2, p.3） |
| Fig.3 | PyClone copy-number/tumour-content corrected likelihood（§2.2, p.3） |
| Methods S1.5 | `O(|V|^2)` marginalized likelihood DP（§2.2.1, p.3） |
| Fig.4 | SMC particle evolution（§2.3, p.4） |
| Methods S1.6.1 | SMC target density（§2.3, p.4） |
| Figs 5–8 | fixed-order reachability and PG ordering correction（§2.3.1, p.4） |
| Fig.9 | AD F-score construction（§2.4.3, p.5） |
| Fig.10 | posterior metrics across TSSB/Pairtree; also Fig.4 support（§3.2–3.3, pp.6–7） |
| Fig.11 | runtime scaling / PhyloWGS > order-of-magnitude slower（§3.2, p.6） |
| Figs 12–13 | node-count and nodes/samples-ratio degradation（§3.3, p.7） |
| Fig.14 | copy-number perturbation（§3.4, p.7） |
| Figs 15–16 | HGSOC patients 2 and 9（§3.5, p.8） |
| Table 1 | HGSOC quantitative metrics incl. patient 3（§3.5, p.8；與 main Table 1 不同） |

## Stable-locator caveat

[STATED] 主文的公式沒有 equation numbers；引用時應用「§2.2 cellular-prevalence identity, p.3」「§2.2 basic likelihood, p.3」「§2.2.1 collapsed joint, p.3」「§2.2.3 outlier joint likelihood, p.3」，避免杜撰 Eq. numbers。

