# PhyClone 來源對照表

## 範圍與證據詞彙

本研究資料包完全依據 `/bip8_disk/boyu114/main_work/research/phyclone_research` 重建；未使用該工作區以外的任何來源。

- `[明示 STATED]`：論文或補充資料中明確陳述的內容。
- `[實作 IMPLEMENTED]`：由目前簽出的原始碼直接確認的內容。
- `[推論 INFERRED]`：作者未明確主張的分析或推導結果。
- `UNRESOLVED`：現有證據不足以支持可靠結論。

重要版本界線：論文實驗使用 **PhyClone 0.7.0**（主文 §2.4.2，第 5 頁）。受檢查的簽出版本是乾淨的 **PhyClone 0.8.0**，commit `27383246c1aff7b1d62c02662017bd61bfdfbc33`。凡屬版本敏感的發現，均會明確標示，而不會回溯歸因於論文結果。

## 工作區清冊與不可變識別碼

| 來源 | 角色 | SHA-256／版本 |
|---|---|---|
| `phyclone.pdf` | 主要研究脈絡、核心方法、實驗設計與主要主張 | `413500e0f30e19d23aaf3fcf99014240fd87036319300053ba0264ab6c7787ad` |
| `btaf344_supplementary_data/supp.pdf` | 完整数學推導、PG-SMC 細節、快取／測試、補充圖表索引 | `d40aa2d3672aebe175ece825e2888b45ff705750bd0946c07641dabd2ebfdf5b` |
| `Experiment_Performance_Metrics.xlsx` | 原始點估計準確度、成功率、執行時間與記憶體結果；補充表 S2–S14 | `d9e00c3029d16523b318d2b2d7ffe35929eeb6d7406e9fd60c59b3dcbab88c6d` |
| `Experiment_Friedman_Nemenyi_Tests.xlsx` | 總體與成對檢定；補充表 S15–S27 | `eabda8bdfe0e8daa502a20a4a14c0532ca6e686b014960c760bb5d0c2bc5eebe` |
| `Experiment_Posterior_Metrics.xlsx` | 原始 RRE/LPR 與檢定；補充表 S28–S36 | `6c25a17d3876930fff83576dd3703ce16cf172a5d33dab7edaf76830973d6268` |
| `PhyClone/` | 目前實作、輸入／輸出契約、預設值與測試 | tag `0.8.0`，commit `27383246c1aff7b1d62c02662017bd61bfdfbc33` |
| `RESEARCH_PLAN.md` | 研究流程與完成契約 | `a222f82b236646163215d21b25b0a53b7ebf036c2a83ff53bcc9c7cbf84dfc3b` |

目前沒有獨立的原始 BAM/VCF、模擬種子、評估指令碼或論文結果追蹤檔案。XLSX 活頁簿是隨附的結果產物；應用程式儲存庫中不含基準測試／統計分析流程。

## 來源關係

```text
主文（問題、模型、基準測試設計、主張）
       ├── 補充資料（推導、演算法、額外圖表、表格索引）
       ├── XLSX（原始結果與統計決策）
       └── 儲存庫（執行期契約與實作）

論文版本：0.7.0                    受檢查程式碼：0.8.0
       └──────── 版本敏感的驗證 ────────┘
```

主文與補充資料界定預期行為。簽出版本可驗證目前行為，但無法自動驗證論文發表時期的結果。方法驗證者曾查閱本機 tag `0.7.0`，以檢查離群值積分、bootstrap proposal 與 subtree-PG 的發現。

## 與研究問題相關的儲存庫架構

| 階段 | 模組 | 研究角色 |
|---|---|---|
| CLI/API 協調 | `phyclone/cli.py`, `phyclone/run.py` | 參數解析、多條鏈、暖機期、PG/SMC 迴圈、軌跡寫入 |
| 輸入與似然網格建構 | `phyclone/data/pyclone.py`, `data/base.py`, `data/validator/*.json` | 整齊格式輸入契約、篩選、CN／純度校正、預分群原子、離群值邊際量 |
| 缺失先驗啟發式方法 | `data/cluster_outlier_probabilities.py` | 幹系叢集（truncal cluster）與染色體聚集檢定 |
| 發射機率數學 | `utils/math_utils.py` | 二項／Beta-二項 PyClone 基因型混合模型 |
| 樹狀態與動態規劃 | `tree/tree.py`, `tree/base.py`, `tree/tree_node.py`, `tree/utils.py` | 虛擬根節點森林、突變指派、後代摺積／累積積分 |
| 聯合先驗／評分 | `tree/distributions.py` | CRP、森林先驗、根節點懲罰、離群值先驗／似然 |
| SMC proposal | `smc/kernels/{bootstrap,fully_adapted,semi_adapted}.py` | 由下而上的樹成長與 proposal 密度 |
| 粒子系統／順序 | `smc/samplers/*.py`, `smc/swarm/swarm.py`, `smc/utils.py` | ESS／重抽樣、條件式／非條件式 SMC、容許排列 |
| MCMC 移動 | `mcmc/particle_gibbs.py`, `mcmc/gibbs_mh.py`, `mcmc/concentration.py` | 整棵樹／子樹 PG、重新指派、剪枝再嫁接、alpha 更新 |
| 輸出 | `utils/save_hdf5.py`, `process_trace/*.py` | 軌跡、MAP、共識、拓樸報告、Newick／TSV／盛行率 |
| 驗證 | `phyclone/tests/` | 小型精確後驗、邊際化、根節點項、順序與摺積檢查 |

