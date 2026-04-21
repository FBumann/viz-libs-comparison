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
    import plotly.express as px
    import plotly.graph_objects as go
    from bokeh.models import ColumnDataSource, LinearColorMapper
    from bokeh.palettes import Viridis256
    from bokeh.plotting import figure


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 04 — Load duration + heatmap

        Chapters 01–03 plotted dispatch along the time axis. Real energy-
        system analysis also asks *"what does the demand profile *look* like
        as a distribution?"* — shape of the load duration curve, when the
        peaks fall, how much of the year sits near peak. Two canonical views:

        - **Load duration curve** (LDC) — demand sorted descending and plotted
          against percentile. Steepness, shoulder, and baseline become
          visible at a glance.
        - **Hour-of-day × day-of-year heatmap** — 24 × 365 cells, demand as
          colour. Daily rhythm shows as horizontal banding; seasonal pattern
          as vertical banding.

        Both plots require **reshaping** the time series — sort + rank for
        LDC, pivot for the heatmap — so this chapter tests how naturally
        each library handles data coming in a shape it can't directly consume.

        ## What the plots should do

        - LDC: one line per lib; x is percentile of hours, y is demand in MW
        - Heatmap: 24 hours × 365 days, smooth Viridis-style colour mapping,
          date on x-axis, hour on y-axis, demand value legible on hover
        - Consistent colour scale across all three libs for apples-to-apples
          visual comparison

        ## Where the libraries differ

        ✅ = does what we want out of the box.
        ⚠️ = works, but needed a specific non-default pattern.
        ❌ = doesn't support / not implemented.

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | LDC (sort + line) | ✅ `px.line` on a pre-sorted DataFrame | ✅ `mark_line` — sort can also live in the encoding via `transform_window` | ✅ `p.line` on pre-sorted arrays |
        | Heatmap API | ✅ `go.Heatmap` or `px.imshow` — single call on a 2D array | ✅ `mark_rect` with `x` + `y` + `color` encodings — fully declarative, no pivot needed | ⚠️ `p.rect` with `LinearColorMapper` — needs explicit coordinate placement and manual palette; no `imshow` equivalent |
        | 2D pivoting | `pd.pivot_table` → `go.Heatmap(z=...)` | done inside the spec — Altair reshapes via encodings | `pd.pivot_table` → flatten to long form for `ColumnDataSource` |
        | Automatic color-bar | ✅ | ✅ | ⚠️ explicit `ColorBar` model added via `p.add_layout(color_bar, "right")` |
        | Categorical y-axis (hour 0–23) | ✅ auto | ✅ `"hour:O"` | ⚠️ cast hour as string + pass `y_range=[str(h) for h in range(24)]` |
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
    # Baseline scenario, 2030 period — one row per hour with demand
    year_demand = (
        df_full[(df_full["scenario"] == "baseline") & (df_full["period"] == 2030)]
        .drop_duplicates(subset="time")[["time", "demand"]]
        .reset_index(drop=True)
    )
    year_demand["hour"] = year_demand["time"].dt.hour
    year_demand["date"] = year_demand["time"].dt.normalize()
    year_demand["day_of_year"] = year_demand["time"].dt.dayofyear
    year_demand
    return (year_demand,)


@app.cell
def _(year_demand):
    # LDC: sort demand descending, compute percentile of year
    ldc = year_demand[["demand"]].sort_values("demand", ascending=False).reset_index(drop=True)
    ldc["percentile"] = (ldc.index + 1) / len(ldc) * 100

    # Heatmap: 2D pivot (hours × dates) for libs that want wide-form; the long
    # form (year_demand) is kept for libs that reshape in the spec
    heatmap_wide = year_demand.pivot_table(index="hour", columns="date", values="demand")
    ldc
    return heatmap_wide, ldc


