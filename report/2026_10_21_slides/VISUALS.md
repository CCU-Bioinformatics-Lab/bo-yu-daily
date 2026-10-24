# 生物示意圖規格（VISUALS）

用途：說明 2026-10-21 投影片的手繪示意圖要畫成什麼樣子，才符合科學事實。
通用規格已提取到 `report/VISUAL_SPEC.md`（全域）。本檔保留這次簡報的原始版本與專用來源。
繪圖元素只用 div 方塊、圓、線、箭頭，以及沒有 `<text>` 的 SVG。
配色沿用 `BRIEF.md`：HP1 `#2C5F9E`、HP1-1 `#8FB3E0`、HP2 `#D9772B`、HP2-1 `#F2B880`、SNV `#D23A2E`、unphased `#9AA3AE`。
數字只用 brief 指定的數字或來源中的數字。標「推論」的項目是本 repo 的分析，論文沒有寫。
出處縮寫：Tarabichi 2021＝Tarabichi et al., *Nat Methods* 18:144（PMC7867630）；PhyClone notes＝`research/phyclone_research/notes/zh-TW/`。

---

## 1. Clone tree、CCF 與 sum rule

- **(a) 定義**：clone tree 的每個節點是一個 clone，就是一群帶有相同突變集合的細胞。每條邊表示子 clone 新獲得的突變。CCF 是帶有某突變的腫瘤細胞比例，等於該節點整棵子樹的細胞比例。
- **(b) 慣例**：root 在上方或左方。常見做法是加一個 normal/germline root。節點圓的大小或塗色面積表示比例。突變常畫成邊上的小記號。Tarabichi 2021 Fig. 1a 用一個 CCF 100% 的祖先，加上兩個 CCF 50% 與 25% 的子 clone。常見的配圖是「魚圖」或「細胞群圓餅」，用來對照樹與 bulk 中的細胞比例。
- **(c) 構圖**：
  - 左側放樹：root 圓（灰）→ A 圓（深色），A 下方分出 B 與 C 兩個圓。邊上各放 1–2 個紅點，表示新突變。
  - 右側放「bulk 樣本」大圓角方塊，裡面放約 20 個小圓細胞。依 clone 塗色，並保留部分灰色 normal 細胞。
  - 節點旁的短標籤依 Tarabichi Fig. 1a 寫「100%」「50%」「25%」。
  - 用括號或虛線框標出 sum rule：B＋C ≤ A。標籤寫「子節點 CCF 總和 ≤ 父節點」。
- **(d) 易錯點**：
  - CCF 是累積值（子樹總和），不是 clone 本身獨有的比例。PhyClone 分開記 `rho_v`（獨有）與 `rho_bar_v`（子樹）。
  - 公式是 CCF(B)+CCF(C) ≤ CCF(A)。子節點總和不需要等於父節點。差額是只帶 A 突變的細胞。
  - 不要把 normal 細胞算進 CCF 的分母。normal 細胞屬於 purity。
  - 樹上的邊不是時間長度。不要用邊長表示時間。
- **(e) 出處**：Tarabichi 2021 Fig. 1a、Box 1（pigeonhole principle 與 sum rule）；PhyClone notes `02_METHODS_DEEP_DIVE.md` §5（`rho_bar_v = rho_v + Σ 子節點 rho_bar`）；`01_PAPER_BIG_PICTURE.md` p.1–2（ISA：祖先突變的盛行率 ≥ 後代突變）。

## 2. Bulk 定序：reads → ref/alt → VAF

- **(a) 定義**：bulk 樣本混合腫瘤細胞與正常細胞。腫瘤細胞所占的比例是 purity（ρ）。在一個 SNV 位點，VAF＝alt reads ÷（ref＋alt reads）。
- **(b) 慣例**：上方畫組織（腫瘤細胞和正常細胞混合）。中間畫 reference 長條，上面疊多條短 reads（pileup）。帶 alt 的 read 在該位置加一個色塊。下方寫計數與 VAF。Tarabichi 2021 Fig. 1b–d 依序畫 SNV calling、CN、VAF → CCF → 分群。
- **(c) 構圖**：
  - 第 1 層：一個圓角方塊，裡面放腫瘤細胞（深色）與正常細胞（灰）。
  - 第 2 層：一條粗灰線當 reference，上方疊 8–10 條細長方塊 reads，並畫一條垂直虛線標出 SNV 位置。部分 reads 在虛線上放紅點（alt），其餘不放（ref）。
  - 第 3 層：兩個計數方塊「ref」「alt」→ 箭頭 → 「VAF」。
  - 右側放公式卡（文字可用 div）：VAF ≈ ρ·m·CCF ÷ (ρ·N_T + 2(1−ρ))。其中 N_T＝腫瘤局部 total CN，m＝multiplicity（帶突變的 copy 數）。
  - 反解：CCF＝VAF·(ρN_T + 2(1−ρ)) ÷ (ρ·m)（Tarabichi Box 1）。
  - 範例：clonal 異型合子、CN=2、m=1、purity=1，則 VAF=0.5。
