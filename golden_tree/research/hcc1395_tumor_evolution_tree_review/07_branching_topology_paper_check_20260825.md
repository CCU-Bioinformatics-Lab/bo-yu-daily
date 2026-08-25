# HCC1395 分支拓樸與目前 sampler 輸出的查核

## 結論先說

有。`Establishing community reference samples, data and call sets for benchmarking cancer mutation detection using whole-genome sequencing` 的 HCC1395 Fig. 4a 明確畫出 branching topology：

```text
Normal cells
└── S1: MRCA
    ├── S2: 60%
    │   └── S4: 51%
    │       ├── S5: 14%
    │       └── S7: 29%
    └── S8: 34%
        └── S9: 27%
            └── S10: 25%
```

論文正文直接說這棵 PhyloWGS tree 顯示 branching evolution，兩個主要分支從 S2 與 S8 開始。S3、S6 因 cancer cell fraction 小於 10% 沒有畫出。這裡的樹是「由資料推斷的候選演化樹」，不是單細胞逐一追蹤得到的直接祖先譜系。

## 論文中各資料的角色

### 直接用來推斷 Fig. 4a 的部分

- bulk WGS / WES 的 somatic mutation 與 clonality 證據。
- PhyloWGS 將這些 bulk mutation / copy-number evidence 組合成 subclone 與 evolutionary relationships。
- 樹上的 CCF 與 driver mutation 標籤用來描述各 subclone 及其演化事件。

論文沒有公開一份足以完整重跑的 PhyloWGS input table、參數檔與每條 edge 的 posterior，因此不能把這棵樹當成可逐欄重建的 ground truth。

### single-cell CNV 的角色

10x single-cell CNV 產生的是 638 個 HCC1395BL cells 與 1,270 個 HCC1395 cells 的 integer-scaled CNA profiles。作者移除 noisy / S-phase cells，再依 CNV 相似性做 hierarchical clustering，顯示 HCC1395 存在 substantial subclonal CNAs 與 cellular heterogeneity。

因此 single-cell CNV 支持：

1. HCC1395 不是單一均質 clone。
2. 多個 subclone 與 branching evolution 是合理候選模型。
3. Fig. 4a 的分支解釋與獨立的細胞層級 CNV 異質性相容。

但它不是 single-cell SNV lineage matrix，也沒有直接測出 Fig. 4a 的每一條樹邊；不能寫成「single-cell 直接證明了 S1→S2 或 S1→S8」。

### 其他 bulk 支持

Extended Data Fig. 9 使用 WES / SuperFreq 依 local copy number 校正 SNV VAF，並對 SNV、CNA 的 clonality 與 uncertainty 做 clustering；另用 subHMM 推斷 clonal / subclonal CNA。這些結果支持多個早期與晚期 subclone 的存在，但不是獨立的 edge-level posterior。

## 和目前 repo pilot 的對照

檢查的 run：

`/bip8_disk/boyu114/main_work/output/tumor_tree_pipeline/20260824T103554Z_7f715611ea9c_rho0p99_K4-6-8_seed20260824`

| K | branching particles（4 repeats） | 解讀 |
|---|---:|---|
| K4 | 0/256、0/256、0/256、0/256 | 目前是線性 chain，不是論文式分支候選 |
| K6 | 38/256、0/256、30/256、1/256 | 有少量分支 particle，但不穩定 |
| K8 | 131/256、256/256、69/256、0/256 | 有明顯 branching-shaped candidate，但跨 repeat 不一致 |

最適合拿來示範「目前有分支候選」的是 K8 / repeat_02。其 raw representative tree 出現 `clone_1` 同時連到兩個子節點的 bifurcation；但 canonical topology summary 顯示後段 edge support 約為 0.55–0.75，替代分支位置也分散。因此目前只能稱為：

> K8/repeat_02 branching-shaped pilot candidate

不能稱為 high-confidence branching topology，也不能稱為 HCC1395 的唯一真實樹。該 pilot 的 `formal_gate_not_evaluated=true`，目前 validation 層尚未完成正式 topology-class scoring、selection margin 與獨立 branch support gate。

## 對目前研究的實際含義

論文提供的方向不是「所有真實資料都必須產生分支」，而是：

> 如果資料真的含有多個 subclone，且 copy-number / clonality 證據支持早晚事件差異，模型應該能保留 branching topology；不能只用固定 chain 當作唯一合理答案。

所以目前應同時保留：

- K4 的線性 topology，作為目前穩定度較高的 baseline candidate。
- K8/repeat_02 的分支 topology，作為需要進一步驗證的 branching candidate。

下一步應比較 topology class 的跨 repeat posterior、branch edge support、CCF nesting 與 CNV compatibility，而不是只挑一張視覺上像分支的 representative tree。

## 來源

- 本地論文：[hcc1395_golden_tree.pdf](/bip8_disk/boyu114/main_work/golden_tree/hcc1395_golden_tree.pdf)，Fig. 4a 位於 PDF p.7（期刊 p.1157）。
- [Nature Biotechnology article](https://www.nature.com/articles/s41587-021-00993-6)
- [Nature Fig. 4](https://www.nature.com/articles/s41587-021-00993-6/figures/4)
- [Nature Extended Data Fig. 9](https://www.nature.com/articles/s41587-021-00993-6/figures/13)
- [PubMed record](https://pubmed.ncbi.nlm.nih.gov/34504347/)
