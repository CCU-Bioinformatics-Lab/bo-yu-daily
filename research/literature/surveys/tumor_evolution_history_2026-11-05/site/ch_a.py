"""Chapters 0-4: the big picture, DNA, how a tumor starts, competition, treatment and spread."""
import random
from lib import S, smooth

G, P, Y = "c1", "c2", "c3"  # clones: green, purple, gold


def big_picture(bk):
    bk.chapter("story", "腫瘤的一生", "這個網站講一個故事：一個細胞怎麼變成一顆腫瘤，以及科學家怎麼從事後的資料猜回這段歷史。每張圖只講一件事，照順序看就好。")
    s = S("0.1", 800, 370)
    s.text(400, 24, "從一個細胞到一顆腫瘤（時間由左到右）", "h", "middle")
    s.cell(60, 130, 22, "normal")
    s.lines(60, 180, ["一個", "正常細胞"], "s", "middle", 17)
    s.arrow(90, 130, 150, 130, "出錯")
    s.cell(185, 130, 22, G, ["mut"])
    s.lines(185, 180, ["第一個", "關鍵突變"], "s", "middle", 17)
    s.arrow(215, 130, 270, 130, "變多")
    s.cluster(330, 130, 44, 44, lambda a, b: G, 6.5)
    s.lines(330, 200, ["一群", "相同細胞"], "s", "middle", 17)
    s.arrow(382, 130, 435, 130, "再出錯")
    s.cluster(510, 130, 66, 62, lambda a, b: P if a > .15 else (Y if b > .35 else G), 6.5)
    s.lines(510, 218, ["分成幾群", "互相競爭"], "s", "middle", 17)
    s.arrow(585, 130, 640, 130, "診斷")
    s.cluster(725, 130, 66, 66, lambda a, b: P if a > -.25 else (Y if b > .5 else G), 6.5)
    s.lines(725, 222, ["切一塊", "拿去定序"], "s", "middle", 17)
    s.rect(745, 75, 34, 34, None, "ink", r=2, sw=2.5)
    s.arrow(40, 262, 770, 262, c="line2", sw=2)
    s.text(40, 284, "往往經過很多年", "s")
    s.text(770, 284, "我們只看得到這一刻", "s", "end")
    s.rect(30, 300, 740, 58, "panel")
    s.text(400, 324, "腫瘤演化研究的難處：過程沒人看到，只拿到最後一刻的一小塊。", "t", "middle")
    s.text(400, 346, "演化「歷史」是用這一塊資料推回去的。", "t", "middle")
    bk.fig(s, "整個故事一張圖", "腫瘤不是一次長成的。細胞一代傳一代，不斷累積錯誤；有些細胞長得比較好，就變多了。",
           "顏色代表帶相同突變的細胞群，不是不同種類的細胞。圖都是示意，不是真實比例。")

    s = S("0.2", 800, 120)
    items = [("mut", "star", "突變"), ("normal", "cell", "正常細胞"), (G, "cell", "腫瘤細胞群 1"), (P, "cell", "腫瘤細胞群 2"), (Y, "cell", "腫瘤細胞群 3")]
    x = 30
    for c, kind, name in items:
        if kind == "star":
            s.star(x, 40, 11, c)
        else:
            s.cell(x, 40, 14, c)
        s.text(x + 22, 45, name, "s")
        x += 150
    s.bar(30, 90, 70, "dad"); s.text(110, 95, "來自爸爸的染色體", "s")
    s.bar(310, 90, 70, "mom"); s.text(390, 95, "來自媽媽的染色體", "s")
    bk.fig(s, "這個網站的圖例", "顏色全站固定。紅星永遠是突變，藍色永遠是爸爸，橘色永遠是媽媽。")