- **(d) 易錯點**：
  - 分母要包含 normal 細胞的 2 個 copy。不能只除以 total CN。
  - 一條 read 來自一條 DNA 分子，不代表一個細胞。
  - VAF 是觀測值，帶有 binomial 抽樣誤差。PhyClone 用 Binomial 或 Beta-Binomial。
  - `tX_nY` 是 nominal purity。圖上的 ρ 不能直接寫成 nominal 百分比。
- **(e) 出處**：Tarabichi 2021 Fig. 1、Box 1；PhyClone notes `02_METHODS_DEEP_DIVE.md`（ξ 公式：normal、reference、variant 三群細胞依 CN 加權；Supplement S1.1）；PyClone（Roth et al. 2014, *Nat Methods*）的三群細胞模型（未核對圖號）。

## 3. 同源染色體、haplotype phasing 與 longphase-s HP tag

- **(a) 定義**：人類每條體染色體有兩個同源 copy，一條來自父方，一條來自母方。Germline het SNP 是兩條 copy 上不同的鹼基。Phasing 用跨過多個 het SNP 的 read，把 reads 分到 HP1 或 HP2。連續可定相的範圍是一個 phase set（PS）block。
- **(b) 慣例**：兩條水平長條上下並排，上條表示 HP1，下條表示 HP2。同一個 het SNP 在兩條上畫成同一 x 位置、不同顏色的 allele。reads 畫成短橫條，顏色跟所屬的 HP 相同。PS block 用長條下方的括號或底色區間表示。
- **(c) 構圖**：
  - 兩條同源長條：上 `#2C5F9E`（HP1），下 `#D9772B`（HP2）。
  - 在 3–4 個 x 位置放 het SNP 小方塊。上條與下條同一位置使用兩種不同的淺色或深淺。
  - 上方畫 3–4 條 HP1 reads，下方畫 3–4 條 HP2 reads。每條 read 至少跨過 2 個 het SNP。
  - 一條 read 只蓋到 0 個 het SNP，塗灰（unphased）。
  - 在 HP1 長條的某個位置放紅點，表示 somatic SNV。帶紅點的 HP1 reads 塗 `#8FB3E0`（HP1-1）。HP1 上沒有蓋到紅點的 reads 維持 HP1 色。HP2-1 的畫法相同，但紅點放在 HP2。
  - 長條下方畫兩段 PS 括號。中間留一段缺口，表示 het SNP 太少、無法連接。
  - 標籤：「HP1」「HP2」「HP1-1」「HP2-1」「PS 1」「PS 2」「unphased」。
- **(d) 易錯點**：
  - HP1 不等於父源。HP1/HP2 只是 block 內的任意標號。不要寫「HP1＝爸爸」，可改寫「兩條同源 copy 之一」。
  - HP 只在同一 sample、chromosome、PS 內有意義。不同 PS 的 HP1 不能連起來。
  - HP 是 germline homolog 標籤，不是 clone 標籤（SYNTHESIS K1）。
  - somatic SNV 只放在一條長條上。不要兩條都放。
  - `HP:1-1` 是 read 層級標記。這條 read 在另一個待測 SNV 位點仍可能是 REF（`plan.md` §3.1）。
  - longphase-s 另有 `3`（ambiguous somatic，不是 LOH）、`4`、`1-2`、`2-2`、`.`。投影片只畫四色時，加註「另有其他 tag」。
- **(e) 出處**：`plan.md` §3.1；`/big8_disk/liaoyoyo2001/Knowledge/05_tools/longphase-s.md`「輸出 HP tag 格式」（`1-1`/`2-1`＝支持 somatic ALT、可追溯到 HP1/HP2 的第一條 somatic haplotype）；B04 README（WhatsHap 建 haplotype block 後 haplotag，p.15：不同 block 的 allele 編號不具共同意義）；`research/literature/SYNTHESIS_phyclone_longphase.md` K1。

