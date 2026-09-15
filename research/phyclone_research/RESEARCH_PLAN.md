# PhyClone Research Analysis Plan

## 1. Objective

本研究任務的目的不是單純摘要 PhyClone 論文，而是利用：

- Main paper
- Supplementary material
- XLSX experimental results
- GitHub implementation

重建並驗證完整的研究邏輯：

```text
Research Problem
      ↓
Motivation / Gap
      ↓
Core Idea
      ↓
Input Data
      ↓
Model
      ↓
Inference
      ↓
Output
      ↓
Experiments
      ↓
Results
      ↓
Supported Claims
      ↓
Assumptions / Limitations
      ↓
Contribution
```

最終成果必須做到：

1. 能快速理解整篇論文。
2. 能追溯重要結論的證據來源。
3. 能區分論文描述、程式實作與分析推論。
4. 能將 paper、supplement、XLSX、code 相互驗證。
5. 能直接轉化成教授報告與後續研究筆記。

---

# 2. Workspace

唯一工作目錄：

```text
/bip8_disk/boyu114/main_work/research/phyclone_research
```

所有：

- 讀取
- 搜尋
- 分析
- scripts
- intermediate outputs
- final notes

都必須限制在此目錄內。

不得主動讀取此目錄之外的資料。

若某項必要資源不在此 workspace：

```text
UNRESOLVED: required resource is outside WORKSPACE_ROOT
```

不要自行到其他 filesystem location 尋找。

---

# 3. Source Policy

預期研究來源包括：

```text
phyclone_research/
├── sources/
│   ├── main paper
│   ├── supplementary material
│   └── XLSX results
│
├── repo/
│   └── PhyClone implementation
│
├── .agent_workspace/
│
└── notes/
```

實際檔名可能不同。

分析開始時應先建立 inventory，而不是假設固定檔名。

原始資料視為 read-only：

- PDF
- XLSX
- repository source
- experiment data

不要修改原始內容。

---

# 4. Primary Research Questions

最終分析必須能回答以下問題。

## Research motivation

1. PhyClone 想解決什麼問題？
2. 為什麼 cancer phylogeny reconstruction 重要？
3. 過去方法有哪些主要限制？
4. 作者認為真正困難的地方是什麼？

## Method

5. PhyClone 的核心 idea 是什麼？
6. Input 是什麼？
7. Mutation 如何表示？
8. Clone / cluster 如何表示？
9. Tree / forest 如何表示？
10. Copy number、tumour content、VAF 如何進入模型？
11. likelihood 如何定義？
12. prior 如何定義？
13. clonal prevalence / cellular prevalence 如何處理？
14. inference 如何進行？
15. preprocessing / pre-clustering 的角色是什麼？
16. outlier model 如何工作？
17. 最終輸出是什麼？

## Experiments

18. 每個主要 experiment 想回答什麼問題？
19. 使用什麼 dataset？
20. synthetic data 如何產生？
21. 使用哪些 baselines？
22. 使用哪些 metrics？
23. paper 的主要結果是什麼？
24. XLSX 是否支持論文中的圖與結論？
25. 哪些結果有 statistical / experimental caveat？

## Implementation

26. paper 中主要模型在 code 的哪裡？
27. equations 如何映射到 implementation？
28. paper 與 code 是否一致？
29. code 是否存在 paper 沒描述的重要細節？
30. default parameters 與 implementation choices 是什麼？

## Interpretation

31. PhyClone 的核心 contribution 是什麼？
32. biological assumptions 是什麼？
33. statistical assumptions 是什麼？
34. computational assumptions 是什麼？
35. known limitations 是什麼？
36. 可以從模型或實作推論出哪些 failure cases？

---

# 5. Evidence Model

所有重要研究結論必須盡可能追溯 evidence。

使用三種 evidence type。

## STATED

```text
[STATED]
```

代表：

作者在 main paper 或 supplement 中明確表達。

---

## IMPLEMENTED

```text
[IMPLEMENTED]
```

代表：

