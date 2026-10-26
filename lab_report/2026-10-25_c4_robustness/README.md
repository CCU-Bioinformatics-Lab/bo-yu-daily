# C4 穩健性：HP 錯標、phase switch、鹼基錯誤（2026-10-25）

問題：C4（read 共現 topology 因子）在無誤差資料上排除了錯誤的直線樹（`lab_report/2026-10-25_c4_pair_term_stress/`）。加入真實 ONT 的觀測誤差後，它還穩健嗎？ε 該怎麼設？計畫見 `research/phyclone_research/C4_ROBUSTNESS_PLAN.md`。

標記：〔實測〕＝本實驗計算；〔論文〕＝文獻數字；〔推論〕＝本檔推論。

## 1. 結論

- **P2（直線樹）在所有條件下都穩健。** 〔實測〕在 ε ≤ 0.06 的 51 個 run 中，`c3_under_c4` 都 ≤ 0.003，包括 5 倍校正值的 switch rate 和 3% 的 base error。不跑 MCMC，只算 pair term：真值樹比直線樹高 21–294 log 單位（ε 0.001–0.03，所有條件）。
- **依計畫第 1 節的判定，C4 不穩健。** 〔實測〕在校正後的 `real` 條件（mistag 2.5%、switch 1／Mb、base error 0.4%）下，seed 2 有一棵錯誤樹：ε = 0.01 時 posterior 0.39，ε = 0.03 時 0.98。這棵樹不是直線樹，而是「C1／C2 合併，C3 變成獨立 root」。
- **失效模式 1：clone 被拆開。** base error 大於 ε 時，同一 clone 的 pair 在 `same` 假設下，每條 10／01 read 都罰 log ε。所以 C4 偏好把一個 clone 拆成祖孫鏈。〔實測〕base error 3% 時，ε = 0.001 推出 5／8／7 個 clone（收縮後的真值是 3–4 個）；ε = 0.06 時降到 3／4／4。pair 層的診斷量 `same_vs_split` 也一致：b03、ε = 0.01 時是 −145 到 −45。
- **失效模式 2：C3 被推成獨立 root。** 〔實測〕這在 C1／C2 先被合併（P1）時發生。合併後，s4（C2）在 trunk 上；s4×s6 的分支證據不允許 C3 掛在 trunk 下，所以 C3 變成另一個 root。〔推論〕phase switch 會加強這個模式：switch 之後，不同 HP 的 s3（C1）與 s6（C3）看起來在同一條 HP 上，產生假的分支證據。sw5 時這棵樹在 ε = 0.03 的 posterior 是 0.995／0.567／0.713。
- **整條 read 錯標 HP 幾乎無害。** 〔實測〕mistag 1–5% 時，segment C 的相容比例都是 1.000，和零誤差一樣。原因：錯標的 read 移到另一條 HP 的 pair 表，在那裡兩個位點都是 ref（n00），不建模。計畫第 3.2 節原本預期它會讓分支 pair 出現 n11，這個預期不成立。
- **調高 ε 不能同時解決兩個模式。** 〔實測〕ε 變大會減少拆分（模式 1），但會：
  - 削弱 C4 對 P1 的幫助（b03 的 `c1c2_merged` 從 ε 0.001 到 0.1 上升）。
  - 讓 P2 開始失守（ε = 0.1 時，b03 的 `c3_under_c4` 最高 0.086，sw5 最高 0.290）。
  - 不能消除模式 2（`real` seed 2：ε 0.03 比 0.01 更糟）。
- **事後挑樹（像 Sakamoto 2022 的肺癌研究）不能取代 in-model C4。** 〔實測〕第 7 節：
  - base＋事後挑樹：12 個 run 中，有 4（軟）／5（硬）個的錯誤樹 posterior > 0.5。base＋C4 是 0 個。
  - 事後挑樹在 24 個 run 中都推不出完整的 4 clone 樹。A2＋C4 有 3 個。
  - 事後的 posterior 只剩很少的有效樣本：ESS 1.0–18.5（每個 run 有 4,000 個樣本）。
  - A2＋事後挑樹的錯誤最少（0／12），但它等於只挑出 1–20 個樣本，不能當作可靠的 posterior。
- **ε 的建議（暫定）：** ε 應 ≥ base error，否則會拆 clone。在實測的 base error（0.4%）下，0.01 已經足夠；0.03 沒有更好。〔推論〕要處理模式 2，需要改模型（見第 6 節），不是調 ε。

## 2. 校正（計畫 §4.1）

