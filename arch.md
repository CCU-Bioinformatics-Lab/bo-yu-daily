# Tumor-tree research architecture

更新日期：2026-08-21

![alt text](image.png)

## 四個模塊與文件引用

| 模塊 | 核心文件 | 大致責任 |
|---|---|---|
| `data input` | [`data.md`](data.md) | 定義資料來源、provenance，以及交給 model 的資料介面 |
| `model` | [`model.md`](model.md) | 定義研究要解的 model、posterior 與參數語意 |
| `inference_algo` | [`inference_algo.md`](inference_algo.md) | 定義如何根據 model 進行參數推理；可替換 MCMC、MAP、VI 或其他方法 |
| `output` | [`output.md`](output.md) | 定義如何解讀推理結果，例如 topology、CCF 與 SNV assignment |

## 文件之間的關係

### 1. `data input → model`

`data.md` 提供 model 所需的資料介面。只要新的 data input 模塊能產生相同
的 model input contract，資料來源或前處理流程就可以替換。

### 2. `model → inference_algo`

`model.md` 定義 inference algorithm 必須解的目標與參數語意。inference
algorithm 可以替換，但必須遵守 model 所定義的 input、state 與 posterior
contract。

### 3. `inference_algo → model`

這個回圈代表 inference algorithm 會反覆將候選參數交回 model 評分，取得
下一個推理狀態；它不代表 inference algorithm 會修改 `model.md`。

### 4. `model → output`

`model.md` 定義輸出參數的意義，`output.md` 負責把這些參數轉成容易理解的
拓樸、CCF 與 SNV assignment 表示方式。

## 可替換模塊的邊界

```text
data input     可替換資料來源與建表流程
model          可替換 posterior／likelihood 定義
inference_algo 可替換參數推理方法
output         可替換結果呈現方式
```

四個文件各自描述一個模塊的 contract，不在彼此之間重複實作細節。研究流程
只需要確認相鄰模塊的輸入／輸出 contract 相容，就能替換其中一個模塊而不必
重寫整個研究架構。