## XLSX 綱要

### 效能活頁簿

| 工作表 | 範圍 | 資料集／條件 | 方法 | 指標／結果 | 重複次數 |
|---|---:|---|---|---|---|
| S2 TSSB-Low | A1:L3001 | 深度 1000；100 個 SNV；樣本數 2/4/8/16/128 | 六種，包含 PhyloWGS | V、突變數、AD F、成功率、記憶體、時間 | 每個條件／方法 100 次 |
| S3 TSSB-High | A1:L2001 | 深度 1000；10,000 個 SNV；樣本數 2/4/8/16 | 五種 | 同上 | 每個條件／方法 100 次 |
| S4 FS-CRP Loss | A1:M601 | 600 個 SNV；8 個樣本；缺失比例 0/0.1/0.2 | PhyClone、PhyClone-N | 同上，另含缺失比例 | 每個條件／方法 100 次 |
| S5 Pairtree | A1:M2881 | 深度、節點、突變、樣本 | 五種 | 同上 | 每個保留組合 4 次；每種方法 576 次 |
| S6/S7 CONIPHER | 各 A1:J751 | 無雜訊／有雜訊；模擬 ID 與樣本 | 五種 | V、AD F、成功率、記憶體、時間 | 每種方法 150 次 |
| S8–S13 HGSOC | 各 A1:I6 | 病患 2/3/9 × WGS／WGS+標靶定序 | 五種 | V、AD F、成功率、記憶體、時間 | 每種方法一次 |
| S14 CN Error | A1:J2251 | 模擬 ID 與樣本；缺少擾動標籤 | 五種 | V、AD F、成功率、記憶體、時間 | 每種方法 450 次 |

### 統計活頁簿

- Friedman 工作表 S15/S17/S20/S22/S24/S26：`A1:C5`（`metric`、`p_value`、`significant`）。
- Nemenyi 工作表 S16 `A1:G61`；S18/S21/S23/S25/S27 `A1:G41`：指標、方法配對、p 值、平均差、表現較佳者、顯著性。
- S19 FS-CRP Loss 為 `A1:F5`，且省略 `significant` 欄。

### 後驗活頁簿

- 原始指標：S28 Pairtree `A1:L2881`、S31 TSSB-Low `A1:K2501`、S34 TSSB-High `A1:K2001`。
- 欄位：方法、RRE、受評估樹的數量、設計變數、困惑度（perplexity）、真實困惑度與 LPR。
- 總體檢定：S29/S32/S35 `A1:C3`；成對檢定：S30/S33/S36 `A1:G21`。

35 個工作表全都可見；皆不含公式或合併儲存格。記憶體單位缺失。圖 S11 指出其執行時間面板的單位為秒，但單靠活頁簿無法定義全域的時間單位。

## 發表項目 → 原始證據對照

| 發表項目 | 證據 |
|---|---|
| 主文圖 2 | 效能 S4；檢定 S19 |
| 主文圖 3 | 效能 S2；檢定 S15–S16 |
| 主文圖 4 的 A/B、C/D、E/F 面板 | 效能 S3、S5、S6；檢定 S17–S23 |
| 主文圖 5 | 效能 S7；檢定 S24–S25 |
| 主文圖 6 | HGSOC S10/S11，加上拓樸影像 |
| 補充圖 S10 | 後驗 S28/S31/S34；檢定 S29–S36 |
| 補充圖 S11 | S2 的時間欄 L |
| 補充圖 S12–S13 | 依節點／樣本分組的 S5 AD 與 S28 RRE/LPR |
| 補充圖 S14 | S14 合併值；缺少錯誤程度的列標籤 |
| 補充圖 S15–S16／表 S1 | S8–S9／S12–S13／S8–S13 |

## 主要問題的涵蓋範圍

- 研究動機與貢獻：`01_PAPER_BIG_PICTURE.md`。
- 輸入、變數、模型、似然、先驗、盛行率、推論、前處理、離群值與輸出：`02_METHODS_DEEP_DIVE.md`。
- 所有主要實驗、資料、基準方法、指標、量化結果與注意事項：`03_EXPERIMENTS_RESULTS.md`。
- 方程式／預設值／執行期行為，以及程式碼版本差異：`04_CODE_MAPPING.md`。
- 主張層級的跨來源可追溯性與衝突：`05_EVIDENCE_MATRIX.md`。
- 生物、統計、運算與資料假設、限制及失敗情境：`06_ASSUMPTIONS_LIMITATIONS.md`。
- 10–15 分鐘的教學／報告敘事：`07_PRESENTATION_BRIEF.md`。

## 全域未解事項

1. 缺少確切的基準評估／統計程式碼與逾時前處理流程。
2. S14 未針對每一列記錄 0/0.1/0.2 的拷貝數擾動程度。
3. 使用直接的區組設定，無法從可見儲存格精確重現數個 Friedman p 值；但所有 `p<0.01` 的判定均維持不變。
4. 目前環境缺少完整測試套件所需的相依套件／Python 版本；僅執行了 `test_root_term`（8 項測試通過）。這是環境限制，不代表斷言失敗。