| 參數 | 值 | 來源 | 等級 |
|---|---|---|---|
| `base_error` | **0.004** | HCC1395BL normal ONT（`/big8_disk/data/HCC1395/ONT/HCC1395BL.cram`），37,321 個 SEQC2 somatic 位點（depth ≥ 10），1,713,564 條 read。ref 被讀成該 somatic alt 的 pooled 比例 0.403%；任何 mismatch 1.065%。位點中位數 0，p90 2.0%，p99 5.3%；431 個位點 > 5% | 〔實測〕`calibration/normal_snv_base_error.tsv` |
| `switch_rate_per_mb` | **1** | LongPhase 原論文：ONT 的 switch error，LongPhase 0.13–0.16%，WhatsHap 0.12–0.15%（WhatsHap compare）。HCC1395BL 有 1,804,018 個 phased het SNP（4,060 個 PS block），約 620／Mb。0.0015 × 620 ≈ 0.9／Mb | 〔論文〕＋〔推論〕換算。論文沒說分母是 het SNP 還是相鄰 pair |
| `mistag_rate` | **0.025** | HCC1395 split-HP 實測的 2.4%（`lab_report/2026-10-25_hcc1395_hp_split/`）。這是上限代理值，混了 switch 和 SEQC2 假陽性 | 〔實測〕代理值 |

- alt 被讀成 ref 的方向沒有量測。模擬器假設對稱。
- 實測的 base error 有長尾。v0.2 的錯誤在位點之間獨立，所以沒有模擬到這個長尾（第 5 節）。

## 3. 結果

壓力測試樹，×10 密度，base＋C4，資料 seed 1／2／3。完整表：`topology_summary.tsv`；本表：`results_by_condition.tsv`。

- `c3_under_c4`：直線樹（P2）的 posterior，真值 0。
- `segC_compat`：只看 segment C 的 s3–s7（C4 的合格 pair 全在這裡）。posterior 中「真值樹收縮任意 parent-child 邊後相同」的比例。
- `segC_max_wrong`：segment C 上，單一錯誤樹的最大 posterior。
- `max_wrong`：所有角色（扣掉遺失的 s2、s10）。零誤差時就有 0.40，來自 segment A 的 s8 放錯，和 C4 無關。
- clone 數：posterior 的眾數。

| 條件 | ε | `c3_under_c4` | `segC_compat` | `segC_max_wrong` | `max_wrong` | clone 數 |
|---|---|---|---|---|---|---|
| 零誤差 e0 | 0.01 | 0／0／0 | 1.000／0.999／1.000 | 0／0／0 | 0.404／0.002／0.012 | 3／3／3 |
| mistag 1% | 0.01 | 0／0／0 | 1.000／1.000／1.000 | 0／0／0 | 0.243／0.001／0.000 | 3／3／3 |
| mistag 2.5% | 0.01 | 0／0／0 | 1.000／1.000／1.000 | 0／0／0 | 0.252／0.001／0.002 | 3／3／3 |
| mistag 5% | 0.01 | 0／0／0 | 1.000／1.000／1.000 | 0／0／0 | 0.244／0.027／0.001 | 3／3／3 |
| base 1% | 0.01 | 0／0／0 | 1.000／0.993／0.051 | 0／0.006／**0.535** | 0.231／0.085／0.434 | 3／4／4 |
| base 1% | 0.03 | 0／0／0 | 1.000／0.979／0.053 | 0／0.020／**0.659** | 0.202／0.066／0.461 | 3／4／4 |
| base 3% | 0.001 | 0／0／0 | 0.488／0.487／0.308 | 0.194／0.087／0.199 | 0.056／0.059／0.075 | 5／8／7 |
| base 3% | 0.01 | 0／0.001／0 | 0.547／0.464／0.382 | 0.326／0.345／0.365 | 0.139／0.163／0.148 | 4／7／5 |
| base 3% | 0.03 | 0／0／0 | 0.869／0.498／0.428 | 0.079／0.450／0.223 | 0.225／0.218／0.180 | 3／5／4 |
| base 3% | 0.06 | 0／0／0.003 | 0.996／0.423／0.594 | 0.002／**0.542**／0.272 | 0.336／0.298／0.418 | 3／4／4 |
| base 3% | 0.1 | 0／0.086／0.035 | 1.000／0.472／0.625 | 0／0.416／0.217 | **0.547**／0.256／0.467 | 3／4／4 |
| switch 1／Mb | 0.01 | 0／0／0 | 1.000／1.000／1.000 | 0／0／0 | 0.449／0／0.017 | 4／3／3 |
| switch 1／Mb | 0.03 | 0／0／0 | 0.501／1.000／0.872 | 0.499／0／0.128 | 0.433／0／0.118 | 3／3／3 |
| switch 5／Mb | 0.001 | 0／0／0 | 1.000／0.788／0.983 | 0／0.086／0.013 | 0.344／0.086／0.012 | 4／4／4 |
| switch 5／Mb | 0.01 | 0／0／0 | 0.425／0.632／0.955 | 0.303／0.144／0.033 | 0.303／0.144／0.046 | 4／4／4 |
| switch 5／Mb | 0.03 | 0／0／0 | 0.004／0.082／0.287 | **0.995／0.567／0.713** | **0.995／0.567／0.682** | 3／4／3 |
| switch 5／Mb | 0.1 | 0.025／**0.290**／0 | 0.949／0.361／0.007 | 0.026／0.298／**0.993** | 0.026／0.298／**0.953** | 3／3／3 |
| **real** | 0.01 | 0／0／0 | 0.762／0.571／1.000 | 0.182／0.417／0 | 0.350／0.392／0.009 | 4／4／3 |
| **real** | 0.03 | 0／0／0 | 0.882／0.000／1.000 | 0.086／**0.989**／0 | 0.495／**0.977**／0.007 | 4／3／3 |

