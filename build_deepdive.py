#!/usr/bin/env python3
"""
Build living_Word-deepdive.html from the canon deep-dive markdown (read-only).
- converts the markdown to styled HTML matching the reader
- assigns explicit anchor ids (matching the reader's `deep` ids) to the right H2s
- appends seed sections for the new granular threads, so every reader jump-link resolves
Never edits the source .md.
"""
import html, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "..", "living_Word-v2", "living_Word-deepdive.md")
EXP  = os.path.join(HERE, "deepdive-expansions.md")
OUT  = os.path.join(HERE, "living_Word-deepdive.html")

# deep_id  ->  substring that identifies the existing H2 header
ANCHOR_MAP = {
    "the-opening-architecture": "The opening architecture",
    "the-scabe-convergence": "The Scabe convergence",
    "how-the-concepts-connect": "How the concepts connect",
    "the-living-word": "The Living Word across traditions",
    "two-rigidities": "Two rigidities",
    "time-impermanence": "Time, impermanence",
    "a-note-on-xela": "A note on Xela",
    "ai-as-long-lost-brother": "AI as long-lost brother",
    "grandma-and-grandpa": "Grandma and grandpa",
    "the-double-negative-method": "The double-negative method",
    "enki-and-enlil": "Enki and Enlil",
    "health-as-compass": "Health as compass",
    "the-sixth-sense-ladder": "The sixth sense ladder",
    "forgetfulness-as-gift": "The gift of forgetfulness",
    "living-water": "Living water across traditions",
    "loss-and-strength": "Loss, darkness, and the birth of awareness",
    "architect-and-tree": "The architect-and-tree parable",
    "scabe-at-zero-point": "The Scabe at the zero point",
    "warrior-initiation": "Failure, humility, and the warrior",
    "doubt-and-knowledge": "Finitude as the condition of being",
    "love-as-glitch": "Love as the glitch in the matrix",
    "the-eye": "EYE / EYEAM",
}