可以從 repository source code 確認實際行為。

---

## INFERRED

```text
[INFERRED]
```

代表：

根據 paper、supplement、XLSX 或 code 合理推論，但作者沒有直接明講。

不得將 `INFERRED` 描述成作者的 explicit claim。

---

# 6. Evidence Location

## Main paper

優先記錄：

```text
Section
Subsection
Page
Equation
Figure
Table
```

## Supplement

優先記錄：

```text
Supplementary section
Page
Equation
Figure
Table
```

## XLSX

至少記錄：

```text
Workbook
Sheet
Columns
Rows / cell range
Experimental condition
Metric
```

## Code

至少記錄：

```text
File path
Module
Class
Function
Relevant implementation logic
```

---

# 7. Conflict Policy

若來源不一致：

```text
paper ≠ supplement
paper ≠ XLSX
paper ≠ code
supplement ≠ code
```

不得默默選擇其中一方。

記錄成：

```text
CONFLICT

Claim:
...

Source A:
...

Source B:
...

Possible explanation:
...

Status:
UNRESOLVED / RESOLVED
```

只有證據充分時才能標記 `RESOLVED`。

---

# 8. Multi-Agent Strategy

本研究採：

```text
Shared Read
+
Isolated Write
+
Single Integrator
```

多個 Agent 可以同時讀取：

```text
sources/
repo/
```

但是不能共同修改同一份 intermediate output。

---

# 9. Agent Workspace

建立：

```text
.agent_workspace/
├── paper/
├── supplement/
├── xlsx/
├── code/
├── methods/
├── experiments/
├── reviewer/
└── integrator/
```

每個 Agent 只能寫自己的 directory。

所有正式研究結果：

```text
notes/
```

只能由 Integrator 修改。

---

# 10. Agent Roles

## A. Paper Analyst

主要負責：

```text
Research question
Motivation
Existing gap
Core idea
Method overview
Major equations
Experiments
Results
Claims
Contribution
Author-stated limitations
```

不要逐頁摘要。

優先重建：

```text
Problem
→ Gap
→ Core Idea
→ Method
→ Evidence
→ Contribution
```

Output：

```text
.agent_workspace/paper/
```

建議內容：

```text
research_story.md
claims.md
methods.md
experiments.md
figures_tables.md
assumptions.md
unresolved.md
```

---

## B. Supplement Analyst

主要負責尋找 main paper 沒有完整描述的內容：

```text
mathematical derivations
algorithm details
parameter settings
simulation procedures
dataset details
additional experiments
sensitivity analyses
extra figures/tables
assumptions
limitations
implementation clues
```

核心 mapping：

```text
Main Paper Concept
        ↓
Supplementary Evidence
```

Output：

```text
.agent_workspace/supplement/
```

---

## C. XLSX Analyst

首先理解 workbook schema：

```text
Workbook
 └── Sheet
      ├── Dataset
      ├── Condition
      ├── Method
      ├── Metric
      ├── Replicate
      └── Result
```

然後嘗試建立：

```text
Paper Figure / Table
        ↓
XLSX Sheet
        ↓
Rows / Columns
        ↓
Metric
        ↓
Reconstructed Result
```

主要任務：

- 找 dataset names
- 找 baselines
- 找 experimental conditions
- 找 metrics
- 找 replicates
- 找 sample counts
- 找 noise conditions
- 重建關鍵 reported results
- 找 outliers / anomalies

若無法可靠對應：

```text
UNRESOLVED
```

Output：

```text
.agent_workspace/xlsx/
```

---

## D. Code Analyst

不要只閱讀 README。

深入追蹤真正實作：

```text
input processing
model
likelihood
prior
cluster representation
tree representation
cellular prevalence
clonal prevalence
CNV
tumour content
outlier handling
pre-clustering
MCMC / VI
proposal moves
split / merge / move
result generation
evaluation
default parameters
```

核心 mapping：

```text
Paper Concept
      ↓
Equation / Algorithm
      ↓
Source Module
      ↓
Class / Function
      ↓
Data Structure
      ↓
Runtime Behavior
```

