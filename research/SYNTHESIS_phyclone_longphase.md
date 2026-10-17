# research/ 文獻去重與 PhyClone × longphase-s 整合地圖

整理日期：2026-10-16。範圍：`research/` 下所有正式筆記（不含 `.agent_workspace/` 中間產物、不含 PDF 全文重讀）。

本文件只做**整理與去重**，不新增論文證據，也不修改既有檔案。標記沿用 repo 慣例：`current`（已核對的程式／檔案狀態）、`inferred`（分析推論）。各論文的頁碼與定位以原 README 為準；本文件只指回去。

---

## 1. 結論先說

1. **檔案層級重複很多，但大多是「同一結論被不同綜整檔重寫」，不是內容衝突。** 最大的三組重複是：PhyClone 筆記中英雙份、`tumor_phylogeny_2026/` 五份綜整檔互相重述、三層 C0–C6 對照表（`plan.md` §4／`REPO_IMPROVEMENTS.md` §4／每篇 README 末段）。
2. **跨論文反覆出現的結論，正是整合 PhyClone + longphase-s 時應保留的設計約束。** 共整理出 12 條（§3），其中 K1–K5 直接決定 C2／C3／C4 的形狀，K6–K12 決定評估與輸出。
3. **每篇論文去重後只剩 1–2 個不可替代的貢獻**（§4）。真正對 C4（同 read pair → topology）有直接證據的只有 B04，B02 是低 coverage 的反例；其他論文主要支撐 C2／C3 的 allele-specific CN 與評估設計。
4. HCC1395 目錄的過時內容已刪除並 commit（§5）。

---

## 2. 檔案層級重複與建議處理

| # | 重複內容 | 出現位置 | 建議保留為單一來源 | 其餘處理 |
|---|---|---|---|---|
| D1 | PhyClone 八份筆記中英全文對照 | `phyclone_research/notes/*.md` 與 `notes/zh-TW/*.md`（8 對，內容逐段對應） | `zh-TW/`（CLAUDE.md 規定繁中為文件語言） | 英文版標為翻譯來源，不再雙邊更新；或只在 zh-TW 有修改時同步 |
| D2 | 「B04：S14 用 long-read 選 linear，但 scDNA 是 S8／S20，不是全樹 truth」 | `tumor_phylogeny_2026/README.md`、`INTERSECTION_SUMMARY.md`、`B_SUMMARY.md`、`REPO_IMPROVEMENTS.md` §2、`B04/README.md` | `B04/README.md` | 綜整檔只留一句＋連結 |
| D3 | 「五篇 B 類不是五個 ONT clone-tree 方法」的篇數聲明 | `README.md`、`B_SUMMARY.md`、`INTERSECTION_SUMMARY.md` | `README.md` | 另兩份刪除重述 |
| D4 | 未納入候選清單（LongSom、HATCHet2、ALPACA、SomaticHaplotype、RCK、Meltos、SAVANA…） | `INTERSECTION_SUMMARY.md` 擴展搜尋表、`B_SUMMARY.md` 暫未列入表、`SEARCH_LOG.md` | `SEARCH_LOG.md` | 兩張表合併進 SEARCH_LOG |
| D5 | AACR 2026 abstract 6912（H2009／H1437 bulk ONT pair timing） | `README.md`、`INTERSECTION_SUMMARY.md`、`B_SUMMARY.md`、`REPO_IMPROVEMENTS.md` §8 | `REPO_IMPROVEMENTS.md` §8（它是 novelty 判斷所在） | 其餘只留連結；**這是本 repo 最需追蹤的競爭工作** |
| D6 | C0–C6 × 論文對照 | `plan.md` §4（設計）、`REPO_IMPROVEMENTS.md` §4（彙總表）、13 篇 README 末段 | 設計以 `plan.md` 為準；文獻對照以本文件 §3、§4 為準 | 各 README 末段保留「最小 benchmark」，C0–C6 逐條建議可縮短 |
| D7 | purity 三種定義（cellular `rho`／tumor DNA fraction `delta`／nominal mixture） | `REPO_IMPROVEMENTS.md` §3、`plan.md` §1.2、`A01`、`A03`、`B06` README、`CONTEXT.md` | `REPO_IMPROVEMENTS.md` §3（有換算式） | 其餘引用即可 |
| D8 | 共用術語 193 條 | `CONTEXT.md`（渲染版）與 `terminology/terms.tsv`（資料版） | `terms.tsv` 為資料源，`CONTEXT.md` 為閱讀版 | 確認兩者由同一流程產生；不要手改 CONTEXT.md |
| D9 | 「HCC1395 Fig. 4a 是 candidate topology，不是 lineage truth」 | `hcc1395.../README.md`、`02`、`04`、`06`、`07`、`TERMINOLOGY`／`CONTEXT` | `04_confidence_and_limits.md` | 其他章節縮成一句 |
| D10 | 「reference tree 與驗證資料不獨立」 | `REPO_IMPROVEMENTS.md` §6、`A01`、`A02`、`B01` README、`hcc1395/04` | `REPO_IMPROVEMENTS.md` §6 | — |

