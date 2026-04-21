# viz-libs-comparison

A task-oriented comparison of **Plotly**, **Altair**, and **Bokeh** for
**energy-system analysis** — specifically, for looking at the kind of
multi-dimensional, time-series xarray output that tools like
[flixopt](https://github.com/flixOpt/flixopt) produce.

Each chapter takes a concrete analysis question ("show me this week's
dispatch", "compare three scenarios side by side") and walks through how each
library answers it. The point isn't *which library wins* — it's what each
library's mental model feels like on real work.

All notebooks are fully interactive and run with **no Python server** —
they're powered by [marimo](https://marimo.io) + [Pyodide](https://pyodide.org)
(WebAssembly) in your browser.

## Chapters

!!! tip
    **Cmd/Ctrl-click a chapter to open it in a new tab.** Pyodide stays booted
    in each tab, so switching between chapters is instant after the first
    boot. Plain clicks navigate in-place and re-boot on return.

| # | Task | Status |
|---|------|:------:|
| 00 | [Smoke test](assets/notebooks/00_smoke_test.html) — sanity check that all three libs render in WASM | ✅ |
| 01 | [Dispatch over one week](assets/notebooks/01_dispatch.html) — stacked area of generation + demand + storage SoC | ✅ |
| 02 | [Faceted scenarios](assets/notebooks/02_faceted.html) — same stacked-area dispatch across 5 scenarios | ✅ |
| 03 | [Performance at scale](assets/notebooks/03_performance.html) — full-year hourly dispatch, each lib's data-volume escape hatch | ✅ |
| 04 | [Load duration + heatmap](assets/notebooks/04_distribution.html) — demand sorted as an LDC and arranged as a 24 × 365 heatmap | ✅ |
| 05 | [Uncertainty bands](assets/notebooks/05_uncertainty.html) — min/max band + mean line + spaghetti of five scenarios | ✅ |
| 06 | [Linked brushing](assets/notebooks/06_linked.html) — brush a time range, see the demand distribution for that range | ✅ |
| 07 | [Dashboard](assets/notebooks/07_dashboard.html) — scenario dropdown driving a dispatch plot + a capacity bar chart | ✅ |

## The data

All chapters draw from a single synthetic `xr.Dataset` shaped like a
`flixopt` `flow_system.solution`:

```
Dimensions:   (time: 8760, flow: 5, scenario: 5, period: 2)
Coords:
  * time      datetime64   2030-01-01 … 2030-12-31 23:00 (hourly)
  * flow      object       'solar' 'wind' 'gas' 'batt_charge' 'batt_discharge'
  * scenario  object       'baseline' 'high_renewables' 'costly_gas' …
  * period    int          2030 2040
Data vars:
  generation  (scenario, period, flow, time)    MW
  demand      (scenario, period, time)          MW
  storage_soc (scenario, period, time)          MWh
  capacity    (scenario, period, flow)          MW
```

Each chapter selects the subset it needs. The full 8760-hour series only
gets stressed in the large-data chapter.

## Running locally

```bash
uv sync --group dev
./scripts/export.sh
uv run python -m http.server --directory _site 8765
```

See the [README](https://github.com/FBumann/viz-libs-comparison#readme) for
more.