Output：

```text
.agent_workspace/code/
```

---

# 11. Cross-Validation Agents

第一階段分析完成後，再執行 cross-validation。

---

## E. Methods Validator

主要比較：

```text
Main Paper
vs
Supplement
vs
Code
```

聚焦：

- model definition
- likelihood
- prior
- cellular prevalence
- clonal prevalence
- tree representation
- inference
- preprocessing
- outlier model
- parameters

尋找：

```text
EXACT
APPROXIMATE
PAPER_ONLY
CODE_ONLY
ADDITIONAL_IMPLEMENTATION_DETAIL
POSSIBLE_MISMATCH
```

Output：

```text
.agent_workspace/methods/
```

---

## F. Experiment Validator

主要比較：

```text
Paper
+
Supplement
+
XLSX
+
Evaluation Code
```

每個 experiment 都重建：

```text
Research Question
        ↓
Dataset
        ↓
Setup
        ↓
Baseline
        ↓
Metric
        ↓
Raw / XLSX Evidence
        ↓
Reported Result
        ↓
Interpretation
        ↓
Supported Claim
```

Output：

```text
.agent_workspace/experiments/
```

---

# 12. Parallel Execution

能獨立分析的工作應平行進行。

推薦 DAG：

```text
                         Root / Coordinator
                                │
                                ▼
                         Workspace Scan
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
   Paper Analyst       Supplement Analyst        XLSX Analyst
         │                      │                      │
         └──────────────┐       │       ┌──────────────┘
                        ▼       ▼       ▼
                         Code Analyst
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       Methods Validator              Experiment Validator
              │                               │
              └───────────────┬───────────────┘
                              ▼
                          Integrator
                              │
                              ▼
                           Reviewer
                              │
                              ▼
                          Integrator
                              │
                              ▼
                        Final Research Notes
```

Paper、Supplement、XLSX、Code analysis 應盡量平行。

Methods 與 Experiments validation 也可以平行。

---

# 13. Write Isolation

禁止：

```text
Agent A ─┐
         ├─> same_file.md
Agent B ─┘
```

必須使用：

```text
Agent A → .agent_workspace/a/
Agent B → .agent_workspace/b/

                 ↓

             Integrator

                 ↓

               notes/
```

避免：

- race conditions
- overwrites
- partial writes
- contradictory edits
- shared append logs

---

# 14. Integration Barrier

Integrator 開始產生正式 `notes/` 之前，至少需要：

```text
Paper analysis
Supplement analysis
XLSX analysis
Code analysis
Methods validation
Experiment validation
```

完成或標記：

```text
COMPLETE
PARTIAL
FAILED
```

某個 Agent 失敗不應阻止其他分析。

缺失部分標：

```text
UNRESOLVED
```

---

# 15. Integrator

Integrator 是唯一可寫：

```text
notes/
```

的 Agent。

Integrator 必須：

1. 合併 findings。
2. 去除重複內容。
3. 解決 terminology inconsistency。
4. 保留真正 conflict。
5. 重新檢查 high-risk claims。
6. 區分 STATED / IMPLEMENTED / INFERRED。
7. 不因某個 Agent 的結論而自動採信。
8. 必要時重新讀 source 驗證。

---

# 16. Required Deliverables

建立：

```text
notes/
├── 00_SOURCE_MAP.md
├── 01_PAPER_BIG_PICTURE.md
├── 02_METHODS_DEEP_DIVE.md
├── 03_EXPERIMENTS_RESULTS.md
├── 04_CODE_MAPPING.md
├── 05_EVIDENCE_MATRIX.md
├── 06_ASSUMPTIONS_LIMITATIONS.md
└── 07_PRESENTATION_BRIEF.md
```

---

# 17. 00_SOURCE_MAP.md

包含：

## Workspace inventory

列出實際找到的：

- main paper
- supplement
- XLSX
- repository
- result files

## Source roles

說明每個 source 在研究中的用途。