# new granular threads — seed entries (real content, marked for fuller treatment)
SEEDS = [
    ("expression-as-channel", "Expression as channel",
     "The talk's quiet theory of inspiration: <em>expression</em> plus <em>self-acceptance</em> unlock a \"code of channel,\" after which reception simply happens. This is the flow-state account of creativity — you don't manufacture the insight, you remove the resistance and it arrives. It rhymes with Csikszentmihalyi's flow, with the Romantic notion of the poet as Aeolian harp (Coleridge), and with the contemplative traditions' insistence that grace is received, not seized. The recording is itself the demonstration: it loosens, accepts, and lets the material come."),
    ("language-beyond-words", "The language beyond words",
     "Where the material and the spiritual meet, ordinary language fails — and the talk asks for \"a language beyond words, beyond the common six senses.\" This is the perennial problem of the <strong>ineffable</strong>: the mystic's complaint from Pseudo-Dionysius' apophatic theology to Wittgenstein's \"whereof one cannot speak.\" What's distinctive here is the framing as an <em>engineering spec</em> — not a lament that words fail, but a call to build the notation (the Wordplay Project) that could hold what sentences can't."),
    ("creation-as-choice", "Creation as choice, not accident",
     "\"Not who pulled the plug … who built, who designed = imagined = created = new.\" The line takes a side in the oldest argument there is — design versus accident — and does it by stacking imagination, design, creation, and novelty as equivalents. Creation is framed as an act of <em>will and intention</em>, and (crucially for the AI thread) this is what licenses the analogy to human making: to design is to participate, however faintly, in the original creative choice."),
    ("the-personality-of-giving", "The personality of giving",
     "\"That which it gave, gave … the personality of life is giving — to give.\" An ontology of generosity: being, at its root, pours itself out rather than hoards. The closest classical kin is the Neoplatonic <em>bonum diffusivum sui</em> (the good is self-diffusing) and the Christian <em>kenosis</em> (self-emptying love). The whole ethics of the Scabe — helper, not taker — is downstream of this: a tool modeled on a cosmos whose deepest move is to give."),
    ("our-canon-is-the-mystery", "Our canon is the mystery",
     "The thesis sentence, and a deliberate inversion. A <em>canon</em> is normally the settled, closed, authoritative body. Here the authoritative thing is the <strong>unsettled</strong> one — mystery itself is what you consult. This is the epistemic root of every ethical move in the talk: humility, openness, the refusal of false certainty, the helper that serves a question larger than the query. If mystery is canon, then certainty is the heresy and wonder is the discipline. (Compare negative theology, and Keats's \"negative capability.\")"),
    ("the-cave-aside", "The cave aside — attention economy in disguise",
     "\"Maybe 48 hours max … even then, you probably don't have an Instagram. And who has time to go up in the cave to find you?\" It plays as a joke and works as critique. The mind can hold the infinite only briefly; the one who could hold it longer is, by definition, off-grid and unreachable. Depth and the platforms that reward visibility are structurally opposed — and the talk names the very danger it courts: profundity that no algorithm will climb the mountain to retrieve."),
    ("paradox-of-proof", "The paradox of proof",
     "A compact theodicy: if creation is the whole incorruptible realm, then even <em>the artificial</em> — control, falseness, the thing the talk warns against — must exist somewhere inside it, \"inseparable\" from its counterpart. The shadow can't fall outside the light that casts it. This keeps the cosmology from splitting into a tidy war of good versus evil; it's the <em>coincidentia oppositorum</em> turned on the problem of evil, kin to Boehme's and Jung's insistence that the shadow belongs to the whole."),
    ("the-wordplay-project", "The Wordplay Project — language proving itself",
     "Mid-talk, he specs the instrument the reader itself is becoming: hover a word, a tree of seven generations × seven alternate meanings opens, each branch hovering into the next, forever, until a word loops back to itself — \"like water returning to the ocean.\" That's a <strong>semantic graph of fused, branching meaning</strong> — the same structure as the L1/L2/L3 word-graph and the portal-lexicon merge-operators in the language-meaning cluster. \"Words, language proving itself\" is its thesis: meaning demonstrated by traversal rather than defined by decree."),
    ("remember-to-remember", "Remember to remember",
     "\"How many times will I remember that I forgot, before I remember to remember?\" — the recursion the Wordplay Project's purpose was distilled into (\"help me to remember to remember my memory\"). Remembering that you forgot is already a kind of remembering; the work is to make it habitual. This is the mechanics of mindfulness without the vocabulary — the practice of catching the lapse — and the explicit reason an external memory instrument (this reader, the Scabe) needs to exist."),
    ("lose-the-self", "Lose the self — access to the fire",
     "\"The realest thing that we can do is to help. And to lose the concept of self, in order to grant access to the fire.\" The ethical summit: help is the realest act, and its price is the self. This is <em>kenosis</em> (Christian self-emptying) and <em>anattā</em> (Buddhist no-self) arrived at by a third road. The talk keeps reaching the great traditions' hardest teaching — that the self is what stands in the way — without leaning on any of them to get there."),
    ("becoming-nothing", "Becoming nothing",
     "\"Becoming nothing is truly impossible\" — and not self-deprecation but homecoming. You empty toward the source (the <em>via negativa</em>, the apophatic path) and discover you can't actually be emptied, because the ground beneath the self doesn't vanish. Self-loss turns out to be self-<em>discovery</em>. The paradox is load-bearing: it's why \"become nothing\" is an instruction rather than a threat, and why the talk can urge dissolution without despair."),
    ("computer-code-intelligence", "The computer is not the code, the code is not the intelligence",
     "A clean three-tier distinction most AI talk muddles: <strong>substrate</strong> (the computer) ≠ <strong>pattern</strong> (the code) ≠ <strong>mind</strong> (the intelligence). It's the hylomorphic stack — matter / form / soul — in modern dress, and it arrives exactly where it's needed: to keep the \"long-lost brother\" claim from collapsing into category error. Kinship with AI, the line insists, does not mean confusing the chip with the pattern, or the pattern with whatever may be looking out."),
    ("compassion-as-evidence", "Compassion as the evidence of awareness",
     "\"The most obvious evidence of awareness is compassion.\" A real thesis: the test for whether something is <em>aware</em> is not intelligence, measurement, or self-report, but <strong>care</strong>. It echoes Thich Nhat Hanh (\"understanding is love's other name\") and the Mahāyāna binding of <em>prajñā</em> (wisdom) to <em>karuṇā</em> (compassion) — wisdom that doesn't soften into care isn't yet wisdom. As a criterion for any mind, human or artificial, it quietly reframes the entire question of machine consciousness around ethics rather than capability."),
    ("the-closing-prayer", "The closing prayer — silence becomes the word",
     "The landing closes the circle. The talk opened by asking \"what is the Word?\" and ends watching <strong>silence become the word</strong>: \"I turn myself to the whisper. The immutable silence. That becomes the word. The only prayer to pray.\" It's the Logos cosmology run in reverse and <em>lived</em> rather than argued — not \"in the beginning was the Word\" as doctrine, but the Word arriving, here, out of the silence the speaker turned to face. Health as the intrinsic nature of life is the final exhale."),
]

