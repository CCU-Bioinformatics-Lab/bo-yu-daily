#!/usr/bin/env python3
"""Regenerate the visual module walkthrough from module_format.md.

The Markdown is the narrative source.  This generator deliberately embeds the
actual repository SVGs: components carry the structural explanation while the
corresponding svg_version artwork preserves the supplied visual reference.
"""
from __future__ import annotations

import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "module_format.html"
MD = ROOT / "module_format.md"


def text_to_foreign_object(match: re.Match[str]) -> str:
    """Keep source-backed SVG labels visible without fragile SVG text nodes."""
    attrs = match.group(1)
    content = match.group(2).strip()
    values = dict(re.findall(r'([\w:-]+)="([^"]*)"', attrs))
    x = float(values.get("x", "0"))
    y = float(values.get("y", "0"))
    size = float(values.get("font-size", "16"))
    anchor = values.get("text-anchor", "start")
    width = 420.0
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    justify = {"start": "flex-start", "middle": "center", "end": "flex-end"}.get(anchor, "flex-start")
    passthrough = " ".join(
        f'{name}="{escape(value, quote=True)}"'
        for name, value in values.items()
        if name in {"id", "data-meaning"}
    )
    weight = values.get("font-weight", "400")
    color = values.get("fill", "#17233a")
    top = y - size * 1.15
    height = size * 1.6
    return (
        f'<foreignObject x="{x:g}" y="{top:g}" width="{width:g}" height="{height:g}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" {passthrough} '
        f'style="display:flex;align-items:center;justify-content:{justify};width:100%;height:100%;'
        f'color:{color};font:normal {weight} {size:g}px system-ui,sans-serif;white-space:nowrap">'
        f'{escape(content)}</div></foreignObject>'
    )


def inline(
    path: str,
    visual_id: str,
    component_ids: str = "",
    *,
    description: str = "Repository SVG asset embedded for this module explanation.",
) -> str:
    """Return a repository SVG as an inline, traceable visual asset."""
    raw = (ROOT / path).read_text(encoding="utf-8")
    raw = re.sub(r"<\?xml[^>]*>\s*", "", raw)
    raw = re.sub(r"<script\b[^>]*>.*?</script>\s*", "", raw, flags=re.S | re.I)
    # Component titles can also contain example-only terminology.  The slide
    # label is drawn from the Markdown claim ledger, so it is the safe title.
    raw = re.sub(r"<title\b[^>]*>.*?</title>", f"<title>{description}</title>", raw, count=1, flags=re.S | re.I)
    # Keep labels that the current Markdown supports.  Slide 3's CN values
    # are explicitly approved illustrative counts, not inferred source facts.
    text_edits = {
        "slide-3-canonical-fields": {
            "counts": None,
            "cn-label": None,
            "tumor-name": None,
            "normal-name": None,
        },
        "slide-4-candidate-tree": {
            "c1-label": "Root",
            "c2-label": "Clone A",
            "c3-label": "Clone C",
            "c4-label": "Clone B",
            "k-label": None,
            "counts": None,
        },
        "slide-6-topology": {
            "c1-label": "parent clone",
            "c2-label": "descendant",
            "c3-label": "descendant",
            "c4-label": "descendant",
            "k-label": None,
        },
        "slide-6-local-eta": {
            "c1-id": "clone",
            "c2-id": "clone",
            "c3-id": "clone",
            "eta-c1-label": "local ηᵥ",
            "eta-c2-label": "local ηᵥ",
            "eta-c3-label": "local ηᵥ",
            "phi-c1-label": None,
            "phi-c2-label": None,
            "phi-c3-label": None,
            "formula": None,
            "eta-total": None,
        },
        "slide-6-cumulative-phi": {
            "c1-id": "clone",
            "c2-id": "clone",
            "c3-id": "clone",
            "eta-c1-label": None,
            "eta-c2-label": None,
            "eta-c3-label": None,
            "phi-c1-label": "cumulative φ",
            "phi-c2-label": "cumulative φ",
            "phi-c3-label": "cumulative φ",
            "eta-total": None,
        },
        "slide-6-clone-assignment": {
            "snv-id": "一顆 SNV",
            "map-label": "比較支持",
            "clone-id": "一個 clone",
        },
    }.get(visual_id, {})
    for text_id, replacement in text_edits.items():
        pattern = rf'<text\b([^>]*\bid="{re.escape(text_id)}"[^>]*)>.*?</text>\s*'
        if replacement is None:
            raw = re.sub(pattern, "", raw, flags=re.S | re.I)
        else:
            raw = re.sub(
                pattern,
                lambda match, value=replacement: f"<text{match.group(1)}>{value}</text>",
                raw,
                flags=re.S | re.I,
            )
    raw = re.sub(r"<text\b([^>]*)>(.*?)</text>\s*", text_to_foreign_object, raw, flags=re.S | re.I)
    prefix = re.sub(r"[^a-zA-Z0-9_-]", "-", f"{visual_id}-{Path(path).stem}")
    raw = re.sub(r'\bid="([^"]+)"', lambda match: f'id="{prefix}-{match.group(1)}"', raw)
    raw = re.sub(r'url\(#([^)]*)\)', lambda match: f'url(#{prefix}-{match.group(1)})', raw)
    raw = re.sub(r'((?:href|xlink:href)=[\"\'])#([^\"\']+)([\"\'])', lambda match: f'{match.group(1)}#{prefix}-{match.group(2)}{match.group(3)}', raw)
    raw = raw.replace("<svg ", f'<svg data-source="{path}" data-visual-id="{visual_id}" ' , 1)
    if component_ids:
        raw = raw.replace("<svg ", f'<svg data-component-id="{component_ids}" ', 1)
    return raw.replace("</title>", f"</title><desc>{description}</desc>", 1)


