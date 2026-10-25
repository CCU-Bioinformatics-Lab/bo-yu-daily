# HP-aware 腫瘤演化樹真值的合理性總結（2026-10-25）

對象：要用來產生 long read bulk 模擬資料的兩棵 HP-aware 真值樹。
- 壓力測試樹：[`figures/hp_truth_tree.png`](../figures/hp_truth_tree.png)
- 典型樹（對照組）：[`figures/typical_truth_tree.png`](../figures/typical_truth_tree.png)

問題：這兩棵樹在生物上合理嗎？用它們產生的模擬資料可信嗎？

證據等級：〔資料實測〕＝本研究用公開或本機資料自己計算；〔論文實測〕＝論文報告的數字，已逐篇核對原文；〔推論〕＝本研究的推論。

## 1. 結論

- **7 類事件在真實腫瘤中都觀察得到。** 每一類都有直接資料實測或已核對的論文數字（第 3 節）。所以「這些事件是編出來的」這個質疑不成立。〔資料實測＋論文實測〕
- **HP 特徵在真實 ONT 資料中確實存在。** 在本機 HCC1395 ONT 資料上，85.9% 的 alt read 有 HP tag，92.2% 的 somatic SNV 可明確分到單一 HP，HP 深度和 haplotype-specific CN 一致（第 4 節）。〔資料實測〕
- **壓力測試樹的事件密度高於典型腫瘤。** 突變遺失 20%、4 個 clone 而且分岔、gain 區 early 比例 0.50，都偏離 cohort 典型值。所以它定位為「由真實事件組成的壓力測試」，不代表一般腫瘤。〔資料實測〕
- **典型樹的每個參數都取自 cohort 實測值。** 它和壓力測試樹用同一套事件，當作對照組（第 5 節）。〔資料實測〕
- **模擬器有一項假設要修改。** SNV pair 的跨越 read 數要依 SNV 間距抽樣，不能每對固定 80 條（第 4 節）。〔資料實測〕

## 2. 兩棵樹

| | 壓力測試樹 | 典型樹 |
|---|---|---|
| 樹形 | C1 → {C2 → C4, C3}，分岔 | C1 → C2 → C3，直線 |
| clone CCF | 1.00／0.80／0.45／0.10 | 1.00／0.58／0.29 |
| purity | 0.40 | 0.40 |
| SNV 數 | 100（50% clonal） | 200（70% clonal） |
| 突變遺失 | 20%（deletion＋cnLOH） | 1.5%（cnLOH） |
| 用途 | 檢查方法在極端情況下的表現 | 代表單一 bulk 樣本的一般腫瘤 |

## 3. 7 類事件 × 證據

| 事件 | 最強證據 | 等級 | 壓力測試樹 | 典型樹 |
|---|---|---|---|---|
| ① 低 purity | TRACERx 421 tumour 中位 0.39；PCAWG 中位 0.66，17% ≤ 0.40；本機 HCC1395 subsample 實測 0.15–0.74 | 資料實測 | ✅ 0.40 | ✅ 0.40 |
| ② subclonal HP gain | TRACERx 421：91% tumour 有 haplotype-specific subclonal gain，其中 91% 只差 1 copy；HG008 有 clonal 2+1 gain | 資料實測 | ✅ | ✅ |
| ③ 突變遺失 | TRACERx 421 區域間：47% tumour ≥ 1 個，每 tumour 中位 0%、Q90 1.4%、最高 11.7%；TRACERx 100 換算約 4% | 資料實測＋論文實測 | ⚠️ 20% 偏高 | ✅ 1.5% |
| ④ 低 CCF clone | TRACERx 421 單區域：8.4% subclone CCF ≤ 0.15；200× 下 CCF 0.10 邊緣可偵測 | 資料實測＋推論 | ✅ 存在但屬少數 | 不放 |
| ⑤ HP 拆分 | HCC1395 ONT：92.2% SNV 可分到單一 HP，HP1:HP2 ≈ 1:1；HG008：2,208:2,385 | 資料實測 | ✅ | ✅ |
| ⑥ subclonal cnLOH | TRACERx 421：72% tumour 有 ≥ 1 Mb，中位 7.2 Mb；HCC1395 ONT cnLOH 區 97.5% 位點只剩一條 HP | 資料實測 | ✅ | ✅ |
| ⑦ CN timing | HG008：gain 區 multiplicity 2:1 = 76:65，cnLOH 區 89:54；PCAWG 2:1 區 early 比例中位 0.28 | 資料實測 | ⚠️ 0.50 偏高 | ✅ 0.30 |

