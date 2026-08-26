# PhyClone 與目前 repo 的 VAF / q 公式核對

更新日期：2026-08-25

## 結論先講

目前 repo 的 `q` 不是 PhyClone 完整的 genotype-aware emission；它是較簡化的特例：固定 normal CN=`2`、把 purity 當作 tumor mixture、把 copy-number uncertainty 壓縮成 latent multiplicity `m`，並只使用 Binomial emission。

目前 active Python／C++ runtime 仍是這個 `q` baseline；本輪 `model.md` 改記錄
PhyClone `xi` 與 `error_rate=0.001` 的文件 target，尚未代表 runtime 已切換。

PhyClone 使用的是對三種細胞 population 與候選 genotype 做 DNA-copy-weighted 的 ALT probability，論文符號為 `xi`，官方程式中可看到 `e_vaf`／population mixture 計算。

## 1. PhyClone 的公式

主論文把 allele-count likelihood 寫成：

```text
p(X | rho, b, T) = product_n f(x_n | rho_bar_{v_n})
```

完整的 allele emission 在 Supplementary Methods S1.1；來源是：

- [PhyClone_paper.xml](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone_paper.xml)，`sec5`、`sec7`、`E1`、`E2`
- [supp.pdf](/bip8_disk/boyu114/main_work/research/phyclone/paper_supplement/content/supp.pdf)，S1.1–S1.2

對一個候選 genotype `G`，先定義 genotype 內的 ALT fraction：

```text
mu(G) = clamp(b(G) / c(G), error_rate, 1-error_rate)
```

再把 normal、未帶 mutation 的 tumor、帶 mutation 的 tumor 三個 population 混合：

```text
w_N = 1 - tumour_content
w_R = tumour_content × (1 - CCF)
w_V = tumour_content × CCF
```

```text
xi(G, CCF, tumour_content) =
    [ w_N c(G_N) mu(G_N)
    + w_R c(G_R) mu(G_R)
    + w_V c(G_V) mu(G_V) ]
    /
    [ w_N c(G_N)
    + w_R c(G_R)
    + w_V c(G_V) ]
```

最後才使用 allele counts：

```text
ALT_count ~ Binomial(total_count, xi)
```

或在 overdispersion 模型下使用 Beta-Binomial。

官方程式來源：

- [math_utils.py:216](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/utils/math_utils.py:216)
- [math_utils.py:228](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/utils/math_utils.py:228)
- [pyclone.py:299](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/pyclone.py:299)
- [pyclone.py:324](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/pyclone.py:324)

## 2. PhyClone 的 genotype candidates

PhyClone 不只猜一個 `m`。它會建立不同 CN timing 的候選 genotype：

```text
mutation before CN event:
    CN = (normal_cn, normal_cn, total_cn)
    mu = (error_rate, error_rate, m / total_cn)

mutation after CN event:
    CN = (normal_cn, total_cn, total_cn)
    mu = (error_rate, error_rate, 1 / total_cn)
```

候選 genotype 以 `pi_c` 邊際化：

```text
P(data | CCF) = sum_c pi_c × P(data | xi_c)
```

這表示 PhyClone 同時保留：

- normal CN
- reference tumor CN
- variant tumor CN
- mutation 是在 CN event 前或後發生
- ALT copy 數與 genotype uncertainty

官方 schema、loader 與 candidate builder：

- [PhyClone_schema.json:21-65](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/validator/PhyClone_schema.json:21)
- [pyclone.py:324-352](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/data/pyclone.py:324)
- [test_load_pyclone_data.py:21-59](/bip8_disk/boyu114/main_work/research/phyclone/PhyClone/phyclone/tests/unit_tests/test_load_pyclone_data.py:21)

官方 v0.8.0 code 預設 `error_rate=0.001`、`tumour_content=1.0`；這些是 PhyClone 的設定，不是目前 repo 的 active contract。

## 3. 目前 repo 的 q

目前 Python 與 C++ 都是：

```text
q_repo =
    rho_ASCAT × phi × multiplicity
    --------------------------------
    (1-rho_ASCAT)×2 + rho_ASCAT×total_cn
```

來源：

- [model.py:333-342](/bip8_disk/boyu114/main_work/tumor_tree_pipeline/model.py:333)
- [model.cpp:206-212](/bip8_disk/boyu114/main_work/inference/src/model.cpp:206)

這個公式隱含：

```text
normal_cn = 2
non-mutated tumor 與 mutated tumor 使用同一個 total_cn denominator
normal population 不帶 ALT
完整 genotype uncertainty 被壓縮成 multiplicity m
rho_ASCAT 同時扮演 purity / tumor-content mixture 的角色
```

目前 repo 沒有 `normal_cn`、`tumour_content`、reference/variant genotype 或 CN timing 的輸入欄位。`phi` 是 tree node 加 descendants 的 cumulative prevalence；`m` 是模型內部的 latent multiplicity。

## 4. 兩者何時會相同？

如果 PhyClone 使用：

```text
normal_cn = 2
reference tumor CN = variant tumor CN = total_cn
normal/reference 沒有 ALT
error_rate = 0
```

它的 post-CN 特例會化成：

```text
q = tumour_content × CCF
    ------------------------------
    (1-tumour_content)×2 + tumour_content×total_cn
```

這在符號上和目前 repo 的 q 相同（將 `tumour_content` 對應到 `rho_ASCAT`、CCF 對應到 `phi`、且 `m=1`）。

