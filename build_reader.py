#!/usr/bin/env python3
"""
Build the full freeflow annotated reader.

Inputs (read-only):
  ../freeflow-v2/freeflow-raw_original.md   — canon transcript (NEVER edited)
  ./freeflow-annotations.json               — annotation data (source of truth)

Output:
  ./freeflow-reader.html                    — full self-contained reader

Architecture: the transcript is rendered verbatim; highlight spans are wrapped
at RUNTIME by matching each annotation's anchor_quote against the page text.
So the transcript stays canon-pure and the JSON drives every door.
"""
import json, html, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "freeflow-v2", "freeflow-raw_original.md")
ANN   = os.path.join(HERE, "freeflow-annotations.json")
OUT   = os.path.join(HERE, "freeflow-reader.html")

# ---------- load canon, strip the editor header + trailing rule ----------
raw = open(CANON, encoding="utf-8").read()
# body sits between the first '---' (after the intro blockquote) and the last '---'
parts = raw.split("\n---\n")
body = parts[1] if len(parts) >= 3 else raw
paras = [p.strip() for p in body.split("\n\n") if p.strip()]

# ---------- render one paragraph: canon text -> safe HTML ----------
def render_para(p):
    p = p.replace("\n", " ").strip()
    cls = "line"
    if re.match(r"^(I|Shortcut|You)\s*=\s", p):
        cls = "def"
    # protect markdown, escape, then restore as tags. Work on a token model.
    # 1) bold **x** -> plain x (keep text, drop weight to keep anchors clean)
    p = re.sub(r"\*\*(.+?)\*\*", r"\1", p)
    # 2) italic *(...)* or *...* -> glossary span. tokenise to escape safely.
    out = []
    i = 0
    for m in re.finditer(r"\*(.+?)\*", p):
        out.append(("t", p[i:m.start()]))
        out.append(("g", m.group(1)))
        i = m.end()
    out.append(("t", p[i:]))
    rendered = ""
    for kind, txt in out:
        esc = html.escape(txt, quote=False)
        rendered += esc if kind == "t" else f'<span class="glossary">{esc}</span>'
    return f'<p class="{cls}">{rendered}</p>', p  # also return plain text (markdown-stripped) for validation

para_html = []
plain_all = ""
for p in paras:
    h, plain = render_para(p)
    para_html.append(h)
    # plain text the BROWSER will see (asterisks/markdown removed, entities decoded)
    plain_all += re.sub(r"\*(.+?)\*", r"\1", re.sub(r"\*\*(.+?)\*\*", r"\1", p.replace("\n"," "))) + "\n"

# ---------- load annotations, validate anchors against the rendered text ----------
data = json.load(open(ANN, encoding="utf-8"))
misses = []
for a in data["annotations"]:
    if a["anchor_quote"] not in plain_all:
        misses.append((a["id"], a["anchor_quote"]))

print(f"paragraphs: {len(para_html)}")
print(f"annotations: {len(data['annotations'])}")
if misses:
    print("\n!!! ANCHOR MISSES (not found verbatim in canon text):")
    for _id, q in misses:
        print(f"  - {_id}: {q[:70]!r}")
    print("\nFix these anchors before the reader will wire them. NOT writing output.")
    sys.exit(1)
print("all anchors matched canon text ✓")

