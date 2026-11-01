# diplosim φ：從純 normal 樣本直接量測（2026-11-01）

問題：diplosim 的 depth overdispersion φ 能不能不靠模擬試誤，直接從真實資料量出來？背景：purity holdout 中，φ = 0.03（在 `t50_n00` 上選的）讓低 purity 的 depth 變異÷平均（VMR）高估最多 +0.50（`lab_report/2026-11-01_diplosim_split_alt_mistag/`）。

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論；〔程式〕＝讀程式得到。

狀態：**量測完成，沒有選估計式，也沒有跑模擬。** 使用者 11-01 決定不再追求單一 φ，改成「旋鈕從範圍抽樣，真實統計量落在模擬區間內即可」（方案 3）。本檔的量測保留，可以拿來定 φ 範圍的依據（0.006–0.025）。

## 1. 結論

- **估出的 φ 取決於估計式，範圍 0.006–0.025**〔實測〕。主因是少數極高 depth 的位點。
  | 估計式 | φ |
  |---|---:|
  | 動差（全部位點，等於 PPC 的 VMR 定義） | 0.025（95% bootstrap 0.020–0.031） |
  | IQR（穩健，看中間 50%） | 0.016 |
  | 去掉最極端 0.5% 位點 | 0.009 |
  | 去掉最極端 1% 位點 | 0.006 |
- **極端位點是 reference 上的重複區**〔實測〕：例如 chr21:10.46 Mb（centromere 旁）、chr4:190.1 Mb（telomere 旁）、chr1:16.6 Mb。normal depth 達 4–7 倍，tumor 也同樣偏高。最極端的 1% 位點貢獻了 26% 的 variance。
- **這些位點也解釋了一部分「真實 VMR 隨 purity 下降」**〔實測〕：它們的 VAF 偏低（多出的拷貝帶 ref），所以 purity 降低後會被 VAF ≥ 0.10 濾掉。normal depth ≥ 2.5 倍中位數的 34 個位點，在 t50 留下 34 個、在 t10 留下 0 個。但它們只占 t50 VMR 的 0.24，不是主因。
- diplosim 的 Gamma 模型只描述「整體一致的雜訊」，不描述這種重複區的長尾〔程式，`diplosim/src/sequencing.rs:154`〕。所以 φ 要用哪個估計式，取決於要不要讓 φ 去吸收長尾。

## 2. 資料與做法

- normal：`/big8_disk/data/HCC1395/ONT/subsample/t00_n25/HCC1395_t00_n25.cram`（0× tumor、25× normal）。normal 沒有 CN 變化，所以 VMR = 1 + φ × 平均 depth〔程式＋推論〕。
- 位點：`t50_n00` 的 31,595 個 ClairS PASS ∩ HC SNV（`lab_report/2026-10-30_diplosim_ppc_hcc1395/tables/clairs_hc_sites.tsv`）。和 tumor 用同一組位點、同一組 pileup 過濾條件。

```bash
D=lab_report/2026-11-01_diplosim_phi_from_normal
# 1. pileup（約 3 分鐘），沿用 tumor 的流程，只換 CRAM
python3 -I tools/diplosim_ppc_hcc1395.py real $D lab_report/2026-10-30_diplosim_ppc_hcc1395/tables/clairs_hc_sites.tsv \
  /big8_disk/data/HCC1395/ONT/subsample/t00_n25/HCC1395_t00_n25.cram
# 2. 估計 φ = (VMR − 1) ÷ 平均 depth
python3 -I tools/diplosim_estimate_knobs.py phi $D/tables/real_per_snv.tsv > $D/tables/phi_estimate.tsv
```

`tools/diplosim_estimate_knobs.py` 是新寫的：一個旋鈕一個子命令，只讀真實資料，不跑模擬。目前只有 `phi`。

## 3. 結果

normal 的 depth：平均 25.1，分位數 0.1%／1%／10%／50%／90%／99%／99.9% = 7／12／18／25／33／40／64，沒有 depth 0 的位點〔實測〕。

每條染色體的 VMR 大多是 1.2–1.5；chr21 11.9、chr16 2.8、chr4 2.1、chr14 2.0，都和上面的重複區有關〔實測〕。

各 purity 去掉這 34 個高 depth 位點後的真實 VMR〔實測〕：

| | t50 | t40 | t30 | t20 | t10 |
|---|---:|---:|---:|---:|---:|
| 留下的高 depth 位點 | 34 | 21 | 6 | 3 | 0 |
| VMR | 9.41 | 6.59 | 4.18 | 2.57 | 1.68 |
| VMR（去掉後） | 9.17 | 6.36 | 4.13 | 2.55 | 1.68 |

## 4. 用 φ 預測各 purity 的相對差距（推論，還沒實跑）

做法：從 11-01 那一輪（φ = 0.03）的模擬 VMR 扣掉 1 + 0.03 × depth，得到模擬的 CN 部分；再加回 1 + φ × depth。depth 用模擬的中位數（48、48、50、51、52）。

| φ | t50 | t40 | t30 | t20 | t10 |
|---:|---:|---:|---:|---:|---:|
| 0.03（目前） | +0.02 | +0.05 | +0.17 | +0.33 | +0.50 |
| 0.025（動差） | 約 0.00 | 約 +0.01 | 約 +0.11 | 約 +0.23 | 約 +0.35 |
| 0.016（IQR） | 約 −0.05 | 約 −0.06 | 約 0.00 | 約 +0.06 | 約 +0.07 |
| 0.009（去掉 0.5%） | 約 −0.08 | 約 −0.11 | 約 −0.09 | 約 −0.08 | 約 −0.15 |

## 5. 估計式的候選（沒有採用）

- A：IQR 穩健估計，φ = 0.016。
- B：NB 加離群混合的最大概似擬合。
- C：全部位點的動差估計，φ = 0.025。

使用者改走方案 3（抽樣範圍），所以三者都沒有採用。

## 6. 副觀察

normal 在這些 somatic SNV 位點上的 alt 比例是 0.87%，有 4.5% 的位點 alt ≥ 2〔實測〕。之後估計 `base_error` 時要先查清楚：這是定序錯誤、ClairS 的假陽性位點，還是兩者都有。

## 7. 限制

- normal（HCC1395BL）和 tumor 是不同細胞株、不同的 DNA 萃取，library 的雜訊可能不同〔推論〕。
- normal 只有 25×，IQR 在整數 depth 上很粗（四分位數是 21 和 29）。
- 位點是 tumor 的 SNV 位點；chrX 沒有位點進入 HC 交集〔實測〕。
