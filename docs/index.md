# viz-libs-comparison

A decision-grade comparison of **Plotly**, **Altair**, and **Bokeh** for interactive
Python visualization.

Every chapter renders the same plot across all three libraries and scores each on
code size, interactivity preserved after static-HTML export, file size,
performance, ergonomics, and customization ceiling.

All embedded plots on this site are **fully interactive and run with no Python server** —
pages are powered by [marimo](https://marimo.io) + [Pyodide](https://pyodide.org)
(WebAssembly) in your browser.

## Why this exists

Choosing between Plotly, Altair, and Bokeh for a project is surprisingly hard:
their ecosystems overlap, their sweet spots differ, and most comparisons online
are either shallow ("here's a bar chart in each") or strongly biased toward one
lib. This site is the reference I wanted to have when that decision comes up.

## How to use this

Each chapter is built the same way:

1. A short framing of the plot category.
2. The same plot in each library, side-by-side with source code.
3. An **evaluation table** scoring the three implementations on:
    - Lines of code
    - Interactivity retained in static HTML
    - Exported file size
    - Subjective render/interaction performance
    - API ergonomics notes
    - Customization ceiling
4. A verdict — which library wins for this category, and why.

## Chapters

| # | Topic | Status |
|---|-------|:------:|
| 00 | [Smoke test](00_smoke_test.md) — sanity check that all three libs work in WASM | ✅ |
| 01 | [Basics](01_basics.md) — scatter, line, bar, histogram | 🚧 |
| 02 | [Statistical](02_statistical.md) — box, violin, KDE, regression + CI | 🚧 |
| 03 | [Faceting](03_faceting.md) — small multiples, grouped bars, heatmaps | 🚧 |
| 04 | [Multi-layer](04_multilayer.md) — overlays, dual axis, annotations | 🚧 |
| 05 | [Interactive](05_interactive.md) — tooltips, zoom, selections, linked brushing | 🚧 |
| 06 | [Geospatial](06_geospatial.md) — choropleth, scatter-on-map | 🚧 |
| 07 | [Large data](07_large_data.md) — 100k–1M points, WebGL / datashader | 🚧 |
| 08 | [Dashboards](08_dashboards.md) — composition, layouts, cross-filtering | 🚧 |

## Running locally

```bash
uv sync --group dev
./scripts/export.sh
uv run python -m http.server --directory _site 8765
```

See the [README](https://github.com/FBumann/viz-libs-comparison#readme) for more.
