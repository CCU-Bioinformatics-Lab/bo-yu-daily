# s1b 草圖：旋鈕說明頁 p3–p6（2026-11-01）

依 OUTLINE v5。四頁同一套三欄版面，位置相同。只用真實 HCC1395 的數值，不放模擬比較，不提 HG008。

## 共用版面（SVG 1664×572，佔內容區 69%）

```
 真實 long read 看到什麼            旋鈕                 輸出多了什麼
┌──────────────────────────┐      ┌─────────────┐      SNV1 的輸出一列 (實際結果)
│(示意) read 堆疊示意        │      │diplosim 面板 │      ┌ ref、alt          ref 36、alt 21 ┐
│  HP1 ═══●═══              │ 模仿 │ 組名         │ 改動 │ allele A、B copy number  1、1  │
│  HP2 ═══○═══              │ ───▶ │ ◎ 旋鈕名     │ ───▶ │ 帶 SNV 的份數              1   │
└──────────────────────────┘      │   預設值     │      │ clone、CCF       trunk、1.0    │
┌──────────────────────────┐      └─────────────┘      │ HP1      ref 0    alt 19       │
│(實際結果) HCC1395 long read│      ┌/////////////┐      │ HP2      ref 27   alt 0        │
│  數值長條或數字卡          │      │CONIPHER：沒有│      │ unphased ref 9    alt 2        │
└──────────────────────────┘      │  一句說明    │      │ 真值：SNV 在 allele  A（HP1）   │
                                  └/////////////┘      └ ▭ 橘框＝這組旋鈕改動的欄位 ───┘
```

- 旋鈕圖示、組名、旋鈕名、預設值照 `t1-knobs`：藍指針＝有值，灰指針＝關閉或 0。
- 右欄數值照 `t1-machines`／BRIEF 貫穿例子（`data/diplosim_default_seed1/diplosim.tsv` chr7:21,792,655）。「帶 SNV 的份數」是同一列的 `MUT_CN` 1.0，這兩頁沒有顯示，這裡新增。
- 左下「實際結果」的資料：HCC1395 ONT `t50_n00`（nominal purity 1；ASCAT 實測 purity 0.97，R4）。

## p3 k-allele

```
示意： SNV1: HP1 read 帶 alt●，HP2 read 是 ref○ │ SNV2: 反過來
實際： [■■■■ HP1 14,707 ■■■■|■■■ HP2 14,261 ■■■]  一半┆  HP2 占 49.2%
旋鈕： SNV 的 allele ── allele B 機率 0.5      CONIPHER：沒有／SNV 一律在 allele A
輸出： 真值列整列橘框；HP1 的 alt 19、HP2 的 alt 0 橘框
```

| 數字 | 來源 |
|---|---|
| 14,707／14,261／49.2% | 〔實測〕`lab_report/2026-11-01_diplosim_detection_curve/t50_n00/tables/real_per_snv.tsv` 重算：alt ≥ 5、VAF ≥ 0.10（purity holdout v2 的硬門檻），tagged alt ≥ 3，alt 在某條 HP ≥ 90%。同表用 alt ≥ 3、VAF ≥ 0.08 是 14,747／14,341（49.3%） |
| 預設 0.5 | 〔程式〕`diplosim/src/params.rs:112`；DECISIONS 2026-10-30（使用者決定，對稱，不是由資料校正） |
| CONIPHER 一律 allele A | 〔程式〕DECISIONS 2026-10-30「對稱改名」列 |

## p4 k-tag

```
示意(推論)： ◆germline 差異位置 ……◆
            HP1 ════○══  HP1 ════●══   (蓋到左邊◆)
            HP2      ══○════  (蓋到右邊◆)
            unphased  ══●══   沒蓋到◆ → unphased
實際： 全部 read [有 HP 標記 86.2% | unphased 13.8%]
      各位點的標記比例 SD 0.254；[…… | 標記比例 < 0.5 的位點 10.3%]
旋鈕： HP 標記 ── 標記比例 0.8（暫定）、位點間差異 關閉   CONIPHER：沒有／不分 HP
輸出： unphased 整列橘框
```