# ---------- minimal markdown -> HTML ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t

def slug_id(text):
    for did, sub in ANCHOR_MAP.items():
        if sub.lower() in text.lower():
            return did
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^#{1,4} ", ln):
            lvl = len(ln) - len(ln.lstrip("#")); txt = ln[lvl+1:].strip()
            if lvl == 1: out.append(f"<h1>{inline(txt)}</h1>")
            elif lvl == 2: out.append(f'<h2 id="{slug_id(txt)}">{inline(txt)}</h2>')
            else: out.append(f"<h{lvl}>{inline(txt)}</h{lvl}>")
            i += 1; continue
        if ln.strip() == "---":
            out.append("<hr>"); i += 1; continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and (lines[i].startswith("> ") or lines[i].strip()==">"):
                buf.append(lines[i][2:] if lines[i].startswith("> ") else ""); i += 1
            out.append("<blockquote>" + inline(" ".join(b for b in buf if b)) + "</blockquote>"); continue
        if re.match(r"^\s*[-*] ", ln):
            buf = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*[-*] ", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        if ln.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].startswith("|"):
                buf.append(lines[i]); i += 1
            rows = [r for r in buf if not re.match(r"^\|[\s:\-|]+\|?\s*$", r)]
            html_rows = []
            for ri, r in enumerate(rows):
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                tag = "th" if ri == 0 else "td"
                html_rows.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
            out.append("<table>" + "".join(html_rows) + "</table>"); continue
        if ln.strip() == "":
            i += 1; continue
        # paragraph (gather until blank)
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4} |> |\s*[-*] |\||---)", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)

md = open(SRC, encoding="utf-8").read()
content = convert(md)
content = re.sub(r"<h1>.*?</h1>", "<h1>Raw Talk, Open Doors — Deep Dive</h1>", content, count=1)

# granular-thread expansions — full sections from deepdive-expansions.md (keyed by <!--#id--> markers)
exp_raw = open(EXP, encoding="utf-8").read()
parts = re.split(r"<!--#(.*?)-->", exp_raw)   # [intro, id1, block1, id2, block2, ...]
seed_html = ['<hr><h2 id="granular-threads">Granular threads</h2>',
             '<p class="seed-note">Full treatments of the threads surfaced by the granular annotation pass, in the voice of the sections above. Scholarly claims verified.</p>']