## Repository architecture

聚焦研究相關 modules，而不是列出所有 files。

## XLSX schema

描述：

```text
Sheet
Dataset
Condition
Method
Metric
Replicate
Result
```

## Source relationship

建立：

```text
               Main Paper
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
 Supplement     XLSX       Repository
```

---

# 18. 01_PAPER_BIG_PICTURE.md

回答：

```text
Problem
↓
Gap
↓
Core Idea
↓
Method
↓
Experiments
↓
Results
↓
Contribution
```

包含：

## One-sentence summary

## Research question

## Why the problem matters

## Existing gap

## Core idea

## Major contribution

## Architecture

```text
Input
  ↓
Preprocessing
  ↓
Model
  ↓
Inference
  ↓
Output
  ↓
Evaluation
```

目標是讓讀者先理解整篇 paper，而不是先看到公式。

---

# 19. 02_METHODS_DEEP_DIVE.md

依照研究邏輯整理，而不是 paper 頁碼順序。

包含：

```text
Input
Variables
Preprocessing
Model
Likelihood
Prior
Tree representation
Prevalence
Inference
Outliers
Parameters
Output
```

每個重要公式使用：

```text
Equation
↓
Variables
↓
Biological Meaning
↓
Statistical Meaning
↓
Inference Role
↓
Implementation Mapping
```

每個重要數學符號都要解釋。

---

# 20. 03_EXPERIMENTS_RESULTS.md

每個 experiment 使用統一格式：

```text
Question
↓
Dataset
↓
Setup
↓
Baseline
↓
Metric
↓
Result
↓
Interpretation
↓
Supported Claim
```

若有 XLSX：

補上：

```text
Workbook
Sheet
Rows / Columns
Reconstructed value
```

避免模糊描述：

```text
PhyClone performed better.
```

應盡量說明：

- better on what metric
- under what condition
- compared with what baseline
- by how much
- where the evidence is

---

# 21. 04_CODE_MAPPING.md

建立：

| Paper concept | Paper location | Source file | Function/Class | Implementation | Match |
|---|---|---|---|---|---|

Match 使用：

```text
EXACT
APPROXIMATE
ADDITIONAL_IMPLEMENTATION_DETAIL
PAPER_ONLY
CODE_ONLY
POSSIBLE_MISMATCH
```

優先追蹤最重要的 computational concepts。

---

# 22. 05_EVIDENCE_MATRIX.md

建立：

| Claim | Main Paper | Supplement | XLSX | Code | Type | Confidence |
|---|---|---|---|---|---|---|

Type：

```text
STATED
IMPLEMENTED
INFERRED
```

Confidence：

```text
HIGH
MEDIUM
LOW
UNRESOLVED
```

只收錄真正重要 claim，不需要把所有細節都放進 matrix。

---

# 23. 06_ASSUMPTIONS_LIMITATIONS.md

分成：

## Biological assumptions

## Statistical assumptions

## Computational assumptions

## Dataset assumptions

## Known limitations

作者明確描述。

## Inferred limitations

分析後合理推論，但作者未直接聲稱。

標記：

```text
[INFERRED]
```

## Failure cases

描述：

```text
Condition
→ Why model may fail
→ Evidence / reasoning
```

---

# 24. 07_PRESENTATION_BRIEF.md

用於 10–15 分鐘教授報告。

## One sentence

一句話說明 PhyClone。

## 30-second version

```text
Problem
→ Method
→ Main Result
```

## 3-minute version

```text
Problem
→ Gap
→ Core Idea
→ Model
→ Experiments
→ Results
→ Contribution
```

## 10–15 minute presentation

建議約：

```text
8–12 slides
```

每頁包含：

```text
Slide title
Key message
Evidence
Suggested visual
Speaker point
```

Presentation 優先呈現：

```text
Why
↓
Core Idea
↓
How
↓
Evidence
↓
Assumptions / Limitations
↓
Contribution
```

不要把所有 Methods 細節塞進簡報。

---

# 25. Reviewer