其他參數：

| 參數 | 證據 | 壓力測試樹 | 典型樹 |
|---|---|---|---|
| clone 數 | PCAWG-11：0／1／2／≥3 個 subclone 為 23%／53%／21%／2.3%；TRACERx 421 單區域中位 5 | ⚠️ 4（上尾） | ✅ 3 |
| 樹形 | TRACERx 421 單區域 73% 為直線 | ⚠️ 分岔（少數） | ✅ 直線 |
| depth | PCAWG 中位 48.5× | ⚠️ 200× | ✅ 50×／200× |

文獻核對：69 條主張中，52 條正確、17 條部分正確、0 條錯誤。修正已寫回 `04_event_evidence_real_tumors.md`。

## 4. HP 特徵的真實資料實測（HCC1395 ONT）

資料：本機 ONT `t50_n00`（100% tumor，約 50×）。phasing 用 SEQC2 germline het SNP，在 ONT normal 上執行 `longphase-s phase`，再用 `longphase-s haplotag` 標記 tumor read。

| 模擬假設 | 實測 | 判定 |
|---|---|---|
| 85% 的 read 有 HP tag | alt read 85.9% | ✅ |
| 每個 somatic SNV 屬於一條 HP | 有 ≥ 3 條 alt read 時 92.2%；2.4% 分散在兩條 HP | ✅ |
| HP 深度反映 haplotype CN | minor HP 比例：3+1 區 0.357（預期 0.333）、6+2 區 0.333（預期 0.333）；LOH 區 95–100% 位點 < 0.1 | ✅ |
| 每對 SNV 有 80 條跨越 read | 間距 < 5 kb 約 44–52 條；5–20 kb 中位 21；20–50 kb 中位 2；> 50 kb 約 0 | ⚠️ 改成依間距抽樣 |

另外，`tX_nY` 的 nominal 比例是 tumor DNA 比例，不是細胞 purity。HCC1395 的實測細胞 purity 比 nominal 低（例如 nominal 40% → 0.32）。給 PhyClone 的 `tumour_content` 要用實測值。

## 5. 典型樹的參數依據

| 參數 | 典型樹 | 依據 |
|---|---|---|
| clone 數、樹形 | 3 個，直線 | PCAWG-11 21% 有 2 個 subclone；TRACERx 421 單區域 73% 直線 |
| subclone CCF | 0.58、0.29 | TRACERx 421 單區域 subclone CCF 中位 0.58、q25 0.29 |
| clonal SNV | 70% | TRACERx 100 中位 30% subclonal |
| 突變遺失 | 1.5% | TRACERx 421 Q90 1.4%、最高 11.7% |
| gain 區 early 比例 | 0.30 | PCAWG 中位 0.28 |
| subclonal CN 範圍 | 約 10% | PCAWG 中位 7.6% 基因組 |

## 6. 限制與未解問題

- **單一 bulk 樣本內的 SNV 層級遺失，沒有直接資料。** TRACERx 只能看到區域之間的遺失。〔資料實測〕
- **HP 實測只有一株細胞株（HCC1395）。** 它的 LOH 比例和突變負荷都偏高。
- **只用了 germline `haplotag`。** 模擬的 HP 標籤要模仿 germline 還是 `somatic_haplotag`，尚未決定。目前的 tag 比例是下限。
- **SNV 數只有 100–200。** 真實腫瘤有數千個，clone 更容易分開，所以兩棵樹都偏保守。
- **HG008、PCAWG-11 consensus 等資料是 draft 或 controlled-access。** 部分數字用第三方或代理值（例如 CliPP）。

## 7. 證據來源

| 主題 | 位置 |
|---|---|
| 文獻調查 | `truth_evidence_2026-10-25/01`–`04` |
| 文獻核對 | `truth_evidence_2026-10-25/05`、`06` |
| HG008 事件統計 | `lab_report/2026-10-25_hg008_truth_tree_plausibility/` |
| HCC1395 實測 purity | `lab_report/2026-10-25_seqc2_hcc1395_measured_purity/` |
| TRACERx 421 統計 | `lab_report/2026-10-25_tracerx_event_stats/` |
| PCAWG 統計 | `lab_report/2026-10-25_pcawg_event_stats/` |
| 典型樹設計 | `lab_report/2026-10-25_typical_truth_tree/` |
| HCC1395 HP 拆分 | `lab_report/2026-10-25_hcc1395_hp_split/` |
| 公開資料 | `/big8_disk/boyu114/benchmark_data/`（各子目錄有 README） |