## 4. Subclonal copy number（60% 1:1、40% 2:1）

- **(a) 定義**：subclonal CN 是只有部分腫瘤細胞帶有的 CN 改變。例子：purity=1，60% 細胞為 1:1，40% 細胞的某條 haplotype 多出一個 copy（2:1）。clonal SNV 位於被複製或未被複製的 haplotype 時，VAF 不同。
- **(b) 慣例**：畫兩個細胞族群。每個族群內用兩條（或三條）短染色體表示 allele copy。被複製的 copy 用同色重複畫。SNV 用紅點表示。
- **(c) 構圖**：
  - 左框「60% 細胞」：一條 HP1 短條＋一條 HP2 短條。
  - 右框「40% 細胞」：兩條 HP1 短條＋一條 HP2 短條（HP1 被複製）。
  - 情境 A（上排）：紅點在 HP1。右框兩條 HP1 都有紅點，因為突變早於複製。計算：(0.6·1 + 0.4·2) ÷ (0.6·2 + 0.4·3) = **0.583**。
  - 情境 B（下排）：紅點在 HP2。計算：(0.6·1 + 0.4·1) ÷ 2.4 = **0.417**。
  - 右側小表：依 1:1 推 CCF，A 約 1.17（超過 1），B 約 0.83（像假 subclone）。
  - 標籤：「60% 1:1」「40% 2:1」「SNV 在被複製的 allele」「SNV 在未複製的 allele」。
- **(d) 易錯點**：
  - 情境 A 預設 SNV 發生在複製之前，所以兩個複製 copy 都帶 SNV。若 SNV 發生在複製之後，只有一個 copy 帶 SNV，數字也會不同。圖上要寫明這個假設。
  - 分母是 2.4（0.6·2 + 0.4·3），不是 3。
  - clonal 2:1 配 purity 0.4 也會給 0.417。單一區段內無法分開 subclonal 比例與 purity。
  - HP 拆分能看出哪條 haplotype 改變了。比例仍要另外估計（推論）。
  - PhyClone 每個 SNV 只使用一組 major/minor CN，不建模 subclonal CN（notes 02 §S1.2）。
- **(e) 出處**：BRIEF s3-subclonal-cn 頁；`/tmp/claude-1024/-bip8-disk-boyu114-main-work/23ba803e-44e2-4cf9-8ce6-3e6e92e46d5c/scratchpad/s5908_text.md` L207–208、L278–286；M07 SMC-Het README（subclonal gain 讓 CP 高估、subclonal loss 讓 CP 低估）；Tarabichi 2021 Fig. 3。

## 5. 同一條 read 上兩個 SNV 的共現與四類關係

- **(a) 定義**：一條 long read 同時覆蓋 SNV a 與 b 時，兩端 allele 組合為 11、10、01、00（1＝ALT，0＝REF）。n11、n10、n01 是各組合的 read 數。四類關係的不允許 pattern：same 不出現 10 和 01；a 是 b 的祖先時不出現 01；b 是 a 的祖先時不出現 10；分支時不出現 11。
- **(b) 慣例**：只畫一條 haplotype 長條，上方疊多條 reads。兩條垂直虛線標出 a、b 兩個位點。read 在該位點畫紅點表示 alt，空心圓表示 ref。旁邊放一棵小樹，表示對應的關係。
- **(c) 構圖**：
  - 上方畫三種 read 範例：alt-alt（兩個紅點）、alt-ref、ref-alt。
  - 下方畫 2×2 小格，每格放一棵三節點小樹與一條 read 組合：
    - same：a、b 在同一節點 → 只會出現 11（加上 00）。
    - a 是 b 祖先：A→B 線性 → 會出現 11 與 10，不會出現 01。
    - b 是 a 祖先：會出現 11 與 01，不會出現 10。
    - 分支：A、B 是兄弟 → 會出現 10 與 01，不會出現 11。
  - 不允許的 pattern 用灰色叉號標記。
  - 底部的條件標籤：「同 PS」「同 HP」「該 HP 的 C_h=1」「不跨 CN breakpoint」。