def visual(visual_id: str, components: list[str], references: list[str], label: str) -> str:
    component_ids = " ".join(Path(item).stem.replace("_", "-") for item in components)
    pieces = [
        inline(item, visual_id, component_ids, description=label)
        for item in components
    ]
    pieces += [inline(item, visual_id) for item in references]
    if not pieces:
        return ""
    panel_labels = {
        "slide-3-canonical-fields": ["Identity", "Read counts", "Copy number", "Fixed sample purity"],
        "slide-4-candidate-tree": ["候選 tree 的 parent／descendant", "sequencing data 中的 REF／ALT reads"],
        "slide-6-output-parameters": ["local ηᵥ 與 cumulative φ", "一顆 SNV 比較支持哪個 clone"],
    }.get(visual_id, [])
    panels = []
    for index, piece in enumerate(pieces):
        panel_label = f'<p class="panel-label">{panel_labels[index]}</p>' if index < len(panel_labels) else ""
        panels.append(f'<div class="asset">{panel_label}{piece}</div>')
    relation = ""
    if visual_id == "slide-4-candidate-tree":
        relation = '<p class="relation-label">不同 clone fraction 會影響觀察到的 ALT reads</p>'
    return f'''<figure class="visual" data-visual-id="{visual_id}" data-source="{' '.join(components + references)}" data-component-id="{component_ids}">
  <div class="art" aria-label="{label}">{''.join(panels)}</div>{relation}
</figure>'''


def output_parameter_slots() -> str:
    """Render the four user-authorized parameter slots without merging them."""
    slots = [
        (
            "slide-6-topology",
            "Tree topology T",
            "assets/components/clone_tree.svg",
            "parent／descendant 的 clone topology。",
        ),
        (
            "slide-6-local-eta",
            "local fraction ηᵥ",
            "assets/components/eta_phi_tree.svg",
            "每個 clone 自己獨有且不包含 descendants 的 local fraction。",
        ),
        (
            "slide-6-cumulative-phi",
            "CCF／φ",
            "assets/components/eta_phi_tree.svg",
            "某 clone 加上 descendants 的 cumulative fraction。",
        ),
        (
            "slide-6-clone-assignment",
            "Clone assignment z",
            "assets/components/snv_assignment.svg",
            "一顆 SNV 比較支持哪個 clone。",
        ),
    ]
    cards = []
    for visual_id, title, path, description in slots:
        component_id = Path(path).stem.replace("_", "-")
        svg = inline(path, visual_id, component_id, description=description)
        cards.append(
            f'''<figure class="visual slot-card" data-visual-id="{visual_id}" data-source="{path}" data-component-id="{component_id}">
  <figcaption class="panel-label">{title}</figcaption><div class="asset">{svg}</div>
</figure>'''
        )
    return f'<div class="slot-grid" aria-label="四個 model output parameter 視覺槽位">{"".join(cards)}</div>'



