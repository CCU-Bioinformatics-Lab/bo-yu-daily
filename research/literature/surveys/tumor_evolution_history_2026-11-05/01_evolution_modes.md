# 腫瘤演化模式與樹形

## 結論

- **共識：** 多數腫瘤有可測到的 subclone。PCAWG 的 informative 樣本有 95.1% 測到 subclonal 擴張（E1-10）。這是單樣本 short read 的保守下限。
- **共識：** 沒有一種樹形適用所有癌別。AML 的 linear／branching 約各半（E1-14）。ccRCC 從單克隆到高度分支都有（E1-05）。
- **爭議：** VAF 的 1/f 尾巴不能單獨證明中性。Williams 2016 的 R2 檢定被實證否定其充分性（E1-02），原作者後來也改用貝氏模型（E1-04）。有爭議的是「中性腫瘤有多少」，不是「尾巴存不存在」：受選腫瘤也有 1/f 尾巴（E1-04、E1-09）。
- **爭議：** TNBC 的 CNA 是早期爆發（E1-11），但爆發後仍持續多樣化（E1-12）。Big Bang 只在大腸癌有 gland 層級的直接資料（E1-03）；Sun 2017 顯示肺與腦的選擇訊號較強（E1-13）。
- **證據不足：** 本批 15 篇全部不是 long read（對全文檢索 `long.read|nanopore|PacBio`，0 篇命中）。單一 bulk 區域能重建多少真實樹，只有模擬與間接證據（E1-08、E1-13）。
- **parent-of-origin：** 本批沒有分析腫瘤演化與父系／母系來源的關係。全文只有 E1-10、E1-12 用到 parental allele，它們只分開兩條 homolog，沒有指認父或母。

## 搜尋範圍

- **來源：** NCBI PMC（`fetch_paper.py`、BioC API）、WebSearch、WebFetch（bioRxiv）、`research/index.md`。
- **關鍵字：** neutral tumor evolution、critique、1/f、subclonal selection、punctuated copy number、Big Bang、spatial structure、linear branching、site frequency spectrum、branching process。
- **期間：** 發表年 2015–2022。搜尋日期 2026-11-05。
- **讀法：** 15 篇都取得全文，但我用關鍵句檢索閱讀，沒有逐段通讀。Figure 與 Supplement 不在文字檔內。
- **沒取得全文：**
  - McDonald 2018 與 Balaparya & De 2018：在 WebSearch 兩次查詢中沒取得原文，只透過 E1-23 的引述得知 McDonald 的論點。
  - Heide 2018 回覆：只讀到 bioRxiv 預印本的 WebFetch 擷取片段（`E1-17`），未逐字核對。
  - Ling 2015（HCC）：NCBI 查詢失敗，未讀。
  - Gunnarsson 2021、Bozic 2016：未讀全文，只當線索列在「未解問題」。

## 假設總表

| 假設 | 預測 | 支持 | 反對 | 適用範圍 | 狀態 |
|---|---|---|---|---|---|
| Linear（序列 sweep） | Subclone 為 parent-child；ITH 在 sweep 之間短暫 | E1-14（AML 55%） | E1-10：實體瘤 sibling 多於 parent-child；E1-03 未見 sweep | AML 有單細胞直接資料；只看 driver panel | 依癌別而定 |
| Branching | Sibling subclone 共存 | E1-10、E1-05、E1-14（45%）、E1-07 | E1-13：部分分支可能是取樣造成；E1-08 | 多數實體瘤；bulk 推得的分支有偏差 | 共識（比例未定） |
| 中性（1/f） | 累積 VAF 隨 1/f 線性 | E1-01、E1-03 | E1-02、E1-04（TRACERx 97% 非中性）、E1-07 | 大腸、胃爭議最多；僅指 subclonal 且可測頻段 | 爭議 |
| Big Bang | 單次擴張、早期 private 變異遍布全腫瘤、無 sweep | E1-03 | E1-13：只適用部分癌別；E1-04：有早期受選 subclone | 大腸癌與大型腺瘤 | 爭議（適用範圍窄） |
| Punctuated CNA（PCNE） | CNA 早期爆發，無中間態，之後穩定 | E1-11 | E1-12：爆發後持續演化 | TNBC；CNA，不是 SNV | 爆發有資料；「停滯」有爭議 |
| 空間結構決定模式 | Gland、擴散、邊界生長產生不同樹形 | E1-07、E1-06、E1-08 | 缺直接的病人長期追蹤 | 模型為主；參數依賴作者設定 | 證據不足（模型結果） |
| 中性尾巴在每個 clone 內都有 | VAF＝clone 峰＋尾巴；尾巴不是單系 | E1-09、E1-04、E1-23 | 尚未在這批找到正面反駁；空間生長會改變尾巴（E1-08） | 高深度 WGS | 接近共識（well-mixed 模型下） |

