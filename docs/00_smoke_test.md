# Smoke test

Sanity check that Plotly, Altair, and Bokeh all render in a browser with no
Python server — powered by marimo's WASM (Pyodide) export. If this page loads
and every plot responds to hover/zoom, the rest of the comparison can be built
on the same pipeline.

!!! info "First boot takes a moment"
    The initial load downloads Pyodide and installs `pandas`, `plotly`,
    `altair`, `bokeh`, and `palmerpenguins` into your browser. ~30–60 s the
    first time; instant on refresh thanks to browser caching.

<div class="marimo-embed-wrapper">
<iframe class="marimo-embed" src="./assets/notebooks/00_smoke_test.html" height="2400"></iframe>
<div class="marimo-embed-actions">
<a href="./assets/notebooks/00_smoke_test.html" target="_blank">Open standalone &rarr;</a>
</div>
</div>

## What we learned

Even this trivial example surfaced a real finding about **interactivity defaults**:

- **Plotly** — clicking a legend entry hides/isolates that trace. Free, no
  configuration.
- **Altair** — legend clicks do nothing by default. You need an explicit
  `alt.selection_point(fields=['species'], bind='legend')` with an
  `opacity=alt.condition(...)` to get the same behavior.
- **Bokeh** — legend clicks do nothing by default. One line fixes it:
  `p.legend.click_policy = "hide"`.

All three *can* do legend toggling; only Plotly gives it to you for free. This
kind of default-behavior gap is exactly what chapter
[05 — Interactive](05_interactive.md) will systematize.