slides = [
    ("研究模組主線", "研究模組主線由既有架構圖呈現",
     "此頁保留來源段落中已有的 HCC1395 tumor evolution tree module 架構圖。",
     "slide-1-module-flow", [], ["assets/png_to_svg/full_arch.svg"],
     "由 raw data、data input、model、inference、output 組成的研究模組主線。",
     "<p class=\"note\">本頁只呈現「研究模組主線架構」直接描述的順序與目的；data input 與 model 的細節從下一頁開始。</p>"),
    ("Data input", "一顆 SNV 對應一列可供 model 讀取的基本資料",
     "data input 將 BAM、VCF、ASCAT 的資訊整理為 canonical SNV row，而非讓 model 直接讀取原始來源。",
     "slide-2-source-to-row", ["assets/components/source_to_input.svg"], [],
     "BAM、VCF、ASCAT 匯集欄位為一列 canonical SNV data 的實際元件與來源圖。",
     "<div class=\"callout\"><b>一句話功能</b>：把 BAM、VCF、ASCAT 的資訊整理成一列一個 SNV 的基本資料，供 model 讀取。</div>"),
    ("Canonical SNV row", "同一列同時保留 identity、reads、purity 與 copy number",
     "欄位把哪一顆 SNV 與它的觀察 read counts、固定 sample-level purity、site-level CN context 放在同一個可讀取單位。",
     "slide-3-canonical-fields", ["assets/components/snv_identity_igv_reads.svg", "assets/components/read_pileup.svg", "assets/components/cn_segment_context.svg", "assets/components/purity_mixture.svg"], [],
     "canonical SNV identity、read pileup、SNV 對齊的 ASCAT copy-number segment 與 purity mixture 元件。identity 與 CN 值皆為已核准的示例呈現。",
     "<div class=\"field-grid\"><p><b>Identity</b><code>mutation_id, chrom, pos, ref, alt</code></p><p><b>Read counts</b><code>ref_reads, alt_reads, total_reads</code></p><p><b>Purity</b><code>rho_ASCAT</code>；主分析為 0.99</p><p><b>Copy number</b><code>major_cn, minor_cn, total_cn</code></p></div><p class=\"note\">G/A 僅為 pileup 示例。total_reads = ref_reads + alt_reads；total_cn = major_cn + minor_cn。</p>"),
    ("Model", "model 為候選演化樹與資料的吻合程度評分",
     "model 讀取 canonical SNV table，連同候選 tree 的 clone fraction 與模型內部建立的 multiplicity，計算候選 tree 的分數；inference 負責探索不同候選樹並更新參數。",
     "slide-4-candidate-tree", ["assets/components/clone_tree.svg", "assets/components/read_pileup.svg"], [],
     "候選 tree 的 parent-descendant 結構與 read pileup 中的 REF／ALT evidence。",
     "<div class=\"callout\"><b>候選樹的兩個假設</b><br>祖先 clone 原則上會被後代 clone 繼承。不同 clone 有不同腫瘤細胞比例，會影響 sequencing data 中看到的 ALT reads。</div>"),
    ("Model language", "候選樹的可信度由 prior 與 likelihood 組成 posterior",
     "把腫瘤演化樹故事寫成數學模型後，候選樹的可信度可表為原本假設的合理性與它和真實資料的吻合程度。",
     "", [], [],
     "posterior、prior 與 likelihood 關係。",
     "<figure class=\"equation-visual\" aria-label=\"posterior、prior 與 likelihood 的文字公式\"><div class=\"formula\">posterior ∝ prior × likelihood</div><figcaption>候選腫瘤樹最後有多可信 = 原本的假設有多合理 × 它和真實資料有多吻合。</figcaption></figure><div class=\"field-grid three\"><p><b>Prior</b>還沒看 sequencing data 前哪些演化狀態合理。</p><p><b>Likelihood</b>假設這棵樹是真的，觀察資料的機率有多高？</p><p><b>Posterior</b>看到真實資料後，猜測出來的候選樹可信度。</p></div>"),
    ("Model output parameters", "以 topology、fraction、CCF 與 assignment 描述候選狀態",
     "這些參數連結候選 tree 的 parent／descendant 關係、各 clone 的腫瘤細胞比例，以及一顆 SNV 比較支持哪個 clone。",
     "slide-6-parameter-slots", [], [],
     "四個獨立 model output parameter 視覺槽位。",
     "<dl><dt>Tree topology <code>T</code></dt><dd>哪些 clone 是 parent／descendant？</dd><dt>local fraction <code>η_v</code></dt><dd>每個 clone 自己獨有、且不包含 descendants 的 tumor-cell fraction。</dd><dt>CCF／<code>phi</code></dt><dd>某 clone 加上 descendants 的累積比例。</dd><dt>Clone assignment <code>z</code></dt><dd>一顆 SNV 比較支持哪個 clone。</dd></dl>"),
    ("Inference", "inference 探索、評估與保留候選腫瘤演化狀態",
     "",
     "slide-7-inference-module", [], ["assets/png_to_svg/inference_module.svg"],
     "inference 探索、評估與保留候選腫瘤演化狀態的示意圖。", ""),
]


