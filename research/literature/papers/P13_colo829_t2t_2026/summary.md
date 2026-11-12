# P13｜COLO829 近 T2T：用配對正常 COLO829BL 的 diploid 組裝看黑色素瘤的體細胞變異；作者沒有比較兩條 haplotype 的 SNV 數量，也沒有親源

## 論文與結論

Sohn MH, Dubocanin D, Vollger MR, …, Bennett JT, Stergachis AB. **A telomere-to-telomere map of somatic mutation burden and functional impact in a cancer.** *Cell* 189(21):6630 (2026). DOI：[10.1016/j.cell.2026.09.033](https://doi.org/10.1016/j.cell.2026.09.033)。PMCID PMC13722029；Cell 正式版 CC BY，PMC 上的作者稿是 TDM 授權。作者 44 位（依 JATS contrib 計數）。

- 同儕審查：是（*Cell*）。
- 讀取層級：全文（PMC JATS XML 轉文字）；補充資料未下載，Figure S5、S6 沒看到。
- 查核日期：2026-11-11。

**組裝的是誰：** 配對正常的淋巴母細胞株 COLO829BL，不是癌細胞 COLO829。癌細胞的 read 再對到這份組裝上。〔論文〕Results 第一節（11-11 會中已更正）

**作者回答的問題：** 有了同一個人近乎完整的 diploid 組裝，傳統參考看不到的區域（著絲點、端粒、衛星重複）裡，癌細胞有多少體細胞變異、怎麼產生、有什麼功能影響。〔論文〕SUMMARY、INTRODUCTION

**作者的主要結論：**〔論文〕

1. 組裝：5.92 Gb，N50 135 Mb，QV 62.16，98.6% 組裝正確；**12 條染色體 T2T**，46 個著絲點都有序列；比 GRCh38 多 342.87 Mb。
2. 44,795 個 sSNV、828 個 sDNV；held-out 的 UL-ONT 驗證 99.9%。15.6% 的 sSNV 落在 GRCh38 缺少的序列。突變譜以 UV 為主，代表多數是成癌前皮膚細胞累積的，不是培養產生的。
3. **多數 sSNV 的 haploid VAF ≈ 1.0，也就是固定在兩條 haplotype 的其中一條。** chr1q hap1 有 38% 的 sSNV hVAF ≈ 0.5，作者用它排時間：hVAF 1.0 的在 t(1;3) 增加之前（早期 clonal），0.5 的在之後（晚期 clonal），而且晚期多了 SBS38。
4. 衛星重複的 sSNV 是非重複區的 3.79 倍，HSat2 達 7.78 倍；控制序列可突變性後仍偏高。
5. 著絲點 kinetochore 結合區（CDR）是 sSNV、sSV 與染色體臂異常斷點的熱點；CDR 的表觀遺傳重塑只在癌中看到。
6. 端粒單分子分析重建出「端粒縮短 → 端粒酶延長」的過程；拷貝數改變的區域伴隨大量染色質表觀突變。

| 查核軸 | 結果 |
|---|---|
| 樣本 | 一位病人：COLO829 黑色素瘤細胞株（兩個 passage）與同一人的 COLO829BL |
| 定序資料 | COLO829BL：Fiber-seq HiFi 186 Gb、UL-ONT 186 Gb、Hi-C 126 Gb；COLO829：HiFi／Fiber-seq、UL-ONT、ONT、Element、Illumina |
| 親代資料與定相方法 | **沒有親代資料**（全文搜 maternal／paternal 0 筆）。Verkko v2.12 組裝，用 Hi-C 定相；hap1／hap2 是組裝編號。性染色體例外：hap1 帶 chrX、hap2 帶 chrY（預印本 Table 1），病人是男性 |
| SNV 怎麼放到 haplotype | DeepVariant 分別呼叫兩個 COLO829 passage 與 COLO829BL，留兩個 passage 都有、COLO829BL 沒有的；**刪掉落在 haploid deletion（該條 hCN＝0）座標上的 SNV**，這些是另一條完整 haplotype 的 read 錯放造成的；兩條都被呼叫的，先用 UL-ONT、再用 ONT 的支持 read 做 Fisher 檢定（p < 0.01）指定一條，仍不明的標記 |
| 突變類型 | sSNV、sDNV、sSV、拷貝數、端粒、甲基化／染色質 |
| 對本問題（SNV 落哪條）的方向 | 作者**沒有**比較兩條 haplotype 的 sSNV 總數或比例（主文；補充資料未讀） |
| 證據類型 | 公開 VCF（DSA 座標）可再分析；程式公開 |

## 對本研究的意義

- **作者沒有回答「SNV 偏向哪條 HP」，也沒有親源。** 本 repo 的 COLO829 比例是再分析：扣掉 LOH 後兩條接近各半（比值 1.004）；同源對的密度占比接近 50%。〔repo〕`lab_report/2026-11-06_colo829_hap_snv_ratio/`、`lab_report/2026-11-10_colo829_hp_depth_snv/`
- **作者的 hVAF 時序是「累積 vs 發生時間」的實例（O4）。** 同一條 haplotype 上，hVAF 可以分出 CN 增加前、後的 SNV。這支持 11-10 的推論「多數 SNV 在拷貝數變化之前」，但只有 chr1q 一處是作者直接分析的。〔論文〕〔repo〕
- **作者在呼叫時就刪掉 deletion 區段的 SNV。** 刪的是丟失那條 haplotype 座標上的錯放 call，完整那條的 SNV 保留。所以公開 VCF 在丟失區段一定是 0 個（公開 VCF 沒有 `CN=DEL` 紀錄〔實測〕），算兩條比例前要扣掉這些區段。〔論文〕Methods「Diploid variant calling」；〔推論〕
- 這是**一位病人、一株細胞**，不能單獨決定模擬器參數。〔推論〕（同 `CLAUDE.md`：COLO829 實驗 11-06 結束，讀論文不重開實驗）
- 衛星與 CDR 的 SNV 富集是位置效應，和 HP 選擇無關；第一階段 SNV-only 模擬不需要。〔推論〕

## 深讀結果（2026-11-12）

詳細筆記：`deep_read_main.md`（主文逐節）、`deep_read_supp_code.md`（補充資料、程式、公開 VCF 欄位）。預印本 v1 的 9 個補充 PDF 已下載到本機 `supp/`（不進 repo）。Cell 版 Document S1 沒拿到：PMC 回瀏覽器驗證頁，要手動下載。

**作者在解決什麼問題：** GRCh38 缺少或對不準著絲點、端粒、衛星重複，所以過去的體細胞變異清單漏掉這些區域。作者先替配對正常的 COLO829BL 做近 T2T 的 diploid 組裝，再把癌細胞的 read 對上去，看這些區域有多少體細胞變異、怎麼產生、有什麼功能影響。問題是「**完整的突變地圖與功能**」，**不是**「SNV 偏向哪一條 haplotype」。〔論文〕SUMMARY、INTRODUCTION

**和 HP 比例的關係：**
- **直接回答：沒有。** Results 共 10 節，沒有一節比較兩條 haplotype 的 sSNV 數或比例，也沒有分析相鄰 SNV 是否獨立、親源或 chrX。程式 repo 也沒找到這類計算。〔論文〕〔程式〕
- **間接有用：**
  - chr1q hVAF 時序：hap1 有 38% 的 sSNV hVAF ≈ 0.5，作者據此把 SNV 分成 t(1;3) 增加之前與之後。這回答的是「何時發生」，不是「落在哪條」，但它是「累積比例會被 CN 改變」（O4）的實例。〔論文〕Results「Genome-wide map of COLO829 sSNVs and their mutational timing」
  - 作者把「一個體細胞變異只在一條 haplotype 上」當成前提，用另一條當功能分析的對照（29,189 個落在兩條都保留的區域）。〔論文〕Results「Functional impact」
  - t(1;3) 斷點旁有 23 個 kataegis 群聚突變，但作者沒寫它們在哪條 haplotype。〔論文〕

**程式和 Methods 不一致的地方：**〔程式〕`StergachisLab/T2T-COLO829BLT-Manuscript` commit `4a9a42e`
- DEL 門檻：Methods 寫「≤ –0.415 (log2(0.5))」，但 –0.415 是 log2(0.75)；程式用 –1，也就是 log2(0.5)（`hCN/CBS_DNAcopy.qmd:281`）。另外有三段 DEL 是手動指定的，都在 hap2（`:294-312`）。
- ONT、UL-ONT 都分不出的 231 對，兩筆都保留，公開 VCF 沒有欄位標出是哪些。這會讓兩條的比例略微偏向 1:1，影響上限約 1%。〔推論〕

**對本 repo 再分析的影響：**
- 11-06、11-10 用的欄位（VAF＝hVAF、INFO/CN＝該條 hCN）和作者的定義一致。
- **11-06 的全基因組合計原本沒有排除性染色體，2026-11-12 已重算。** 只算體染色體：hap1 9.24、hap2 9.31 個／Mb，比值 0.993（95% CI 0.974–1.012），結論不變。原本是 9.34 比 9.31（1.004）。成對比較不受影響。〔實測〕`lab_report/2026-11-06_colo829_hap_snv_ratio/haplotype_totals_autosomes.tsv`