### 生成模型預測的 SNV 頻譜

| 模型 | 預測 | 來源 | 層級 |
|---|---|---|---|
| 指數生長、中性、well-mixed | 累積 M(f)∝1/f；非累積約 1/f2 | E1-01、E1-04 | 模型 |
| 指數生長＋一個受選 subclone | clonal 峰、subclonal 峰＋兩條重疊尾巴 | E1-04、E1-09 | 模型 |
| 兩型 branching process | 每型內部都遵循 1/f；足夠資料可分辨中性與此一選擇形式 | E1-23 | 數學證明，限特定選擇形式 |
| 中性邊界生長 | f>5% 呈 1/f2 形式，突變負荷高於 well-mixed | E1-08 | 模擬 |
| Stochastic 與 deterministic 比較 | Stochastic branching process 下 R2>0.98 非必要也非充分 | E1-02 | 模擬 |

注意：E1-04 的 1/f2 是非累積分布，E1-08 寫的 1/f2 是 M(f) 的 scaling。兩者不同，不要混用。〔推論〕

## 論文卡片

### E1-01 Williams 2016, Nat Genet — 10.1038/ng.3489
- **資料：** 904 例、14 癌別；含 TCGA exome 819 例；bulk；short read；單區域為主；無真值。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 符合 1/f 的腫瘤「在中性動態下生長」。
- **演化假設：** 指數生長、新突變不改適應度，預測累積 VAF 呈 1/f。檢定用 VAF 0.12–0.24、R2≥0.98。
- **真實結論：** 323/904 符合（摘要）。CRC 7 例加 TCGA 101 例中 38/108（35.1%）符合（Results）。胃、肺、膀胱、子宮頸、大腸較多；腎、黑色素瘤、胰、甲狀腺、GBM 擬合差。這裡量到的是「曲線擬合」，不是「中性」。
- **限制與反證：** E1-02。exome 突變數少，作者也提到深度可能造成誤判。
- **支持哪一層（N3）：** 觀測特徵（VAF 形狀）。它不支持演化路徑。
- **對 diplosim 的意義〔推論〕：** diplosim 的邊沒有對應時間或族群大小，沒有產生低頻尾巴的機制。屬真值層。

### E1-02 Tarabichi 2018, Nat Genet — 10.1038/s41588-018-0258-x
- **資料：** 重新分析 TCGA exome；分支過程模擬；short read；非新資料。
- **讀取層級：** 全文（短 letter）。
- **用了建樹工具：** 無。
- **觀點：** R2>0.98 不足以判定中性；Williams 法會過度判定中性。
- **演化假設：** 檢驗 Williams 模型的假設：同步分裂、固定死亡率、固定突變與分裂率。
- **真實結論：** 真正拒絕中性只有約 11% 的模擬；非中性腫瘤有 53.5% 被誤判；AUC 0.42（各 1,919 例）。37% 腫瘤有 WGD，clonal 峰落在 VAF 0.25 或以下。dN/dS 在被判中性的腫瘤也測到 subclonal 正選擇。
- **限制與反證：** 回覆見 E1-17（Heide，預印本片段）：原作者主張多數癌症並非中性。E1-23 主張足夠資料下 SFS 仍可分辨一種選擇形式。dN/dS 是群體層級檢定，不能判斷單一腫瘤。〔推論〕
- **支持哪一層（N3）：** 否定「觀測特徵能推演化路徑」。
- **對 diplosim 的意義〔推論〕：** 這是 N3 的直接例子：VAF 形狀相同，過程可以不同。diplosim 的驗證不能只看 VAF 形狀。