粗體：超過判定門檻（錯誤樹 > 0.5，或 `c3_under_c4` ≥ 0.1 的最大值）。

### 3.1 失效時的錯誤樹（posterior 最大的錯誤樹）

| run | 錯誤樹（角色層；`A<B` 表示 A 的 parent 是 B） | posterior |
|---|---|---|
| real s2，ε 0.03 | `s1+s3+s4+s9<root; s5+s8<trunk; s6+s7<root`（C1／C2 合併，C3 是第二個 root） | 0.977 |
| sw5 s1，ε 0.03 | 同上 | 0.995 |
| base 1% s3，ε 0.03 | 同上 | 0.461 |
| base 3% s2，ε 0.06 | segment C：`s3<root; s4+s5<s3; s6<s7; s7<s3`（C3 被拆成 s7 → s6） | 0.542 |

`real` seed 2 在 segment C 有兩個 switch（10,000,170 與 10,142,550），seed 1、3 沒有。`truth/phase_switches.tsv`。

### 3.2 pair 層證據（不跑 MCMC）

`pair_evidence.tsv`（`tools/c4_pair_evidence.py`）。SNV 放在真值的 origin clone 上，只改 clone 的 parent。

| 條件 | ε | 真值 − 直線樹（min–max） | `same_vs_split`（min–max） |
|---|---|---|---|
| e0 | 0.01 | 60.0–128.5 | 46.4–72.3 |
| e0 | 0.1 | −2.3–11.0 | 28.4–35.2 |
| base 1% | 0.01 | 76.3–133.0 | −19.1–21.2 |
| base 3% | 0.01 | 125.7–153.3 | −144.7–−45.2 |
| base 3% | 0.1 | 15.4–23.8 | −19.3–13.1 |
| switch 5／Mb | 0.01 | 43.7–137.6 | 38.0–96.0 |
| real | 0.01 | 125.0–142.6 | 20.8–42.7 |

- `same_vs_split` < 0：pair term 偏好把同一 clone 的 pair 拆成祖孫。這是逐 pair 的樂觀上限，不是一棵具體的樹。
- ε = 0.1 時，即使零誤差，pair term 在一個 seed 也已經不偏好真值樹（−2.3）。所以 ε 不能設到 0.1。

## 4. 做法

```bash
# longbulksim v0.2（錯誤模型）測試：27 個
cd longbulksim && python3 -m unittest discover -s tests && cd ..
# 校正
python3 -I tools/measure_snv_base_error.py
# 模擬＋PhyClone（每個 job：SIM METHOD EPS）
L=lab_report/2026-10-25_c4_robustness
bash $L/run_all.sh $L/jobs_stage1.txt     # 8 條件 × 3 seed，ε 0.01
bash $L/run_all.sh $L/jobs_stage2.txt     # real；b03、sw5 的 ε 掃描
bash $L/run_all.sh $L/jobs_stage2b.txt    # real、sw1、b01 的 ε 0.03
bash $L/run_all.sh $L/jobs_posthoc.txt    # 第 7 節：base、A2（沒有 C4）
bash $L/run_all.sh $L/jobs_a2c4.txt       # 第 7 節：A2＋C4，ε 0.01
bash $L/run_posthoc.sh > $L/posthoc.log   # 事後挑樹（tools/c4_posthoc.py）
bash $L/summarize.sh > $L/topology_summary.tsv
env PYTHONPATH=research/phyclone_research/PhyClone ~/venvs/phyclone/bin/python \
  tools/c4_pair_evidence.py $L/sims/* > $L/pair_evidence.tsv
```

