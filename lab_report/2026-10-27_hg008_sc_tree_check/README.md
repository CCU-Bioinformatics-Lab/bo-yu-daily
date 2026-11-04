# HG008 clone 樹能不能當單細胞證據樹：用 119 顆 PTA 單細胞檢查（2026-10-27）

> **2026-11-04 註記：** 本實驗的輸入 `2026-10-27_hg008_clone_tree_hp/`（clone 樹與 `tables/snv_patterns.tsv`、`bulk_hp.tsv`）已刪除，未進 git，無法取回。文中引用保留原文；重跑指令已無法執行。

問題：`2026-10-27_hg008_clone_tree_hp/` 的 clone 樹，是用 8 株單細胞衍生 clone（PacBio）排出來的。逐顆單細胞看時，這棵樹站得住嗎？能不能把它當成「有單細胞證據的真實樹」？

標記：〔實測〕＝本次用公開資料算出；〔推論〕＝本檔的推論。

## 1. 結論

**部分可以。** truncal 枝與兩個共享 clade 有單細胞直接支持，而且單細胞比例和 bulk CCF 對得上。各 clone 的 private 枝無法用單細胞證實。樹還要補兩處：3E4 是最早分出的一支；chr10 有在多個 lineage 重複發生的 LOH。

| clone 樹的枝 | 單細胞結果（119 顆，第 23 代） | 判定 |
|---|---|---|
| truncal（7,970 個 SNV） | 119／119 顆都帶；偵測靈敏度 0.69–0.93 | **支持** 〔實測〕 |
| {SC14, SC28}（145 個） | 16 顆帶（13%）；bulk CCF 約 0.14 | **支持**，比例吻合 〔實測〕 |
| {SC9, SC14, SC24, SC28}（22 個，原樹沒畫成節點） | 48 顆帶（40%）；bulk VAF 中位 0.187（CCF 約 0.37） | **新 clade**；{SC14, SC28} 的 16 顆全在這 48 顆內，巢狀一致 〔實測〕 |
| 「只缺 3E4」（411 個） | 8 顆細胞缺其中約 300 個，散在 20 條染色體；這 8 顆保留 3E4 自己 deletion 區（chr10、chr11）的 SNV | **真的分枝**：3E4 那一支最早分出，有 8 顆姊妹細胞（7%） 〔實測〕；原 README 的推論成立 |
| {2D6, 2E6}（59 個） | 16 顆細胞帶其中 11 個（呼叫率 ≥ 0.88），其餘 48 個幾乎沒有 | **部分支持**：枝的前段在第 23 代仍有 16 顆後代，後段只在 2D6、2E6 的祖先 〔實測＋推論〕 |
| 8 條 private 枝（464–1,157 個） | 沒有任何細胞帶 > 50%。最高是 3E4 private 在 2 顆細胞約 0.2–0.45（部分帶），其餘 7 條 ≤ 0.18 | **無法證實** 〔實測〕。〔推論〕多數 private SNV 在分離後的培養中才產生，或創始細胞的 lineage 在第 23 代已極少 |
| 「只缺 2E6」（82 個，71 個在 chr10） | 44 顆細胞缺全部 chr10 SNV，而且這段 germline het 少 93% | **不是分枝，是 chr10 LOH**，見 §4.3 〔實測〕 |

**對簡報的意義：**
- 能當「單細胞證據樹」的部分：truncal → {SC9, SC14, SC24, SC28} → {SC14, SC28}，以及 3E4 那一支早期分枝。
- 第 8 頁的 HP 拆分（{SC14, SC28} HP1 24：HP2 27）可以加註「16／119 顆單細胞帶這條枝」。
- chr10 是 mirrored LOH 的實例：兩群細胞在同一段失去不同的 haplotype（§4.3）。只看 copy number 時兩群都是 LOH；要靠 haplotype 才分得開。這可以支持「③ 突變遺失」和「HP 才看得到的事件」。

## 2. 資料

- 單細胞：GIAB HG008-T 119 顆 BioSkryb ResolveDNA（PTA）單細胞，Ultima UG100 300 bp 單端，中位約 23–30×。只用 `*.vep.PASS_filtered.vcf.gz`（每顆約 370 萬筆，含 germline）。批次 0823p23，與 bulk ONT 同代。位置：`/big8_disk/boyu114/benchmark_data/GIAB/HG008/single_cell_vcf/vcf/`。
- clone 樹 SNV：`lab_report/2026-10-27_hg008_clone_tree_hp/tables/snv_patterns.tsv`（15,431 個 chr1–22、X、Y 上的 SNV）。

## 3. 做法

```bash
python3 -I tools/hg008_sc_tree_check.py \
  lab_report/2026-10-27_hg008_clone_tree_hp/tables/snv_patterns.tsv \
  /big8_disk/boyu114/benchmark_data/GIAB/HG008/single_cell_vcf/vcf \
  lab_report/2026-10-27_hg008_sc_tree_check/tables 8      # 8 process，約 1.3 分鐘
```

