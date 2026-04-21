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
| 02 | [Faceted scenarios](assets/notebooks/02_faceted.html) — same stacked-area dispatch across 5 scenarios, full year (8760 hours) | ✅ |
| 03 | Load duration + heatmap — full-year demand distribution views | 🚧 |
| 04 | Capacity & cost breakdown — multi-dim categorical bars | 🚧 |
| 05 | Uncertainty visualization — mean dispatch with inter-scenario bands | 🚧 |
| 06 | Energy balance / Sankey — where energy flows | 🚧 |
| 07 | Interactive exploration — linked brushing across plots | 🚧 |
| 08 | Large time series — full-year hourly stress test (WebGL / datashader) | 🚧 |

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