def dna(bk):
    bk.chapter("dna", "細胞裡的 DNA", "演化的材料是 DNA 上的錯誤。先知道細胞裡有什麼、錯誤從哪裡來。")

    s = S("1.1", 800, 290)
    s.person(170, 14, 62, "dad"); s.text(170, 96, "爸爸給一份", "s", "middle")
    s.person(630, 14, 62, "mom"); s.text(630, 96, "媽媽給一份", "s", "middle")
    s.arrow(205, 72, 280, 130); s.arrow(595, 72, 520, 130)
    s.text(400, 112, "你的每個細胞都有兩份", "h", "middle")
    s.bar(170, 148, 460, "dad", 18); s.bar(170, 200, 460, "mom", 18)
    for x, a, b in [(270, "A", "G"), (400, "C", "T"), (530, "G", "A")]:
        s.line(x, 159, x, 189, "line2", 1.5, True)
        s.circle(x, 148, 11, "paper", "ink", 1.2); s.text(x, 153, a, "b", "middle")
        s.circle(x, 200, 11, "paper", "ink", 1.2); s.text(x, 205, b, "b", "middle")
    s.text(645, 153, "這一條的 A-C-G", "s"); s.text(645, 171, "連在一起，叫一個", "s"); s.text(645, 189, "haplotype（HP）", "b")
    s.text(155, 153, "爸爸的", "s", "end"); s.text(155, 205, "媽媽的", "s", "end")
    s.text(400, 240, "兩份內容幾乎一樣，只差少數幾個字母（SNP）。", "t", "middle")
    s.text(400, 268, "這些差異是後面分辨兩條的依據。", "s", "middle")
    bk.fig(s, "雙倍體：每條染色體都有兩份", "你每條染色體都有兩份，一份來自爸爸，一份來自媽媽。同一份上連在一起的字母組合，就叫 haplotype。",
           "染色體照片上的 X 形，左右兩半是複製出來的相同拷貝，不是爸媽各一半。所以這裡都畫成橫條。")

    s = S("1.2", 800, 300)
    s.text(200, 24, "Germline：生下來就有", "h", "middle"); s.text(600, 24, "Somatic：後來才發生", "h", "middle")
    s.line(400, 12, 400, 290, "line", 1.5)
    s.person(200, 40, 76, "panel3"); s.star(200, 90, 7); s.text(240, 80, "爸或媽", "s")
    s.arrow(200, 122, 200, 160)
    s.person(200, 166, 76, "panel3")
    for dx, dy in [(0, 40), (-9, 54), (9, 54), (0, 68)]:
        s.star(200 + dx, 166 + dy, 5)
    s.text(240, 200, "每個細胞都有", "s"); s.text(240, 220, "會傳給小孩", "s")
    s.person(600, 40, 110, "panel2")
    s.circle(600, 104, 16, "mut", None, op=.25); s.star(600, 104, 7)
    s.text(628, 90, "只有這一群", "s"); s.text(628, 110, "細胞有", "s")
    s.line(600, 156, 600, 200, "line2", 2, True); s.xmark(600, 178, 8)
    s.person(600, 206, 66, "panel2")
    s.text(628, 182, "不會傳給小孩", "s")
    bk.fig(s, "兩種突變", "遺傳來的突變全身都有。出生後才發生的 somatic 突變，只在某一群細胞裡。腫瘤演化追蹤的是後者。")

    s = S("1.3", 800, 300)
    rows = [("吸菸", [8, 3, 3, 2, 1, 2], 0), ("陽光（UV）", [1, 1, 9, 1, 1, 1], 2), ("老化", [1, 1, 8, 1, 2, 1], 2)]
    names = ["C>A", "C>G", "C>T", "T>A", "T>C", "T>G"]
    s.text(400, 22, "不同原因，留下不同的「筆跡」", "h", "middle")
    for i, (src, vals, hi) in enumerate(rows):
        y = 40 + i * 80
        s.rect(50, y + 12, 150, 44, "panel")
        s.text(125, y + 39, src, "t", "middle")
        s.arrow(210, y + 34, 280, y + 34)
        for j, v in enumerate(vals):
            x = 310 + j * 62
            s.rect(x, y + 62 - v * 6, 44, v * 6, "mut" if j == hi else "panel3", r=2)
        s.line(305, y + 62, 685, y + 62, "line2", 1)
    for j, n in enumerate(names):
        s.text(310 + j * 62 + 22, 282 + 4, n, "s", "middle")
    bk.fig(s, "突變的來源：mutational signature", "不同原因造成的突變，類型比例不同。看比例可以猜原因，就像看筆跡猜兇手。一個腫瘤通常混合好幾種筆跡。",
           "長條只畫「哪一類最多」的大概樣子，高度不是資料。真正的 signature 分成 96 類，老化和 UV 都以 C>T 為主，要看前後字母才分得開。",
           "吸菸和 UV 的 signature 隨腫瘤演化變少，APOBEC 變多。變化有多大，不同指標的結論不同。", "還在爭論", ("E3-03", "E3-13"))

    s = S("1.4", 800, 280)
    x0, y0, W, H = 90, 226, 620, 180
    s.arrow(x0, y0, x0 + W + 20, y0, c="line2"); s.arrow(x0, y0, x0, y0 - H - 20, c="line2")
    random.seed(4)
    for i in range(14):
        t = .05 + i / 14
        s.circle(x0 + t * W, y0 - t * H * .95 + random.uniform(-13, 13), 5, "panel3", "cellline", 1)
    s.line(x0, y0, x0 + W * .98, y0 - H * .93, "c1", 2.5)
    for t, h in [(.16, 26), (.5, 40), (.84, 42)]:
        s.person(x0 + t * W, y0 + 6, h, "panel2")
    s.text(x0 + W + 12, y0 + 34, "年齡", "t", "end")
    s.text(x0 + 10, y0 - H - 6, "細胞裡累積的突變數", "t")
    bk.fig(s, "突變像時鐘一樣累積", "年紀越大，細胞裡累積的突變通常越多。所以突變數可以當成粗略的時間尺。",
           "時鐘不是每個組織都一樣快，也不一定一直同速。腫瘤裡尤其可能改變速度。",
           "人類結腸的細胞每年約多 47 個替換；ccRCC 約 87 個。突變率在腫瘤內是否固定，研究結果不一致。", "還在爭論", ("E3-08", "E3-04", "E3-18"))