---

## 3. 跨論文收斂的設計約束（應保留的核心）

這些是「多篇論文各自獨立得出、內容重複」的結論。重複本身就是證據強度，因此整合時要保留。每條標示支撐來源、對應模組，以及 `plan.md` 目前是否已涵蓋。

| ID | 收斂結論 | 支撐來源 | 對應模組 | `plan.md` 狀態 |
|---|---|---|---|---|
| **K1** | HP1／HP2 是 germline homolog 標籤，只在 `(sample, chrom, PS)` 內有意義；**不是 clone ID**，PS block 也不是 clone | B02、B04、B05、B07、A04、lab glossary、`hcc1395/05`、PhyloWGS review | C0、C1 key 設計 | 已涵蓋（§3.1） |
| **K2** | 同一 molecule 的 `n11/n10/n01` pattern 可給局部 partial order；但只在 `C_h=1`、clonal CN、不跨 breakpoint 時能映射到 cell ancestry | B04（直接）、B03、B07、B08（多 copy／ecDNA 反例）、B01 | C4 eligibility | 已涵蓋（§4.5.1） |
| **K3** | `n11=0` 不能硬判 branching；需 coverage-aware 的 soft factor 與 error `ε` | B02（n=4 實例）、B04、`REPO_IMPROVEMENTS` §2 表 | C4 likelihood | 已涵蓋（`ε`、`λ`） |
| **K4** | total CN 或 major/minor 會把不同親代歷史壓成同一狀態；haplotype-specific CN 可把 multiplicity 上限由 major CN 改為 `C_h` | A04、B03（Fig. 5d–e）、B05、B07、A01 | C2 | 已涵蓋（§4.3） |
| **K5** | phasing／CN orientation 的不確定性要一路保留到樹（soft `π_i(h)`），不能當無誤差標籤 | B07（核心）、B05（phase provenance）、`REPO_IMPROVEMENTS` §2 優先二 | C2、C3（F2、F3） | 已涵蓋，但 F3 定向門檻仍是提案 |
| **K6** | CN loss、parallel LOH、breakpoint loss 會造成 mutation loss，看起來像 branching | A03、B03、B08、B01（deletion-rescued）、PhyClone outlier 模型（notes 02 §8、06） | C6 flags；評估分層 | **部分**：第一版關閉 outlier，只能在報告中標示失效 |
| **K7** | purity 至少分 cellular purity、tumor DNA fraction、nominal mixture；longphase-s 的 0.992 不能直接當 `tumour_content` | A01、A03、B06、`REPO_IMPROVEMENTS` §3、`tumor_sample.md` | C1 schema | 已涵蓋（§1.2） |
| **K8** | 所有「參考樹」都是推論所得；以同一資料建樹又驗證會循環 | A01–A05、B01、HCC1395、A02（固定 topology 的 MEDICC2） | 評估設計 | 已涵蓋（I10 模擬真值） |
| **K9** | 同一 read 產生的多個 pair 不是獨立觀測；tagging 用到的 somatic site 與評估 site 重疊會洩漏 | `REPO_IMPROVEMENTS` §6、B05（segment／chromosome bootstrap）、B01（block holdout） | C4 `λ`、去重、holdout | **部分**：有去重與 `λ`，尚未規定 tagging 前切分 holdout |
| **K10** | 固定預分群會把有順序訊號的 SNV 壓在同一 cluster，下游無法修回 | B04（C5）、B07（迭代分群）、B02、PhyClone notes 06（預分群全有或全無） | C5 | 已涵蓋為診斷；未設計重新分群 |
| **K11** | 輸出應包含 edge／relation uncertainty 與衝突，而非單一 MAP tree | A01、A02、B01、B03、B04、PhyClone notes 03／05 | C6 | 已涵蓋（§4 C6） |
| **K12** | 必要對照組：pair 打亂、PS 內 switch-error 注入、coverage downsample、PS 整體對調（不變性檢查） | B02、B04、B05、B07、`REPO_IMPROVEMENTS` §5 | 評估 ablation | 已涵蓋（`evaluation_v1.md:106–108`、`plan.md:554–558`） |

**`inferred`：** 對 `plan.md` 的實際補強點只有三處——K6（mutation loss 在 no-outlier 版本的報告方式）、K9（holdout 必須在 tagging 前切分）、K10（是否允許 C4 衝突觸發重新分群）。其他 9 條已被現行計畫吸收，文獻整理的價值在於提供引用來源。

---

## 4. 每篇論文去重後的唯一貢獻

下表回答「這篇若刪掉，會失去什麼」。「可省略的重述」指已被 §3 收斂、在本篇 README 中只是重複的段落。