### E1-03 Sottoriva 2015, Nat Genet — 10.1038/ng.3214
- **資料：** 15 個大腸癌與大型腺瘤、349 個 gland、左右兩側；CNA array、WGS、單細胞 mitotic 分析；short read；多區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 無（作者做空間模型比對）。
- **觀點：** 部分腫瘤「born-to-be-bad」。
- **演化假設：** Big Bang：單次擴張，無 stringent selection，可測的 private 變異早期發生。
- **真實結論：** 未見 selective sweep；99% non-unique CNA 也在 bulk 測到；49/55 樣本同一 gland 內有多個 mitotic sub-clone。
- **限制與反證：** 只有大腸癌。「無 sweep」是對可測尺度而言。E1-04 認為可測受選 subclone 也早期出現，所以「早期」不等於「中性」。
- **支持哪一層（N3）：** 克隆結構（gland 層級）；Big Bang 過程是推論。
- **對 diplosim 的意義〔推論〕：** diplosim 的 private SNV 依邊切段，沒有「發生得越早、頻率越高」的關係。屬真值層，單點突變階段。

### E1-04 Williams 2018, Nat Genet — 10.1038/s41588-018-0128-6
- **資料：** 高深度定序的乳、胃、血、大腸、肺癌與轉移；bulk；short read。模型：stochastic branching process＋誤差模型＋貝氏選模。
- **讀取層級：** 全文。
- **用了建樹工具：** 無（自建模型）。
- **觀點：** 舊頻率法只能拒絕虛無假設，不能證明中性。
- **演化假設：** 受選 subclone 造成 VAF 叢集，並有自己的 1/f 尾巴。
- **真實結論：** 受選 subclone 早期出現、適應度優勢 >20%。比例：胃 29%（5/17）、大腸 21%（15/70）、MET500 51%（58/113）、TRACERx 97%（36/37）。同一肺腫瘤 5 區只有 1 區有強證據。
- **限制與反證：** 「>20%」受偵測限制：弱選擇或晚期 subclone 較難測到。〔推論〕不同定序設計的比例不能直接比較。單區域判定會隨區域改變。
- **支持哪一層（N3）：** 觀測特徵＋模型推論的動態。
- **對 diplosim 的意義〔推論〕：** diplosim 的 subclonal SNV 叢集之間沒有尾巴；每個 clone 只有固定邊上的 SNV。屬真值層。

### E1-05 Turajlic 2018, Cell — 10.1016/j.cell.2018.03.043
- **資料：** ccRCC，101 病人、106 腫瘤、1,206 區域（每腫瘤中位 7，3–75）；bulk panel，部分 WES／WGS；short read；多區域。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（作者流程建樹；工具細節未在檢索片段確認）。
- **觀點：** 演化具 deterministic 性質。
- **演化假設：** Driver 順序與共現可定義亞型。
- **真實結論：** Clone 數中位 4（1–23）；約 10 cm 後持平。七種亞型。VHL 突變 clonal 於 77/106。PBRM1→SETD2 高度分支（>10 clones；3–23）。VHL mono-driver 分支有限、單克隆結構。13% 有平行演化。MSAI 見於 15/41。
- **限制與反證：** Panel 以 driver 為主，所以樹是 driver 樹。Clone 數隨區域數增加，比較腫瘤時有偏差。
- **支持哪一層（N3）：** 克隆結構（多區域 driver）；deterministic 是解讀。
- **對 diplosim 的意義〔推論〕：** diplosim 不分腫瘤亞型，樹形只由隨機二分決定。MSAI 代表兩條 homolog 在不同分支各自改變，和 HP 直接相關，屬 CNA 後階段。

### E1-06 Waclaw 2015, Nature — 10.1038/nature14971
- **資料：** 空間模擬；無新定序。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 作者認為大型腫瘤多數細胞共有核心變異。
- **演化假設：** 短距離擴散與細胞更替造成快速混合，限制異質性。
- **真實結論：** 這是模型結果，不是量測：無擴散時大小約 T3，有擴散時趨近指數生長。細胞更替是限制異質性的前提。
- **限制與反證：** 參數未由單一病人資料直接校正。〔推論〕和 E1-07 的 gland 模型結論不同，代表空間假設影響結論。
- **支持哪一層（N3）：** 無直接資料支持；提供機制假說。
- **對 diplosim 的意義〔推論〕：** diplosim 沒有族群動態，也沒有空間。研究目標是 bulk 樹重建，是否需要空間要另評估。

