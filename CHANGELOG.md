# Freeflow Annotated Reader — CHANGELOG

## 2026-06-21 — Stages 1–3 (Claude Code)

Resumed from the Claude.ai slice. Held to the evolved direction (final-result orientation; the
last voice-revision message treated as a *principle*, not a frozen 14-item task).

### Stage 1 — re-voice the slice
- Rewrote all 14 slice annotations for the two locked principles: **compressed flow-state voice**
  + **calibrated praise/synchronicity in an editorial register** (ideas/convergences are the striking
  thing, never the author).
- Applied content fix: **Scabe = "learned the word from a friend, it stuck," not Xela.** De-linked the
  Xela annotation from being Scabe's source.
- Surfaced one tier change (not locked to original count): **`double-negative` 3 → 2** (it's the talk's
  duality-dissolving method + the literal Wordplay-Project seed).
- Kept `living_Word-reader-slice.html` + its inline data in byte-for-byte sync (verified).

### Stage 2 — full annotation pass
- Read the full canon (5,513 words). Authored the complete door set: **43 annotations** across all three
  tiers, whole talk (opening → closing prayer), in the locked voice.
- `living_Word-annotations.json` is now the **full source of truth** (was the 14-slice).

### Stage 3 — production build
- `build_reader.py` → **`living_Word-reader.html`** (79 KB). Architecture: canon transcript rendered
  *verbatim*; highlights wrapped **at runtime** by matching `anchor_quote` against the page text — so the
  transcript stays canon-pure and the JSON drives every door. Reused the slice's CSS + panel/peek
  machinery (click-to-open, one-at-a-time, faint hover preview, Esc/×/click-away). Added a reading-progress
  bar. Validated: all 43 anchors match canon, fit a single text node, and are unique.
- `build_deepdive.py` → **`living_Word-deepdive.html`** (114 KB). Converts the canon deep-dive markdown
  (read-only) to styled HTML, assigns anchor ids matching the reader's `deep` ids (21 existing sections),
  and appends **14 seed sections** for the new granular threads. Verified: **all 36 deep-ids resolve** —
  every "Read full analysis →" lands on real content.

### Source files — untouched (canon)
`living_Word-raw_original.md`, `living_Word-raw transcript_tracking.md`, `living_Word-deepdive.md`,
`living_Word-overview.md`, `living_Word-notes.md`, and the parent-folder raw copy. Both HTML files are derived;
re-run the two builders to regenerate.

### Stage 3b — deepen the 14 seed sections (next step #1, done)
- Ran a 2-agent research pass; verified ~17 scholarly/theological claims (kenosis, bonum diffusivum sui,
  apophatic/Pseudo-Dionysius, coincidentia oppositorum/Cusa, tzimtzum, anattā, prajñā/karuṇā, Thich Nhat
  Hanh "understanding is love's other name", hylomorphism, Keats negative capability, flow, etc.).
- Wrote the 14 threads to **full treatment** in `deepdive-expansions.md` (new file — Cursor-editable; canon
  `living_Word-deepdive.md` untouched). Each: freeflow blockquote → grounded cross-cultural treatment →
  "why it matters in the freeflow" → further-reading links. Matches the canonical sections' voice.
- `build_deepdive.py` now folds expansions in via `<!--#id-->` markers (forces anchor ids). Rebuilt
  `living_Word-deepdive.html` (129 KB); all 36 reader deep-ids resolve to real sections.

### Open / next
- Audio (`.m4a`) not yet synced to the reader — needs WhisperX word-level timestamps (recoverable?).
- Emit/define the JSON sidecar usage for the Wordplay Project / Exocortex consumption.
- (Optional) fold the expansions into the canonical `living_Word-deepdive.md` — a confirmed step, not done.