- 樹與 spec：壓力測試樹 ×10 密度（`specs/stress_x10.yaml`，同上一個實驗）。purity 0.40，200×，100 個 SNV。
- 錯誤模型：`longbulksim` v0.2（`longbulksim/README.md`「觀測誤差」）。錯誤率 0 時輸出與 v0.1 逐位相同。〔實測〕e0 的 3 個 run 與上一個實驗的 `run_base_c4` 的 `topology_report.tsv` 逐位相同。
- PhyClone 設定同上一個實驗：`-d binomial -b 100 -n 1000 --num-chains 4 --seed 1`，outlier 關閉，C4 經 `tools/phyclone_hp.py --pairs --pair-eps`。每個 run 的 `run.log` 都有「C4 pair term on, N eligible pairs」。
- 指標：
  - `tools/summarize_hp_truth_topologies.py`：`c3_under_c4`、`c1c2_merged` 等。
  - `tools/summarize_c4_robustness.py`：`exact`、`compat`、`map_compat`、`max_wrong`。`--roles` 可只看部分角色。
- base（沒有 C4）沒有重跑。mistag 與 switch 不改 `data.tsv`；base error 0.4% 只會小幅改變 alt 計數。上一個實驗的 base 在 ×10 下，`c3_under_c4` 是 0.39–0.43。〔推論〕

## 5. 限制

- **只有一棵手寫樹、一種密度（×10）、一個 MCMC seed。** 計畫第 3 階段（×1 密度、A2＋C4、40 個隨機樹）沒有做。
- **錯誤在位點之間獨立。** 實測 base error 有長尾（1.2% 位點 > 5%）。同一位點在很多 read 上一起錯，比獨立錯誤更像真的 subclone，可能比本實驗更危險。
- **×10 密度放大了 switch 的影響。** switch rate 是每 Mb 固定的，但 ×10 的 segment 短 10 倍、SNV 密 10 倍。所以每個 switch 影響的 pair 是實測密度下的約 10 倍。〔推論〕
- **switch 依 read 中點決定，PS block 等於 segment。** 真實的 longphase 在 block 邊界重設 HP，跨 switch 的 read 依多數 het SNP 決定。
- **mistag 校正值是代理值。** 2.4% 混了 switch 與 SEQC2 假陽性。不過 mistag 對 C4 幾乎沒有影響，所以影響不大。
- **switch rate 的換算是推論。** 論文沒有說分母，HCC1395 本身也沒有 phasing 真值。
- **相容指標以角色的多數 clone 判斷。** 同一角色的 SNV 被拆到兩個 clone 時，指標看不到；只能從 clone 數看出來。
- **sw5 的 ε 0.03 比 0.01 和 0.1 都差，原因未查明。** 可能和 proposal 不知道 pair term、抽樣混合不足有關。〔推論〕

## 6. 下一步（需要決定）

1. **模型改進（處理失效模式）。**
   - (a) pair score 加入背景錯誤率：把 `same` 的 10／01 機率設成 ε_err，與「真正的 subclone 比例」用 Beta 積分分開。這能處理模式 1。
   - (b) 合格 pair 加入 PS block 與 switch 風險：遠距 pair 降權，或只用距離 < 某值的 pair。這能減輕模式 2。
   - (c) ~~檢查模式 2 是否只在 P1 合併時發生；A2＋C4 是否能避開~~：已做（第 7 節）。A2＋C4 在 `real` seed 2 仍出現模式 2（0.53）。
2. **計畫第 3 階段：** ×1 密度、A2＋C4、40 個隨機樹。
3. **位點相關錯誤：** 在模擬器加入「位點錯誤率」分布（用 `calibration/normal_snv_base_error.tsv`）。

成功門檻（第 1 節的判定）仍是 Claude 的提案，需要老闆同意。

## 7. 事後挑樹 vs in-model C4（2026-10-26）

問題：pair SNV 要不要改成像肺癌研究（Sakamoto 2022，`research/literature/papers/B04_lung_longread_phasing_2022/`）那樣，在建樹之後挑樹，而不是放進模型？

### 7.1 做法

