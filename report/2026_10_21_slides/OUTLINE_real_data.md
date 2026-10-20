# 追加大綱：新軟體怎麼用真實資料驗證（2026-10-20，v2 審查後）

使用者原話：「現在換成如何新軟體驗證真實資料部分」。
主問題（一句）：沒有 single-cell 真值時，新軟體在真實 long read 資料上是否比 PhyClone 好、而且結果可信？
使用者確認：四種檢查全放；可以點名 HCC1395（CASTLE 公開 ONT）；放在模擬頁之後，同段落「2 · 我們怎麼驗證」，拆成 2 頁。

現有順序：1 cover → 2 s1-features → 3 s1-feat-lung → 4 s1-feat-methyl → 5 s2-sim-check（短讀資料不退步）→ 6 s2-sim-plan（模擬 long read 資料量增益）→ 新 7。頁尾全部改 /7（2026-10-20 刪除原第 8 頁）。
橋接（第 6 頁講稿結尾 → 第 7 頁開頭）：「模擬顯示可能有增益，接著看真實資料上是否成立。」

## 第 7 頁 `s2-real-ref`
- 標題（結論）：HCC1395 有公開參考樹，可以比新軟體和 PhyClone 誰比較接近
- 流程（每步都畫）：HCC1395 ONT 資料 → 分兩路：PhyClone（只用計數）／新軟體（加 HP 訊號）→ 兩棵輸出的樹 → clone 對應 → 各自和參考樹比對 → 得分
- 參考樹：SEQC2 研究以多平台 bulk 資料加 PhyloWGS 推出的候選樹（S1 下分 S2、S8 兩大支）。圖上標「參考樹，不是真值」。不寫 1,500×（那只用在 call rescue；PhyloWGS 輸入與指令未公開）。
- clone 對應：SEQC2 沒公開每個 SNV 的 clone，所以用參考圖上標的 driver 基因當定位點。我們的樹中，帶同一 driver 的 clone 對到參考樹同一個 clone。
- 得分（兩項）：
  1. driver 祖孫關係一致比例：兩個 driver 誰是誰的祖先，和參考樹相同的比例（示意）。
  2. CCF 差距：對應到的 clone，CCF 和參考值差多少（示意柱）。S3、S6 低於 10%，參考圖沒畫，不算漏掉。
- 講稿：參考樹也是推論；CASTLE 與 SEQC2 的細胞可能不同批次，培養會有 drift，CCF 可能本來就不同。

## 保留在計畫，不上投影片：兩種一致性檢查（原第 8 頁 `s2-real-consistency`）
- 2026-10-20 使用者刪除第 8 頁，但兩項檢查保留在驗證計畫中。原頁檔在 `removed_slides/s2-real-consistency.html`。
- 原標題：沒有真值時，再用兩種一致性檢查，PhyClone 與新軟體並列比較
- 目的：真實資料沒有真值樹時，檢查軟體結果是否穩定、是否和 read 證據矛盾。一致不等於正確；正確性仍靠第 7 頁參考樹。
- 左欄 purity 稀釋一致性：
  - 先用 100% 樣本固定 SNV 清單 → 對 20%–80% 各 subsample 計數 → PhyClone、新軟體各跑 → 比較各 subsample 的樹與 CCF 是否和 100% 一致。
  - 預期：加 normal 只讓 cellular prevalence 等比例縮小，CCF 應不變。
  - 一致度只比兩邊都有的 clone。低 purity 時 tumor 深度低（20% 只有約 10×），少數 clone 偵測不到是深度不足，不算錯。
  - `t00_n25`（純 normal）當負對照：不應推出 clone。
  - 講稿：nominal 是混合設計比例，不是實測 purity；各 subsample 可能共用 read，一致度可能偏高。
- 右欄 long read 留出檢查（使用者 2026-10-20 決定：保留，只當驗證，不進入建樹。頁面與講稿寫「同一條 read 上兩個 SNV」，不寫 pair）：
  - 依染色體區段留出（不是隨機分 read）→ 其餘資料給 PhyClone、新軟體建樹 → 用留出區段裡同一 haplotype（cis）的兩個 SNV 檢查：樹說 SNV2 是 SNV1 的後代，卻出現「只有 SNV2 alt」的 read → 矛盾比例。
  - 只算 cis pair。講稿交代噪音下限：phasing switch error、germline 錯誤、LOH 區無 HP、拷貝增加都會產生矛盾 read。
  - 公平性：PhyClone 本來不用 read 資訊，這項偏向新軟體；講稿明說。
- 原講稿（保留原文）：參考樹只能比 driver 和 CCF，所以我們再加兩種一致性檢查，一樣讓 PhyClone 和新軟體並列比較。這也是計畫，還沒有結果。先看左邊：用 nominal 100% 的樣本定好 SNV 清單，再對 20% 到 80% 的樣本計數，兩套軟體各跑一次。加 normal 只讓突變比例等比例變小，CCF 應該不變，所以點越貼近虛線越好。橘框的純 normal 是負對照，不應推出 clone。注意，這些百分比是混合設計，不是實測 purity；20% 時腫瘤深度只有約 10 倍，所以只比兩邊都有的 clone；各樣本可能共用 read，一致度可能偏高。再看右邊：按染色體區段留出一部分，其餘拿去建樹。樹說 SNV2 是 SNV1 的後代，留出的 read 卻只帶 SNV2，就是矛盾。phasing 切錯、germline 判錯、只剩一條 haplotype 的區域和拷貝增加也會造成矛盾。PhyClone 本來不用 read，這項偏向新軟體。

## 證據類型
- 論文描述：SEQC2 HCC1395 參考樹形、driver 標註、CCF（S2 60%、S8 34%；出處 SEQC2 論文 Fig. 4a）。
- 分析推論／計畫：全部比對設計與得分；兩頁都沒有結果，講稿口語說「這是計畫」。
- 假想值：所有分數、柱高都是示意。BRIEF H 節「全冊沒有假想數值」要改寫。
- 參考樹（SEQC2，Fang et al. 2021 Nat Biotech Fig. 4a，PDF p.7，已目視確認）：
  Normal →（TP53、PTEN、GATA3、NF1、MAP3K1）→ S1 MRCA；S1 →（PIK3CA）→ S2 60% →（KRAS）→ S4 51% → 分出 S5 14% 與（CASP8、SF3B1）→ S7 29%；S1 → S8 34% → S9 27% → S10 25%（S8 支沒有 driver）。
  S8 支沒有 driver 定位點，只能靠樹的位置與 CCF 對應，講稿要說。
