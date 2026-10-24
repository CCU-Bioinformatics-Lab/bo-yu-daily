# 文獻對本 repo 的改進方案

本文件是研究設計，**尚未修改 PhyClone、longphase-s，也沒有執行新的 BAM/CRAM 分析**。2026-10-15 已將第一版評估選擇同步至 `plan.md` 與 [第一版評估規格](../../../../evaluation_v1.md)。下面的效益都是待驗證的 `inferred`，並非已證明提升。

## 1. 先對齊目前系統能做什麼

| 主張 | status | source／locator | 對研究設計的影響 |
|---|---|---|---|
| repo 目標是 PhyClone 加入 longphase-s HP 與同 read SNV 共現 | current | `../../CLAUDE.md`，研究目標；`../../plan.md` §0、§4.0 | 文獻要回答「特徵如何改 likelihood／topology」，不能只整理 variant caller |
| PhyClone 目前讀取 total ref/alt、major/minor/normal CN、tumour_content | current | `../phyclone_research/PhyClone/phyclone/data/pyclone.py:299`，`create_sample_data_point` | 沒有原生 PS／HP／read-pair 欄位；新特徵需明確介面 |
| multiplicity 與 before/after-CN genotype 在 likelihood grid 階段混合 | current | 同檔 `get_major_cn_prior:325`；`utils/math_utils.py:180`、`:216` | C2/C3 可接在單 SNV grid，不能以為下游保留每個 genotype 的 posterior |
| tree score 有三個公開計分入口 | current | `tree/distributions.py:124`，`log_p`、`log_p_one`、`compute_log_p_and_log_p_one` | C4 如實作，三入口都須一致，並檢查 cache、partial tree 及 proposal weight |
| C0–C6 都是既有設計，不是此文獻調查新增實作 | current | `../../plan.md` §4.0、§5 | 可研究、比較與排優先序，不能報稱已開發或改善 |
| 現有主 pilot 是 full HCC1395 一個 sample 的 old tagging | current | `../../data_input.md` §1–2；30,368 個 baseline SNV | 单樣本 CCF 容許多種 topology；首先需要額外局部 linkage 支持 |
| 既有 20,470 對 co-read 表未做 read-level HP/PS 與 primary alignment 篩選，且集中 CN gain | current | `../../data_input.md` §3、差異 1–3 | 不能直接送進 `plan.md` 第一版 C4 的同 HP、同 PS、`C_h=1` 模型 |
| 六種 ONT 材料是細胞株，tX_nY 是 nominal target-depth mixture | current／lab-canonical | `../../tumor_sample.md`；lab `02_samples/cancer-samples.md`、`08_references/glossary.md:71–85` | 不可稱為病人 lineage truth 或已量測 cellular purity |
| HP1/HP2 是 PS 內任意標籤，HP3 不是 LOH | lab-canonical | `/big8_disk/liaoyoyo2001/Knowledge/08_references/glossary.md:67–85` | key 至少包含 sample、chromosome、PS；LOH 需要 CN／regional evidence |
| 既有 HCC1395 Fig.4a 是 bulk 推斷候選樹，scCNV 沒有逐邊證明 | historical | `../hcc1395_golden_tree_research/hcc1395_tumor_evolution_tree_review/07_branching_topology_paper_check_20260825.md` | 只能作相容性對照；原始輸入／posterior 仍需另外取得 |
| 歷史 KB 不存在 | not-found | `/bip8_disk/boyu114/bip8_disk_boyu_database`，2026-10-15 preflight | 未把無法讀取的歷史工作當成已查證事實 |

本表的 current 是此次簽出內容，不表示未追蹤的 `plan.md`、`data_input.md` 已經成為經實驗驗證的標準。實作核對使用源碼；本地盤點的資料位置沒有在這次重新做全 BAM/CRAM 掃描。

## 2. 最值得做的三個方向

### 優先一：先證明 read pairs 能排除哪種候選樹

[B04 肺癌](../../papers/B04_lung_longread_phasing_2022/README.md) 的價值非常具體：long-read 局部突變順序可以在 bulk VAF 容許多種解時提供額外限制。這正對應 C4，而非只改善 SNV calling。

先做一份 **held-out pair consistency report**：對 baseline trace 中每棵候選樹，檢查 pair 對 same／ancestor／descendant／branch 四種關係的支持；報告可辨識 pair 比例與衝突，而不是先挑最像文獻圖的樹。

