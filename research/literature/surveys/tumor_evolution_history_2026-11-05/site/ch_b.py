"""Chapters 5-8: large chromosome events, how we see tumors, dad and mom, what is settled."""
import json
import random
from pathlib import Path
from lib import S


def big_events(bk):
    bk.chapter("events", "染色體層級的大事件", "除了單一字母的錯誤，整段甚至整套染色體也會改變。這會影響我們怎麼解讀資料。")

    s = S("5.1", 800, 330)
    def stage(x, y, bars):
        s.rect(x, y, 170, 92, "panel", r=6)
        n = len(bars)
        for i, (c, st) in enumerate(bars):
            by = y + 46 + (i - (n - 1) / 2) * 25
            s.bar(x + 15, by, 140, c, 13)
            if st:
                s.star(x + 85, by, 10)
    y1, y2 = 42, 192
    s.text(30, 26, "先突變，再影印", "h"); s.text(30, 176, "先影印，再突變", "h")
    D, M = "dad", "mom"
    stage(30, y1, [(D, 0), (M, 0)]); stage(250, y1, [(D, 1), (M, 0)]); stage(470, y1, [(D, 1), (D, 1), (M, 0)])
    stage(30, y2, [(D, 0), (M, 0)]); stage(250, y2, [(D, 0), (D, 0), (M, 0)]); stage(470, y2, [(D, 1), (D, 0), (M, 0)])
    s.arrow(205, y1 + 46, 245, y1 + 46, "突變"); s.arrow(425, y1 + 46, 465, y1 + 46, "gain")
    s.arrow(205, y2 + 46, 245, y2 + 46, "gain"); s.arrow(425, y2 + 46, 465, y2 + 46, "突變")
    s.lines(660, y1 + 38, ["共 3 條", "2 條帶突變"], "b", "start", 22)
    s.lines(660, y2 + 38, ["共 3 條", "1 條帶突變"], "b", "start", 22)
    s.text(400, 316, "「帶突變的條數」（multiplicity）能告訴我們：突變和 gain 誰先發生。", "t", "middle")
    bk.fig(s, "影印機比喻：gain 和突變的先後", "影印之前就有的錯字，兩份都會有；影印之後才出現的錯字，只有一份有。所以從帶突變的條數，可以推算先後。這是為腫瘤事件定時間的主要方法。",
           "「帶突變的條數」和「總共幾條」是兩個不同的數字。",
           "PCAWG 2,116 個樣本：gain 的相對時間中位 0.60，80–90% 的染色體臂 gain 只讓一條 allele 多一份。這個時間是相對值，不是年份。", "確定", ("E7-01",))

    s = S("5.2", 800, 290)
    cols = [("原本", [("dad", 0), ("mom", 0)], "藍 1、橘 1，共 2"), ("LOH：流失一條", [("dad", 0), ("mom", 1)], "藍 1、橘 0，共 1"), ("Copy-neutral LOH：被取代", [("dad", 0), ("dad", 0)], "藍 2、橘 0，共 2")]
    for i, (t, bars, c) in enumerate(cols):
        x = 30 + i * 262
        s.text(x + 110, 28, t, "h", "middle")
        s.circle(x + 110, 112, 74, "panel", "cellline", 2)
        for j, (col, gone) in enumerate(bars):
            s.bar(x + 55, 92 + j * 40, 110, col, 16, dash=bool(gone))
        s.text(x + 110, 214, c, "t", "middle")
    s.arrow(232, 112, 300, 112, "兩種可能", sw=3); s.text(530, 120, "或", "big", "middle")
    s.rect(30, 236, 740, 42, "panel")
    s.text(400, 262, "右邊的總數還是 2，只看條數會以為沒事。其實兩條已經一模一樣，媽媽那份沒了。", "t", "middle")
    bk.fig(s, "LOH：兩份變一種", "兩份不一樣的基因變成只剩一種版本。有時少了一條，有時總數還是兩條，但兩條已經相同。兩次打擊的第二次常常就是這樣發生。",
           "LOH 不一定是「少一條」。而且 LOH 會讓流失那條上的突變一起消失。")

    s = S("5.3", 800, 280)
    def chroms(cx, cy, r, copies):
        s.circle(cx, cy, r, "panel", "cellline", 2)
        lens = [130, 90, 56]
        y = cy - (len(lens) * (copies * 14 + 12)) / 2 + 9
        for L in lens:
            for k in range(copies):
                s.bar(cx - L / 2, y, L, "dad" if k < copies / 2 else "mom", 10)
                y += 14
            y += 12
    chroms(180, 130, 110, 2); chroms(600, 130, 124, 4)
    s.text(180, 268, "每一號各 2 條", "t", "middle"); s.text(600, 272, "每一號各 4 條", "t", "middle")
    s.arrow(310, 130, 450, 130, "整套一次加倍", sw=4, head=14)
    bk.fig(s, "WGD：整套染色體一次加倍", "細胞把整套染色體一次多留一份，每一號都從兩份變四份。藍橘比例不變。圖上只畫三號當代表。",
           "WGD 不是某一條 gain。它一次影響全部，所以之前的突變都會變成兩倍份數。",
           "9,692 例晚期癌症有 28.2% 發生 WGD，比例依癌別差很多。可定時病例中，97.3% 的 WGD 在 TP53 突變之後。WGD 算不算「早」還有爭議。", "還在爭論", ("E7-02", "E7-01", "E7-09"))

    s = S("5.4", 800, 350)
    random.seed(5)
    xs, x = [], 95
    while x < 750:
        if not 440 < x < 540:
            xs.append(x)
        x += random.uniform(30, 58)
    cl = [460 + i * 7 for i in range(10)]
    all_x = sorted([(x, 0) for x in xs] + [(x, 1) for x in cl])
    s.text(40, 26, "染色體上的突變（紅色是擠在一起的那段）", "h")
    s.rect(452, 40, 90, 290, "mut", None, r=4, op=.09)
    s.bar(40, 60, 720, "dad", 12)
    for x, k in all_x:
        s.star(x, 60, 7, "mut" if k else "star3")
    s.line(70, 104, 70, 310, "line2", 1.5); s.line(70, 310, 760, 310, "line2", 1.5)
    s.text(80, 114, "離上一個突變很遠", "s"); s.text(80, 300, "很近", "s")
    prev = None
    for x, k in all_x:
        if k:
            y = 288
        else:
            y = 130 + random.uniform(0, 62)
        s.circle(x, y, 5, "mut" if k else "panel3", "cellline", 1)
        prev = x
    s.text(415, 334, "在染色體上的位置", "s", "middle")
    s.text(552, 268, "像一陣雨集中落下", "s")
    bk.fig(s, "Kataegis：突變的驟雨", "大部分突變散得很開，但有一小段擠了一大串，而且多半在同一條染色體上。下面這種圖叫 rainfall plot。",
           "點越「低」不是突變越少，反而代表彼此越近、越密。",
           "21 個乳癌中 13 個有 kataegis，microcluster 內的突變多數在同一條親代染色體上。但 PCAWG 中 clustered 突變只占全部 3.7%。", "確定", ("E4-02", "E4-20"))