def start(bk):
    bk.chapter("start", "腫瘤怎麼開始", "癌症要累積好幾個關鍵錯誤。這些錯誤有的像踩下油門，有的像弄壞煞車。")

    s = S("2.1", 800, 330)
    stages = [("正常", 0), ("小隆起", 1), ("大隆起", 2), ("穿過底線", 3)]
    for i, (name, n) in enumerate(stages):
        x = 40 + i * 190
        base = 92
        s.line(x, base + 24, x + 150, base + 24, "ink2", 2, True)
        for k in range(12):
            s.circle(x + 6 + k * 12.5, base + 15, 6, "normal", "cellline", .8)
        if n >= 1:
            for r, cnt in [(0, 4 + n * 2), (1, 2 + n * 2)] + ([(2, 4)] if n >= 2 else []):
                for k in range(cnt):
                    s.circle(x + 75 + (k - (cnt - 1) / 2) * 11.5, base + 15 - 11 - r * 10.5, 5.8, G, "cellline", .8)
        if n == 3:
            for k in range(3):
                s.circle(x + 62 + k * 12, base + 36, 5.8, G, "cellline", .8)
            s.circle(x + 75, base + 46, 5.8, G, "cellline", .8)
        s.text(x + 75, 26, name, "h", "middle")
        s.circle(x + 75, 196, 42, G if n else "normal", "cellline", 2)
        for k in range(n):
            s.star(x + 75 + (k - (n - 1) / 2) * 25, 196, 11)
        if i < 3:
            s.arrow(x + 122, 196, x + 182, 196, sw=3.5, head=12)
    s.text(115, 258, "放大一個細胞", "s", "middle")
    for i in range(3):
        s.text(40 + i * 190 + 152, 176, "多一個突變", "s", "middle")
    s.rect(30, 280, 740, 40, "panel")
    s.text(400, 305, "同一條細胞家族一路累積，不是不同細胞各自出錯。", "t", "middle")
    bk.fig(s, "一步一步變壞", "癌症不是一次造成的。同一群細胞一代傳一代，身上的錯誤愈積愈多，才慢慢變成腫瘤。",
           "步驟順序只是常見例子（大腸癌最經典），不適用所有腫瘤。",
           "大腸癌資料的時序符合 APC → KRAS → TP53，而且常見 driver 通常先於罕見 driver。", "確定", ("E2-04",))

    s = S("2.2", 800, 300)
    titles = [("兩份都好", "煞車正常", 0, "c4"), ("第一次打擊", "還有一份能用", 1, "c4"), ("第二次打擊", "煞車全壞", 2, "mut")]
    for i, (t, note, hits, c) in enumerate(titles):
        cx = 140 + i * 260
        s.circle(cx, 128, 92, "panel", "cellline", 2)
        s.bar(cx - 66, 106, 132, "dad", 16); s.bar(cx - 66, 150, 132, "mom", 16)
        s.rect(cx - 12, 96, 24, 20, "paper", "ink", r=2, sw=1.5); s.rect(cx - 12, 140, 24, 20, "paper", "ink", r=2, sw=1.5)
        if hits >= 1:
            s.xmark(cx, 106, 8)
        if hits >= 2:
            s.xmark(cx, 150, 8)
        s.text(cx, 24, t, "h", "middle")
        s.text(cx, 245, note, "b", "middle", c)
        if i < 2:
            s.arrow(cx + 100, 128, cx + 158, 128, sw=3, head=11)
    s.rect(30, 268, 14, 14, "paper", "ink", r=2, sw=1.5); s.text(52, 280, "方塊：抑癌基因（細胞的煞車）", "s")
    s.text(770, 280, "第二次打擊也可能是整段流失（見 5.2）", "s", "end")
    bk.fig(s, "Two-hit：煞車要兩份都壞", "抑癌基因有兩份。壞一份還撐得住，兩份都壞才失控。這是 Knudson 提出的經典想法。",
           "第二次打擊不一定是小突變，也可以是一整段染色體不見。而且不是所有抑癌基因都這樣。",
           "BRCA 帶因者的腫瘤多半流失好的那份，但 BRCA2 乳癌有 46% 仍保留好的那份。", "確定", ("E4-10", "E8-08"))

    s = S("2.3", 800, 330)
    s.text(195, 24, "一開始：4 個細胞，各有不同突變", "h", "middle"); s.text(605, 24, "之後：有 driver 的細胞變多了", "h", "middle")
    left = [[(70, "d"), (150, "p"), (250, "p")], [(120, "p"), (280, "p")], [(200, "p")], [(90, "p"), (180, "p")]]
    for i, marks in enumerate(left):
        y = 62 + i * 46
        s.bar(40, y, 310, "panel3", 12)
        for x, k in marks:
            if k == "d":
                s.star(40 + x, y, 13)
            else:
                s.circle(40 + x, y, 5.5, "ink")
    s.arrow(362, 130, 432, 130, sw=3.5, head=12)
    s.text(397, 110, "長得快", "s", "middle")
    for i in range(4):
        y = 62 + i * 46
        s.bar(450, y, 310, "panel3", 12)
        s.star(450 + 70, y, 13); s.circle(450 + 150, y, 5.5, "ink"); s.circle(450 + 250, y, 5.5, "ink")
    s.rect(450 + 130, 44, 140, 156, None, "ink2", r=6, dash=True)
    s.star(40, 244, 12); s.text(60, 249, "driver：真的讓細胞長得快", "t")
    s.circle(40, 280, 5.5, "ink"); s.text(60, 285, "passenger：沒有貢獻，只是剛好在同一個細胞", "t")
    s.text(650, 226, "這兩個也跟著變多", "s", "middle")
    s.text(650, 246, "（搭便車）", "s", "middle")
    bk.fig(s, "Driver 和 passenger：搭便車", "每條長條是一個細胞的基因組。真正讓細胞長得快的是 driver；其他突變剛好在同一個細胞裡，就跟著被複製。",
           "「很常見的突變」不一定是 driver。而且 driver 和 passenger 是同一個細胞上的不同突變，不是兩種細胞。",
           "Martincorena 2017（Cell）用 TCGA 29 種癌別、7,664 個腫瘤的定序資料估計：基因裡的單點突變，除了 driver，約 99% 對細胞沒有明顯好壞影響；每個腫瘤平均約 4 個真正有作用（各癌別平均 1–10 個）。這是統計估計，不是實驗證明，也只看基因區。", "確定", ("E2-01",))