- 在 e0、real、sw5、b03 的 12 個 sim 上，補跑 base 與 A2（沒有 C4），以及 A2＋C4（ε 0.01）。PhyClone 設定同第 4 節。
- `tools/c4_posthoc.py` 對沒有 C4 的 run 做兩種事後挑樹，不再跑 MCMC：
  - **軟（soft）**：每棵抽到的樹乘上 exp(C4 pair term)，ε 0.01。理論上和 in-model C4 的目標分布相同，但只能在已抽到的樹裡選。
  - **硬（hard）**：照肺癌研究的條數門檻判定 pair（k = 3 條、容忍 t = 1 條）。branch：n10 ≥ 3、n01 ≥ 3、n11 ≤ 1；i 在 j 之前：n11 ≥ 3、n10 ≥ 3、n01 ≤ 1。只保留違反最少的樹。
- 輸出目錄和 run 目錄格式相同（`run_*_ph_soft`、`run_*_ph_hard`），所以用同一套 summarizer。每個 run 的 ESS 與保留比例：`posthoc_weights.tsv`。完整比較：`posthoc_vs_inmodel.tsv`。
- e0 的 base 與上一個實驗的 `run_base` 逐位相同。

### 7.2 結果（12 個 run／方法）

| 方法 | 錯誤樹 > 0.5 | 直線樹 ≥ 0.1 | C1／C2 分開（合併 < 0.5） | 完整 4 clone 樹 > 0.5 |
|---|---|---|---|---|
| base | 2 | 12 | 0 | 0 |
| base＋事後軟 | **4** | 0 | 3 | 0 |
| base＋事後硬 | **5** | 1 | 2 | 0 |
| base＋C4 | 0 | 0 | 9 | 2 |
| A2 | 0 | 12 | 0 | 0 |
| A2＋事後軟 | 0 | 0 | 3 | 0 |
| A2＋事後硬 | 0 | 1 | 2 | 0 |
| A2＋C4 | 1 | 0 | 8 | 3 |

- 「錯誤樹」用第 3 節的 `max_wrong`（所有角色，扣掉遺失的 s2、s10）。
- base＋事後挑樹的錯誤樹：real s1／s2（軟與硬都是 1.00）、sw5 s3（軟 1.00）、b03 s2（軟 0.98）、e0 s3 與 b03 s3（硬 1.00）、sw5 s1（硬 1.00）。
- A2＋C4 的錯誤樹：real s2，「C3 是第二個 root」，0.53。

### 7.3 事後的有效樣本數

| | ESS（軟） | 保留比例（硬） |
|---|---|---|
| base | 1.0–10.5 | 0.025%–77% |
| A2 | 1.0–18.5 | 0.025%–99.9% |

- 24 個 run 中，硬篩選有 15 個只保留 ≤ 0.5% 的樣本（≤ 20 個）。
- 軟重加權的 ESS 都 ≤ 18.5，也就是權重集中在一到十幾個樣本上。
- 所以事後挑樹的「posterior」其實接近一個點估計。表 7.2 的 0／1 主要反映「選到的那幾個樣本對不對」。

### 7.4 解讀

- **事後挑樹能排除直線樹（P2），但其他都比 in-model 差。** 〔實測〕
  - 它在 24 個 run 中都推不出完整的 4 clone 樹。base 和 A2 幾乎沒有抽到 C1／C2 分開的樹，所以事後也挑不到。
  - base＋事後挑樹選錯的次數（4–5／12）比 base＋C4（0／12）多。
- **「C3 變成第二個 root」不是 in-model 造成的。** 〔實測〕e0 s3 沒有任何誤差，base＋事後硬篩選也選出這棵樹（1.00）。base 在這個 seed 一律把 C1／C2 合併；在 base 的樣本裡，滿足 s4×s6 分支 call 的只剩這種樹。〔推論〕這是「bulk 分不開 C1／C2」與「pair 說 C2、C3 是分支」的結構衝突。正確的解法是分開 C1／C2，而 in-model 才有機會做到。
- **A2＋事後挑樹錯得最少，但證據最弱。** 〔推論〕它的 0／12 來自很少的樣本。要用它，必須先讓 base／A2 的抽樣涵蓋 pair 支持的樹（例如更多 chain、更長的 run）。這等於把 C4 的搜尋成本移到抽樣。
- **建議：** 保留 in-model C4 作為主方法。事後硬篩選可以當報告用的檢查：列出 MAP 樹違反哪些條數過門檻的 pair（肺癌研究的做法），但不拿它來選樹。