納入條件沿用現有計畫：同 sample、同 chromosome、同 PS、可可靠定位同 HP、單筆 primary alignment 跨兩位點、有效 base call、沒有跨 CN breakpoint；第一輪限制 `C_h=1` 且 clonal CN。每個排除原因都記錄 denominator。long read 只證明同一分子上的狀態；在 amplified copy、mutation loss、phase switch 或 mapping artifact 下，不能直接等同 whole-cell genotype。

| 觀測／關係 | 可提供的支持 | 不能直接得到的結論 |
|---|---|---|
| 有可靠 `11` | 至少部分分子同時帶兩變異 | A 在 B 前，或 B 在 A 前 |
| `11+10`，在無 loss、單 copy 等前提下 | 可支持 A 在 B 前，排斥同 node／反向關係 | 排除所有含 CN 重排或觀測錯誤的其他模型 |
| `11+01`，同前提 | 可支持 B 在 A 前 | 全基因組唯一 clone tree |
| `10+01`、沒有 `11` | 在有充分 joint coverage 與 error model 時支持互斥／branching | 只憑 `n11=0` 證明不同 clone；不同 HP 本來就可有此現象 |

`plan.md` §4.5 已設計將 nuisance mixture 積分以維持 topology-only factor。這是可測試的近似：真實 pair frequency 仍受 clone mixture、purity、CN、tagging 與 coverage 影響，不能把「條件積分掉」解讀為生物學上不依賴 CCF。

### 優先二：用 allele-specific CN 限縮 multiplicity，保留不確定性

[A04 Strand-seq](../../papers/A04_aml_strandseq_2024/README.md)、[B03 parallel CN evolution](../../papers/B03_singlecell_mutational_processes_2022/README.md)、[B05 MEDICC2](../../papers/B05_medicc2_2022/README.md)、[B07 Numbat](../../papers/B07_numbat_2022/README.md) 一起提示：total CN 與 major/minor 可能把不同親代染色體歷史壓成同一狀態。把 germline haplotype 對到 CN allele，才有機會將 multiplicity 的候選上限由 major CN 改為該 HP 的 `C_h`。

對應 C2 的最低版本是 **soft phase-aware genotype prior**：對 mutation 所在 HP、major/minor orientation、CN uncertainty 做加權混合。只有高可信 segment 才使用 hard cap；不能用稀少或有 mapping bias 的 HP depth 直接宣告某 HP 就是 major。

C3 應保留 phased 與 unphased counts，且每個 read 在一個位點只進一個 count bin。先測 phased probability 是否依 ALT/REF、HP、read length、MAPQ、距離 germline SNP 而變。LongPhase-S 的 somatic tag 用了 somatic variants，這種選擇過程可能讓 phased 子集的 VAF 偏離原始 VAF。B07 的 RNA expression／allelic bursting 模型不能當成 DNA sampling likelihood。

### 優先三：採兩層 benchmark，分開檢驗真實性與可識別性

第一層用 [B01 23 個 ONT 單細胞衍生株](../../papers/B01_melanoma_longread_2026/README.md) 或完整 read simulator，建立可控制的 clone mixture、normal contamination、CN 與 read span。它最接近目前手上的 ONT cell-line workflow。B01 的參考樹仍由 SNV 推斷，phylogeny-constrained calls 不能反過來當獨立 topology 真值。

第二層用 A01–A05 真實病人 scDNA/scWGS reference phylogeny 檢查泛化與錯誤模式。這些資料沒有同樣的 ONT reads 時，只能測 bulk/CN/tree 端或以受控模擬補 read-level observations；不能說已驗證真實病人 long-read pipeline。

## 3. purity、VAF、CCF 的建模契約

`purity` 至少要拆成 cellular purity `rho`、tumor DNA fraction `delta`、nominal mixture 三種，且另外記來源與 uncertainty。PhyClone 的 `tumour_content` 在目前程式中先形成 population weights，再乘 CN；因此不能不經換算就把 LongPhase-S 的 DNA fraction 放入當 cellular mixture weight。

在只有 normal 與一個腫瘤 population、正常平均 DNA content 為 `P_N`、腫瘤為 `P_T` 的簡化條件下：

