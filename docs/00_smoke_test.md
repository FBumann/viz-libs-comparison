# Smoke test

Sanity check that Plotly, Altair, and Bokeh all render in a browser with no
Python server — powered by marimo's WASM (Pyodide) export. The same scatter
plot in each of the three libraries, with the source code visible next to each
plot.

[Open notebook &rarr;](./assets/notebooks/00_smoke_test.html){ .md-button .md-button--primary target=_blank }

!!! info "First boot takes a moment"
    The initial load downloads Pyodide and installs `pandas`, `plotly`,
    `altair`, `bokeh`, and `palmerpenguins` into your browser. ~30–60 s the
    first time; instant on refresh.