1. 每個 clone 樹 SNV，查每顆細胞的 PASS VCF 有沒有呼叫到同一個 ALT（GT 不是 0/0）。
2. 每顆細胞的 truncal 呼叫率＝偵測靈敏度（PTA allele dropout 與深度造成的漏呼叫）。
3. 每條枝：相對呼叫率＝該枝呼叫率 ÷ truncal 呼叫率。約 1 表示細胞帶這條枝，約 0 表示不帶。以 0.5 為界。
4. 分群後，對特定 SNV 群看染色體分佈與逐 SNV 的呼叫比例（分析在對話中執行，未存成腳本）。
5. chr10 LOH：每顆細胞在 chr10:1,240,656–39,265,327（71 個 chr10 SNV 的範圍，38 Mb）數 germline het SNP（`bcftools view -g het -v snps`）。結果在 `tables/chr10_germline_het.tsv`。

## 4. 結果

表格在 [`tables/`](tables/)：`sc_branch_recall.tsv`（細胞 × 枝）、`sc_calls.tsv.gz`（每個呼叫到的樹 SNV，含 alt read 與 depth）、`chr10_germline_het.tsv`。

### 4.1 背景值

private 枝與兩兩組合的相對呼叫率，多數細胞在 0.02–0.08。這是假陽性與共享 PTA 錯誤的背景。〔推論〕

### 4.2 細胞分群（相對呼叫率 > 0.5）

| 群 | 細胞數 | 備註 |
|---|---:|---|
| {SC9, SC14, SC24, SC28} clade | 48 | 其中 16 顆也帶 {SC14, SC28}；不帶此 clade 的細胞，{SC14, SC28} 都 ≤ 0.02 |
| 3E4 姊妹支 | 8 | 和上一群、{2D6, 2E6} 前段群都不重疊 |
| {2D6, 2E6} 前段（11 個 SNV） | 16 | 和 chr10 失去 SNV 的 44 顆不重疊 |

{SC14, SC28} 的 16 顆中，有 2 顆（SC321、SC268）屬於 chr10 失去 SNV 的那群，見 4.3。

### 4.3 chr10：同一段，不同 lineage 失去不同的 haplotype

| 細胞 | 數量 | 71 個 chr10 SNV | chr10 這段 germline het（中位） |
|---|---:|---|---:|
| 失去 SNV 那條 haplotype | 44（42 顆不在 {SC9, SC14, SC24, SC28} 群；2 顆在 {SC14, SC28}） | 全部沒有 | 2,110 |
| 失去另一條 haplotype | 24（20 顆在 {SC9, SC14, SC24, SC28} 群） | 保留 | < 10,000（1,569–6,211） |
| 沒有 LOH | 51 | 保留 | 約 29,700 |

- clone 層級：2E6 也缺這 71 個 SNV（原 README 記為 2E6 的 deletion），2D6 沒缺。
- 〔推論〕失去 SNV 的那群跨越 {SC14, SC28} 與非該群的細胞，單一起源解釋不了，所以 chr10 LOH 至少獨立發生兩次以上，而且失去的 haplotype 不同（mirrored）。只看 copy number，兩群都是 LOH；要看 SNV 或 haplotype 才分得開。
- 〔推論〕區段邊界只用 71 個 SNV 的範圍與 germline het 總數判斷。兩群的 LOH 區段可能不完全相同。

## 5. 限制

- **VCF 只有 PASS 呼叫。** 沒呼叫到不等於沒有。相對呼叫率修正了整體靈敏度，但個別位點的 dropout 沒有修正。要逐點確認「沒有」需要 CRAM（119 個共 4.8 TB，未下載）。
- **PTA 擴增錯誤可能在細胞間共享**，造成低背景值（約 0.05）。
- **單細胞是第 23 代，clone 是第 14、19 代。** 單細胞看到的比例是第 23 代的族群組成。
- **chr10 LOH 用 germline het 數量判斷**，沒有做 copy number，分不出 deletion（1+0）和 cnLOH（2+0）。
- **{2D6, 2E6} 前段的 11 個 SNV 是逐 SNV 篩選的結果**，沒有逐顆細胞確認 chr2 gain。

## 6. 補充：7 株共同枝的 HP（2026-10-27）

「只缺 3E4」411 個 SNV 拆開後，在 SC14 PURPLE 為 1+1 的區域用 bulk ONT 判 haplotype（`2026-10-27_hg008_clone_tree_hp/tables/bulk_hp.tsv`）：

| SNV 群 | HP1 | HP2 | 判不出 |
|---|---:|---:|---:|
| 真分枝 303 個（3E4 姊妹細胞也沒有） | 54 | 68 | 9 |
| 3E4 deletion 遺失 108 個（姊妹細胞有） | 0 | 101 | 5 |

〔實測〕真分枝兩條 HP 都有；deletion 遺失的全在同一條 HP，符合單一 haplotype deletion。原 `branch_bulk_hp.tsv` 的 53：166 是兩群混在一起的結果。分析在對話中執行，未存成腳本。