- **(d) 易錯點**：
  - 分支時沒有 alt-alt read。原因：a、b 在不同的細胞譜系，同一條 DNA 分子不會同時帶有兩者。前提是兩者在同一條 haplotype，而且 C_h=1。
  - a、b 在不同 HP 時，共現永遠是 0，不能拿來判斷關係。圖上的兩個點必須畫在同一條長條上。
  - 如果該 haplotype 有多個 copy（C_h>1）、有 ecDNA，或兩點之間跨 CN breakpoint，pattern 不再對應細胞譜系（K2）。
  - n11=0 不能直接判為分支。coverage 低時本來就可能看不到 11（K3）。
  - 只有 11 也不能證明 same（B04 EGFR 例）。
  - 一條 read 是一個分子觀測，不是一個細胞。
  - n00 不提供關係資訊，計分時不使用。
- **(e) 出處**：`plan.md` §4.5.1–4.5.3；SYNTHESIS K2、K3；Tarabichi 2021 正文（read phasing 顯示同一 chromosome copy 上的鄰近 SNV 互斥時，表示分支）；B04 README（主文 Fig. 3f：NKAIN4–BIRC7 pair）；M02 TreeClone 使用 00/01/10/11 read count。

## 6. B04 例子：branched vs linear（S14）

- **(a) 定義**：B04 的 S14 病人中，PyClone-VI 分群後，ClonEvol 同時給出 branched 與 linear 兩棵候選樹。兩者都符合 sum rule。long read 看到 C-2 與 C-3 雙突變的 reads，因此作者選 linear。
- **(b) 慣例**：原圖並排兩棵候選樹，並附 long-read 證據。可以參考 BRIEF 的 image8。
- **(c) 構圖**：
  - 左右兩棵樹。左（branched）：C-1 → C-2、C-1 → C-3。右（linear）：C-1 → C-2 → C-3。
  - 節點標籤：「C-2 CCF 0.616」「C-3 CCF 0.212」。
  - 樹下方畫一條 read，在 C-2 與 C-3 的 SNV 位置各放一個紅點，表示 double mutant。
  - 從 read 畫箭頭指向右樹，右樹加打勾。左樹加淡化或叉號，並加註「branched 不允許 alt-alt」。
- **(d) 易錯點**：
  - 0.616 + 0.212 = 0.828 ≤ 1，所以 sum rule 不能排除 branched。這正是需要 read 證據的原因。圖上不要暗示 CCF 本身就能選出 linear。
  - B04 的 scDNA 驗證病人是 S8、S20，不是 S14。不要在 S14 圖旁放 scDNA。
  - B04 只用 read pair 篩選候選，不是建樹模型。
  - 「C-2」「C-3」是 cluster，不是單一 SNV。read 證據只針對特定 SNV pair。
  - C-1 的 CCF 若未核對，不要寫數字。
- **(e) 出處**：Sakamoto et al. 2022 *Nat Commun* 13:3464，Supplementary Fig. S9c–d（p.19–20）；`research/literature/papers/B04_lung_longread_phasing_2022/README.md`；BRIEF s4-topology-constraint 頁。

## 7. 相同 CCF 不等於同一個 clone

- **(a) 定義**：兩個兄弟 clone 可能有相近的 CCF。只看 CCF 分群時，它們會被併成一群，或被排成線性。
- **(b) 慣例**：左右並排「真樹」與「CCF 推出的樹」，中間放一條 CCF 數線。
- **(c) 構圖**：
  - 左（真樹）：A → B、A → C。B 用藍色，C 用橘色。兩者都標「約 0.4」。
  - 中間：一條 0–1 的水平數線。B、C 兩點幾乎重疊在 0.4 附近，A 的點在右側。
  - 右上（錯誤 1）：A → (B+C) 合成一個節點。這個節點用藍橘對半的圓表示。
  - 右下（錯誤 2）：A → B → C 線性排列。
  - 右側兩棵樹用紅框或叉號標成錯誤。
  - 可另加一條 read 小圖：B 與 C 的 SNV 只有 10、01，沒有 11，支持分支（連到概念 5）。
- **(d) 易錯點**：
  - 0.4 + 0.4 = 0.8 ≤ A 的 CCF 時，sum rule 不能排除線性。A 的 CCF 必須 ≥ 0.8 才符合真樹。如果標 A 的數字，要寫 ≥ 0.8（例如 1）。
  - PhyClone 可以合併前分群，但不能拆開前分群。錯誤 1 在 PhyClone 中無法修回（K10）。
  - 不要把 B、C 畫成不同大小。這樣會暗示 CCF 不同。
- **(e) 出處**：BRIEF s3-clone-def 頁；s5908_text.md L179–180（TreeClone Sim 2：Cloe 與 PhyloWGS 把 M2、M3 併群成線性；PhylEx Fig. 1 的同類問題）；SYNTHESIS K10；s5908_text.md L376（真樹分支、預測成線性時 sc3 仍有 0.875）。