def compete(bk):
    bk.chapter("compete", "細胞之間的競爭", "腫瘤裡的細胞像一個族群：會出現差異，也會互相競爭。這一章也教你看懂兩種最常見的圖：魚形圖和演化樹。")

    s = S("3.1", 800, 330)
    s.cell(60, 165, 18, G)
    s.text(60, 205, "一個細胞", "s", "middle")
    s.path("M78 165 C120 165 120 70 170 70", "line2", 2.5); s.path("M78 165 H170", "line2", 2.5); s.path("M78 165 C120 165 120 262 170 262", "line2", 2.5)
    s.cell(190, 70, 15, P, [], op=.5); s.star(190, 70, 7)
    s.line(208, 70, 300, 70, "line2", 2, True); s.xmark(315, 70, 11)
    s.text(340, 75, "消失", "b")
    s.cell(190, 165, 15, Y); s.star(190, 165, 7)
    s.line(208, 165, 300, 165, "line2", 2)
    for dx in (0, 24):
        s.cell(320 + dx, 165, 10, Y)
    s.text(370, 170, "沒有擴大", "b")
    s.cell(190, 262, 15, "c4"); s.star(190, 262, 7)
    s.line(208, 262, 350, 262, "line2", 2)
    s.cluster(570, 250, 200, 60, lambda a, b: "c4", 7.5)
    s.text(570, 176, "贏了，變很多", "b", "middle")
    s.star(40, 24, 9); s.text(56, 29, "新突變", "s")
    bk.fig(s, "Clonal evolution：有些消失，有些勝出", "腫瘤裡的細胞不斷出現差異。多數差異不會帶來好處；少數長得比較快的，就愈來愈多。帶相同突變的一群細胞，叫一個 clone。",
           "新 clone 一出現不代表會贏。多數可能從來沒有擴大。",
           "A549 xenograft 實驗：植入約 2,150 個 clone，只有約 100 個長起來。這是實驗系統，不是病人。", None, ("E5-03",))

    s = S("3.2", 800, 360)
    tree = ("c1", [(0, .03), (.12, .3), (.5, .85), (1, 1)], [("c2", [(.2, 0), (.3, .03), (.6, .42), (1, .78)], [("c3", [(.5, 0), (.6, .02), (.85, .22), (1, .46)], [])])])
    s.fish(40, 44, 560, 240, tree)
    cx = 40 + .86 * 560
    s.line(cx, 36, cx, 296, "ink", 2, True)
    s.arrow(cx + 4, 164, 668, 164, sw=2)
    t = .86
    p0 = smooth(tree[1], t); c0 = smooth(tree[2][0][1], t); y0 = smooth(tree[2][0][2][0][1], t)
    bx, by, bw, bh = 672, 44, 40, 240
    s.rect(bx, by, bw, bh * y0 / p0, "c3", r=0)
    s.rect(bx, by + bh * y0 / p0, bw, bh * (c0 - y0) / p0, "c2", r=0)
    s.rect(bx, by + bh * c0 / p0, bw, bh * (p0 - c0) / p0, "c1", r=0)
    s.text(720, by + bh * y0 / p0 / 2 + 5, "最新", "s"); s.text(720, by + bh * (y0 + c0) / p0 / 2 + 5, "中間", "s"); s.text(720, by + bh * (c0 / p0 + 1) / 2 + 5, "最早", "s")
    s.text(692, 32, "這一刻", "s", "middle")
    def mark(x, y, n):
        s.circle(x, y, 11, "ink"); s.text(x, y + 5, n, "s", "middle", "paper")
    mark(62, 164, "1"); mark(320, 90, "2"); mark(375, 164, "3")
    s.arrow(40, 310, 600, 310, c="line2", sw=2); s.text(600, 332, "時間", "t", "end")
    s.text(40, 332, "上下位置沒有意義", "s")
    bk.fig(s, "怎麼讀魚形圖（fish plot）", "① 尖端：這群細胞剛出現。② 色帶變寬：這群細胞變多。③ 新顏色長在舊顏色裡面：它是舊細胞的後代。要看某一刻的比例，就沿虛線切開，像右邊的長條。",
           "上下位置不是腫瘤裡的實際位置。色帶之間的平滑曲線多半是內插，真正量到的只有少數幾個時間點。")

    s = S("3.3", 800, 330)
    random.seed(2)
    def grid(x, y, frac, n=6, r=13):
        cells = [(i, j) for i in range(n) for j in range(n)]
        random.shuffle(cells)
        k = max(1, int(round(frac * n * n)))
        won = set(cells[:k]) if frac < .99 else set(cells)
        for (i, j) in cells:
            s.circle(x + i * r * 2 + r, y + j * r * 2 + r, r * .9, "c2" if (i, j) in won else "c1", "cellline", .8)
    for i, (f, t) in enumerate([(.03, "一個新 clone 出現"), (.5, "它長得比較快"), (1, "幾乎全部都是它")]):
        x = 40 + i * 205
        grid(x, 40, f)
        s.text(x + 78, 24, t, "h", "middle")
        if i < 2:
            s.arrow(x + 162, 118, x + 202, 118, sw=3, head=11)
    s.circle(715, 112, 54, "c2", "cellline", 2)
    s.star(695, 112, 13, "star2"); s.star(735, 112, 13, "mut")
    s.text(715, 24, "放大一個細胞", "s", "middle")
    s.lines(715, 186, ["舊突變還在", "加上一個新突變"], "s", "middle", 18)
    s.fish(40, 224, 600, 90, ("c1", [(0, 1), (1, 1)], [("c2", [(.05, 0), (.15, .03), (.5, .5), (.95, .97), (1, .98)], [])]))
    bk.fig(s, "Clonal sweep：一群取代其他", "有一群細胞長得特別好，慢慢把別人比下去，最後幾乎整個腫瘤都是它的後代。下面的色帶和上面的方陣是同一件事。",
           "「取代」不是舊突變消失。新 clone 是舊 clone 的後代，舊突變還在它身上。",
           "血液腫瘤單細胞研究：6 例 MPN 轉成 AML 中有 4 例出現 sweep。實體瘤多常發生，本次沒找到直接量測。", "還不知道", ("E2-15",))

    s = S("3.4", 800, 560)
    def row(y, name, note, tree, final):
        s.text(30, y + 40, name, "h")
        s.lines(30, y + 62, note, "s", "start", 17)
        s.fish(210, y + 6, 390, 112, tree)
        s.arrow(608, y + 62, 648, y + 62, sw=2.5)
        s.cluster(720, y + 62, 56, 56, final, 5.5)
    row(14, "一波接一波", ["Linear：新的", "取代舊的"],
        ("c1", [(0, 1), (1, 1)], [("c2", [(.1, 0), (.18, .03), (.42, 1), (1, 1)], [("c3", [(.5, 0), (.58, .03), (.85, 1), (1, 1)], [])])]),
        lambda a, b: "c3")
    row(148, "幾群並存", ["Branching：分岔", "後一起活著"],
        ("c1", [(0, 1), (1, 1)], [("c2", [(.2, 0), (.3, .03), (.75, .44), (1, .44)], []), ("c3", [(.35, 0), (.45, .03), (.85, .38), (1, .4)], [])]),
        lambda a, b: "c2" if b < -.1 else ("c3" if b < .75 and a > -.2 else "c1"))
    row(282, "誰都沒贏", ["Neutral：很多小", "群，沒有贏家"],
        ("c1", [(0, 1), (1, 1)], [(c, [(st, 0), (st + .08, .02), (st + .3, .13), (1, .16 - i * .012)], []) for i, (c, st) in enumerate([("c2", .05), ("c3", .12), ("c4", .2), ("c2", .28), ("c3", .36)])]),
        lambda a, b: ["c1", "c2", "c3", "c4", "c2", "c3"][int((a + 1) * 3 + (b + 1) * 2.1) % 6])
    row(416, "早期爆發", ["Punctuated：一開", "始就定型"],
        ("c1", [(0, 1), (1, 1)], [("c2", [(.03, 0), (.08, .05), (.18, .35), (1, .35)], []), ("c3", [(.04, 0), (.09, .05), (.18, .3), (1, .3)], [])]),
        lambda a, b: "c2" if b < -.2 else ("c3" if b > .3 else "c1"))
    s.text(400, 548, "這是簡化的典型圖樣。真實腫瘤可能混合，也可能隨時間改變。", "s", "middle")
    bk.fig(s, "四種演化模式", "同樣從一個細胞開始，有的一波取代一波，有的幾群並存，有的誰都沒特別贏，有的早期爆發後就穩定。右邊是最後腫瘤的樣子。",
           "這四種不是互斥的分類。而且光看最後的資料很難分辨，所以科學家還在爭論。",
           "AML 單細胞：123 人中 55% linear、45% branching。ccRCC 每腫瘤 clone 數中位 4（1–23）。實體瘤的比例沒有直接量測。", "還在爭論", ("E1-14", "E1-05", "E1-03"))

    s = S("3.5", 800, 360)
    s.text(195, 24, "細胞家譜：每個圓是一個細胞", "h", "middle"); s.text(610, 24, "Clone 樹：每個圓是一群細胞", "h", "middle")
    s.line(195, 56, 195, 104, "line2", 2.5); s.cell(195, 52, 11, "normal"); s.star(195, 84, 9, "mut")
    leaves_g = [60, 104, 148]; leaves_p = [240, 284, 328]
    s.line(195, 104, 104, 170, "line2", 2.5); s.line(195, 104, 284, 170, "line2", 2.5)
    s.star(150, 137, 9, "mut"); s.star(240, 137, 9, "mut")
    for x in leaves_g:
        s.line(104, 170, x, 262, "line2", 2); s.cell(x, 272, 15, "c2")
    for x in leaves_p:
        s.line(284, 170, x, 262, "line2", 2); s.cell(x, 272, 15, "c3")
    s.arrow(362, 170, 436, 170, sw=4, head=13)
    s.text(399, 150, "同色合併", "s", "middle")
    s.circle(610, 54, 10, "normal", "cellline")
    s.line(610, 64, 610, 124, "c1", 8); s.circle(610, 136, 22, "c1", "cellline", 1.5)
    s.line(610, 156, 520, 240, "c2", 3); s.line(610, 156, 700, 240, "c3", 3)
    s.circle(520, 260, 28, "c2", "cellline", 1.5); s.circle(700, 260, 28, "c3", "cellline", 1.5)
    s.text(628, 90, "樹幹：每個癌細胞都有", "s"); s.text(468, 190, "樹枝：只有", "s"); s.text(468, 208, "部分細胞有", "s")
    s.rect(30, 310, 740, 40, "panel")
    s.text(400, 335, "樹表示「誰從誰來」，通常不表示比例，線長也不一定代表時間。", "t", "middle")
    bk.fig(s, "從細胞家譜到演化樹", "把一個個細胞的家譜裡同色的部分合成一個圓，就是 clone 樹。樹幹的突變人人有，樹枝的突變只有部分細胞有。",
           "樹上的祖先節點不代表已經消失，它們可能還活著。clone 的切法也不是天生的：subclone 數會隨定序的細胞數改變。",
           "TNBC 單細胞：每腫瘤 7–22 個 subclone，可併成 3–5 個 superclone。", None, ("E1-12",))