```text
delta = rho * P_T / [rho * P_T + (1-rho) * P_N]
rho   = delta * P_N / [P_T * (1-delta) + delta * P_N]
```

這是定義導出的換算，不是對任何 nominal mixture 的實測校正；subclonal ploidy／source filtering／library sampling 可使簡化式不適用。

在忽略錯誤、normal CN 為 2、腫瘤所有 clone 有相同 local total CN `C`、mutation 在腫瘤中 CCF 為 `f`、每個攜帶細胞有 `m` 個 ALT copy 的簡化模型：

```text
E[VAF] = rho * f * m / [2 * (1-rho) + rho * C]
```

目前 PhyClone 的 genotype 模型更一般，包含 reference-tumor 與 variant-tumor 不同 CN，見 `utils/math_utils.py:180–244`。本式只用來說明：VAF 不是 CCF，haplotype-specific VAF 也不自動消除 multiplicity 歧義。遇到 subclonal CNA、LOH 與 WGD 時，應明確改用相應 genotype mixture，不能沿用固定 `C` 式。

另外，node 的 exclusive clone fraction 與以該 node 為根的整個 subtree 的 CCF 不同。比較論文與 repo 輸出時需先對分母與「包含後代」的定義；A01 的 cfDNA relative clone abundance 也不等於原組織中的 cell fraction。

## 4. C0–C6 與文獻的直接對照

| 現有模組 | 應補的契約或實驗 | 主要文獻 | 可檢查的產出 |
|---|---|---|---|
| C0 feature extraction | read-level PS/HP、primary alignment、reference build、CN boundary、callability、read ID；從 base 而非 somatic tag 判 ALT | B04、A04、B01 | 單 SNV counts、pair counts、每層 QC attrition；抽查 reads 可追溯 |
| C1 schema | `sample,chrom,PS,HP` scope；missing phase 與 zero evidence 分開；cellular purity 與 DNA fraction 分欄 | B04、B07、lab glossary | phase provenance 與 uncertainty；輸入驗證報告 |
| C2 multiplicity prior | HP/major-minor orientation posterior，低信心退回原本 prior；CN loss/WGD 分層；各 genotype 情況在 likelihood 中邊際化 | A04、B03、B05 | CCF／祖先關係結果；genotype 候選與權重為選用診斷，不計 multiplicity 正確率 |
| C3 per-SNV likelihood | phased+unphased、tag-selection bias、minor-CN 錯誤與 switch-error sensitivity | B07、B03、A02 | held-out likelihood、CCF interval coverage、bias |
| C4 topology factor | local partial order、完整 joint coverage、error／CN 限制；同 read 多 pair 的依賴性 | B04 | held-out relation log score、conflict rate、edge posterior、ESS/runtime |
| C5 clustering | HP linkage 可反駁錯誤 merge；先比較固定 cluster 與重新分群，不能混淆收益來源 | A05、B07 | V-measure/ARI 與拓樸指標分別報告 |
| C6 posterior／診斷 | 輸出可識別與不可識別邊；分開 timing、assignment、topology uncertainty | A01、A02、B05、B01 | trace、pair conflict table、alternate topology 與 loss 註記 |

## 5. 最小可執行的比較設計

第一版依 [evaluation_v1.md](../../../../evaluation_v1.md) 採用 AD F-score、V-measure、CCF MAE、四類關係 confusion matrix、合格／informative pair 數與比例。依使用者決定取消 multiplicity 正確率；保留 PhyClone 在 likelihood 中對不同 multiplicity／genotype 情況的加權邊際化，不要求逐 SNV 真值或 MAP multiplicity 輸出。這是已採用的設計，尚未實作或開跑；本文件其餘 posterior／held-out 指標為後續擴充。

| 比較 | 固定條件 | 主要問題 |
|---|---|---|
| baseline | 原 PhyClone、同 mutations、CN、clusters、purity 與 outlier 設定 | 原資料本來有多少拓樸不確定性？ |
| baseline + C2 | 只改 genotype prior，保留 genotype 邊際化 | allele-specific CN 調整候選後，CCF／祖先關係是否改善？ |
| baseline + C3 | 保持相同 cluster 與 CN | phase-split counts 是否提供額外證據，或只是 tagging bias？ |
| baseline + C4 | 同 clusters，獨立校準 pair factor | 同 read linkage 是否降低錯誤 ancestor／branch 關係？ |
| C2+C3+C4 | 同 read partitions／held-out loci | 合併效益、資訊重複計分與 calibration 是否可接受？ |
| Pair shuffled／PS 內 switch-error control | 打亂 pair 對應或注入局部相位錯誤，其他觀測一致 | 模型是否真的利用正確的 phase，而非額外樣本數？ |
| downsampled short-span control | matched coverage、錯誤率、callability | 效益有多少來自 molecule span，而非較深 coverage？ |

