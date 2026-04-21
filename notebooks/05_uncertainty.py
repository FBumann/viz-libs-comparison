# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.2",
#     "pandas==2.3.3",
#     "pyarrow==24.0.0",
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
    import pandas as pd
    import plotly.graph_objects as go
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 05 — Uncertainty across scenarios

        Scenarios are a stand-in for *uncertainty* — different demand
        assumptions, policies, weather. When presenting a dispatch result,
        you often want to show the **central tendency** (mean) together with
        the **spread** across scenarios as a band. This chapter takes the
        five scenarios as an ensemble and plots, per hour, the **min–max
        band** with the **mean** line on top, plus thin **individual-scenario
        lines** underneath so you see the actual realisations.

        ## What the plot should do

        - Filled band from min to max of `demand` across the 5 scenarios
          for each hour
        - Mean line in a contrasting colour on top of the band
        - Thin individual-scenario lines overlaid for context (spaghetti plot)
        - One week, hourly — same window as chapters 01 and 02 for continuity
        - Shared colour palette so scenarios line up across the three libs

        ## Where the libraries differ

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Band between two series | ⚠️ two `go.Scatter` traces — first invisible (the upper bound), second with `fill='tonexty'` filling down to the first; legend + hover require extra flags | ✅ `mark_area` with both `y` and `y2` encodings — natural | ✅ `p.varea(y1=..., y2=...)` — one call |
        | Aggregation across a group | pandas pre-aggregate → one row per time with `mean`, `min`, `max` columns | inline via `transform_aggregate` or pre-aggregate; both are clean | pandas pre-aggregate |
        | Spaghetti overlay | loop over scenarios, one `go.Scatter` per | `mark_line` with `color='scenario:N'` on the raw frame — one chart covers all 5 lines | loop over scenarios, one `p.line` per |
        | Consistent colour palette across marks | pass `fillcolor` + `line.color` explicitly | shared colour scale via `alt.Color` + `alt.Scale(domain=..., range=...)` | pass colour explicitly per glyph |
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
            (df_full["period"] == 2030)
            & (df_full["time"] >= pd.Timestamp("2030-07-14"))
            & (df_full["time"] <= pd.Timestamp("2030-07-20 23:00"))
        ]
        .drop_duplicates(subset=["scenario", "time"])[["scenario", "time", "demand"]]
        .reset_index(drop=True)
    )
    agg = (
        week.groupby("time")["demand"]
        .agg(["mean", "min", "max"])
        .reset_index()
        .rename(columns={"mean": "mean_demand", "min": "min_demand", "max": "max_demand"})
    )
    scenarios = sorted(week["scenario"].unique().tolist())
    agg
    return agg, scenarios, week


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(agg, scenarios, week):
    _t0 = time.perf_counter()
    fig_unc_plotly = go.Figure()

    # Upper bound (invisible line, just the anchor for fill)
    fig_unc_plotly.add_trace(
        go.Scatter(
            x=agg["time"],
            y=agg["max_demand"],
            mode="lines",
            line={"width": 0, "color": "rgba(26,115,232,0)"},
            showlegend=False,
            hoverinfo="skip",
        )
    )
    # Lower bound, fills up to previous trace = the band
    fig_unc_plotly.add_trace(
        go.Scatter(
            x=agg["time"],
            y=agg["min_demand"],
            mode="lines",
            line={"width": 0, "color": "rgba(26,115,232,0)"},
            fill="tonexty",
            fillcolor="rgba(26,115,232,0.22)",
            name="min–max band",
        )
    )
    # Individual scenarios (spaghetti)
    for _scen in scenarios:
        _s = week[week["scenario"] == _scen]
        fig_unc_plotly.add_trace(
            go.Scatter(
                x=_s["time"],
                y=_s["demand"],
                mode="lines",
                line={"width": 1, "color": "rgba(100,100,100,0.55)"},
                name=_scen,
                showlegend=False,
            )
        )
    # Mean on top
    fig_unc_plotly.add_trace(
        go.Scatter(
            x=agg["time"],
            y=agg["mean_demand"],
            mode="lines",
            line={"width": 2.5, "color": "#1A73E8"},
            name="mean",
        )
    )
    fig_unc_plotly.update_layout(
        yaxis={"title": "Demand (MW)"},
        hovermode="x unified",
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), fig_unc_plotly])
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(agg, week):
    _t0 = time.perf_counter()
    _band = (
        alt.Chart(agg)
        .mark_area(opacity=0.22, color="#1A73E8")
        .encode(
            x=alt.X("time:T").title(None),
            y=alt.Y("min_demand:Q").title("Demand (MW)"),
            y2="max_demand:Q",
        )
    )
    _spaghetti = (
        alt.Chart(week)
        .mark_line(strokeWidth=1, color="#64646488")
        .encode(x="time:T", y="demand:Q", detail="scenario:N")
    )
    _mean = (
        alt.Chart(agg)
        .mark_line(strokeWidth=2.5, color="#1A73E8")
        .encode(x="time:T", y="mean_demand:Q")
    )
    chart_unc_altair = (
        (_band + _spaghetti + _mean)
        .properties(width=720, height=340)
        .interactive()
    )
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_unc_altair])
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(agg, scenarios, week):
    _t0 = time.perf_counter()
    p_unc_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=340,
        y_axis_label="Demand (MW)",
        tools="pan,wheel_zoom,box_zoom,reset,hover",
    )
    _src = ColumnDataSource(agg)
    p_unc_bokeh.varea(
        x="time",
        y1="min_demand",
        y2="max_demand",
        source=_src,
        fill_color="#1A73E8",
        fill_alpha=0.22,
        legend_label="min–max band",
    )
    for _scen in scenarios:
        _s = week[week["scenario"] == _scen]
        p_unc_bokeh.line(
            _s["time"], _s["demand"], line_width=1, color="#64646488"
        )
    p_unc_bokeh.line(
        x="time",
        y="mean_demand",
        source=_src,
        line_width=2.5,
        color="#1A73E8",
        legend_label="mean",
    )
    p_unc_bokeh.legend.click_policy = "mute"
    p_unc_bokeh.add_layout(p_unc_bokeh.legend[0], "right")
    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), p_unc_bokeh])
    return


if __name__ == "__main__":
    app.run()