| 數字 | 來源 |
|---|---|
| 13.8% | 〔實測〕R5 `t50_n00/tables/ppc_stats.tsv` real `HP0_frac_pooled` 0.138 |
| SD 0.254 | 〔實測〕同表 `tag_frac_SD_sites` 0.2542（depth ≥ 20 的位點） |
| 10.3% | 〔實測〕同表 `tag_frac_lt_0.5_sites` 0.1026 |
| 沒蓋到 germline 差異位置 → unphased | 〔推論〕OUTLINE v5 |
| 0.8（暫定）、關閉 | 〔程式〕`params.rs:113-114`；DECISIONS 2026-10-30（0.8 是使用者暫定整數）、2026-10-31（`tag_concentration`） |

## p5 k-error

```
示意： SNV1: HP1 ●●○(①鹼基讀錯)  HP2 ○●(②HP 標錯)○
      SNV2: HP1 ●●●              HP2 [●●](③標錯集中)○
實際： [alt 在兩條 HP 的 SNV 2.7%] [另一條 HP alt ≥ 2 的位點 2.4%] [VAF 90% 分位 0.97，不是 1]
旋鈕： read 錯誤 ── 鹼基讀錯 關閉、HP 標錯 關閉、標錯集中 關閉   CONIPHER：沒有／沒有 read 錯誤
輸出： HP1 的 ref 0、HP2 的 alt 0 橘框（預設關閉，所以是 0）
```

| 數字 | 來源 |
|---|---|
| 2.7% | 〔實測〕R5 `split_alt_frac` 0.02717 |
| 2.4% | 〔實測〕`lab_report/2026-11-01_diplosim_split_alt_mistag/README.md` §3 表 `t50_n00`「O 上 alt ≥ 2 的位點」 |
| 0.97 | 〔實測〕R5 `VAF_q90` 0.9697 |
| 錯誤怎麼作用 | 〔程式〕`diplosim/src/hp.rs:117-124`（`base_error` 在 HP 內 ref↔alt 互換；mistag 把 read 換到另一條 HP，`mistag_concentration` 讓每個位點有自己的機率） |
| 預設都關閉 | 〔程式〕`params.rs:115-117`；DECISIONS 2026-10-31、2026-11-01 |

## p6 k-cn（C-19：份數圖照時間順序）

```
份數 ■HP1 ■HP2                                     帶 SNV 2 份
 ■■(HP2)      LOH     ■■      SNV     ■■      gain    ■●■
 ■■(HP1)     ─────▶   ■■     ─────▶   ■●■    ─────▶   ■●■
                                                       ■■■
 1＋1               2＋0             2＋0             3＋0
 事件前             LOH 後           SNV 出現          gain 後
實際： [先 LOH 再 gain 的位點 20.7%] [帶 SNV ≥ 2 份的位點 43.9%] [較少那條 HP depth < 0.1 48.2%]
旋鈕： copy number ── 第二個 CN 事件 0   CONIPHER：沒有／每位置最多 1 個 CN 事件
輸出： allele A、B copy number 與 帶 SNV 的份數 兩列橘框（預設 0，所以是 1、1）
```

| 數字 | 來源 |
|---|---|
| 20.7% | 〔實測〕`lab_report/2026-10-31_cn_state_ascat_vs_diplosim/README.md` §1（ASCAT on HCC1395 long read，CN 是工具推論） |
| 43.9% | 〔實測，粗估〕同檔 §3 摘要表 multiplicity ≥ 2 0.439（round(VAF × total CN)） |
| 48.2% | 〔實測〕R5 `minorHP_depth_lt_0.1` 0.4822 |
| LOH → SNV → gain 得到 3 份中 2 份帶 SNV | 〔程式〕DECISIONS 2026-10-31（SNV 可夾在 cnloh 與 gain 之間，(3,0) mutated = 2） |
| 預設 0；CONIPHER 每位置最多 1 個 CNA | 〔程式〕`params.rs:96`；DECISIONS 2026-10-31（`evolution.py:308-320`） |

## 量測（F-2）

| 頁 | 圖外字數 | SVG 佔內容區 | 講稿字數（去空白） |
|---|---:|---:|---:|
| k-allele | 0 | 69% | 244 |
| k-tag | 0 | 69% | 233 |
| k-error | 0 | 69% | 244 |
| k-cn | 0 | 69% | 248 |

圖外字數不含段落標籤、標題、頁尾；文字全在 SVG 內。