每組至少跨多個 seeds 與多種 clone mixtures；`C_h=1` 與 amplified/subclonal CN 分層；pure normal、normal admixture、phase switch、minor CN ±1、mutation loss、低 pair coverage 都應覆蓋。第一版遵守 `plan.md` 的 no-outlier 範圍；loss stress test 超出此模型時，要顯示失效並與適合處理 loss 的比較基線對照，不能把損失全歸因於 long reads 無效。

整個 PS 的 HP1／HP2 與相應 CN 一起對調是等價改名，應作不變性檢查，不能作破壞 phase 的負對照。獨立模擬資料集／生物樣本是統計比較單位，seeds 用於檢查同一資料集的推理穩定性。

評估分三層：feature 的 phasing／orientation accuracy；CCF 的 MAE，以及後續可擴充的 bias、interval coverage、held-out likelihood；tree 的 ancestor-descendant F-score、四類關係，以及後續可擴充的 clade／edge support、topology uncertainty 與 posterior calibration。Multiplicity 保留為 likelihood 內的潛在 genotype 情況，不另計正確率。clone assignment 的 ARI/V-measure 單獨報，不能代替 tree correctness。真實病人只評估有證據的 edge／clade；未識別的邊應保留 uncertain。

## 6. 四個容易造成假改善的地方

**同一批 reads 重複計分。** 單位點 counts 與多個 pair 經常來自同一條 molecule。把每對當獨立因子會隨密集 SNV block 放大證據。可先以 PS/read blocks 做 resampling，限制一條 read 的總權重，或使用留出 molecules；報告 composite likelihood 的權重敏感度，未推導前不要宣稱是完整 generative likelihood。

**tagging 洩漏。** 用來打 somatic HP 的 ALT 位點與拿來評估的 held-out 位點重疊，會造成循環支持。嚴格 holdout 要在 tagging／feature extraction 前切分，必要時 retag 或遮罩 held-out somatic variants；不能只切最後的 pair 表。

**參考樹與驗證資料不獨立。** A02 的 MEDICC2 使用固定 SNV topology；B01 使用 phylogeny-constrained calls；A01 的 CCFtree 依賴既定參考樹。這些適合驗證相容性或事件定位，不能當兩套獨立資料一致就證明每條 edge。

**資料來源不相容。** `data_input.md` 已記錄 tagged BAM、ASCAT segment 與 subsample 的來源差異。原始 reference、caller/version、CN來源、tagging SNV集合、PS方向與 read filter 必須一併保存。不能把另一批次的 major/minor CN 當作同樣本已 phase 的 copy-number truth。

## 7. 資料優先序與交付邊界

先用本地 HCC1395 設計 C0 QC 與候選樹 consistency report；B01 作最貼近 ONT 的外部 clone mixture 資源；B04 作局部方向判斷的重現目標；A01/A04 作 allele-CN 與 loss 事件的病人參考。需要 controlled-access 的病人 raw data 時，先用公開 processed data／source data 驗證欄位與可重現範圍，再依正式程序申請。

論文 PDF、補充資料與 accession 已在逐篇目錄整理。本任務未下載 TB 級原始 reads、未申請受控人類資料、未對外聯絡作者；因此上面的 benchmark 可行性屬設計判斷，沒有假稱已重跑。

## 8. Related work 與新穎性應如何收斂

不能把「同一條 read 的 somatic mutation pairs 能推先後」本身當作新貢獻：B04已直接用來選候選樹；BitPhylogeny（M08）也已讓整條read的多位點pattern共用一個clone來源推樹。

本repo較值得檢驗的差異是：在明確PS／HP／CN條件下，將局部molecular evidence接入PhyClone的posterior tree inference，同時保留multiplicity、phase error與非唯一topology的不確定性；並證明改善不是coverage、固定分群、重複計分或tagging洩漏所造成。這是待驗證的研究定位，不是已證成的原創性宣告。
