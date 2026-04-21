# viz-libs-comparison

A reference comparing **Plotly**, **Altair**, and **Bokeh** for interactive
Python visualization. Every chapter renders the same plot across all three
libraries and shows the source code side-by-side, so you can see the API
differences directly.

All notebooks are **fully interactive and run with no Python server** —
they're powered by [marimo](https://marimo.io) +
[Pyodide](https://pyodide.org) (WebAssembly) in your browser.

## Why this exists

Choosing between Plotly, Altair, and Bokeh for a project is surprisingly
hard: their ecosystems overlap, their sweet spots differ, and most
comparisons online are either shallow ("here's a bar chart in each") or
strongly biased toward one lib. This site lets the code and the plots speak
for themselves — no verdicts, no "winner per chapter." Readers form their
own opinion from the same evidence.

## Chapters

Each chapter links to a standalone marimo notebook with source and plots
visible together.

| # | Topic | Status |
|---|-------|:------:|
| 00 | [Smoke test](00_smoke_test.md) — sanity check that all three libs work in WASM | ✅ |
| 01 | [Basics](01_basics.md) — scatter, line, bar, histogram | ✅ |
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

See the [README](https://github.com/FBumann/viz-libs-comparison#readme) for
more.
