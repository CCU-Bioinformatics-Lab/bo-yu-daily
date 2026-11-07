#!/usr/bin/env python3
"""Build the tumor evolution primer: python3 build_site.py (run inside this directory).

Writes index.html. Figures come from ch_a.py and ch_b.py; the paper table comes from ../source.md.
Prints label problems and the share of vertical space taken by figures.
"""
import re
from html import escape
from pathlib import Path

import ch_a
import ch_b
from lib import PROBLEMS, Book

HERE = Path(__file__).resolve().parent

GLOSSARY = [("Clone", "同一個祖先細胞傳下來、帶相同突變的一群細胞。"), ("Subclone", "只占腫瘤一部分的 clone。"),
            ("Coding 突變", "落在基因製造蛋白質那段 DNA 上的突變。"), ("Driver", "真的讓細胞長得更好的突變。"), ("Passenger", "對生長沒有明顯幫助，只是跟著被複製的突變。"),
            ("Clonal／Subclonal", "每個腫瘤細胞都有／只有一部分有。"), ("Trunk／Branch", "樹幹：所有癌細胞共有的突變。樹枝：部分細胞才有的突變。"),
            ("Sweep", "一個 clone 長到幾乎取代其他 clone。"), ("ISA（無限位點假設）", "假設同一個位置一生只突變一次。"), ("Mb", "一百萬個鹼基。「個／Mb」是每一百萬個鹼基有幾個突變。"), ("Read", "定序機讀出的一段 DNA。"), ("Depth", "一個位置被多少條 read 蓋到。"),
            ("VAF", "一個位置上，帶突變的 read 比例。"), ("Purity", "樣本裡腫瘤細胞的比例。"), ("CCF", "腫瘤細胞裡，帶這個突變的細胞比例。"),
            ("Haplotype（HP）", "同一條染色體上連在一起的字母組合。資料裡的 HP1、HP2 只是組名。"), ("Phase block", "能確定彼此關係的一段染色體。"), ("HP0／unphased", "分不到兩組的 read。"),
            ("Germline／Somatic", "遺傳來、全身都有／出生後才發生、只有部分細胞有。"), ("LOH", "兩份不同的版本變成只剩一種。"), ("cnLOH", "總條數不變，但兩條已相同。"),
            ("Copy number（CN）", "一段 DNA 有幾份。"), ("Multiplicity", "這幾份裡，帶突變的有幾份。"), ("WGD", "整套染色體一次加倍。"),
            ("Cis／Trans", "在同一條／在不同條。"), ("Imprinting", "基因只用爸爸或媽媽那一份。"), ("Signature", "某個突變來源留下的突變類型比例。"),
            ("GIAB benchmark", "NIST 的 GIAB 團隊整理的標準突變清單，用來檢查其他方法。HG008 的版本還是 draft。"), ("Kataegis", "一小段染色體上突然出現的一串突變。"), ("PDX／Xenograft", "把人類腫瘤或細胞種到小鼠身上。"), ("Lineage tracing", "在細胞裡寫入條碼，直接追蹤家族關係。")]