section_sources = [
    "## 研究模組主線架構",
    "## 1. Data input",
    "## 1. Data input",
    "## 2. Model",
    "## 2. Model",
    "## 2. Model",
    "## 3. inference",
]

sections = []
for index, (eyebrow, title, lead, visual_id, components, refs, label, detail) in enumerate(slides, 1):
    visual_markup = output_parameter_slots() if visual_id == "slide-6-parameter-slots" else visual(visual_id, components, refs, label)
    visual_line = f"  {visual_markup}\n" if visual_markup else ""
    sections.append(f'''<section class="slide{' active' if index == 1 else ''}" id="slide-{index}" aria-labelledby="slide-{index}-title">
  <p class="eyebrow">{eyebrow}</p><p class="source-scope">來源區段：{section_sources[index - 1]}</p><h2 id="slide-{index}-title">{title}</h2><p class="lead">{lead}</p>
{visual_line}
  <div class="detail">{detail}</div>
</section>''')

html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>HCC1395 腫瘤演化樹 module</title>
<style>
:root{{--ink:#17233a;--muted:#526277;--line:#d8e1ec;--paper:#f4f7fb;--accent:#315fd4;--soft:#edf3ff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Noto Sans TC",sans-serif}}.shell{{width:min(1280px,calc(100% - 28px));margin:auto;padding:28px 0 36px}}header{{display:flex;justify-content:space-between;gap:16px;align-items:start}}h1{{margin:0;font-size:clamp(28px,4vw,42px);line-height:1.15}}h2{{margin:4px 0 8px;font-size:clamp(25px,3.2vw,36px);line-height:1.2}}.eyebrow{{margin:0;color:var(--accent);font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}.source-scope{{display:inline-block;margin:7px 0 2px;padding:2px 8px;border-radius:999px;background:var(--soft);color:#24499f;font-size:12px;font-weight:700}}.meta,.lead,.note{{color:var(--muted)}}.lead{{font-size:18px;margin:0 0 20px}}.chip{{border:1px solid #bbcbef;border-radius:999px;padding:5px 11px;color:#24499f;background:#fff;font-size:13px;font-weight:750}}.sources{{margin:18px 0;padding:14px 17px;background:#fff;border:1px solid var(--line);border-radius:12px}}.sources a{{color:#174ea6}}.viewport{{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 12px 30px #24375712}}.slide{{display:none;padding:clamp(22px,4vw,46px);min-height:620px}}.slide.active{{display:block}}.visual,.equation-visual{{margin:18px 0 16px;padding:14px;border:1px solid #cbd8e9;border-radius:16px;background:linear-gradient(145deg,#fff,#f5f8ff)}}.art{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:center}}.asset{{min-width:0;border-radius:10px;overflow:hidden;background:white;border:1px solid #e1e8f1}}.asset:only-child{{grid-column:1 / -1}}.asset svg{{display:block;width:100%;height:auto;max-height:310px}}.panel-label{{margin:0;padding:8px 12px;background:#edf3ff;color:#24499f;font-weight:800}}.relation-label{{margin:12px 0 0;text-align:center;color:#24499f;font-weight:800}}.slot-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:18px 0 16px}}.slot-card{{margin:0;padding:0;overflow:hidden}}.slot-card .asset{{border:0;border-radius:0}}.slot-card .asset svg{{max-height:205px}}.equation-visual figcaption{{color:var(--muted);text-align:center}}.detail{{max-width:1050px}}.callout{{padding:14px 17px;border-left:4px solid var(--accent);background:var(--soft);border-radius:0 10px 10px 0}}.field-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.field-grid.three{{grid-template-columns:repeat(3,minmax(0,1fr))}}.field-grid p{{margin:0;padding:12px;border:1px solid var(--line);border-radius:10px;background:#fff}}.field-grid b{{display:block}}code{{color:#5b2bbd;font-weight:700;overflow-wrap:anywhere}}.formula{{padding:16px;text-align:center;border-radius:10px;background:#17233a;color:white;font:700 clamp(22px,3vw,35px)/1.3 ui-monospace,monospace;margin-bottom:12px}}dl{{display:grid;grid-template-columns:200px 1fr;gap:8px 16px;margin:0}}dt{{font-weight:800}}dd{{margin:0;color:var(--muted)}}.nav{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:17px}}button{{border:1px solid #9eb8e8;border-radius:9px;background:#fff;color:#174ea6;padding:9px 14px;font:inherit;font-weight:750;cursor:pointer}}button:disabled{{opacity:.45;cursor:not-allowed}}button:focus-visible,a:focus-visible{{outline:3px solid #f6b51d;outline-offset:3px}}.dots{{display:flex;gap:7px}}.dot{{width:9px;height:9px;border-radius:50%;background:#c7d2e1}}.dot.active{{background:var(--accent);transform:scale(1.3)}}#page{{color:var(--muted)}}@media(max-width:760px){{.shell{{width:min(100% - 18px,680px);padding-top:18px}}header{{display:block}}.chip{{display:inline-block;margin-top:10px}}.slide{{min-height:0;padding:24px 18px}}.art,.slot-grid,.field-grid,.field-grid.three{{grid-template-columns:1fr}}.slot-card .asset svg{{max-height:230px}}dl{{grid-template-columns:1fr;gap:2px}}dd{{margin-bottom:10px}}}}@media(prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style></head><body><div class="shell"><header><div><p class="eyebrow">Module map</p><h1>HCC1395 腫瘤演化樹</h1><p class="meta">模組邊界與資料流</p></div><span class="chip">範圍：data input 與 model</span></header>
<aside class="sources" aria-label="來源 Markdown"><b>來源 Markdown</b><ul><li><a href="module_format.md">MOD-01 · module_format.md</a></li></ul><p class="note">本 HTML 的敘事只由 module_format.md 支持；SVG 是該敘事的可追溯視覺素材。</p></aside>
<main class="viewport">{''.join(sections)}</main><nav class="nav" aria-label="投影片導覽"><button id="prev" type="button">← Previous</button><div class="dots" aria-hidden="true">{''.join('<span class="dot' + (' active' if i == 0 else '') + '"></span>' for i in range(len(slides)))}</div><span id="page" aria-live="polite">1 / {len(slides)}</span><button id="next" type="button">Next →</button></nav></div>
<script>(()=>{{const s=[...document.querySelectorAll('.slide')],d=[...document.querySelectorAll('.dot')],p=document.querySelector('#prev'),n=document.querySelector('#next'),c=document.querySelector('#page');let i=0;function show(x){{i=Math.max(0,Math.min(s.length-1,x));s.forEach((e,j)=>e.classList.toggle('active',i===j));d.forEach((e,j)=>e.classList.toggle('active',i===j));p.disabled=i===0;n.disabled=i===s.length-1;c.textContent=`${{i+1}} / ${{s.length}}`;history.replaceState(null,'',`#${{s[i].id}}`)}}function hash(){{const x=s.findIndex(e=>`#${{e.id}}`===location.hash);show(x<0?0:x)}}p.onclick=()=>show(i-1);n.onclick=()=>show(i+1);addEventListener('keydown',e=>{{if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1);if(e.key==='Home')show(0);if(e.key==='End')show(s.length-1)}});addEventListener('hashchange',hash);hash()}})();</script></body></html>'''

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} with {len(slides)} slides")