### E1-07 Noble 2022, Nat Ecol Evol — 10.1038/s41559-021-01615-9
- **資料：** 空間模型，與已發表多區域資料的摘要指標對照；組織切片估 gland 大小。
- **讀取層級：** 全文。
- **用了建樹工具：** 無（用已發表的樹）。
- **觀點：** 空間結構決定演化模式。
- **演化假設：** 四種模式來自空間結構：rapid clonal expansion、progressive diversification、branching、effectively almost neutral。
- **真實結論：** 量測：gland 約數百到數千細胞。對照：實體瘤資料對應少數主分支的 branching；中性模型的 tree balance 和實體瘤資料不合。模型估計：多區域定序低估 subclonal driver 約 25%。
- **限制與反證：** 用 driver 樹，非全部 SNV。樹來自多區域推論，本身有偏差。作者標明「For our parameter values」。
- **支持哪一層（N3）：** 克隆結構（樹形指標），模型支持過程。
- **對 diplosim 的意義〔推論〕：** 這篇提供不靠 VAF 的樹形指標（tree balance）。diplosim 目前不控制樹形平衡。

### E1-08 Chkhaidze 2019, PLoS Comput Biol — 10.1371/journal.pcbi.1007243
- **資料：** 空間 cellular automaton 模擬，產生多區域 bulk 與單細胞資料；真值來自模擬。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 取樣偏差是主要干擾。
- **演化假設：** 空間限制改變頻譜；中性邊界生長在 f>5% 呈 1/f2 形式。
- **真實結論：** 模擬結果：純 spatial drift 也能造成突變叢集；單細胞定序明顯降低此偏差。
- **限制與反證：** 沒有病人真值，參數為模型設定。
- **支持哪一層（N3）：** 說明「觀測特徵」與「演化路徑」的距離。
- **對 diplosim 的意義〔推論〕：** diplosim 把 sample 視為 clone 的混合，沒有取樣偏差。這屬觀測層的差距。研究只優化單一 bulk，所以這個偏差不能靠多區域排除。

### E1-09 Caravagna 2020, Nat Genet — 10.1038/s41588-020-0675-5
- **資料：** 2,606 樣本 WGS；n=150 模擬；short read；單樣本、多區域與縱向。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（MOBSTER 去尾巴，下游用 sciClone 等）。
- **觀點：** 應把尾巴和受選 clone 分開建模。
- **演化假設：** VAF＝受選 clone（Beta）＋中性尾巴（power law）。尾巴內的突變不是單系。
- **真實結論：** 只用 Binomial 混合會把尾巴切成假 subclone。一例由原本 3 subclones 改為 2 subclones 加尾巴。<60x 不足以可靠偵測尾巴；低於 90x/100x 與低 purity 阻礙可靠重建。尾巴只在高 coverage、高 purity 樣本穩定出現。
- **限制與反證：** 尾巴模型假設 well-mixed；E1-08 顯示空間會改變形狀。
- **支持哪一層（N3）：** 觀測特徵＋方法層；不直接支持演化路徑。
- **對 diplosim 的意義〔推論〕：** 這是本主題最相關的差距：diplosim 的真值 clone 不含尾巴，所以 HP 擴充的樹重建沒有在有尾巴的資料上測試過。深度閾值是 short read 的結果，不能當 diplosim 的設定值。

### E1-10 Dentro 2021, Cell — 10.1016/j.cell.2021.03.009
- **資料：** PCAWG 2,658 癌症；bulk WGS，中位約 46×；short read；單樣本；11 種重建方法的 consensus。
- **讀取層級：** 全文（僅檢索相關段落）。
- **用了建樹工具：** 有（11 種重建方法的 consensus）。
- **觀點：** ITH 普遍存在。
- **演化假設：** 用 phasing 判斷 subclone 是 parent-child 或 sibling。
- **真實結論：** 95.1% 有 subclonal 擴張（1,705 個可測到 >30% subclone 的基因組）。Sibling 比 parent-child 多 3.11 倍（95% CI 1.71–7.50）。Subclone 內平均 14% SNV 低於偵測極限，CCF<30% 時為 21%。黑色素瘤例外（31/62）。85% 有 subclone 的樣本沒有已知 subclonal driver（1,381/1,621）。Driver 有 9.0% 是 subclonal（357/3,933）。
- **限制與反證：** 作者明示這是保守下限，測不到罕見族群。這些數字描述可測 subclone，不是全部 clone。
- **支持哪一層（N3）：** 克隆結構（單 bulk 的可測部分）。
- **對 diplosim 的意義〔推論〕：** 回答「單一 bulk 能看到多少」：大約只有 CCF 30% 以上。diplosim 的真值包含所有 clone，觀測層需要分清「存在」和「可測」。