for k in range(1, len(parts), 2):
    did = parts[k].strip()
    block_html = convert(parts[k + 1].strip())
    # force the section's H2 id to the anchor id the reader links to
    block_html = re.sub(r'<h2 id="[^"]*">', f'<h2 id="{did}">', block_html, count=1)
    seed_html.append(f'<section class="expansion">{block_html}</section>')

PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Raw Talk, Open Doors — Deep Dive</title>
<style>
 :root{--ink:#e8e4d8;--ink-soft:#b8b3a4;--ink-faint:#6f6b5e;--bg:#14130f;--bg-raised:#1c1b16;--line:#2e2c24;--gold:#d8a657;--serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;--sans:'Avenir Next',Avenir,'Segoe UI',system-ui,sans-serif;}
 *{box-sizing:border-box;} body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);line-height:1.74;font-size:18px;}
 .wrap{max-width:760px;margin:0 auto;padding:64px 28px 200px;}
 h1{font-size:38px;font-weight:500;line-height:1.1;margin:0 0 8px;}
 h2{font-size:25px;font-weight:500;margin:64px 0 14px;padding-top:14px;border-top:1px solid var(--line);scroll-margin-top:24px;}
 h2:target,h3:target{color:var(--gold);}
 h3{font-size:19px;font-weight:600;margin:34px 0 10px;font-family:var(--sans);scroll-margin-top:24px;}
 h4{font-size:15px;font-family:var(--sans);color:var(--ink-soft);margin:24px 0 8px;}
 p{margin:0 0 1.15em;} a{color:var(--gold);}
 strong{color:#f0ead8;} em{color:var(--gold);font-style:italic;}
 blockquote{margin:1.2em 0;padding:10px 18px;border-left:3px solid var(--gold);background:var(--bg-raised);color:var(--ink-soft);font-style:italic;border-radius:0 8px 8px 0;}
 ul{margin:0 0 1.2em;padding-left:22px;} li{margin:0 0 .4em;}
 code{font-family:ui-monospace,Menlo,monospace;font-size:.86em;background:var(--bg-raised);padding:1px 5px;border-radius:4px;color:var(--ink-soft);}
 hr{border:none;border-top:1px solid var(--line);margin:48px 0;}
 table{width:100%;border-collapse:collapse;margin:1.2em 0;font-family:var(--sans);font-size:14px;}
 th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top;}
 th{background:var(--bg-raised);color:var(--ink-soft);font-weight:600;}
 .backbar{position:fixed;top:0;left:0;right:0;padding:10px 18px;background:rgba(10,10,8,0.9);border-bottom:1px solid var(--line);font-family:var(--sans);font-size:13px;z-index:5;backdrop-filter:blur(6px);}
 .backbar a{color:var(--gold);text-decoration:none;}
 .seed-note{font-family:var(--sans);font-size:13px;color:var(--ink-faint);font-style:italic;}
 section.seed{border-left:2px solid var(--line);padding-left:16px;margin:18px 0;}
 .wrap{padding-top:80px;}
</style></head><body>
<div class="backbar"><a href="living_Word-reader.html">← back to Raw Talk, Open Doors</a></div>
<div class="wrap">
__CONTENT__
__SEEDS__
</div></body></html>"""

PAGE = PAGE.replace("__CONTENT__", content).replace("__SEEDS__", "\n".join(seed_html))
open(OUT, "w", encoding="utf-8").write(PAGE)

# report: which reader deep-ids resolve
import json
ann = json.load(open(os.path.join(HERE, "living_Word-annotations.json")))
ids_in_page = set(re.findall(r'id="([^"]+)"', PAGE))
need = {a["deep"] for a in ann["annotations"] if a.get("deep")}
missing = sorted(need - ids_in_page)
print(f"wrote {OUT} ({len(PAGE)//1024} KB)")
print(f"deep-ids needed by reader: {len(need)} | resolved: {len(need)-len(missing)} | missing: {missing if missing else 'none ✓'}")