def after(bk):
    bk.chapter("after", "治療和轉移", "演化不會停。藥物和移動到新器官，都是新的篩選。")

    s = S("4.1", 800, 340)
    def scale(t):
        return smooth([(0, .1), (.4, 1), (.62, .18), (1, .95)], t)
    tree = ("c1", [(0, 1), (1, 1)], [("c3", [(.14, 0), (.2, .01), (.4, .02), (.62, .55), (.85, .98), (1, 1)], [])])
    s.fish(50, 50, 700, 210, tree, scale)
    s.rect(50 + .4 * 700, 270, .22 * 700, 16, "drug", r=2)
    s.line(50 + .4 * 700, 44, 50 + .4 * 700, 286, "ink2", 1.5, True); s.line(50 + .62 * 700, 44, 50 + .62 * 700, 286, "ink2", 1.5, True)
    s.text(50 + .51 * 700, 304, "用藥期間", "s", "middle")
    s.text(190, 30, "用藥前：大多怕藥", "b", "middle"); s.text(50 + .51 * 700, 30, "用藥中：怕藥的死掉", "b", "middle"); s.text(640, 30, "復發：不怕藥的長回來", "b", "middle")
    s.arrow(220, 248, 262, 165, c="ink", sw=1.5, head=7)
    s.text(60, 262, "一開始就有少數不怕藥的細胞", "s")
    s.text(50, 332, "上下寬度：腫瘤大小", "s")
    s.arrow(620, 326, 750, 326, c="line2", sw=2); s.text(610, 331, "時間", "s", "end")
    bk.fig(s, "用藥是一次篩選", "藥物殺掉怕藥的細胞（綠色）。原本很少的不怕藥細胞（金色）失去競爭對手，就長成新的腫瘤。這也是一種演化。",
           "藥物通常不是「製造」抗藥突變，而是把早就存在的細胞篩出來。不過抗藥性也可能在治療中才出現。復發的腫瘤大小回來了，組成已經不同。",
           "TNBC PDX 時序研究：cisplatin 下的抗藥 clone，來自未治療時適應度較低的譜系。這是 PDX，不是病人。", None, ("E2-26",))

    s = S("4.2", 800, 340)
    s.cluster(165, 170, 130, 130, lambda a, b: "c1" if a < -.2 and b < .4 else ("c2" if a >= -.2 and b < .1 else "c3"), 8)
    s.text(165, 330, "原本的腫瘤", "t", "middle")
    s.path("M340 16 C310 110 360 230 330 320", "vessel", 11, op=.5); s.text(350, 332, "血管", "s")
    s.cluster(650, 92, 70, 58, lambda a, b: "c2", 7)
    s.cluster(650, 262, 70, 58, lambda a, b: "c2" if a < 0 else "c3", 7)
    s.text(650, 18, "器官 A 的新腫瘤", "t", "middle"); s.text(650, 186, "器官 B 的新腫瘤", "t", "middle")
    s.path("M230 110 C330 70 450 80 570 90", "ink2", 2.5); s.poly([(578, 90), (566, 84), (566, 96)], "ink2")
    s.cell(400, 76, 11, "c2"); s.text(470, 58, "一種來源", "s", "middle")
    s.path("M240 165 C340 190 450 225 572 240", "ink2", 2.5); s.poly([(580, 241), (568, 234), (568, 247)], "ink2")
    s.path("M220 245 C340 275 450 280 572 268", "ink2", 2.5); s.poly([(580, 267), (568, 262), (569, 274)], "ink2")
    s.cell(400, 202, 11, "c2"); s.cell(410, 279, 11, "c3"); s.text(480, 305, "多種來源", "s", "middle")
    bk.fig(s, "轉移：細胞到別的器官重新長大", "有些癌細胞離開原來的腫瘤，到別的器官重新長大。新腫瘤可能只來自一群細胞，也可能來自好幾群。",
           "單一顏色不一定只來自一個細胞，也可能是同色的一團細胞。轉移也不一定很晚才發生。",
           "小鼠胰臟癌 lineage tracing：轉移部位 80–90% 細胞通常來自單一 clone，95 個 clone 中 48 個完全沒有轉移。人類病人還沒有同等級的資料。", None, ("E5-02",))


def build(bk):
    big_picture(bk); dna(bk); start(bk); compete(bk); after(bk)