### E1-11 Gao 2016, Nat Genet — 10.1038/ng.3641
- **資料：** 12 名 TNBC、1000 單細胞；單細胞 CN；short read（Illumina 76 cycles）。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（作者自建樹與 branching process 模擬）。
- **觀點：** 挑戰漸進演化。
- **演化假設：** PCNE：CNA 短暫爆發，然後穩定擴張。
- **真實結論：** 每腫瘤 1–3 個主克隆；未見漸進中間態。非克隆 CN 譜比例：aneuploid 7.4%、diploid 7.9%、鄰近正常 5.9%。
- **限制與反證：** 每腫瘤細胞數少，不易看到低頻族群。E1-12 用更多細胞看到更多 subclone。只測 CN，不能外推到 SNV。
- **支持哪一層（N3）：** 克隆結構（CN）；爆發是推論。
- **對 diplosim 的意義〔推論〕：** diplosim 每 position 獨立抽 CNA，沒有 burst 也沒有 segment。屬 CNA 階段，現在不處理（N4）。

### E1-12 Minussi 2021, Nature — 10.1038/s41586-021-03357-x
- **資料：** 8 TNBC、4 細胞株、16,178 單細胞（腫瘤 9,765）；單細胞 CN；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（CN 分群與作者流程）。
- **觀點：** TNBC 持續演化並維持多樣性。
- **演化假設：** PCNE 後的持續 CNA 累積 vs. 短暫不穩定（作者建模比較）。
- **真實結論：** 7–22 subclones 組成 3–5 superclones。
- **限制與反證：** 8 個腫瘤。Subclone 定義依 CN 分群解析度。
- **支持哪一層（N3）：** 克隆結構（單細胞 CN）。
- **對 diplosim 的意義〔推論〕：** Clone 數隨解析度增加：同為 TNBC，E1-11 是 1–3 個主克隆，E1-12 是 7–22。真值的 clone 數需要先定義解析度。

### E1-13 Sun 2017, Nat Genet — 10.1038/ng.3891
- **資料：** 1400 個虛擬腫瘤（7 模式）；已發表多區域資料（COAD、ESCA、LUAD、LUSC、GBM 等）；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（SciClone 分群）。
- **觀點：** 不同癌別的模式不同。
- **演化假設：** 強選擇會改變區域間 subclonal 分歧；弱選擇與中性差異不大。
- **真實結論：** 模擬中各模式 >70% subclonal SSNV 是區域專屬。COAD、ESCA 分歧較低，肺與腦較高、選擇訊號較強。加入區域後，subclonal cluster 溶解；不同 lineage 可有相似 VAF。
- **限制與反證：** 病人樣本少。弱選擇（s=0.01）無法和中性區分。
- **支持哪一層（N3）：** 克隆結構＋模型支持的模式。
- **對 diplosim 的意義〔推論〕：** 單區域 cluster 不一定是 clone：這對真值與重建結果的比對方式有影響。

### E1-14 Morita 2020, Nat Commun — 10.1038/s41467-020-19119-8
- **資料：** AML，123 病人、154 樣本；scDNA-seq（19 或 37 基因 panel）；每樣本中位 6102 細胞；short read。
- **讀取層級：** 全文。
- **用了建樹工具：** 有（作者的單細胞貝氏模型）。
- **觀點：** 同時有 linear 與 branching，包括收斂演化。
- **演化假設：** 單細胞共現可重建 driver 歷史。
- **真實結論：** 68（55%）linear、55（45%）branching。ADO 中位 5.8%。
- **限制與反證：** 只有 panel driver，少量突變較容易判為 linear。〔推論〕血液腫瘤無空間結構，不能外推到實體瘤。
- **支持哪一層（N3）：** 克隆結構（單細胞直接共現）；本批最直接的樹形比例。
- **對 diplosim 的意義〔推論〕：** diplosim 的樹由遞迴二分產生，linear 比例不受控制，也沒有依癌別的比例。屬真值層。