@app.cell
def _():
    mo.md("## Load duration curve")
    return


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(ldc):
    _t0 = time.perf_counter()
    fig_ldc_plotly = px.line(
        ldc,
        x="percentile",
        y="demand",
        labels={"percentile": "Percentile of hours (%)", "demand": "Demand (MW)"},
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), fig_ldc_plotly])
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(ldc):
    _t0 = time.perf_counter()
    chart_ldc_altair = (
        alt.Chart(ldc)
        .mark_line()
        .encode(
            x=alt.X("percentile:Q").title("Percentile of hours (%)"),
            y=alt.Y("demand:Q").title("Demand (MW)"),
        )
        .properties(width=720, height=300)
        .interactive()
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_ldc_altair])
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(ldc):
    _t0 = time.perf_counter()
    p_ldc_bokeh = figure(
        width=720,
        height=300,
        x_axis_label="Percentile of hours (%)",
        y_axis_label="Demand (MW)",
        tools="pan,wheel_zoom,box_zoom,reset,hover",
    )
    p_ldc_bokeh.line(ldc["percentile"], ldc["demand"], line_width=2)
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), p_ldc_bokeh])
    return


@app.cell
def _():
    mo.md("## Hour × Day heatmap")
    return


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(heatmap_wide):
    _t0 = time.perf_counter()
    fig_hm_plotly = go.Figure(
        data=go.Heatmap(
            z=heatmap_wide.values,
            x=heatmap_wide.columns,
            y=heatmap_wide.index,
            colorscale="Viridis",
            colorbar={"title": "Demand (MW)"},
            hovertemplate="%{x|%b %d} · %{y}:00<br>%{z:.1f} MW<extra></extra>",
        )
    )
    fig_hm_plotly.update_layout(
        xaxis_title="Date",
        yaxis_title="Hour of day",
        yaxis={"dtick": 3},
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), fig_hm_plotly])
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(year_demand):
    _t0 = time.perf_counter()
    chart_hm_altair = (
        alt.Chart(year_demand)
        .mark_rect()
        .encode(
            x=alt.X("date:T").title("Date"),
            y=alt.Y("hour:O").title("Hour of day"),
            color=alt.Color(
                "demand:Q",
                scale=alt.Scale(scheme="viridis"),
                legend=alt.Legend(title="Demand (MW)"),
            ),
            tooltip=[
                alt.Tooltip("date:T", format="%b %d"),
                alt.Tooltip("hour:O"),
                alt.Tooltip("demand:Q", format=".1f"),
            ],
        )
        .properties(width=720, height=300)
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_hm_altair])
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(year_demand):
    _t0 = time.perf_counter()
    from bokeh.models import ColorBar

    _data = year_demand.copy()
    _data["hour_str"] = _data["hour"].astype(str).str.zfill(2)
    _source = ColumnDataSource(_data)

    _mapper = LinearColorMapper(
        palette=Viridis256, low=_data["demand"].min(), high=_data["demand"].max()
    )

    p_hm_bokeh = figure(
        width=720,
        height=340,
        x_axis_type="datetime",
        x_axis_label="Date",
        y_axis_label="Hour of day",
        y_range=[str(h).zfill(2) for h in range(24)],
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        tooltips=[
            ("date", "@date{%F}"),
            ("hour", "@hour_str"),
            ("demand", "@demand{0.1} MW"),
        ],
    )
    p_hm_bokeh.rect(
        x="date",
        y="hour_str",
        width=1000 * 60 * 60 * 24,  # 1 day in ms
        height=1,
        source=_source,
        fill_color={"field": "demand", "transform": _mapper},
        line_color=None,
    )
    _color_bar = ColorBar(color_mapper=_mapper, label_standoff=10, title="Demand (MW)")
    p_hm_bokeh.add_layout(_color_bar, "right")
    p_hm_bokeh.hover.formatters = {"@date": "datetime"}
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), p_hm_bokeh])
    return


if __name__ == "__main__":
    app.run()