# ---------- assemble the HTML ----------
ann_json = json.dumps(data, ensure_ascii=False)
TRANSCRIPT = "\n    ".join(para_html)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Raw Talk, Open Doors — Annotated Reader</title>
<style>
  :root {
    --ink:#e8e4d8; --ink-soft:#b8b3a4; --ink-faint:#6f6b5e;
    --bg:#14130f; --bg-raised:#1c1b16; --bg-panel:#201e18; --line:#2e2c24;
    --t1:#d8a657; --t1-glow:rgba(216,166,87,0.16);
    --t2:#a8b89a; --t2-glow:rgba(168,184,154,0.12);
    --t3:#8a93a3; --t3-glow:rgba(138,147,163,0.10);
    --serif:'Iowan Old Style','Palatino Linotype','Palatino','Book Antiqua',Georgia,serif;
    --sans:'Avenir Next','Avenir','Segoe UI',system-ui,sans-serif;
  }
  * { box-sizing:border-box; }
  html { -webkit-text-size-adjust:100%; }
  body { margin:0; background:var(--bg); color:var(--ink); font-family:var(--serif);
    line-height:1.72; font-size:19px; letter-spacing:0.01em; }
  .wrap { max-width:720px; margin:0 auto; padding:64px 28px 240px; }
  header.masthead { margin-bottom:56px; padding-bottom:28px; border-bottom:1px solid var(--line); }
  .title-lockup { display:grid; grid-template-columns:78px minmax(0,1fr); gap:20px; align-items:center; margin:0 0 22px; }
  .portal-mark { width:78px; height:auto; overflow:visible; }
  .portal-frame { fill:none; stroke:var(--ink-faint); stroke-width:1.2; vector-effect:non-scaling-stroke; }
  .portal-frame.mid { opacity:0.72; }
  .portal-frame.inner { stroke:var(--t1); opacity:0.78; }
  .portal-ray { fill:none; stroke:var(--t1); stroke-width:1; opacity:0.5; vector-effect:non-scaling-stroke; }
  .portal-seed { fill:var(--t1); filter:drop-shadow(0 0 5px rgba(216,166,87,0.5)); }
  .eyebrow { font-family:var(--sans); font-size:10px; letter-spacing:0.32em; text-transform:uppercase; color:var(--ink-faint); margin:0 0 10px; }
  h1.title { font-size:43px; line-height:0.98; font-weight:500; margin:0; letter-spacing:-0.025em; }
  .title-line { display:block; }
  .title-line.open { color:var(--t1); font-style:italic; }
  .download-link { display:inline-block; margin-top:13px; font-family:var(--sans); font-size:10.5px; letter-spacing:0.08em; color:var(--ink-faint); text-decoration:none; border-bottom:1px dotted transparent; transition:color 140ms ease,border-color 140ms ease; }
  .download-link:hover,.download-link:focus-visible { color:var(--ink-soft); border-bottom-color:var(--ink-faint); }
  .standfirst { font-family:var(--sans); font-size:15px; line-height:1.6; color:var(--ink-soft); max-width:60ch; }
  .howto { font-family:var(--sans); font-size:13px; line-height:1.65; color:var(--ink-faint); margin-top:22px; padding:14px 16px; border:1px solid var(--line); border-radius:8px; background:var(--bg-raised); }
  .howto b { color:var(--ink-soft); font-weight:600; }
  .swatch { display:inline-block; width:11px; height:11px; border-radius:50%; vertical-align:middle; margin:0 3px 0 0; }
  p.line { margin:0 0 1.35em; }
  p.def { margin:0 0 0.7em; color:var(--ink-soft); font-style:italic; }
  .glossary { color:var(--ink-soft); font-style:italic; }

  .mark { cursor:pointer; position:relative; transition:background 160ms ease, box-shadow 160ms ease, color 160ms ease; border-radius:2px; }
  .mark:focus-visible { outline:2px solid var(--t1); outline-offset:2px; }
  .mark.t3 { border-bottom:1px dotted var(--t3); color:var(--ink); }
  .mark.t3:hover { background:var(--t3-glow); }
  .mark.t2 { border-bottom:1.5px solid var(--t2); background:linear-gradient(var(--t2-glow),var(--t2-glow)); }
  .mark.t2:hover { background:var(--t2-glow); border-bottom-color:#c4d2b6; }
  .mark.t1 { background:var(--t1-glow); border-bottom:2px solid var(--t1); padding:1px 2px; box-shadow:0 0 0 0 var(--t1-glow); }
  .mark.t1:hover { box-shadow:0 2px 18px -4px var(--t1-glow); background:rgba(216,166,87,0.22); }
  .mark.active { background:rgba(216,166,87,0.26) !important; box-shadow:0 2px 22px -6px var(--t1-glow); }

  .peek { position:fixed; z-index:40; max-width:320px; font-family:var(--sans); font-size:12.5px; line-height:1.5; color:var(--ink-soft); background:rgba(8,8,6,0.96); border:1px solid var(--line); border-radius:7px; padding:9px 12px; pointer-events:none; opacity:0; transform:translateY(4px); transition:opacity 120ms ease, transform 120ms ease; box-shadow:0 8px 30px -10px rgba(0,0,0,0.7); }
  .peek.show { opacity:1; transform:translateY(0); }
  .peek .peek-label { display:block; font-size:10px; letter-spacing:0.18em; text-transform:uppercase; color:var(--ink-faint); margin-bottom:4px; }

  .panel { position:fixed; z-index:60; width:min(440px,calc(100vw - 32px)); max-height:min(70vh,620px); overflow-y:auto; background:var(--bg-panel); border:1px solid var(--line); border-radius:12px; box-shadow:0 24px 60px -18px rgba(0,0,0,0.8),0 0 0 1px rgba(216,166,87,0.06); opacity:0; transform:translateY(8px) scale(0.99); transition:opacity 150ms ease, transform 150ms ease; pointer-events:none; }
  .panel.show { opacity:1; transform:translateY(0) scale(1); pointer-events:auto; }
  .panel-accent { height:3px; width:100%; border-radius:12px 12px 0 0; }
  .panel.tier1 .panel-accent { background:var(--t1); }
  .panel.tier2 .panel-accent { background:var(--t2); }
  .panel.tier3 .panel-accent { background:var(--t3); }
  .panel-inner { padding:20px 22px 22px; }
  .panel-quote { font-family:var(--serif); font-style:italic; font-size:15px; line-height:1.5; color:var(--ink-soft); margin:0 0 14px; padding-left:13px; border-left:2px solid var(--line); }
  .panel-body { font-family:var(--sans); font-size:14.5px; line-height:1.66; color:var(--ink); margin:0; }
  .panel-body em { color:var(--t1); font-style:italic; }
  .panel-body strong { color:var(--ink); font-weight:600; }
  .panel-foot { margin-top:18px; padding-top:14px; border-top:1px solid var(--line); display:flex; align-items:center; justify-content:space-between; gap:12px; }
  .deep-link { font-family:var(--sans); font-size:12.5px; letter-spacing:0.02em; color:var(--t1); text-decoration:none; border:1px solid rgba(216,166,87,0.32); border-radius:6px; padding:7px 12px; transition:background 140ms ease, border-color 140ms ease; white-space:nowrap; }
  .deep-link:hover { background:rgba(216,166,87,0.12); border-color:var(--t1); }
  .deep-link.none { visibility:hidden; }
  .panel-close { font-family:var(--sans); font-size:12px; letter-spacing:0.06em; color:var(--ink-faint); background:none; border:none; cursor:pointer; padding:6px 4px; transition:color 140ms ease; }
  .panel-close:hover { color:var(--ink); }
  .panel-close kbd { font-family:var(--sans); font-size:10px; border:1px solid var(--line); border-radius:4px; padding:1px 5px; margin-left:5px; color:var(--ink-faint); }
  .scrim { position:fixed; inset:0; z-index:50; background:transparent; opacity:0; pointer-events:none; transition:opacity 150ms ease; }
  .scrim.show { opacity:1; pointer-events:auto; }
  .progress { position:fixed; top:0; left:0; height:3px; width:0; background:var(--t1); opacity:0.55; z-index:70; transition:width 120ms ease; }
  footer.endnote { margin-top:80px; padding-top:24px; border-top:1px solid var(--line); font-family:var(--sans); font-size:12.5px; color:var(--ink-faint); line-height:1.6; }
  @media (max-width:600px) {
    body { font-size:18px; }
    .wrap { padding:40px 20px 220px; }
    .title-lockup { grid-template-columns:58px minmax(0,1fr); gap:15px; }
    .portal-mark { width:58px; }
    h1.title { font-size:34px; }
    .panel { left:16px !important; right:16px !important; bottom:16px !important; top:auto !important; width:auto; max-height:64vh; }
    .peek { display:none; }
  }
  @media (prefers-reduced-motion:reduce) { * { transition:none !important; } }
</style>
</head>
<body>
<div class="progress" id="progress"></div>
<div class="wrap">
  <header class="masthead">
    <div class="title-lockup">
      <svg class="portal-mark" viewBox="0 0 90 112" role="img" aria-labelledby="portal-title portal-desc">
        <title id="portal-title">Nested open doorways</title>
        <desc id="portal-desc">Three thresholds open around a single point of light.</desc>
        <path class="portal-frame" d="M9 100V42C9 21 25 7 45 7s36 14 36 35v58"/>
        <path class="portal-frame mid" d="M20 100V45c0-16 11-27 25-27s25 11 25 27v55"/>
        <path class="portal-frame inner" d="M31 100V49c0-10 6-18 14-18s14 8 14 18v51"/>
        <path class="portal-ray" d="M45 55v45M45 100 8 108M45 100l37 8"/>
        <circle class="portal-seed" cx="45" cy="53" r="2.8"/>
      </svg>
      <div>
        <p class="eyebrow">Annotated transcript · a reading in depth</p>
        <h1 class="title"><span class="title-line">Raw talk.</span><span class="title-line open">Open doors.</span></h1>
        <a class="download-link" href="https://github.com/laredjeach/freeflow-annotated-reader/archive/refs/heads/main.zip">download complete reader (.zip) ↓</a>
      </div>
    </div>
    <p class="standfirst">The transcript stands exactly as spoken — nothing changed, nothing trimmed. The marked passages open onto what sits beneath them: where a line goes deeper than it looks, what it has a name for in older traditions, why it lands.</p>
    <div class="howto">
      Tap or click any <b>marked passage</b> to open its reading. One opens at a time; the last closes itself. Dismiss with the ×, a click outside, or <b>Esc</b> — then read on.
      <br><br>
      <span class="swatch" style="background:var(--t1)"></span> a major passage &nbsp;·&nbsp;
      <span class="swatch" style="background:var(--t2)"></span> a strong moment &nbsp;·&nbsp;
      <span class="swatch" style="background:var(--t3)"></span> a quick touch
    </div>
  </header>

  <main id="text">
    __TRANSCRIPT__
  </main>

  <footer class="endnote" id="endnote"></footer>
</div>

<div class="scrim" id="scrim"></div>
<div class="peek" id="peek"><span class="peek-label">reading</span><span id="peek-text"></span></div>
<div class="panel" id="panel" role="dialog" aria-modal="false" aria-label="Passage reading">
  <div class="panel-accent"></div>
  <div class="panel-inner">
    <p class="panel-quote" id="panel-quote"></p>
    <p class="panel-body" id="panel-body"></p>
    <div class="panel-foot">
      <a class="deep-link" id="panel-deep" href="#" target="_blank" rel="noopener">Read full analysis →</a>
      <button class="panel-close" id="panel-close">Close<kbd>Esc</kbd></button>
    </div>
  </div>
</div>

<script type="application/json" id="ann-data">__ANN_JSON__</script>
<script>
const DATA = JSON.parse(document.getElementById('ann-data').textContent);
const DEEP_DIVE_URL = DATA.meta.deep_dive_file || "freeflow-deepdive.html";
const ANN = {};
DATA.annotations.forEach(a => { ANN[a.id] = {tier:a.tier, type:a.type, quote:a.quote_display, body:a.body_html, deep:a.deep}; });

/* ── wrap each anchor_quote in a .mark span, at runtime, over the canon text ── */
const textRoot = document.getElementById('text');
function wrapAnchor(quote, a){
  const walker = document.createTreeWalker(textRoot, NodeFilter.SHOW_TEXT, null);
  let node;
  while((node = walker.nextNode())){
    if(node.parentElement && node.parentElement.closest('.mark')) continue;
    const idx = node.nodeValue.indexOf(quote);
    if(idx !== -1){
      const range = document.createRange();
      range.setStart(node, idx);
      range.setEnd(node, idx + quote.length);
      const span = document.createElement('span');
      span.className = 'mark t' + a.tier;
      span.dataset.ann = a.id;
      span.tabIndex = 0;
      try { range.surroundContents(span); return true; }
      catch(e){ /* range crossed a tag boundary; skip */ }
    }
  }
  console.warn('anchor not wrapped:', a.id, JSON.stringify(quote).slice(0,60));
  return false;
}
let wrapped = 0;
DATA.annotations.forEach(a => { if(wrapAnchor(a.anchor_quote, a)) wrapped++; });

/* ── panel / peek machinery ── */
const panel=document.getElementById('panel'), scrim=document.getElementById('scrim');
const peek=document.getElementById('peek'), peekTxt=document.getElementById('peek-text');
const qEl=document.getElementById('panel-quote'), bEl=document.getElementById('panel-body');
const deepEl=document.getElementById('panel-deep'), closeBtn=document.getElementById('panel-close');
let activeMark=null;

function plainFirstSentence(h){ const t=document.createElement('div'); t.innerHTML=h; const x=t.textContent||''; const m=x.match(/^.*?[.;:](\s|$)/); return (m?m[0]:x).trim(); }
function openPanel(markEl){
  const a=ANN[markEl.dataset.ann]; if(!a) return;
  if(activeMark && activeMark!==markEl) activeMark.classList.remove('active');
  activeMark=markEl; markEl.classList.add('active');
  qEl.textContent=a.quote; bEl.innerHTML=a.body; panel.className='panel tier'+a.tier;
  if(a.deep){ deepEl.href=DEEP_DIVE_URL+'#'+a.deep; deepEl.classList.remove('none'); }
  else { deepEl.classList.add('none'); }
  panel.classList.add('show'); scrim.classList.add('show');
  requestAnimationFrame(()=>positionPanel(markEl)); hidePeek();
}
function positionPanel(markEl){
  if(window.matchMedia('(max-width:600px)').matches) return;
  const r=markEl.getBoundingClientRect(), pw=panel.offsetWidth, ph=panel.offsetHeight, gap=16, pad=16;
  let left=r.right+gap; if(left+pw>window.innerWidth-pad) left=r.left-pw-gap; if(left<pad) left=pad;
  let top=r.top; if(top+ph>window.innerHeight-pad) top=window.innerHeight-ph-pad; if(top<pad) top=pad;
  panel.style.left=left+'px'; panel.style.top=top+'px';
}
function closePanel(){ panel.classList.remove('show'); scrim.classList.remove('show'); if(activeMark){ activeMark.classList.remove('active'); activeMark=null; } }

document.querySelectorAll('.mark').forEach(m=>{
  m.addEventListener('click', e=>{ e.stopPropagation(); openPanel(m); });
  m.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); openPanel(m); } });
  m.addEventListener('mouseenter', e=>{
    if(window.matchMedia('(max-width:600px)').matches) return;
    if(panel.classList.contains('show')) return;
    const a=ANN[m.dataset.ann]; if(!a) return;
    peekTxt.textContent=plainFirstSentence(a.body); peek.classList.add('show'); movePeek(e);
  });
  m.addEventListener('mousemove', movePeek);
  m.addEventListener('mouseleave', hidePeek);
});
function movePeek(e){ const px=e.clientX+16, py=e.clientY+18, pw=peek.offsetWidth, ph=peek.offsetHeight, pad=12;
  peek.style.left=Math.min(px,window.innerWidth-pw-pad)+'px'; peek.style.top=Math.min(py,window.innerHeight-ph-pad)+'px'; }
function hidePeek(){ peek.classList.remove('show'); }
closeBtn.addEventListener('click', closePanel);
scrim.addEventListener('click', closePanel);
document.addEventListener('keydown', e=>{ if(e.key==='Escape') closePanel(); });
window.addEventListener('resize', ()=>{ if(activeMark) positionPanel(activeMark); });

/* reading-progress bar + endnote count */
const prog=document.getElementById('progress');
window.addEventListener('scroll', ()=>{ const h=document.documentElement; const p=h.scrollTop/(h.scrollHeight-h.clientHeight); prog.style.width=(p*100)+'%'; }, {passive:true});
document.getElementById('endnote').textContent =
  `The full talk — ${DATA.annotations.length} passages marked across three weights, each a door into the reading. The raw transcript is preserved separately as canon; this reader never edits it.`;
</script>
</body>
</html>
"""

HTML = HTML.replace("__TRANSCRIPT__", TRANSCRIPT).replace("__ANN_JSON__", ann_json)
open(OUT, "w", encoding="utf-8").write(HTML)
print(f"wrote {OUT} ({len(HTML)//1024} KB)")
