# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.2",
#     "pandas==2.3.3",
#     "pyarrow==24.0.0",
#     "numpy==2.4.4",
#     "plotly==6.7.0",
#     "altair==6.1.0",
#     "bokeh==3.9.0",
# ]
# ///
import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


with app.setup:
    import warnings

    warnings.filterwarnings("ignore", message=".*narwhals.*")

    import io
    import time

    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from bokeh.models import BoxSelectTool, ColumnDataSource
    from bokeh.plotting import figure


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 06 — Linked brushing

        Linked brushing — drag-select a range in one plot and see another
        plot update in response — is one of the most useful interactions
        in data analysis and one of the sharpest differences between the
        three libraries. Each has a completely different model for *how* a
        selection propagates:

        - **Altair** runs Vega's selection signals entirely in the browser.
          Declare a selection, reference it in another chart's
          `transform_filter`, done.
        - **Plotly** has no native cross-plot selection in a static export.
          The usual path is a Python-side callback (Dash, FigureWidget) or,
          in marimo, a `mo.ui` widget whose value triggers the dependent
          cells to re-run.
        - **Bokeh** propagates selections automatically between glyphs that
          share a `ColumnDataSource`. No callback needed for visual
          highlighting; a `CustomJS` callback if you need to recompute
          anything (like a histogram of the selected subset).

        ## What the plot should do

        - Top view: one week of hourly demand, drag-selectable along the
          x-axis
        - Bottom view: histogram (or analogous summary) of the demand
          values in the selected range. No selection → all values
        - Selecting and deselecting should feel smooth — this is the
          interaction we're grading

        ## Where the libraries differ

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Native cross-plot selection in static HTML | ❌ none — cross-plot only via Dash callback (server) or FigureWidget (Python kernel) | ✅ `selection_interval` + `transform_filter` — pure Vega in the browser | ✅ shared `ColumnDataSource` — selection propagates to any glyph bound to that source |
        | Recompute an aggregate (histogram) on selection | ⚠️ possible via marimo `mo.ui.range_slider`; Python re-runs the cell. Works but requires Python round-trip | ✅ automatic — Vega recomputes `bin()` on the filtered subset | ⚠️ `CustomJS` callback that recomputes histogram edges + counts in JS and writes back to a second source |
        | Code lines for linked histogram | ~15 (incl. `mo.ui` widget + filter + re-plot) | ~15 (selection + filter on second chart) | ~25 (source + callback JS + second source for histogram) |
        | Interaction feel | slight lag — Python round-trip through marimo | snappy — all in Vega | snappy — JS-only |
        """
    )
    return


@app.cell
async def _():
    _path = str(mo.notebook_location() / "public" / "dispatch.parquet")
    if _path.startswith(("http://", "https://")):
        from pyodide.http import pyfetch

        _resp = await pyfetch(_path)
        df_full = pd.read_parquet(io.BytesIO(await _resp.bytes()))
    else:
        df_full = pd.read_parquet(_path)
    df_full
    return (df_full,)


@app.cell
def _(df_full):
    week = (
        df_full[
            (df_full["scenario"] == "baseline")
            & (df_full["period"] == 2030)
            & (df_full["time"] >= pd.Timestamp("2030-07-14"))
            & (df_full["time"] <= pd.Timestamp("2030-07-20 23:00"))
        ]
        .drop_duplicates(subset="time")[["time", "demand"]]
        .reset_index(drop=True)
    )
    week
    return (week,)


@app.cell
def _():
    mo.md("### Altair — `selection_interval` + `transform_filter`")
    return


@app.cell
def _(week):
    _t0 = time.perf_counter()

    _brush = alt.selection_interval(encodings=["x"])
    _line = (
        alt.Chart(week)
        .mark_line(color="#1A73E8")
        .encode(
            x=alt.X("time:T").title(None),
            y=alt.Y("demand:Q").title("Demand (MW)"),
        )
        .add_params(_brush)
        .properties(width=720, height=200)
    )
    _hist = (
        alt.Chart(week)
        .mark_bar()
        .encode(
            x=alt.X("demand:Q", bin=alt.Bin(maxbins=30)).title("Demand (MW)"),
            y=alt.Y("count():Q").title("Hours"),
        )
        .transform_filter(_brush)
        .properties(width=720, height=160)
    )
    chart_linked_altair = _line & _hist

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_linked_altair])
    return


@app.cell
def _():
    mo.md("### Plotly — via `mo.ui.range_slider` (Python round-trip)")
    return


@app.cell
def _(week):
    range_plotly = mo.ui.range_slider(
        start=0,
        stop=len(week) - 1,
        value=(0, len(week) - 1),
        step=1,
        label="Selected hour range",
        show_value=True,
        full_width=True,
    )
    range_plotly
    return (range_plotly,)


@app.cell
def _(range_plotly, week):
    _t0 = time.perf_counter()

    _lo, _hi = range_plotly.value
    _selected = week.iloc[_lo : _hi + 1]

    fig_linked_plotly = go.Figure()
    fig_linked_plotly.add_trace(
        go.Scatter(
            x=week["time"],
            y=week["demand"],
            mode="lines",
            line={"color": "#1A73E8"},
            name="demand",
            showlegend=False,
        )
    )
    fig_linked_plotly.add_vrect(
        x0=_selected["time"].iloc[0],
        x1=_selected["time"].iloc[-1],
        fillcolor="#1A73E8",
        opacity=0.12,
        line_width=0,
    )
    fig_linked_plotly.update_layout(
        yaxis_title="Demand (MW)",
        height=240,
        margin={"t": 20, "b": 30},
    )

    fig_hist_plotly = go.Figure(
        data=go.Histogram(
            x=_selected["demand"], nbinsx=30, marker_color="#1A73E8", opacity=0.8
        )
    )
    fig_hist_plotly.update_layout(
        xaxis_title="Demand (MW)",
        yaxis_title="Hours",
        height=200,
        margin={"t": 20, "b": 30},
    )

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [
            mo.md(f"_Python build: **{_elapsed:.1f} ms**_"),
            fig_linked_plotly,
            fig_hist_plotly,
        ]
    )
    return


@app.cell
def _():
    mo.md("### Bokeh — shared `ColumnDataSource` (highlight) + `CustomJS` (histogram)")
    return


@app.cell
def _(week):
    _t0 = time.perf_counter()
    from bokeh.layouts import column as bk_column
    from bokeh.models import CustomJS

    _src = ColumnDataSource(week)

    _n_bins = 30
    _edges = np.linspace(week["demand"].min(), week["demand"].max(), _n_bins + 1)
    _counts, _ = np.histogram(week["demand"], bins=_edges)
    _hist_src = ColumnDataSource(
        {"left": _edges[:-1], "right": _edges[1:], "top": _counts}
    )

    p_line_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=220,
        y_axis_label="Demand (MW)",
        tools="pan,wheel_zoom,reset",
    )
    p_line_bokeh.line(
        "time", "demand", source=_src, color="#1A73E8", line_width=1.5
    )
    p_line_bokeh.add_tools(BoxSelectTool(dimensions="width"))

    p_hist_bokeh = figure(
        width=720,
        height=180,
        x_axis_label="Demand (MW)",
        y_axis_label="Hours",
        tools="",
    )
    p_hist_bokeh.quad(
        left="left", right="right", top="top", bottom=0, source=_hist_src, color="#1A73E8", alpha=0.8
    )

    _callback = CustomJS(
        args={"src": _src, "hist_src": _hist_src, "edges": _edges.tolist()},
        code="""
        const indices = src.selected.indices;
        const demand = src.data['demand'];
        const n = edges.length - 1;
        const counts = new Array(n).fill(0);
        const values = indices.length ? indices.map(i => demand[i]) : demand;
        for (const v of values) {
            for (let b = 0; b < n; b++) {
                if (v >= edges[b] && (v < edges[b+1] || b === n-1)) {
                    counts[b] += 1;
                    break;
                }
            }
        }
        hist_src.data['top'] = counts;
        hist_src.change.emit();
        """,
    )
    _src.selected.js_on_change("indices", _callback)

    chart_linked_bokeh = bk_column(p_line_bokeh, p_hist_bokeh)

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_linked_bokeh])
    return


if __name__ == "__main__":
    app.run()
