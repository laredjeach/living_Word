# Freeflow Annotated Reader

An interactive annotated transcript with a linked deep-dive analysis.

## Read it

- On GitHub Pages: open the published site URL.
- From a downloaded copy: open `index.html` in any modern browser.

No installation, local server, or build step is needed to read it. Keep
`freeflow-reader.html` and `freeflow-deepdive.html` in the same folder so their
links continue to work.

## Project files

- `freeflow-reader.html` - complete interactive reader
- `freeflow-deepdive.html` - linked long-form analysis
- `freeflow-annotations.json` - annotation source data
- `build_reader.py` and `build_deepdive.py` - local generation scripts

The builder scripts expect canonical source material from the adjacent
`freeflow-v2` folder. Those source files are only needed to regenerate the HTML,
not to read or publish the finished project.