因此目前 repo 不是完全錯，而是把 PhyClone 的複雜 genotype model 壓成一個 restricted special case。

## 5. 數值例子

為了比較公式，先使用同一個 mixture 值 `t=0.6`、`CCF=0.5`：

| normal CN | total CN | m | repo q | PhyClone pre-CN | PhyClone post-CN |
|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 1 | 0.15000 | 0.15000 | 0.15000 |
| 2 | 4 | 1 | 0.09375 | 0.11538 | 0.09375 |
| 2 | 4 | 2 | 0.18750 | 0.23077 | 不適用 |
| 1 | 3 | 1 | 0.11538 | 0.18750 | 0.13636 |

解讀：

- diploid CN 下，兩者可相同。
- normal CN=`2`、post-CN、`m=1` 時，兩者可相同。
- CN 改變且 mutation 可能早於 CN event 時，PhyClone 會產生不同 q。
- normal CN 不等於 `2` 時，目前 repo 會產生結構性差異。

## 6. 目前驗證邊界

目前 repo tests 只驗證 Python/C++ 內部一致性、likelihood matrix 與 smoke oracle；沒有測試「repo q 是否等於 PhyClone q」。另外，現有 `smoke.cpp` oracle 在 production q 已包含 `site.purity` 的情況下，仍把 `cellular_fraction` 再乘一次 `0.99`；Release build 因 `NDEBUG` 會關閉 `assert`，因此表面上可通過，但 Debug CTest 實際在該 assertion 失敗。這是 repo 內部 oracle 不一致，並非 PhyClone 公式差異。

此外，PhyClone 的官方 targeted tests 在目前環境因缺少 `numba` 尚未執行；本次結論是由論文、supplement、官方 source、schema 與官方 tests 靜態交叉核對而來。

## 7. 其他 primary literature 的交叉支持

這些論文不是 PhyClone `xi` 的逐字重複證明，而是獨立支持其核心 observation model：VAF 需要由 purity／tumour content、copy number、mutation multiplicity 或 genotype mixture 共同決定，不能直接把 VAF 當成 CCF。

- [ABSOLUTE (Carter et al., 2012)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4383288/) 將 purity、local copy number 與 mutation multiplicity 放進 expected mutant allele fraction；其 denominator 具有 `purity × tumour CN + 2 × (1-purity)` 的相同 DNA-mass-balance 結構。
- [PyClone (Roth et al., 2014)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4864026/) 使用 allele counts、tumour content、allele-specific copy number 與 genotype prior，並對 genotype candidate 做 likelihood marginalization；PhyClone 的 emission 是此模型家族的延伸。
- [PhyloWGS (Deshwar et al., 2015)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4359439/) 顯式處理 mutation 與 CNV timing，支持相同 mutation 在 CN event 前後必須有不同 expected VAF。
- [PyClone-VI (Gillis and Roth, 2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/) 在不同 tumour content、copy number、depth 的 simulated data 上評估 purity/CN-aware CCF inference，支持此模型家族的 simulation validation。
- [DeCiFer (Satas et al., 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8542635/) 顯示 genotype mixture、mutation multiplicity 與 copy-number loss 會造成 bulk VAF 的不可識別性；這是對 PhyClone 公式適用範圍的重要限制，而不是公式本身的反證。
- [CNAqc (Antonello et al., 2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10832148/) 以 purity、copy-number state 與 multiplicity 計算 expected VAF profile，並用 simulation、single-cell pseudo-bulk 與 real cancer data 做 QC 驗證，提供較新的外部支持。

因此，外部證據支持的是「DNA-copy-weighted expected VAF 是合理且反覆使用的 observation model」，不是「每一個真實 locus 的 `xi` 都可被視為無偏真值」。

## 8. 可信度分級

| 對象 | 判定 | 理由 |
|---|---|---|
| PhyClone `xi` 的數學結構 | 高 | 與 DNA copy-number mass balance 一致，並獲 ABSOLUTE、PyClone、PhyloWGS 等獨立方法支持。 |
| PhyClone paper／supplement／官方 code 一致性 | 高 | v0.8.0 的 `e_vaf`、population weights、CN timing、candidate prior 與 supplement 對得上。 |
| PhyClone 在其假設成立時的 expected VAF | 高至中高 | simulation、posterior／marginalization tests 與 real-data downstream validation 支持，但多數是 model-consistent validation。 |
| 每個真實 bulk locus 的 VAF 真值 | 中或更低 | 受 subclonal CNV、LOH、mapping bias、normal genotype、overdispersion 與 purity 語意影響。 |
| 目前 repo 的簡化 `q` 作為完整 PhyClone 模型 | 不足以稱高 | 它只涵蓋固定 normal CN=2、單一 tumour CN denominator、簡化 multiplicity 的 restricted special case。 |

最重要的限制是 bulk VAF 的 non-identifiability：不同的 CCF、multiplicity、CN timing 或 genotype mixture 可能產生相同 VAF。因此「q 的 observation model 合理」與「由 q 唯一反推出真實 clone state」必須分開判斷。

因此最準確的結論是：

> 目前 repo 的 q 是 PhyClone `xi` 的簡化特例，不是完整的 PhyClone VAF / genotype emission。兩者在 diploid、post-CN、`m=1` 等條件下可以相同，但在 normal CN、CN timing、genotype candidate 與 tumour content 不同時會有系統性差異。