## 8. Single-cell DNA 樹作為真值

- **(a) 定義**：single-cell DNA 定序分別讀取每顆細胞的基因組，得到每顆細胞的突變或 CN 狀態。依據細胞的基因型可以建細胞樹或 clone 樹，再拿來對照 bulk 推出的 clone tree。
- **(b) 慣例**：左側畫組織解離成單顆細胞，中間畫 cell × mutation 的 0/1 矩陣（行＝細胞，列＝突變，有突變的格子塗色），右側畫細胞樹，葉節點是細胞，同色細胞聚成 clade。最後加一條箭頭，連到 bulk clone tree 做比對。
- **(c) 構圖**：
  - 第 1 欄：一團細胞 → 箭頭 → 一列分開的小圓。
  - 第 2 欄：6 行 × 5 列格子矩陣。部分格子塗紅，表示有突變。依 clone 排序後會看到區塊結構。少數格子用灰色斜線表示 missing 或 dropout。
  - 第 3 欄：細胞樹，葉子用與 clone 對應的顏色。
  - 第 4 欄：bulk 推出的 clone tree，中間用雙向箭頭與「對照」標籤連接。
- **(d) 易錯點**：
  - single-cell 資料有 allelic dropout 與低 coverage。沒有 alt 的格子不等於真陰性（B04 S10 Note）。
  - CN dendrogram 不等於 SNV evolution tree（B04）。
  - single-cell 樹本身也是推論，不是絕對真值（K8）。
  - scRNA 不能代替 scDNA。
  - 對照時，細胞要先聚成 clone 再比較，不能直接用細胞樹比 clone tree。
- **(e) 出處**：B04 README（10x Chromium scDNA，S8 QC 後 138 顆、S20 QC 後 376 顆細胞，Fig. S10）；SYNTHESIS K8；BRIEF s1-why-truth 頁（PhyClone HGSOC 真值來自 McPherson 2016 單核定序＋targeted deep sequencing，`research/literature/papers/R01_mcpherson_hgsoc_2016/README.md`）；M07 Discussion（建議 single-cell WGS pseudo-bulk 當補充真值）。

## 9. SMC-Het 子任務管線

- **(a) 定義**：SMC-Het 把 single-sample subclonal reconstruction 拆成七個 subchallenge：1A purity、1B subclone 數、1C SNV CP 分布、2A／2B SNV 分群（hard／soft）、3A／3B phylogeny（hard／soft）。
- **(b) 慣例**：由左到右的管線，每站一個方塊，站與站之間用箭頭。輸入放在最左，評分放在每站下方。
- **(c) 構圖**：
  - 最左放輸入方塊：「MuTect VCF」＋「Battenberg CN、purity」。
  - 五站方塊：1A purity → 1B clone 數 → 1C CP → 2A/2B 分群 → 3A/3B 樹。
  - 每站下方小字寫評分：1A `1−|ρ−c|`；1B `(L−d+1)/(L+1)`；1C `1−EMD`；2A/2B AUPR 與 AJSD 的平均；3A/3B 四矩陣的 Pearson correlation。
  - 第 3 站之後畫一個小樹圖示，第 5 站畫四個小方陣圖示（co-clustering、cousin、ancestor–descendant、轉置）。
  - 上方一行規模：31 個方法、51 個模擬腫瘤、12,061 次執行。
  - 每站下方第二行放 long read 的可能幫助（標「推論」），內容照 BRIEF s5-smchet-decompose 頁。
- **(d) 易錯點**：
  - 1C 的 CP 是 cellular prevalence。它的單位是否含 purity 待確認（BRIEF s5-next 待確認項）。不要直接寫成 CCF。
  - 分數在每個腫瘤內做 min–max 正規化，表示相對排名，不是絕對正確率。
  - 2A/2B 與 3A/3B 各是 hard 和 soft 兩個版本，不是兩個步驟。
  - 只有 7 個方法提交 phylogeny。PhyClone 沒有參賽。
  - 管線箭頭只表示任務順序。參賽方法不一定照這個順序計算。
- **(e) 出處**：Salcedo, Tarabichi et al. 2024 *Nat Biotechnol* 43:581（Methods p.13、Table 1）；`research/literature/papers/M07_smchet_benchmark_2024/README.md`；BRIEF s5-smchet-decompose 頁。