| 論文 | 不可替代的貢獻 | 主要服務模組 | 可省略的重述 |
|---|---|---|---|
| **B04 肺癌 ONT 2022** | 唯一一篇以實測 long-read pair 排除候選 topology（S14, supp. Fig. S9）；phased-mutation 成功率對 VAF／purity 的分層 | **C4**（核心）、C0 feasibility | K1、K7 |
| **B02 MM linked-read 2021** | 同 HP 兩個 NRAS 互斥的低 coverage 實例（n=4），是 C4 soft factor 的反例 fixture | C4（負共現）、K12 coverage downsample | 臨床 scRNA 敘述 |
| **B07 Numbat 2022** | phase uncertainty 進模型、soft genotype、分群與建樹迭代 | **C2／C3**（F2）、C5 | K4 |
| **B05 MEDICC2 2022** | 獨立 CN-only tree 作衝突對照；segment／chromosome bootstrap 作 resampling 單位 | C6 對照、K9 | K4 |
| **B03 SIGNALS 2022** | 相同 total CN、相反 HSCN 的 pseudo-bulk 壓力測試（Fig. 5d–e） | **C2／C3** 壓力測試 | ONT 只是 SV 驗證，不重複引用 |
| **A04 CK-AML Strand-seq 2024** | 同 total CN 不同 homolog／SV 的 clone；curated SV clone matrix | C2、C5、C6 | Strand-seq ≠ long read 的反覆聲明 |
| **B01 melanoma ONT 2026** | 公開 ONT clone genomes，可做受控 mixture（最貼近本 repo cell-line workflow） | **模擬／benchmark 資料源** | germline phase 不足 → 不用於 HP 驗證 |
| **A01 卵巢 cfDNA 2025** | scWGS clone 的 pseudobulk，可驗 CN-aware CCF | C2／C3 的 CCF 驗證 | K7 |
| **A02 SPRINTER 2025** | S-phase／replication 造成假 CN clone | C0 CN QC、C5 | K8 |
| **A03 胰臟 snDNA 2023** | 公開 PA04 SCG_input（最低成本起步資料）；CN loss → mutation loss 實例 | 評估起步、K6 | K7 |
| **A05 MPAL 2024** | 公開 genotype＋FP/FN 敏感度設定 | 評估 relation check | 與 C2–C4 無直接關係 |
| **B06 HCC multisite ONT 2025** | SV breakpoint presence → sample tree；SV CCF | 未來加 SV 觀測（C0 擴充） | 第一版不需要 |
| **B08 HPV 2023** | ecDNA／高 CN 下同 read 不能套 `C_h=1` 規則 | K2 邊界條件 | 第一版只需一句排除規則 |
| **PhyClone notes** | 程式定位：`data/pyclone.py:299`（輸入）、`get_major_cn_prior:325`（C2 接點）、`utils/math_utils.py:180–244`（C3）、`tree/distributions.py:124`（C4 三個計分入口）；假設清單（notes 06） | 全部 C 模組的接點 | 英文版與中文版重複（D1） |
| **HCC1395 review** | 分層 evidence grade（06 §9）；Fig. 4a 拓樸作 candidate-tree 相容性檢查 | HCC1395 pilot 的解讀上限 | D9；C++ backend 相關段落已過時 |
| **PhyloWGS review** | 「topology 變動與連續 mass 更新分開」的 sampler 教訓 | 若改 M6 sampler 時參考 | 針對舊 C++ backend 的段落 |

**依整合優先序閱讀：** B04 → B07 → B03 → B02 → B05 → B01，然後 PhyClone `zh-TW/04_CODE_MAPPING.md`、`06_ASSUMPTIONS_LIMITATIONS.md`。A 類五篇只在設計評估時需要。

---

## 5. 發現的過時內容與不一致

HCC1395 目錄的過時內容已於 2026-10-16 刪除，分 6 個 commit（`89bf0ba`…`b938ab3`）保存：C++ finite-K backend 相關段落、K4／K6／K8 pilot 對照、舊 pipeline 模塊邊界、失效的 `golden_tree/` 與 `data.md` 等連結。舊內容可由 `git show <commit>^:<path>` 取回。

| 位置 | 仍待處理 |
|---|---|
| `INTERSECTION_SUMMARY.md` | 自述只整合四篇，但後段又補 B08，與 README 的 13 篇分類並行，容易誤讀為獨立結論 |

---

## 6. 建議的後續整理（尚未執行，需你決定）

1. **合併綜整檔**：把 `INTERSECTION_SUMMARY.md` 與 `B_SUMMARY.md` 的候選表併入 `SEARCH_LOG.md`；`README.md` 保留篇數聲明與閱讀路線；其餘重述改成連結（處理 D2–D5）。
2. **PhyClone 筆記單語化**：確定以 `zh-TW/` 為主，英文版移到 `notes/en/` 或標記為翻譯來源（D1）。
3. **回寫 `plan.md` 三個缺口**：K6 報告方式、K9 tagging 前 holdout、K10 是否允許重新分群。
4. 把本文件加入 `research/INDEX.md`（已加）。