### E1-23 Tung & Durrett 2021, PLoS Comput Biol — 10.1371/journal.pcbi.1008701
- **資料：** 數學分析與已發表資料的討論；無新定序。
- **讀取層級：** 全文。
- **用了建樹工具：** 無。
- **觀點：** 與已發表批評不同：足夠資料下，SFS 能分辨中性與兩型模型。
- **演化假設：** 兩型 branching process；每型內都有 1/f。
- **真實結論：** 數學結果，不是量測。只針對「一種特定選擇形式」。
- **限制與反證：** 需要足夠資料，E1-09 顯示真實資料常常不足。
- **支持哪一層（N3）：** 理論（生成模型）。
- **對 diplosim 的意義〔推論〕：** 提供單點突變階段可參考的生成模型類別。不寫實作。

### 已收錄、未重抓
- **B04 Sakamoto 2022（long read）：** 它用 long read 的同 read 順序，在 S14 的候選中選出 linear。這是本主題少數 long-read 樹形證據，但只有局部約束。見 `research/literature/papers/B04_lung_longread_phasing_2022/summary.md`。

## 對 diplosim 的差距（照優先順序）

| 真實腫瘤的現象 | diplosim 現況（檔案:行號） | 差距 | 證據強度 | 階段 |
|---|---|---|---|---|
| 每個 clone 內有低頻突變尾巴，且不是單系（E1-09、E1-04） | SNV 只放在樹的邊上（`src/evolution.rs:273`） | 真值沒有 within-clone 突變 | 高（模型）；資料支持限高深度 short read | 單點突變 |
| SNV 累積和時間、族群大小有關（E1-01、E1-23） | 沒有突變率，邊長和時間無關（`src/evolution.rs:273`） | 無生成過程 | 中（生成模型的選擇仍有爭議） | 單點突變 |
| Clone 頻率反映選擇與出現時間（E1-04） | Dirichlet(1)（`docs/conipher_steps.md` S7） | 頻率和樹、時間無關 | 中 | 單點突變 |
| 樹形依癌別不同；linear／branching 比例不一（E1-14、E1-05、E1-10） | 遞迴二分加剪葉（`src/topology.rs:57-109`） | 樹形不可解釋、不受控制 | 中（比例依解析度而定） | 單點突變 |
| Bulk 只測得到高頻 subclone（E1-10） | 真值與觀測都含全部 clone（`docs/conipher_steps.md` S7） | 應區分「存在」與「可測」 | 高（short read） | 觀測層 |
| 空間取樣造成假叢集（E1-08、E1-13） | 無空間 | 尚未決定是否需要 | 中（模型） | 待評估 |
| CNA 爆發、segment（E1-11、E1-12） | 每 position 獨立抽（`docs/conipher_steps.md` S4–S6） | 無 burst、無 segment | 中（TNBC） | CNA 後 |
| 兩條 homolog 在不同分支平行改變（E1-05 MSAI） | 只有 allele A／B（`src/hp.rs:30`）；無父／母標籤 | 無平行事件；無 parent-of-origin 真值 | 中 | CNA 後 |

## 未解問題

1. Long read bulk 資料下，尾巴與可測 clone 的界線在哪裡？在本批 15 篇的全文中，以 `long.read|nanopore|PacBio` 檢索，沒有命中。
2. 實體瘤的 linear／branching 真實比例：只有 AML 有單細胞比例（E1-14）。E1-10 的 sibling 倍數來自 phasing 子集。本次搜尋沒有找到大型實體瘤單細胞 SNV 樹的比例。
3. 樹深與分岔數：本批沒有直接報告；只有 clone 數。E1-07 的 tree balance 是最接近的指標，數值在 Figure 內，文字檔沒有。
4. 尚未讀到全文的線索：McDonald 2018、Balaparya & De 2018、Heide 2018 正式版、Ling 2015、Bozic 2016、Gunnarsson 2021（低頻 SFS 隨 birth／death rate 改變，只讀到 arXiv 摘要的 WebFetch 摘要，不當證據）。
5. 文獻裡的 subclone 數隨解析度變動（E1-11 與 E1-12）。diplosim 的真值 clone 應該對應哪個解析度，要由使用者決定。
6. Parent-of-origin 是否影響演化模式：本批沒有資料，交給主題 08。
