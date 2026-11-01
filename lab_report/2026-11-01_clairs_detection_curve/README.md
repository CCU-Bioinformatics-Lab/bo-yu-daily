# ClairS 偵測曲線：同一組 SNV 在 4 個 purity 下被叫出的比例（2026-11-01）

問題：ClairS 叫出一個 SNV 的機率，是不是只看 alt read 數（或 VAF），和 purity 無關？如果無關，就可以用一條曲線取代 diplosim 比較流程裡的硬門檻（alt ≥ 5、VAF ≥ 0.10），而且不必擔心對 HCC1395 過擬合。

標記：〔實測〕＝本實驗計算；〔推論〕＝本檔推論；〔程式〕＝讀程式得到。

狀態：只量了曲線，還沒有接進模擬。

![偵測曲線](detection_curve.png)

## 1. 結論

- **曲線和 purity 有關，一條共用曲線不夠。** 有兩個不同的效果〔實測〕：
  1. **上升段大致重疊，但 purity 越低越往右移，約 1 條 alt read。** alt = 5 時，被叫出的比例在 t10／t20／t30／t40 分別是 0.11／0.15／0.24／0.36；alt = 6 時是 0.31／0.36／0.43／0.57；alt ≥ 9 時都在 0.78–0.88 以上。
  2. **低 purity 時，高 VAF 的 SNV 反而叫不出來。** t10 從 VAF 約 0.26 開始下降，t20 約 0.35，t30 約 0.5，t40 到 0.6 仍幾乎不降。t10 中 VAF ≥ 0.26 的 1,725 個位點，只叫出 685 個（PASS），70 個是 LowQual，**970 個根本沒出現在 ClairS 的 VCF**。
- **留一驗證（用另外 3 個 purity 的曲線，預測第 4 個的 call 數）**〔實測〕：

  | | t10 | t20 | t30 | t40 |
  |---|---:|---:|---:|---:|
  | 真實 call 數（在 t50 位點內） | 7,436 | 19,234 | 25,940 | 29,264 |
  | 留一預測（依 alt 數） | 9,467（+27%） | 19,914（+4%） | 25,024（−4%） | 26,958（−8%） |
  | 只看 VAF < 0.25 的位點：真實 | 6,585 | 11,103 | 10,161 | 7,566 |
  | 只看 VAF < 0.25 的位點：留一預測 | 7,580（+15%） | 11,223（+1%） | 9,779（−4%） | 7,135（−6%） |

  中間的 purity（t20、t30）誤差在 ±4% 內；兩端誤差較大，t10 主要來自高 VAF 位點的掉落。
- **高 VAF 掉落的原因還不知道**〔推論〕。970 個位點根本沒進 ClairS 的候選，表示是在候選篩選階段就被排除，不是模型打分數太低。可能和 ClairS 怎麼處理「VAF 高到不像該 purity 的 somatic」有關，例如被當成 germline。這要讀 ClairS 的程式才能確認，目前沒讀。
- **這些位點在 t10 為什麼 VAF 能到 0.26 以上，也還沒查。** purity 0.14 時，要所有拷貝都帶突變、CN 約 4 以上，VAF 才到得了 0.26〔推論，公式〕。也可能是 t50 call 集合中的假陽性（例如 reference 重複區）。

## 2. 資料與做法

- 位點：`t50_n00` 的 31,595 個 ClairS PASS ∩ HC SNV，當作真 SNV。低 purity 的 call 有 99% 以上落在這組位點內（t40 29,264／29,508、t30 25,940／26,058、t20 19,234／19,277、t10 7,436／7,452）〔實測〕。
- 每個 subsample：在它的 haplotag CRAM 上 pileup 這 31,595 個位點（每個約 3 分鐘）。「叫出」＝該位點在該 subsample 自己的 ClairS PASS ∩ HC 集合裡。

```bash
D=lab_report/2026-11-01_clairs_detection_curve
for p in t40_n10 t30_n20 t20_n30 t10_n40; do
  python3 -I tools/diplosim_ppc_hcc1395.py real $D/$p lab_report/2026-10-30_diplosim_ppc_hcc1395/tables/clairs_hc_sites.tsv \
    /big8_disk/boyu114/hcc1395_hp_split/tagged_$p.cram
done
python3 tools/plot_clairs_detection_curve.py $D lab_report/2026-10-31_diplosim_purity_holdout
```

輸出：`detection_by_alt.tsv`、`detection_by_vaf.tsv`（每格的位點數、叫出數、比例）、`detection_curve.png`。

## 3. 限制

- t50 的 call 集合不是真值：ClairS recall 約 0.74，漏掉的多半是低 VAF 的 subclonal SNV；也含少數假陽性。
- 曲線只代表 ClairS v0.4.1 在 ONT HCC1395 上的表現。
- 這裡的 alt 數是我們自己的 pileup（MAPQ ≥ 20、BQ ≥ 7），不是 ClairS 內部看到的數字。

## 4. 方案 A 調查：高 VAF 位點為什麼叫不出來（進行中，2026-11-01）

- **ClairS 的候選篩選規則**〔程式，ClairS v0.4.1 `src/extract_pair_candidates.py:443-450`，`shared/param.py:38,120`〕：normal AF ≥ 0.05，而且 tumor AF < 6 × normal AF，就把這個位點從候選中刪掉。
- **t10 的 970 個缺席位點中，952 個不在 ClairS 的候選檔裡**〔實測，`tmp/candidates/`〕。
- **這些位點在 normal（t00_n25）中幾乎都有 alt**〔實測〕：normal AF ≥ 0.05 的比例是 0.99，符合上面刪除規則的比例是 0.98；在 t50 的 VAF 中位數是 0.96，也就是 LOH 後全帶突變的位點。被叫出的低 VAF 位點只有 0.02 符合。
- **normal 的 alt 比例隨 tumor VAF 增加**〔實測〕：t50 VAF 0.1 時是 0.003，0.5 時是 0.006，0.9 以上時是 0.021。這符合 normal 樣本混到約 2% tumor DNA〔推論〕。
- **初步解讀**〔推論〕：低 purity 時 tumor AF 小，「tumor AF ≥ 6 × normal AF」比較難達到。所以 normal 裡有幾條 alt read 的高 VAF 位點，會被當成 germline 而刪除。這是 ClairS 的規則加上 normal 混到 tumor 造成的，和 diplosim 的生成機制無關。
- **ClairS 用的 normal 和 `t00_n25` 是同一批 read**〔實測〕。`normal_25x.bam` 已經不在原路徑，只剩它的 mosdepth 結果（`/big8_disk/mingen112/test_data/HCC1395/ONT/subsample_bam/normal_25x/mosdepth/`）。在相同的過濾條件下（排除 flag 1796、MAPQ ≥ 0、含 deletion），對 `t00_n25` 算每條染色體的總鹼基數：chr21 兩者都是 1,206,595,697，chr1 兩者都是 7,163,965,232，完全相同。如果是兩次獨立的 subsample，總鹼基數會差到數十萬以上〔推論〕。`t00_n25` 的 header 記錄它來自 `HCC1395BL.cram`（SRR25005625）的 `--subsample 0.5556 --subsample-seed 0`。所以上面用 `t00_n25` 分析 normal alt 的結果，可以直接代表 ClairS 看到的 normal。
- **還沒做**：如果要在模擬中重現，要讓模擬也產生 normal 樣本的 alt 數，並套用同一條規則。