REFS_VISUAL = [("魚形圖", "Miller 2016, fishplot", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5100182/"),
               ("四種模式", "Davis 2017, Tumor evolution: Linear, branching, neutral or punctuated?", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5558210/"),
               ("Clone 與細胞團", "Wikimedia Commons: Clonal Evolution Model", "https://commons.wikimedia.org/wiki/File:Clonal_Evolution_Model.png"),
               ("VAF、CCF、峰圖", "Dentro 2017, Principles of reconstructing the subclonal architecture", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5538405/"),
               ("Purity、峰圖", "Caravagna 2020, MOBSTER", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7610388/"),
               ("不同歷史同資料", "Qi 2019", "https://almob.biomedcentral.com/articles/10.1186/s13015-019-0155-6"),
               ("Bulk 和單細胞", "Kuipers 2017", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5813714/"),
               ("多區域", "Tarabichi 2021", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7867630/"),
               ("Multiplicity", "GRITIC 2024", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7616501/"),
               ("Two-hit", "Wikimedia Commons: The two-hit hypothesis", "https://commons.wikimedia.org/wiki/File:The_two-hit_hypothesis.jpg"),
               ("Kataegis", "Wikimedia Commons: Rainplot for Kataegis", "https://commons.wikimedia.org/wiki/File:Rainplot_for_Kataegis_in_Breast_Cancer_Genome.jpg"),
               ("搭便車", "eLife 67790", "https://elifesciences.org/articles/67790/figures")]

CSS = """
/* Layout: a picture book with one column. One chapter at a time; the figure is the page. */
:root{--paper:#fbfcfb;--panel:#eef2ef;--panel2:#dfe6e1;--panel3:#bcc7c0;--ink:#1c2a26;--ink2:#46574f;--mute:#5a6a62;--line:#d4dcd6;--line2:#8a9a91;--read:#d8dfda;--normal:#e3e8e4;--cellline:#6f7f76;--fishline:#ffffff;
--hap1:#56666e;--hap2:#a3b0a9;--dad:#2f6fc0;--mom:#e0812a;--mut:#d3263f;--star2:#1a3a78;--star3:#46574f;--c1:#2ea57f;--c2:#8456c4;--c3:#d8a31e;--c4:#2f8f6a;--drug:#7b2d4e;--vessel:#c2697b;--gene:#2f8f6a;--hl:#fbeeb4;--on:#ffffff;
--stok:#2f8f6a;--stdis:#c9741c;--stgap:#6a6a86;
--sans:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#141a18;--panel:#1f2825;--panel2:#2a3531;--panel3:#55655d;--ink:#e8efea;--ink2:#b9c6be;--mute:#a4b3aa;--line:#33403b;--line2:#7d8f85;--read:#37443e;--normal:#46534d;--cellline:#8fa097;--fishline:#141a18;
--hap1:#7f909a;--hap2:#4d5b55;--dad:#5a93e0;--mom:#ec9a4a;--mut:#ef5168;--star2:#bcd2f5;--star3:#b9c6be;--c1:#3fb68f;--c2:#a07de0;--c3:#e3b640;--c4:#49a884;--drug:#a64a72;--vessel:#c2697b;--gene:#49a884;--hl:#4d4720;--on:#ffffff;--stok:#2f8f6a;--stdis:#b5671a;--stgap:#6a6a86;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#141a18;--panel:#1f2825;--panel2:#2a3531;--panel3:#55655d;--ink:#e8efea;--ink2:#b9c6be;--mute:#a4b3aa;--line:#33403b;--line2:#7d8f85;--read:#37443e;--normal:#46534d;--cellline:#8fa097;--fishline:#141a18;
--hap1:#7f909a;--hap2:#4d5b55;--dad:#5a93e0;--mom:#ec9a4a;--mut:#ef5168;--star2:#bcd2f5;--star3:#b9c6be;--c1:#3fb68f;--c2:#a07de0;--c3:#e3b640;--c4:#49a884;--drug:#a64a72;--vessel:#c2697b;--gene:#49a884;--hl:#4d4720;--on:#ffffff;--stok:#2f8f6a;--stdis:#b5671a;--stgap:#6a6a86;color-scheme:dark}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.75}
.wrap{max-width:920px;margin:0 auto;padding-block:22px 70px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.top{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 14px;margin-bottom:10px}
.brand{font-size:21px;font-weight:700}
nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:34px}
nav a{padding:3px 11px;border-radius:999px;background:var(--panel);color:var(--ink);text-decoration:none;font-size:14.5px}
nav a:hover{background:var(--panel2)}
nav a[aria-current="page"]{background:var(--ink);color:var(--paper);font-weight:700}
h1{font-size:32px;line-height:1.3;margin:0 0 10px;text-wrap:balance}
.lead{font-size:18px;color:var(--ink2);margin:0 0 36px;max-width:42em}
figure{margin:0 0 58px}
h2{font-size:20px;margin:0 0 12px;text-wrap:balance}
.no{font-family:var(--mono);font-size:14px;color:var(--mute);margin-right:9px;font-weight:400}
.draw{overflow-x:auto}
.draw svg{display:block;width:100%;min-width:660px;height:auto}
figcaption{font-size:17.5px;margin-top:12px;max-width:44em}
.more{margin-top:10px;font-size:15px}
summary{cursor:pointer;color:var(--ink2);font-size:14.5px;width:fit-content}
.note{font-size:15px;margin:8px 0 0;max-width:46em;color:var(--ink2)}
.note b{color:var(--ink)}
.state{display:inline-block;font-size:12.5px;padding:0 8px;border-radius:999px;color:#fff;margin-left:3px;line-height:1.7}
.st-ok{background:var(--stok)}.st-dis{background:var(--stdis)}.st-gap{background:var(--stgap)}
.src{font-family:var(--mono);font-size:12px;color:var(--mute);margin-left:5px}
.pager{display:flex;justify-content:space-between;gap:12px;font-size:16.5px;border-top:1px solid var(--line);padding-top:18px}
.pager a{color:var(--ink);font-weight:700}
dl{display:grid;grid-template-columns:minmax(120px,190px) minmax(0,1fr);gap:9px 18px;margin:0 0 44px;font-size:16px}
dt{font-weight:700}dd{margin:0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td a{color:var(--ink2);word-break:break-all}
.tw{overflow-x:auto}
h3{font-size:19px;margin:34px 0 10px}
input[type=search]{width:100%;max-width:26em;padding:7px 10px;border:1px solid var(--line2);border-radius:6px;background:var(--paper);color:var(--ink);font:inherit;margin-bottom:12px}
ul{padding-left:1.2em;max-width:46em;font-size:16px}
a:focus-visible,input:focus-visible{outline:2px solid var(--mut);outline-offset:2px}
svg text{font-family:var(--sans);fill:var(--ink)}
svg .t{font-size:14px}svg .s{font-size:12.5px;fill:var(--ink2)}svg .h{font-size:15px;font-weight:700}svg .b{font-size:14px;font-weight:700}svg .n{font-size:13px;font-family:var(--mono)}svg .big{font-size:22px;font-weight:700}
"""

JS = """
const views=[...document.querySelectorAll('section.view')];const ids=views.map(v=>v.id);
const links=[...document.querySelectorAll('nav a')];
function show(){let h=location.hash.slice(1);if(!ids.includes(h))h=ids[0];
views.forEach(v=>v.hidden=v.id!==h);
links.forEach(a=>{if(a.getAttribute('href')==='#'+h)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
window.scrollTo(0,0)}
addEventListener('hashchange',show);show();
const q=document.getElementById('paperq');
function filter(){const t=q.value.trim().toLowerCase();document.querySelectorAll('#papers tbody tr').forEach(r=>{r.hidden=t&&!r.textContent.toLowerCase().includes(t)})}
q.addEventListener('input',filter);
document.addEventListener('click',e=>{const a=e.target.closest('a.src');if(!a)return;e.preventDefault();q.value=a.dataset.ref;filter();location.hash='refs'});
"""


def paper_rows():
    out = []
    for line in (HERE.parent / "source.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (.+?) \| (.*?) \| (全文|摘要|網頁片段) \| (\S+) \|", line)
        if m:
            ids, cite, lvl, url = m.groups()
            out.append(f'<tr><td>{escape(ids)}</td><td>{escape(cite)}</td><td>{lvl}</td><td><a href="{escape(url)}" rel="noreferrer">{escape(url.replace("https://doi.org/", ""))}</a></td></tr>')
    return out


def main():
    bk = Book()
    ch_a.build(bk)
    ch_b.build(bk)
    nav, sections = [], []
    chs = bk.chapters
    extra = [("words", "詞典"), ("refs", "來源")]
    for i, ch in enumerate(chs):
        nav.append(f'<a href="#{ch["id"]}">{escape(ch["title"])}</a>')
        prev_ = f'<a href="#{chs[i - 1]["id"]}">← {escape(chs[i - 1]["title"])}</a>' if i else "<span></span>"
        next_ = f'<a href="#{chs[i + 1]["id"]}">下一章：{escape(chs[i + 1]["title"])} →</a>' if i + 1 < len(chs) else '<a href="#words">詞典 →</a>'
        sections.append(f'<section class="view" id="{ch["id"]}"><h1>{escape(ch["title"])}</h1><p class="lead">{escape(ch["lead"])}</p>{"".join(ch["figs"])}<div class="pager">{prev_}{next_}</div></section>')
    for cid, name in extra:
        nav.append(f'<a href="#{cid}">{name}</a>')
    words = "".join(f"<dt>{escape(a)}</dt><dd>{escape(b)}</dd>" for a, b in GLOSSARY)
    sections.append(f'<section class="view" id="words"><h1>白話詞典</h1><p class="lead">看到不懂的詞，回來這裡查。</p><dl>{words}</dl><div class="pager"><a href="#{chs[-1]["id"]}">← {escape(chs[-1]["title"])}</a><a href="#refs">來源 →</a></div></section>')
    rows = paper_rows()
    vis = "".join(f'<li>{escape(a)}：<a href="{escape(u)}" rel="noreferrer">{escape(b)}</a></li>' for a, b, u in REFS_VISUAL)
    sections.append(f"""<section class="view" id="refs"><h1>來源和限制</h1>
<p class="lead">這個網站由 AI 整理，不是第一手證據。下決定前，回原文核對你要用的那一條。</p>
<ul>
<li>圖都是原創示意，除非寫明「真實資料」，形狀和比例都不是資料。圖中算術例子（例如 10 條 read）是教學用的數字。</li>
<li>「真實資料」來自本 repo 的文獻調查。多數論文只讀相關段落，當天 NCBI 失敗，所以不是系統性回顧。</li>
<li>除了標 long read 的，數字幾乎都來自 short read，或單細胞、實驗系統。它們是生物知識的證據，不是模擬器的設定值。</li>
<li>部分論文文字曾由子代理用偽裝 User-Agent 抓取。核心 preprint 的數字已重新確認，其他沒有逐一重抓。</li>
<li>確定、還在爭論、還不知道：這是整理時的判斷，不是領域的正式評等。</li>
<li>基礎定義（雙倍體、VAF、CCF、WGD 等）來自教科書層級的知識，圖 1.3 的 signature 高低也只是大概樣子。</li>
</ul>
<h3>論文</h3>
<input type="search" id="paperq" placeholder="搜尋編號、作者、期刊" aria-label="搜尋論文">
<div class="tw"><table id="papers"><thead><tr><th>編號</th><th>論文</th><th>層級</th><th>DOI</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<h3>畫法參考</h3>
<p>這些圖只參考構圖，沒有複製。子代理共看過 76 張外部圖片。</p><ul>{vis}</ul></section>""")
    table = "".join(rows)
    for x in sorted(bk.used):
        if not re.search(r"(?<![\w-])(E\d-)?" + re.escape(x) + r"(?![\w-])", table):
            PROBLEMS.append(f"citation not in paper table: {x}")
    n_fig = sum(len(c["figs"]) for c in chs)
    head = """<title>腫瘤演化入門</title><meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;700&display=swap">"""
    html = f"""{head}<style>{CSS}</style>
<div class="wrap"><div class="top"><span class="brand">腫瘤演化入門</span></div><nav aria-label="章節">{''.join(nav)}</nav>
<main>{''.join(sections)}</main></div><script>{JS}</script>"""
    (HERE / "index.html").write_text(html, encoding="utf-8")
    heights = [int(h) for h in re.findall(r'viewBox="0 0 \d+ (\d+)"', html)]
    texts = re.findall(r"<figcaption>(.*?)</figcaption>|(<summary>)", html, flags=re.S)
    svg_px = sum(h * 888 / 800 for h in heights)
    txt_px = sum((len(re.sub('<[^>]+>', '', a or b)) // 44 + 1) * 30 for a, b in texts) + 48 * n_fig
    print(f"figures {n_fig}; size {len(html) // 1024} KB; estimated figure share {svg_px / (svg_px + txt_px):.0%}")
    print("problems", len(PROBLEMS))
    for p in PROBLEMS:
        print(" ", p)


if __name__ == "__main__":
    main()