def seeing(bk):
    bk.chapter("seeing", "我們怎麼看腫瘤", "前面講的是真實發生的事。這一章講科學家實際拿到什麼資料，以及為什麼很難推回歷史。")

    s = S("6.1", 800, 300)
    random.seed(12)
    s.cluster(115, 130, 90, 90, lambda a, b: random.choice(["c1", "c1", "c2", "c3", "normal", "normal"]), 9)
    s.text(115, 248, "腫瘤組織：很多種細胞", "s", "middle")
    s.arrow(215, 130, 290, 130, "全部打碎", sw=3)
    # tube
    s.path("M320 40 L320 200 Q320 228 350 228 Q380 228 380 200 L380 40", "ink2", 2.5)
    for i in range(26):
        x, y = random.uniform(330, 370), random.uniform(120, 215)
        s.line(x, y, x + random.uniform(-8, 8), y + random.uniform(-8, 8), "ink2", 1.8)
    s.text(350, 248, "DNA 混在一起", "s", "middle")
    s.arrow(395, 130, 470, 130, "定序", sw=3)
    for i in range(9):
        off = [0, 40, 16, 60, 8, 50, 26, 66, 4][i]
        x, y = 490 + off, 50 + i * 19
        s.rect(x, y, 150, 11, "read", r=3)
        s.text(x + 165, y + 11, "?", "b")
    s.text(590, 248, "每條 read 都不知道來自哪個細胞", "s", "middle")
    s.text(400, 288, "就像把一籃水果打成果汁：喝得出整體味道，說不出哪一口來自哪顆水果。", "t", "middle")
    bk.fig(s, "Bulk 定序：打成果汁", "把很多細胞的 DNA 全部混在一起定序。我們得到很多 read，但每條 read 的細胞標籤不見了。",
           "每條 read 其實仍然來自某一個細胞，只是我們不知道是哪一個。同一條 long read 上的多個突變，確實在同一條 DNA 上。")

    s = S("6.2", 800, 320)
    seq = "GATTACAGCCTAGGA"
    x0, cw = 110, 30
    s.rect(x0 - 8, 22, cw * 15 + 16, 28, "ink2", r=3)
    col = 7
    reads = [(0, 11), (3, 14), (1, 9), (5, 15), (2, 12), (4, 13), (0, 10), (6, 15), (3, 11), (1, 13)]
    mut = {1, 4, 8}
    for i, (a, b) in enumerate(reads):
        s.rect(x0 + a * cw - 2, 60 + i * 23.5, (b - a) * cw, 19, "read", r=3)
    s.rect(x0 + col * cw - 3, 16, cw, 282, "hl", r=3, op=.75)
    for i, c in enumerate(seq):
        s.text(x0 + i * cw + 12, 41, c, "n", "middle", "ink" if i == col else "on")
    s.text(x0 - 16, 41, "參考序列", "s", "end")
    for i, (a, b) in enumerate(reads):
        y = 60 + i * 23.5
        if i in mut:
            s.text(x0 + col * cw + 12, y + 15, "T", "b", "middle", "mut")
        else:
            s.text(x0 + col * cw + 12, y + 15, seq[col], "n", "middle")
    s.arrow(575, 170, 625, 170, sw=3)
    s.text(712, 165, "3 ÷ 10", "big", "middle"); s.text(712, 196, "= 30%", "big", "middle"); s.text(712, 224, "VAF", "b", "middle")
    bk.fig(s, "VAF：數 read", "在同一個位置數 read。10 條裡有 3 條帶突變，VAF 就是 30%。VAF 是 bulk 資料最基本的數字。",
           "VAF 算的是 read，不是細胞。30% 不代表 30% 的細胞有這個突變，原因在下一張圖。")

    s = S("6.3", 800, 320)
    def rowp(y, title, n_t, n_n, red, res):
        s.text(30, y, title, "h")
        x = 44
        for i in range(n_t + n_n):
            tumor = i < n_t
            cx = 44 + i * 33
            s.cell(cx, y + 34, 15, "c1" if tumor else "normal", ["mut"] if tumor else [], dash=not tumor)
        bx = 390
        for i in range(20):
            s.rect(bx + (i % 20) * 15, y + 22, 13, 24, "mut" if i < red else "read", r=2)
        s.text(bx + 150, y + 66, "每個細胞貢獻 2 份 DNA，共 20 份", "s", "middle")
        s.text(708, y + 40, res, "big", "start")
    rowp(28, "全部是腫瘤（purity 100%）", 10, 0, 10, "50%")
    rowp(138, "混入正常細胞（purity 60%）", 6, 4, 6, "30%")
    s.arrow(698, 80, 698, 150, c="line2", sw=1.5, head=6)
    s.rect(30, 240, 740, 64, "panel")
    s.text(400, 264, "為什麼最高只有 50%？突變通常只在兩份裡的一份，所以純腫瘤也只有一半 read 帶突變。", "t", "middle")
    s.text(400, 288, "正常細胞沒有這個突變，卻貢獻了 DNA，所以比例又被沖淡。", "t", "middle")
    bk.fig(s, "Purity：被正常細胞沖淡", "樣本裡一定混著正常細胞。它們沒有這個突變，卻貢獻了 DNA，所以 VAF 被沖淡。", "看 read 無法判斷它來自腫瘤還是正常細胞。purity 也是用資料估計出來的。圖中假設每個細胞都是兩份，沒有 copy number 變化。")

    s = S("6.4", 800, 280)
    def rowc(y, title, marks, col, res, label):
        s.text(30, y, title, "h")
        for i in range(10):
            s.cell(44 + i * 40, y + 34, 16, "c1", [col] if i < marks else [])
        s.text(470, y + 40, res, "big")
        s.text(650, y + 40, label, "s")
    rowc(26, "每個腫瘤細胞都有", 10, "mut", "10 ÷ 10", "CCF 100%：clonal")
    rowc(126, "只有一部分有", 4, "mut", "4 ÷ 10", "CCF 40%：subclonal")
    s.cell(60, 240, 15, "normal", [], dash=True); s.cell(96, 240, 15, "normal", [], dash=True); s.text(122, 245, "正常細胞不算在內", "s")
    bk.fig(s, "CCF：有多少腫瘤細胞帶這個突變", "只看腫瘤細胞：每個都有就是 clonal，只有一部分有就是 subclonal。CCF 就是這個比例。",
           "這塊樣本裡每個細胞都有，不代表整顆腫瘤每個細胞都有（見 6.7）。")

    s = S("6.5", 800, 340)
    x0, y0, W = 80, 280, 640
    s.line(x0, y0, x0 + W + 10, y0, "ink2", 2); s.line(x0, y0, x0, 40, "ink2", 2)
    import math
    fx = lambda v: x0 + v / .6 * W
    for i in range(1, 60):
        v = i / 100
        cl = 170 * math.exp(-.5 * ((v - .5) / .03) ** 2)
        sub = 90 * math.exp(-.5 * ((v - .25) / .028) ** 2)
        tail = (1.6 / v if v < .22 else 0)
        for val, c, base in [(tail, "panel3", 0), (sub, "c2", 0), (cl, "mut", 0)]:
            if val > 1.5:
                s.rect(fx(v) - 4.7, y0 - min(val, 170), 9.4, min(val, 170), c, r=1)
    for v in (.1, .25, .5):
        s.text(fx(v), y0 + 20, f"{v:g}", "s", "middle")
    s.text(x0 + W / 2, y0 + 44, "VAF（越往右，帶這批突變的細胞越多）", "t", "middle")
    s.text(x0 - 8, 58, "突變", "s", "end"); s.text(x0 - 8, 76, "數量", "s", "end")
    s.lines(fx(.5), 72, ["clonal", "每個腫瘤細胞都有"], "s", "middle", 17)
    s.lines(fx(.25) + 8, 158, ["subclonal", "約一半腫瘤細胞有"], "s", "middle", 17)
    s.lines(fx(.09), 170, ["低頻尾巴", "很少細胞有"], "s", "middle", 17)
    bk.fig(s, "VAF 直方圖怎麼讀", "每根柱子是在數突變。越靠右，帶這些突變的細胞越多。科學家就是從這些「峰」猜有幾群細胞。圖中假設 purity 100%。",
           "最大的誤解：把峰的高度當成細胞數。高度是突變的數量，峰的位置才和細胞比例有關。另外，尾巴不一定代表一個 clone。",
           "低頻尾巴要夠深才看得清楚：深度低於 90–100× 或 purity 低時無法可靠重建，而 PCAWG 中位只有 45×。尾巴的解讀還有爭議。", "還在爭論", ("E1-09", "E1-04", "E1-02"))

    s = S("6.6", 800, 330)
    for i in range(50):
        s.cell(40 + i % 25 * 29, 34 + (i // 25) * 29, 12, "c1" if i != 37 else "c2", ["mut"] if i == 37 else [])
    s.text(400, 104, "50 個細胞只有 1 個帶突變：100 份 DNA 裡只有 1 份", "t", "middle")
    s.text(195, 136, "讀 30 條：多半一條都抓不到", "h", "middle")
    for i in range(30):
        s.rect(50 + i % 15 * 19, 150 + (i // 15) * 19, 16, 16, "read", r=2)
    s.text(600, 136, "讀 300 條：平均抓到 3 條", "h", "middle")
    random.seed(1)
    reds = set(random.sample(range(300), 3))
    for i in range(300):
        s.rect(430 + i % 30 * 11.5, 150 + (i // 30) * 11.5, 10, 10, "mut" if i in reds else "read", r=1)
    s.text(600, 288, "可是定序錯誤也會產生這種零星訊號", "s", "middle")
    s.text(195, 214, "看不到，不等於不存在", "b", "middle")
    bk.fig(s, "為什麼 bulk 看不到小 clone", "小 clone 的 DNA 太少。read 不夠多就抽不到；抽到了，也很難和定序錯誤分開。深度（depth）是一個位置被多少條 read 蓋到。",
           "看不到不等於不存在。文獻裡的 clone 數通常是低估的。",
           "PCAWG 約 46×：只有能力偵測到 CCF 超過 30% 的 subclone，所以 95.1% 有 subclone 只是下限。", "確定", ("E1-10",))

    s = S("6.7", 800, 340)
    def region(a, b):
        if b > .05:
            return "c1"
        return "c2" if a < 0 else "c3"
    def regionc(a, b):
        return region(a, b)
    s.cluster(210, 170, 180, 150, regionc, 8)
    s.rect(70, 70, 92, 92, None, "ink", r=3, sw=3); s.rect(258, 70, 92, 92, None, "ink", r=3, sw=3)
    s.rect(92, 104, 48, 24, "paper", "ink", r=4); s.text(116, 121, "切 A", "b", "middle")
    s.rect(280, 104, 48, 24, "paper", "ink", r=4); s.text(304, 121, "切 B", "b", "middle")
    def bars(x, y, vals, title):
        s.text(x, y - 8, title, "h")
        for i, (v, c, n) in enumerate(vals):
            yy = y + i * 28
            s.text(x, yy + 15, n, "s")
            s.rect(x + 96, yy, 170, 20, "read", r=2); s.rect(x + 96, yy, 170 * v, 20, c, r=2)
    bars(490, 54, [(1, "c1", "全部共有"), (.85, "c2", "紫色那群"), (.03, "c3", "金色那群")], "切 A 看到")
    bars(490, 196, [(1, "c1", "全部共有"), (.03, "c2", "紫色那群"), (.85, "c3", "金色那群")], "切 B 看到")
    s.path("M116 70 C180 6 370 6 480 46", "line2", 2, dash=True); s.path("M350 130 C400 160 430 190 480 195", "line2", 2, dash=True)
    s.text(490, 320, "只切 A，會以為沒有金色那群。", "b")
    bk.fig(s, "切不同地方，看到不同腫瘤", "同一顆腫瘤切不同地方，看到的突變不一樣。只切一塊可能漏掉其他地方的 clone，也可能把區域性的突變看成人人都有。",
           "多區域不是重複實驗，每一區看到的內容不同。臨床上常常只有一塊。",
           "PCAWG 多區域對照：單樣本漏掉 44% 變異，26% 的 subclonal 突變看起來像 clonal。模擬中超過 70% 的 subclonal SNV 是區域專屬。", "確定", ("E2-03", "E1-13"))

    s = S("6.8", 800, 416)
    def eight(cx, cy, marks, r=15):
        for i, ms in enumerate(marks):
            s.cell(cx + (i % 4 - 1.5) * 36, cy + (i // 4) * 36, r, "c1", ms)
    M = "mut"; O = "c3"; V = "c2"
    cells = [[M, O], [M, O], [M, O, V], [M, O, V], [M], [M], [M], [M]]
    eight(400, 46, cells)
    s.text(400, 18, "同一批 8 個細胞", "h", "middle")
    s.arrow(320, 84, 230, 132, sw=2.5); s.arrow(480, 84, 570, 132, sw=2.5)
    s.text(215, 126, "Bulk", "h", "end"); s.text(585, 126, "單細胞", "h")
    for i, (n, v, c) in enumerate([("A", 1, M), ("B", .5, O), ("C", .25, V)]):
        y = 164 + i * 40
        s.text(50, y + 19, n, "b")
        s.rect(76, y, 270, 26, "read", r=2); s.rect(76, y, 270 * v, 26, c, r=2)
        s.text(356, y + 19, f"{v:.0%}", "n")
    s.text(200, 314, "只知道比例", "b", "middle")
    # matrix
    x0, y0, cw = 480, 164, 34
    for j, n in enumerate("ABC"):
        s.text(x0 + 58 + j * cw + 14, y0 - 6, n, "b", "middle")
    table = [[1, 1, 0], [1, 1, 0], [1, 1, 1], [1, 1, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]
    colors = [M, O, V]
    for i, row in enumerate(table):
        y = y0 + i * 22
        s.text(x0 + 46, y + 15, f"細胞 {i + 1}", "s", "end")
        for j, v in enumerate(row):
            s.rect(x0 + 58 + j * cw, y, cw - 3, 19, colors[j] if v else "read", r=2)
    s.rect(x0 + 58 + 1 * cw, y0 + 2 * 22, cw - 3, 19, "paper", "ink2", r=2, dash=True)
    s.text(x0 + 58 + 1 * cw + 14, y0 + 2 * 22 + 15, "?", "b", "middle")
    s.text(x0 + 180, y0 + 2 * 22 + 15, "單細胞也會漏讀", "s")
    s.text(600, 356, "知道每個細胞有什麼", "b", "middle")
    s.rect(30, 372, 740, 34, "panel")
    s.text(400, 395, "真正的差別：單細胞看得到同一個細胞裡，哪些突變一起出現。", "t", "middle")
    bk.fig(s, "單細胞和 bulk 的差別", "Bulk 告訴你每個突變佔多少；單細胞告訴你每個細胞裡有哪些突變。",
           "單細胞資料不是乾淨的答案，常有漏讀，樹也仍然是推論出來的。",
           "單細胞研究看到：12 個資料集中 11 個有「同一位置多次受影響」的強證據，表示建樹的基本假設不總是成立。", "確定", ("E5-06",))

    s = S("6.9", 800, 400)
    M, O, V = "mut", "c3", "c2"
    def scene(cx, title, tree, cells, box):
        s.text(cx, 24, title, "h", "middle")
        tree(cx)
        for i, ms in enumerate(cells):
            s.cell(cx + (i % 4 - 1.5) * 38, 186 + (i // 4) * 38, 15, "c1", ms)
        s.rect(*box, None, "ink", r=6, sw=2.5, dash=True)
    def linear(cx):
        s.line(cx, 44, cx, 136, "line2", 3); s.star(cx, 56, 9, M); s.star(cx, 92, 9, O); s.star(cx, 128, 9, V)
    def branch(cx):
        s.line(cx, 44, cx, 84, "line2", 3); s.line(cx, 84, cx - 44, 136, "line2", 3); s.line(cx, 84, cx + 44, 136, "line2", 3)
        s.star(cx, 56, 9, M); s.star(cx - 44, 132, 9, O); s.star(cx + 44, 132, 9, V)
    A = [M]
    scene(140, "歷史一：一條線", linear, [[M, O], [M, O], [M, O, V], [M, O, V], A, A, A, A], (140 - 42, 167, 80, 38))
    scene(660, "歷史二：分岔", branch, [[M, O], [M, O], [M, O], [M, O], [M, V], [M, V], A, A], (660 - 76, 205, 80, 38))
    for i, (n, v, c) in enumerate([("A", 1, M), ("B", .5, O), ("C", .25, V)]):
        y = 92 + i * 38
        s.text(304, y + 18, n, "b")
        s.rect(326, y, 150, 24, "read", r=2); s.rect(326, y, 150 * v, 24, c, r=2)
        s.text(486, y + 18, f"{v:.0%}", "n")
    s.text(400, 70, "bulk 看到的資料", "h", "middle"); s.text(400, 226, "兩邊完全一樣", "b", "middle")
    s.arrow(246, 150, 296, 150, sw=2.5); s.arrow(556, 150, 520, 150, sw=2.5)
    s.rect(30, 290, 740, 96, "panel")
    s.lines(400, 316, ["虛線框：帶紫星（C）的 2 個細胞。歷史一裡它們同時有金星（B）；歷史二裡沒有。", "兩段不同的歷史，留下一模一樣的比例。只看比例，分不出哪一段才是真的。", "這也是 11-04 會議提醒的事：最終資料相似，不能證明演化過程相同。"], "t", "middle", 25)
    bk.fig(s, "不同歷史，可以有相同的資料", "這是整個領域最核心的困難。比例裡沒有「誰和誰在同一個細胞」的資訊，所以同一份 bulk 資料可以對應好幾棵樹。",
           "這不只是雜訊問題。資料再多，只看比例還是分不開。需要額外資訊，例如單細胞或同一條 read 上的共現。",
           "同一批 PCAWG 資料，有研究說選擇普遍，也有研究說高功效案例只有 3% 有持續選擇。", "還在爭論", ("E2-03", "E1-09"))


def parents(bk):
    bk.chapter("parents", "爸爸、媽媽、HP", "Long read 能把 read 分回兩條染色體。但分出來的組名，和爸爸媽媽是兩回事。這是最容易混淆的一章。")

    s = S("7.1", 800, 340)
    s.bar(40, 34, 720, "read", 10); s.text(40, 20, "參考基因組", "s")
    snp = [190, 330, 470]
    for x in snp:
        s.line(x, 40, x, 330, "line2", 1, True)
    s.text(205, 20, "每條虛線：一個爸媽不同的位置（SNP）", "s")
    # mixed reads
    mixed = [(150, "A", "C", None), (280, "T", "A", None), (140, "A", "C", "G"), (160, "G", "T", "A"), (295, "C", "G", None), (300, "T", "A", None)]
    s.text(105, 76, "混在一起", "h", "middle")
    for i, (x, a, b, c) in enumerate([(150, "A", "C", ""), (150, "G", "T", ""), (150, "A", "C", "G"), (150, "G", "T", "A"), (290, "", "C", "G"), (290, "", "T", "A")]):
        pass
    rows = [("A", "C", "", 0), ("G", "T", "", 1), ("A", "C", "G", 0), ("", "T", "A", 1), ("", "C", "G", 0), ("G", "T", "A", 1)]
    # left block drawn in full width by SNP columns, compact
    for i, (a, b, c, g) in enumerate(rows):
        y = 92 + i * 38
        xs = [snp[k] for k, v in enumerate((a, b, c)) if v]
        x1, x2 = min(xs) - 30, max(xs) + 30
        s.rect(x1, y, x2 - x1, 24, "read", r=4)
        for k, v in enumerate((a, b, c)):
            if v:
                s.text(snp[k], y + 17, v, "b", "middle")
    s.arrow(525, 200, 575, 200, "看字母分組", sw=3)
    s.rect(590, 76, 180, 110, "panel", r=6); s.text(680, 98, "HP1", "h", "middle"); s.text(680, 128, "A — C — G", "t", "middle"); s.text(680, 150, "這些 read 歸一組", "s", "middle")
    s.rect(590, 214, 180, 110, "panel", r=6); s.text(680, 236, "HP2", "h", "middle"); s.text(680, 266, "G — T — A", "t", "middle"); s.text(680, 288, "另一組", "s", "middle")
    bk.fig(s, "Phasing：把 read 分回兩條", "一條長 read 同時蓋到好幾個爸媽不同的位置。字母組合相同的 read，就歸成同一組。這就是 long read 的強項：一條 read 夠長，能把位置串起來。",
           "沒有蓋到 SNP 的 read 無法分組，常標成 HP0（unphased）。它不是第三條染色體，只是分不出來。",
           "B04（20 例肺癌，ONT）：phase block N50 834 kb，但只有 43% 的突變能指派到 HP；VAF ≥ 0.2 時提高到 71%。", None, ("B04",))

    s = S("7.2", 800, 250)
    s.bar(30, 50, 740, "read", 10)
    snps = [60, 110, 160, 210, 260, 310, 500, 550, 600, 650, 700, 745]
    for x in snps:
        s.star(x, 50, 6, "ink2")
    for i in range(5):
        s.rect(55 + i * 40, 70 + i * 13, 120, 10, "c1", r=3)
    for i in range(5):
        s.rect(495 + i * 36, 70 + i * 13, 110, 10, "c2", r=3)
    s.xmark(400, 96, 13)
    s.text(400, 136, "沒有 read 跨過去", "s", "middle")
    s.path("M50 148 L50 158 L330 158 L330 148", "ink2", 2); s.path("M490 148 L490 158 L760 158 L760 148", "ink2", 2)
    s.text(190, 180, "phase block 1", "b", "middle"); s.text(625, 180, "phase block 2", "b", "middle")
    s.text(400, 222, "每段內部接得起來，段和段之間接不起來。", "t", "middle")
    bk.fig(s, "Phase block：為什麼會斷", "Read 一條接一條重疊，像鏈條。遇到沒有 read 跨過去的地方就斷了，兩段的關係接不起來，每段自成一區。",
           "一條染色體通常不是一個 block。只靠 nanopore 的 N50 約 4.85 Mb，遠短於整條染色體。",
           None, None, ("E8-09",))

    s = S("7.3", 800, 340)
    s.text(30, 26, "真實：來自誰（生物事實）", "h")
    s.bar(30, 56, 740, "dad", 20); s.bar(30, 90, 740, "mom", 20)
    s.text(400, 61, "爸爸", "s", "middle", "on"); s.text(400, 95, "媽媽", "s", "middle", "on")
    s.text(30, 146, "軟體看到：只有組名", "h")
    def seg(x, w, top, bot):
        s.bar(x, 182, w, "dad", 20); s.bar(x, 216, w, "mom", 20)
        for y, t in ((182, top), (216, bot)):
            s.rect(x + w / 2 - 27, y - 13, 54, 26, "paper", "ink", r=4, sw=1.5)
            s.text(x + w / 2, y + 5, t, "b", "middle")
    seg(30, 340, "HP1", "HP2"); seg(430, 340, "HP2", "HP1")
    s.text(400, 205, "?", "big", "middle")
    s.text(200, 248, "block 1：HP1 是爸爸", "s", "middle"); s.text(600, 248, "block 2：HP1 是媽媽", "s", "middle")
    s.rect(30, 272, 740, 56, "panel")
    s.text(400, 296, "軟體只知道哪些字母同一組，不知道這組來自爸爸還是媽媽。", "t", "middle")
    s.text(400, 318, "HP1 只是這一段的分組名字。", "b", "middle")
    bk.fig(s, "HP1 不等於爸爸", "電腦只知道哪些字母屬於同一組，不知道這組來自誰。所以跨 block 比較「HP1 比 HP2 多」沒有意義，也不能回答爸媽問題。",
           "看到論文寫 maternal、paternal，不代表真的知道親源。例如 B04 這樣稱呼 HP，但沒有親源資訊；Wakhan 就明寫親代狀態未知。",
           "要知道親源，得另外用親代資料，或靠 imprinting 甲基化加 Strand-seq。後者在 5 個 trio 的正常細胞驗證過，220 條全部判對，但腫瘤還沒驗證。", None, ("E6-11", "E8-09", "B04"))

    s = S("7.4", 800, 280)
    s.text(40, 76, "爸爸的", "b", "start"); s.text(40, 186, "媽媽的", "b", "start")
    s.bar(110, 70, 480, "dad", 18); s.bar(110, 180, 480, "mom", 18)
    s.rect(290, 54, 90, 32, "gene", "ink", r=3); s.rect(290, 164, 90, 32, "panel3", "ink", r=3)
    s.text(335, 75, "基因", "s", "middle", "on"); s.text(335, 185, "基因", "s", "middle")
    s.arrow(390, 40, 480, 40, c="ink2", sw=2.5)
    s.path("M490 40 q10 -14 20 0 t20 0 t20 0 t20 0", "gene", 3)
    s.text(530, 26, "有在用（產生 RNA）", "s", "middle")
    for i in range(4):
        x = 305 + i * 20
        s.line(x, 164, x, 148, "ink2", 2); s.circle(x, 145, 5, "ink2")
    s.text(335, 130, "關掉的記號（甲基化）", "s", "middle")
    s.arrow(390, 210, 460, 210, c="line2", sw=2.5); s.xmark(482, 210, 10); s.text(505, 215, "沒在用", "s")
    s.text(400, 256, "兩份的字母可以完全一樣。另外一些基因相反：只用媽媽的。", "t", "middle")
    bk.fig(s, "Imprinting：有些基因只用爸爸或媽媽那份", "有些基因雖然有兩份，但細胞只用其中一份。另一份不是壞了，而是被貼上「不要讀」的標記。這是「親源會影響腫瘤」的主要假說。",
           "被關掉的那份沒有突變。而且不是所有基因都這樣，imprinted 區只占基因組很小一部分。",
           "血液腫瘤的 14q aUPD：22 例中 21 例是父系那條被複製；同研究的 22q 則沒有偏差。所以偏差依基因座而定。", "確定", ("E8-16",))

    s = S("7.5", 800, 280)
    s.text(195, 26, "Cis：在同一條", "h", "middle"); s.text(605, 26, "Trans：在不同條", "h", "middle")
    s.bar(50, 70, 290, "dad", 18); s.bar(50, 116, 290, "mom", 18)
    s.star(150, 70, 12); s.star(240, 70, 12)
    s.bar(460, 70, 290, "dad", 18); s.bar(460, 116, 290, "mom", 18)
    s.star(560, 70, 12); s.star(650, 116, 12)
    s.text(195, 156, "媽媽這條還是好的", "b", "middle", "c4"); s.text(605, 156, "兩條都有問題", "b", "middle", "mut")
    s.line(400, 14, 400, 170, "line", 1.5)
    s.text(40, 192, "真實資料（都是 driver）", "h")
    rows = [("oncogene 雙突變", 91, 0, "cis 91%"), ("抑癌基因", 0, 71, "trans 71%"), ("抑癌基因（long read）", 2 / 19 * 100, 17 / 19 * 100, "17 trans、2 cis")]
    for i, (n, c, t, lab) in enumerate(rows):
        y = 202 + i * 25
        s.text(40, y + 15, n, "s")
        s.rect(210, y, 400, 19, "read", r=2)
        if c:
            s.rect(210, y, 400 * c / 100, 19, "c1", r=2)
        if t:
            s.rect(210 + 400 * (1 - t / 100), y, 400 * t / 100, 19, "c2", r=2)
        s.text(620, y + 15, lab, "s")
    s.rect(620, 186, 12, 12, "c1", r=2); s.text(636, 197, "cis", "s"); s.rect(668, 186, 12, 12, "c2", r=2); s.text(684, 197, "trans", "s")
    bk.fig(s, "Cis 和 trans：突變數相同，結果不同", "兩個突變落在同一條，另一條還是好的；分別落在兩條，就沒有好的了。這是 long read 最擅長回答的問題之一。",
           "這些比例只適用 driver，因為有選擇壓力。不能套到 passenger。short read 對 trans 較不敏感，所以 cis 可能被高估。灰色是該列來源沒有再分的部分。",
           None, "確定", ("E4-12", "E6-02"))

    s = S("7.6", 800, 400)
    s.text(400, 24, "你想問的問題，其實是兩個問題", "h", "middle")
    # ratio question
    s.rect(30, 40, 360, 210, "panel", r=8)
    s.text(210, 68, "問題一：總量差不多嗎？", "h", "middle")
    for i in range(10):
        s.rect(62 + i * 30, 90, 26, 34, "dad", r=3); s.star(75 + i * 30, 107, 8, "on")
    for i in range(10):
        s.rect(62 + i * 30, 132, 26, 34, "mom", r=3); s.star(75 + i * 30, 149, 8, "on")
    s.lines(210, 190, ["目前：沒偵測到差異", "但只有一篇 preprint（21 人，short read）"], "s", "middle", 20)
    s.text(210, 238, "上限約 4–5.7%", "b", "middle")
    # independence
    s.rect(410, 40, 360, 210, "panel", r=8)
    s.text(590, 68, "問題二：每個突變互相獨立嗎？", "h", "middle")
    s.bar(440, 110, 300, "dad", 12); s.bar(440, 150, 300, "mom", 12)
    for x in (480, 494, 508, 522, 536, 680):
        s.star(x, 110, 8)
    for x in (460, 590, 620, 720):
        s.star(x, 150, 8)
    s.lines(590, 190, ["局部不獨立：kataegis 擠在同一條", "其餘大部分：沒有人直接檢驗"], "s", "middle", 20)
    s.text(590, 238, "clustered 只占全部 3.7%", "b", "middle")
    s.rect(30, 268, 740, 120, "paper", "line")
    s.text(50, 294, "另外三個例外", "h")
    s.text(50, 322, "女性的 inactive X：突變常較多，一例校正後達 3.5 倍（是 X 的活性差異，不是爸媽差異）。", "s")
    s.text(50, 346, "Driver：受選擇影響，不是隨機。Passenger 接近隨機。", "s")
    s.text(50, 370, "Imprinted 區：21 人只有 2 個突變可分析，所以這篇 preprint 也沒測到。", "s")
    bk.fig(s, "突變平均分給爸爸和媽媽嗎？", "總量大致對稱，但證據還很薄。「每個突變獨立落在某一條」則沒有人完整驗證過。目前只能當合理的假設，不能當已證實的事實。",
           "基因 RB1、1p、11p15 等單一位置的親源偏差，不能推廣到全基因組。「爸爸的新生突變比較多」（父系 55.4、母系 14.2）是生殖細胞的事，也不能外推到腫瘤。",
           None, "還不知道", ("E4-26", "E4-02", "E4-20", "E4-04", "E4-17", "E8-G1"))


    s = S("7.7", 800, 722)
    ticks = json.loads((Path(__file__).parent / "colo829_ticks.json").read_text())
    def step(y, n, title):
        s.circle(40, y - 5, 13, "ink")
        s.text(40, y, n, "b", "middle", "paper")
        s.text(62, y, title, "h")
    x0 = 110
    step(26, "1", "直接數突變：hap1 看起來多很多")
    for y, name, n, c in [(46, "hap1", 27410, "hap1"), (86, "hap2", 17400, "hap2")]:
        w = 500 * n / 27410
        s.rect(x0, y, w, 30, c, r=4)
        s.text(x0 - 10, y + 20, name, "t", "end")
        s.text(x0 + w + 10, y + 20, f"{n:,}", "b")
    s.text(740, 69, "61%", "big", "end"); s.text(740, 109, "39%", "big", "end")
    step(160, "2", "看染色體：有些 hap2 沒有任何突變")
    y = 192
    for p in ticks:
        for off, ln, tk, c, label, n in ((0, p["hap1_mb"], p["hap1_ticks"], "hap1", p["name"] + " hap1", p["hap1_n"]), (24, p["hap2_mb"], p["hap2_ticks"], "hap2", "hap2", p["hap2_n"])):
            s.text(x0 - 10, y + off + 4, label, "s", "end")
            s.bar(x0, y + off, ln * 1.92, c, 12, dash=n == 0)
            for q in tk:
                s.line(x0 + q / 1e6 * 1.92, y + off - 8, x0 + q / 1e6 * 1.92, y + off + 8, "mut", 1.1)
            s.text(x0 + 500, y + off + 4, f"{n:,}", "b")
        if p["hap2_n"] == 0:
            s.rect(x0 + 118, y + 15, 244, 18, "paper", r=3)
            s.text(x0 + 240, y + 29, "沒有任何突變：很可能已被腫瘤丟掉", "s", "middle")
            s.text(x0 + 560, y + 28, "少了一條", "s")
        else:
            s.text(x0 + 560, y + 16, "差不多", "s")
        y += 70
    s.line(x0, y - 16, x0, y - 6, "mut", 1.6)
    s.text(x0 + 10, y - 6, "每條紅線代表 20 個突變，位置來自真實資料。圖上只畫 3 對做例子。", "s")
    s.rect(30, y + 8, 740, 40, "panel")
    s.text(400, y + 33, "全基因組有 844 Mb 的 hap2 沒有任何突變，hap1 只有 1 Mb。沒有那段 DNA，就數不到它的突變。", "t", "middle")
    y += 88
    step(y, "3", "只算還留著的片段：兩條幾乎一樣")
    y += 22
    for i, (name, n, ln, d, c) in enumerate([("hap1", 27410, 2934, 9.34, "hap1"), ("hap2", 17400, 1869, 9.31, "hap2")]):
        yy = y + i * 44
        s.text(x0 - 10, yy + 21, name, "t", "end")
        s.text(x0, yy + 21, f"{n:,} 個突變 ÷ {ln:,} Mb", "t")
        s.rect(x0 + 200, yy, 30 * d, 30, c, r=4)
        s.text(x0 + 200 + 30 * d + 10, yy + 21, f"{d:g} 個／Mb", "b")
    s.text(x0 + 200, y + 104, "長條長度代表每 Mb 的突變數（0 到 10）。比值 1.004，95% CI 0.985–1.023。", "s")
    y += 124
    s.rect(30, y, 740, 76, "panel")
    s.text(50, y + 28, "這只是一個黑色素瘤細胞株，而且不知道 hap1、hap2 哪條是爸爸。", "t")
    s.text(50, y + 54, "灰色只分兩條，不代表爸媽。丟掉那條原本有多少突變，已經無從得知。", "t")
    bk.fig(s, "用真實資料算一次：COLO829", "突變數看起來差很多，主要是因為這批細胞丟掉了部分 hap2（LOH）。只算還留著的片段，兩條每 Mb 的突變數幾乎相同。這張圖的紅線和數字是真實資料，灰色不代表爸媽。",
           "這不代表每對染色體都完全相等，chr14、chr16 就偏離預期較多。「留著的片段」也是用突變位置定義的，所以這是密度比較，不是獨立證明。另外，不同批的 COLO829 不完全一樣：實驗室另一批的 chr1p 還留著另一條。",
           "Sohn 2026（Cell）公開的 long read 突變表，由本 repo 計算，不是論文結論。獨立 ONT 資料用同一條 read 判斷，兩條都在的 2:1 區是 1,639 比 1,425。分早晚後，1 份那條仍比預測少約 10%，原因還不清楚，也不等於爸媽偏向。細節見 lab_report/2026-11-06_colo829_loss_events/。", "還不知道", ("E6-12",))


    s = S("7.8", 800, 732)
    bx, bw = 130, 230
    tx = 400
    def stars(y, xs):
        for x in xs:
            s.star(bx + x, y, 7)
    s.text(30, 28, "看整體：扣掉流失的片段，兩條幾乎一樣", "h")
    s.rect(30, 42, 740, 92, "panel", r=8)
    s.text(tx, 62, "COLO829（黑色素瘤）", "s")
    s.text(tx + 180, 62, "HG008（胰臟癌，體染色體）", "s")
    for y, name, c, xs, d1, d2 in [(84, "hap1", "hap1", (15, 50, 85, 120, 155, 190, 222), "9.34 個／Mb", "2.31 個／Mb"), (116, "hap2", "hap2", (30, 65, 100, 135, 170, 205), "9.31 個／Mb", "2.39 個／Mb")]:
        s.text(bx - 12, y + 5, name, "s", "end")
        s.bar(bx, y, bw, c, 14)
        stars(y, xs)
        s.text(tx, y + 5, d1, "b")
        s.text(tx + 180, y + 5, d2, "b")
    top = s
    # Every balanced window from lab_report/2026-11-06_prcgap_hap_snv_ratio/summary.tsv.
    panel8 = S("7.8", 800, 202)
    panel8.text(30, 24, "再逐段比：明顯不同的段很少", "h")
    panel8.rect(30, 36, 740, 150, "panel", r=8)
    panel8.text(50, 58, "每一格是一段 20 Mb，這一段兩條都在，拷貝數也相同。格子順序不代表位置。", "s")
    panel8.rect(50, 69, 9, 9, "ink", r=1)
    panel8.text(64, 78, "校正後顯著", "s")
    panel8.rect(150, 69, 9, 9, "panel3", r=1)
    panel8.text(164, 78, "沒有顯著差異", "s")
    panel8.text(756, 78, "顯著／全部", "s", "end")
    for i, (name, n, k) in enumerate([("COLO829", 33, 1), ("HG008", 43, 0)]):
        y = 90 + i * 20
        panel8.text(50, y + 10, name, "s")
        for j in range(n):
            panel8.rect(120 + j * 7.5, y, 6, 11, "ink" if j < k else "panel3", r=1)
        panel8.text(756, y + 10, f"{k}／{n}", "s", "end")
    panel8.text(50, 148, "合計 1／76。顯著的那段：COLO829 chr15 80–100 Mb，131 比 83。", "b")
    panel8.text(50, 170, "COLO829 的段間差異比純隨機大（卡方／自由度 2.44），HG008 接近隨機（1.21）。", "s")
    s = S("7.8", 800, 732)
    s.text(30, 170, "看區域：有四種不同的偏向", "h")
    rows = [
        (184, "LOH 區", "COLO829 實測", "一條不見了", ["186／189 個突變在留下的那條。", "另一條的突變已經看不到，", "所以這不代表突變率偏向。"]),
        (306, "2:1 區", "COLO829 實測", "兩條都在，接近各半", ["2 份那條 1,639 個，1 份那條 1,425 個（46.5%）。", "各染色體的 1 份那條占 41%–51%。", "1 份那條仍比預測少約 10%，原因未定。"]),
        (428, "Kataegis", "論文，其他腫瘤", "一串突變擠在同一條", ["這才是突變真的集中在一條。", "但只占很小一部分：", "clustered 突變占全部的 3.7%（PCAWG）。"]),
        (550, "chrX", "HG008 實測", "inactive X 那條突變較多", ["2.46 比 3.71 個／Mb，比值 0.66。", "論文也寫 inactive 那條的 SNV 較多。", "這是 X 不活化的差異，不是爸媽差異。"]),
    ]
    for y, name, where, title, body in rows:
        s.rect(30, y, 740, 112, "panel", r=8)
        s.text(44, y + 26, name, "b")
        s.text(44, y + 46, where, "s")
        s.text(tx, y + 28, title, "h")
        s.lines(tx, y + 52, body, "s", "start", 20)
    # LOH: the second copy is gone
    s.bar(bx + 40, 216, bw - 40, "hap1", 14)
    stars(216, (55, 90, 125, 160, 195, 222))
    s.bar(bx + 40, 256, bw - 40, "hap2", 14, dash=True)
    s.text(bx + 135, 280, "這條已丟失", "s", "middle")
    # 2:1: two copies against one
    for y in (330, 356):
        s.bar(bx + 40, y, bw - 40, "hap1", 14)
        stars(y, (60, 105, 150, 195))
    s.star(bx + 222, 330, 7)
    s.bar(bx + 40, 390, bw - 40, "hap2", 14)
    stars(390, (75, 120, 165, 210))
    # Kataegis: a tight cluster on one copy
    s.bar(bx + 40, 462, bw - 40, "hap1", 14)
    stars(462, (108, 120, 132, 144, 156, 168))
    s.bar(bx + 40, 506, bw - 40, "hap2", 14)
    stars(506, (70, 205))
    # chrX: the inactive copy carries more
    s.bar(bx + 40, 584, bw - 40, "hap1", 14)
    stars(584, (60, 100, 140, 180, 218))
    s.bar(bx + 40, 628, bw - 40, "hap2", 14)
    stars(628, (52, 80, 108, 136, 164, 192, 220))
    s.text(bx + 135, 652, "inactive X", "s", "middle")
    s.rect(30, 674, 740, 46, "paper", "line")
    s.text(400, 703, "整體接近各半，不代表每一段都各半；某一段偏向，也不代表爸爸或媽媽較多。", "t", "middle")
    region = s
    body = S("7.8", 800, 934)
    for part, dy in ((top, 0), (panel8, 146), (region, 202)):
        place(body, part, dy)
    # Unit strip above the comparison. The chr1 bar is to scale: 680 px for about 250 Mb.
    offset = 206
    s = S("7.8", 800, body.h + offset)
    s.text(30, 24, "先看單位：個／Mb", "h")
    s.rect(30, 36, 740, 158, "panel", r=8)
    s.text(60, 60, "chr1：約 250 Mb（長度照比例）", "s")
    s.text(400, 60, "這一小格是 1 Mb", "s", "middle")
    s.bar(60, 76, 680, "hap1", 14)
    s.rect(398, 66, 3, 20, "ink", r=1)
    s.line(398, 86, 170, 108, "line2", 1.5, dash=True)
    s.line(401, 86, 630, 108, "line2", 1.5, dash=True)
    s.bar(170, 118, 460, "hap1", 18)
    s.star(300, 118, 8)
    s.star(500, 118, 8)
    s.text(160, 123, "1 Mb", "b", "end")
    s.text(640, 123, "1,000,000 個鹼基", "s")
    s.text(400, 150, "放大這一格：HG008 平均每格約 2.3 個突變（紅星位置只是示意）", "s", "middle")
    s.text(400, 179, "4,351 個突變 ÷ 1,884 Mb = 2.31 個／Mb（HG008 體染色體的 hap1）", "b", "middle")
    place(s, body, offset)
    bk.fig(s, "看整體和看區域，答案不同", "兩個細胞株的體染色體，留著的片段兩條都接近一樣多。再逐段比，兩條拷貝數相同的 76 段中，只有 1 段校正後顯著。區域上仍可能偏向一邊，但原因不同：可能是一條不見了、一串突變擠在同一條，或是 X 不活化。",
           "區域偏向沒有固定方向。2 份那條在各染色體不一定來自同一位親代，這裡也沒有量親源，所以不能說成「偏向爸爸」或「偏向媽媽」。逐段比的 hap1、hap2 也不能加總成全基因組比例：和 GIAB 比對時，HG008 的 23 條染色體有 14 條標籤是對調的（圖 7.10）。那 1 段的原因沒有查，圖上的 4 種類型不是它們的解釋。",
           "COLO829 和 HG008 都是本 repo 用公開突變表算的，不是論文結論。HG008 體染色體的比值是 0.97（95% CI 0.93–1.01），只含 truncal 突變，原始比例 44:56 也有 LOH 的影響；它的 chr5 比值 1.32，校正後仍顯著，原因沒有查。COLO829 的調查到此結束，再查細節也不能推廣到其他腫瘤。B04（肺癌，long read）也找到超過 80% 突變集中在一條 HP 的區域，但這些突變只占全部約 0.35–0.41%，而且是否超過偶然還沒有核對。逐段比的格子圖用 PRCGAP 公開結果（Sakamoto 2026，未經同儕審查的預印本）由本 repo 計算，不是論文結論，所以來源和最上面那格不同。校正是因為每株同時比很多段（Bonferroni）。過濾後幾乎只看高 VAF 的突變，subclonal 的情況看不到；這個過濾只在 HG008 用 GIAB 驗證過（吻合 99.9%，涵蓋 64.5%），單倍型判定也只有 HG008 和 GIAB 比對過（整條染色體可對調後，一致 97.4%），所以 COLO829 這部分沒有同等驗證。細節見 lab_report/2026-11-06_colo829_loss_events/、lab_report/2026-11-06_hg008_hap_snv_ratio/、lab_report/2026-11-06_prcgap_hap_snv_ratio/。",
           "還不知道", ("E6-12", "E6-HG008", "E6-15", "E6-16", "E4-02", "E4-20", "B04"))
    label_strength(bk)
    giab_comparison(bk)


def label_strength(bk):
    """What an assembly's hap1 and hap2 labels can and cannot prove."""
    s = S("7.9", 800, 640)
    bx, bw = 180, 250
    tx = 470
    rows = [
        (20, "同一條內", "兩個突變在同一條嗎？", "相對強", ["組裝把 long read 接成連續序列，", "同一條 contig 上的突變，", "通常真的在同一條染色體拷貝上。"], "stok"),
        (172, "同一對內", "這對的兩條，誰的突變多？", "可以，但要控制拷貝數", ["兩條比的是同一對染色體。", "但份數多的那條，突變也可能較多，", "所以要比拷貝數相同的區段。"], "stok"),
        (324, "跨染色體", "全部 hap1 加起來比 hap2？", "不行", ["chr1 的 hap1 和 chr2 的 hap1，", "不一定來自同一位親代。", "編號只在一條染色體內有意義。"], "stdis"),
        (476, "爸爸媽媽", "突變偏向爸爸或媽媽？", "不行", ["hap1 只是編號，沒有量到親源。", "要有爸媽的序列，", "或印記區的甲基化這類標記。"], "stdis"),
    ]
    for y, name, question, verdict, why, tone in rows:
        s.rect(30, y, 740, 136, "panel", r=8)
        s.text(46, y + 28, name, "h")
        s.text(tx, y + 28, question, "b")
        s.text(tx, y + 52, verdict, "h", color=tone)
        s.lines(tx, y + 76, why, "s", "start", 19)
    # The same contig: two stars tied together.
    s.text(bx - 12, 77, "hap1", "s", "end")
    s.bar(bx, 72, bw, "hap1", 14)
    s.star(bx + 70, 72, 8)
    s.star(bx + 180, 72, 8)
    s.line(bx + 70, 54, bx + 180, 54, "ink2", 1.5)
    s.line(bx + 70, 54, bx + 70, 62, "ink2", 1.5)
    s.line(bx + 180, 54, bx + 180, 62, "ink2", 1.5)
    s.text(bx + 125, 46, "同一條連續序列", "s", "middle")
    s.text(bx - 12, 117, "hap2", "s", "end")
    s.bar(bx, 112, bw, "hap2", 14)
    # One pair: count stars on the two bars of one chromosome.
    for y, name, c, xs, n in ((222, "hap1", "hap1", (50, 120, 190), "3 個"), (262, "hap2", "hap2", (35, 90, 150, 215), "4 個")):
        s.text(bx - 12, y + 5, name, "s", "end")
        s.bar(bx, y, bw - 50, c, 14)
        for x in xs:
            s.star(bx + x * .8, y, 8)
        s.text(bx + bw - 40, y + 5, n, "s")
    # Across chromosomes: the same word, two unknown parents.
    for x, chrom in ((90, "chr1"), (280, "chr2")):
        s.text(x + 66, 372, chrom, "b", "middle")
        s.text(x, 398, "hap1", "s", "end")
        s.bar(x + 6, 393, 120, "hap1", 14)
        s.text(x + 66, 432, "來自哪一位？不知道", "s", "middle")
    # Parents: the label does not connect to a person.
    s.person(160, 498, 70, "dad")
    s.text(160, 590, "爸爸", "s", "middle")
    s.person(420, 498, 70, "mom")
    s.text(420, 590, "媽媽", "s", "middle")
    s.text(290, 520, "hap1", "s", "middle")
    s.bar(230, 530, 120, "hap1", 14)
    s.line(216, 537, 186, 537, "line2", 2, dash=True)
    s.line(364, 537, 394, 537, "line2", 2, dash=True)
    s.text(201, 528, "？", "b", "middle")
    s.text(379, 528, "？", "b", "middle")
    s.text(290, 572, "沒有資料能連起來", "s", "middle")
    bk.fig(s, "組裝標籤能證明什麼", "組裝標籤是相對強的證據，但它回答的是「這些突變是否在同一條染色體拷貝上」。它不回答「這條來自爸爸還是媽媽」。",
           "把 hap1 看成爸爸、hap2 看成媽媽。實際上它們只是組裝時給的編號。",
           "HG008 和 GIAB 對照時，23 條染色體有 14 條的編號整條相反（圖 7.10）。在目前查過的 PRCGAP 8 株、COLO829 和 HG008 公開資料中，都沒有能驗證親源的資料；這不代表所有公開細胞株都沒有。",
           "確定", ("E6-16", "E6-HG008"))


# lab_report/2026-11-07_hg008_giab_hap_concordance/per_chromosome.tsv: same label, swapped label.
GIAB_CHROMS = [("1", 468, 11), ("2", 603, 26), ("3", 470, 15), ("4", 8, 273), ("5", 3, 376), ("6", 13, 261), ("7", 332, 2), ("8", 9, 324),
               ("9", 2, 136), ("10", 352, 10), ("11", 8, 316), ("12", 5, 222), ("13", 13, 302), ("14", 9, 267), ("15", 1, 205), ("16", 145, 4),
               ("17", 83, 1), ("18", 140, 1), ("19", 68, 0), ("20", 0, 146), ("21", 0, 56), ("22", 1, 46), ("X", 21, 548)]


def giab_comparison(bk):
    """How the PRCGAP haplotype of an HG008 SNV is compared with the GIAB benchmark, with the real counts."""
    s = S("7.10", 800, 910)

    def step(y, h, n, title):
        s.rect(30, y, 740, h, "panel", r=8)
        s.circle(58, y + 26, 15, "ink")
        s.text(58, y + 31, str(n), "b", "middle", color="paper")
        s.text(84, y + 32, title, "h")

    step(16, 188, 1, "兩個團隊，各自得到一份答案")
    for x, team, how, count in ((50, "PRCGAP（Sakamoto 2026）", ["把 read 比到自己組裝的正常基因體，", "找出突變，看它落在哪條 contig。"], "HG008 過濾後 6,821 個 SNV"),
                                (415, "GIAB benchmark v0.4（draft）", ["直接比對腫瘤組裝和正常組裝 v6.3，", "再用多種定序資料確認每個突變。"], "GRCh38 上 9,574 個 truncal SNV")):
        s.rect(x, 62, 335, 130, "paper", "line", r=6)
        s.text(x + 16, 86, team, "b")
        s.lines(x + 16, 110, how, "s", "start", 19)
        s.text(x + 16, 174, count, "s")

    step(220, 150, 2, "換到同一把尺：找出同一個突變")
    s.text(84, 276, "GRCh38 同一位置、同樣的鹼基變化，才算同一個突變。", "s")
    s.bar(84, 300, 420, "panel3", 14)
    s.star(300, 300, 9)
    s.text(300, 340, "示意：同一個位置，同樣是 G→A", "s", "middle")
    s.text(740, 286, "6,306 個對到", "h", "end")
    s.text(740, 312, "4 個 GIAB 標籤不明，扣除", "s", "end")
    s.text(740, 338, "實際比較 6,302 個", "b", "end")

    step(386, 140, 3, "比編號：一條染色體可以整條相反")
    s.text(84, 440, "兩邊的 hap1 是各自取的名字，所以只看「整條是不是一致」。", "s")
    for x, chrom, same, swap, result in ((84, "chr7", 332, 2, "編號相同，一致"), (430, "chr5", 3, 376, "編號整條相反，對調後一致")):
        s.text(x, 472, f"{chrom}：相同 {same}，相反 {swap}", "b")
        s.text(x, 498, result, "s")

    step(542, 282, 4, "真實結果：23 條染色體，每條都幾乎一面倒")
    s.rect(84, 588, 10, 10, "ink", r=1)
    s.text(100, 598, "編號相同", "s")
    s.rect(190, 588, 10, 10, "panel3", r=1)
    s.text(206, 598, "編號相反", "s")
    x0, step_x, top, height = 78, 28.4, 620, 120
    for i, (chrom, same, swap) in enumerate(GIAB_CHROMS):
        x = x0 + i * step_x
        top_h = height * same / (same + swap)
        if same:
            s.rect(x, top + height - top_h, 20, top_h, "ink", r=1)
        if swap:
            s.rect(x, top, 20, height - top_h - (1 if same else 0), "panel3", r=1)
        s.text(x + 10, top + height + 18, chrom, "s", "middle")
    s.text(400, 790, "對調後一致：6,139 ／ 6,302 = 97.4%", "h", "middle")
    s.text(400, 812, "14 條編號相反，9 條編號相同", "s", "middle")

    s.rect(30, 838, 740, 56, "paper", "line")
    s.text(400, 860, "這是兩份組裝結果互相一致，不是和絕對真值比對。", "t", "middle")
    s.text(400, 882, "兩邊都沒有親源資訊，所以 97.4% 也不能回答爸爸或媽媽。", "s", "middle")
    bk.fig(s, "HG008 怎麼和 GIAB benchmark 對照", "先找出兩邊都有的同一個突變，再比它落在哪一條。因為編號是各自取的，所以每條染色體可以整條對調一次。6,302 個突變中，對調後有 97.4% 一致。",
           "以為 97.4% 代表和真值一致。GIAB 也來自組裝，而且還是 draft；這裡證明的是兩份結果互相吻合。",
           "只比較 GIAB 也有的 truncal SNV，所以低 VAF 的 subclonal 突變不在內。每條染色體取較多的方向當一致，所以比例會略為偏高，但各條都幾乎一面倒，影響很小。其餘 163 個不一致的原因沒有查。兩邊是否用到相同的定序資料沒有核對，所以不能算完全獨立。GIAB 會用多種定序資料確認突變，也抽查過 34 個重複出現的位點，但沒有逐一人工檢查所有突變。GIAB 的做法見其 v0.4 README；細節見 lab_report/2026-11-07_hg008_giab_hap_concordance/。",
           None, ("E6-16", "E6-HG008"))


def place(target, part, dy):
    """Draw part inside target, shifted down by dy, and keep its labels in the overlap check."""
    target.raw(f'<g transform="translate(0,{dy})">' + "".join(part.items) + "</g>")
    target.boxes += [(x0, y0 + dy, x1, y1 + dy, t) for x0, y0, x1, y1, t in part.boxes]


def closing(bk):
    bk.chapter("map", "目前知道多少", "到這裡，你已經看過整個故事。這一章把重要結論分成三堆：確定的、還在爭論的、還不知道的。")
    s = S("8.1", 800, 590)
    cols = [("比較確定", "ok", ["癌症是一步步累積的", "基因裡的突變，大多數|對癌細胞沒有明顯影響", "多數腫瘤測得到 subclone", "沒有一種樹形|適用所有癌別", "1/f 尾巴不能單獨證明中性", "Driver 在兩條上不是隨機的", "HP1 不等於爸爸", "CN 事件以一段為單位發生"]),
            ("還在爭論", "dis", ["有多少腫瘤有效中性", "Subclone 是選擇還是漂變", "負選擇有多強", "腫瘤內突變率是否固定", "突變量能不能當分裂時鐘", "WGD 算不算早期事件", "低頻尾巴代表什麼", "Big Bang 適用多少癌別"]),
            ("還不知道", "gap", ["long read 的 HP 比例|（目前只放兩個細胞株）", "其餘突變是否互相獨立", "未治療實體瘤的|clone 比例分布", "實體瘤的 linear／branching|比例", "Sweep 在實體瘤多常發生", "單一 bulk 能重建|多少真實的樹", "腫瘤的親源能否|用 long read 定", "LOH、gain 的|全基因組親源偏差"])]
    fills = {"ok": "stok", "dis": "stdis", "gap": "stgap"}
    for i, (t, k, items) in enumerate(cols):
        x = 20 + i * 258
        s.rect(x, 12, 244, 40, fills[k], r=6)
        s.text(x + 122, 38, t, "h", "middle", "on")
        for j, it in enumerate(items):
            y = 62 + j * 64
            s.rect(x, y, 244, 56, "panel", r=6)
            rows = it.split("|")
            s.lines(x + 122, y + 33 - (len(rows) - 1) * 9, rows, "s", "middle", 18)
    bk.fig(s, "三堆結論", "每一項的來源和細節，都在前面對應的圖下面。這些分類是整理時的判斷，不是領域的正式評等。")

    s = S("8.2", 800, 300)
    s.text(400, 24, "每一種證據能告訴你多少", "h", "middle")
    rows = [("統計量相似", "資料看起來像", "panel3", 250), ("單細胞、克隆分群", "克隆結構大概對", "c2", 480), ("lineage tracing、時序取樣", "過程真的這樣發生", "c1", 690)]
    for i, (a, b, c, w) in enumerate(rows):
        y = 46 + i * 62
        s.rect(50, y, w, 48, c, r=6)
        s.text(60 + w, y + 30, "", "s")
        s.text(66, y + 30, a, "t", "start", "on" if c != "panel3" else "ink")
    s.text(310, 75, "只能說：資料看起來像", "s"); s.text(540, 137, "能說：克隆結構大概對", "s")
    s.text(66, 225, "", "s")
    s.text(66, 246, "最右邊的證據最強，但多半只能在小鼠或細胞株做。", "t")
    s.text(66, 272, "而且只要是病人的資料，演化樹就仍然是推論出來的。", "t")
    s.text(690, 199, "能說：過程真的這樣發生（在該實驗系統）", "s", "end", "on")
    bk.fig(s, "讀論文時先問：這是哪一種證據", "看到一個關於演化的結論，先問它來自哪種資料。bulk 統計相似，不能證明演化過程正確。這是 11-04 會議的核心提醒。長條長度是整理時的判斷，不是量測值。")


def build(bk):
    big_events(bk); seeing(bk); parents(bk); closing(bk)