Integrator 第一版完成後，由獨立 Reviewer 檢查。

Reviewer 不直接修改 `notes/`。

輸出：

```text
.agent_workspace/reviewer/review_report.md
```

檢查至少包含：

- unsupported claims
- missing evidence
- incorrect citations
- STATED / IMPLEMENTED / INFERRED confusion
- paper vs supplement mismatch
- paper vs code mismatch
- paper vs XLSX mismatch
- incorrect equation interpretation
- incorrect figure/table mapping
- missing biological assumptions
- missing statistical assumptions
- missing limitations
- overclaiming
- logical gaps
- presentation unnecessary detail

---

# 26. Final Revision

Reviewer 完成後，由 Integrator：

1. 閱讀 review report。
2. 重新驗證重要問題。
3. 修正 `notes/`。
4. 保留無法解決的 conflict。
5. 將證據不足項目標記 `UNRESOLVED`。

Reviewer 不直接修改 canonical output。

---

# 27. High-Risk Claims

以下內容應優先取得多來源或獨立驗證：

```text
Core contribution
Likelihood definition
Prior definition
Clonal prevalence treatment
Cellular prevalence treatment
Inference algorithm
Outlier handling
Copy-number handling
Main experiment conclusions
Paper ↔ XLSX mapping
Paper ↔ code mapping
Major biological assumptions
```

不要只依賴單一 Agent 的 interpretation。

---

# 28. Quality Standard

最終研究筆記應優先做到：

```text
Correct
↓
Traceable
↓
Internally consistent
↓
Easy to explain
↓
Concise
```

不要追求：

```text
Longest possible summary
```

而應追求：

```text
Smallest complete model of the paper
```

---

# 29. Completion Criteria

只有在以下條件達成後才視為完成：

- [ ] Source map 已建立
- [ ] Research question 已明確
- [ ] Main method architecture 已重建
- [ ] 主要 equations 已解釋
- [ ] Major experiments 已重建
- [ ] XLSX schema 已理解
- [ ] 關鍵 XLSX ↔ paper mapping 已嘗試
- [ ] Paper ↔ code mapping 已完成
- [ ] Assumptions 已分類
- [ ] Limitations 已分類
- [ ] Important conflicts 已記錄
- [ ] Evidence matrix 已建立
- [ ] Presentation brief 已完成
- [ ] Reviewer pass 已完成
- [ ] Unsupported claims 已處理
- [ ] 所有 unresolved issues 已明確列出

---

# 30. Final Summary

完成後提供簡短 execution summary：

```text
Research analysis completed.

Workspace:
 /bip8_disk/boyu114/main_work/research/phyclone_research

Completed:
 - Paper analysis
 - Supplement analysis
 - XLSX analysis
 - Code analysis
 - Methods validation
 - Experiment validation
 - Integration
 - Review

Generated:
 notes/00_SOURCE_MAP.md
 notes/01_PAPER_BIG_PICTURE.md
 notes/02_METHODS_DEEP_DIVE.md
 notes/03_EXPERIMENTS_RESULTS.md
 notes/04_CODE_MAPPING.md
 notes/05_EVIDENCE_MATRIX.md
 notes/06_ASSUMPTIONS_LIMITATIONS.md
 notes/07_PRESENTATION_BRIEF.md

Important conflicts:
 ...

Unresolved:
 ...

Most important research finding:
 ...

Recommended reading order:
 01_PAPER_BIG_PICTURE.md
 → 02_METHODS_DEEP_DIVE.md
 → 03_EXPERIMENTS_RESULTS.md
 → 05_EVIDENCE_MATRIX.md
 → 07_PRESENTATION_BRIEF.md
```

---

# Guiding Principle

Do not merely summarize the paper.

Reconstruct and verify the research argument:

```text
Paper
+
Supplement
+
Experimental Results
+
Implementation
        ↓
Cross-validation
        ↓
Evidence-backed Research Understanding
```

All work must remain inside:

```text
/bip8_disk/boyu114/main_work/research/phyclone_research
```