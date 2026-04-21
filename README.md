# viz-libs-comparison

A decision-grade comparison of **Plotly**, **Altair**, and **Bokeh** for interactive
Python visualization — same plots across all three libraries, systematically evaluated,
published as static HTML pages that stay fully interactive **without a Python kernel**.

## Goal

Answer the question: *"Which library should I reach for, when?"*

Every notebook renders the same plot in all three libraries and scores each on:

- Lines of code
- Interactivity features retained after static HTML export
- Exported file size
- Render / interaction performance
- API ergonomics
- Customization ceiling

The output is published via GitHub Pages, where every chart remains interactive in
a browser with no server running — powered by
[marimo](https://marimo.io) + [Pyodide](https://pyodide.org) (WASM).

## Live site

<https://fbumann.github.io/viz-libs-comparison/> *(published by CI on push to `main`)*

## Notebooks

| # | Topic |
|---|-------|
| 00 | Index (landing page) |
| 01 | Basics — scatter, line, bar, histogram |
| 02 | Statistical — box, violin, KDE, regression + CI |
| 03 | Faceting — small multiples, grouped bars, heatmaps |
| 04 | Multi-layer — overlays, dual axis, annotations |
| 05 | Interactive — tooltips, zoom, selections, linked brushing |
| 06 | Geospatial — choropleth, scatter-on-map |
| 07 | Large data — 100k–1M points, WebGL / datashader |
| 08 | Dashboards — composition, layouts, cross-filtering |

## Quick start

Prerequisites: [`uv`](https://docs.astral.sh/uv/).

```bash
# Install deps
uv sync

# Edit a notebook interactively
uv run marimo edit notebooks/01_basics.py

# Build the static site locally and preview
./scripts/export.sh
uv run python -m http.server --directory _site 8765
# then open http://localhost:8765
```

## Adding a new chapter

1. Create `notebooks/NN_topic.py` as a marimo notebook. Include the PEP 723
   inline script header declaring every WASM dependency the notebook imports
   (transitively — Pyodide only bundles packages you list):

   ```python
   # /// script
   # requires-python = ">=3.12"
   # dependencies = [
   #     "marimo", "pandas", "plotly", "altair", "bokeh",
   #     # ...any extras
   # ]
   # ///
   ```

2. Create `docs/NN_topic.md` with the prose discussion + an `<iframe>` embedding
   the exported notebook:

   ```html
   <iframe class="marimo-embed"
           src="./assets/notebooks/NN_topic.html"
           height="2000"></iframe>
   ```

3. Add a `nav` entry for the page in `mkdocs.yml`.
4. Push — CI rebuilds the WASM export and the mkdocs site, then redeploys.

## Project layout

```
.
├── data/                         # shared dataset loaders
├── notebooks/                    # marimo .py notebooks — source of truth for plots
├── docs/                         # mkdocs-material prose pages that embed notebooks
│   ├── index.md
│   ├── NN_topic.md
│   └── assets/
│       ├── embed.css
│       └── notebooks/            # generated WASM HTML, gitignored
├── scripts/export.sh             # two-stage build: marimo export → mkdocs build
├── mkdocs.yml
├── tests/                        # loader sanity checks
└── .github/workflows/            # CI (ruff) + Pages deploy
```
