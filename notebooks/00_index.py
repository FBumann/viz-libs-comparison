# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # viz-libs-comparison

        A decision-grade comparison of **Plotly**, **Altair**, and **Bokeh**.

        Every page renders the same plot across all three libraries and scores each
        one on code size, interactivity preserved after static-HTML export, file size,
        performance, ergonomics, and customization ceiling.

        All plots here are fully interactive and run **without any Python server** —
        the page is powered by marimo + Pyodide (WASM) in your browser.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Notebooks

        - [00 — Smoke test](./00_smoke_test.html) &nbsp;·&nbsp; sanity check that all three libs render in WASM
        - [01 — Basics](./01_basics.html) *(coming soon)*
        - [02 — Statistical](./02_statistical.html) *(coming soon)*
        - [03 — Faceting](./03_faceting.html) *(coming soon)*
        - [04 — Multi-layer](./04_multilayer.html) *(coming soon)*
        - [05 — Interactive](./05_interactive.html) *(coming soon)*
        - [06 — Geospatial](./06_geospatial.html) *(coming soon)*
        - [07 — Large data](./07_large_data.html) *(coming soon)*
        - [08 — Dashboards](./08_dashboards.html) *(coming soon)*
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Source

        [github.com/FBumann/viz-libs-comparison](https://github.com/FBumann/viz-libs-comparison)
        """
    )
    return


if __name__ == "__main__":
    app.run()
