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
    from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool, LinearAxis, Range1d
    from bokeh.plotting import figure


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 01 — Dispatch over one week

        One of the most common outputs of an energy-system optimization is an
        **hourly dispatch schedule**: which generators run, how much storage
        charges and discharges, how demand is met. This chapter takes such a
        dispatch (synthetic, shaped like a `flixopt` `flow_system.solution`)
        and asks: *"How does each library let you show one week of system
        operation?"*

        The source is a long-form DataFrame with columns
        `scenario, period, flow, time, generation, demand, storage_soc, capacity`,
        pre-built by `scripts/build_data.py` and shipped as a parquet. We
        filter to one scenario (`baseline`), one period (`2030`), and a
        summer week where the battery cycles visibly.

        ## What the plot should do

        - Stacked area of supply flows (solar, wind, gas, batt_discharge) **above zero**
        - Battery charge flipped **below zero**
        - Demand overlaid as a dotted line
        - Battery state-of-charge on a **secondary y-axis**
        - Interactive: hover, zoom, pan, legend-click to toggle series
        - Toggling a series **restacks** so the remaining ones fill the freed space
        - Unified hover — all values at the cursor's time shown together

        ## Where the libraries differ

        ✅ = does what we want out of the box.
        ⚠️ = works, but needed a specific non-default pattern.
        ❌ = doesn't support / not implemented in this chapter.

        Rows where all three are ✅ (positive stacking, demand-line overlay,
        render performance at this size) are omitted — they aren't
        differentiating at 168 points.

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Signed stacking (charge below zero) | ⚠️ `px.area` mis-handles mixed signs; drop to `go.Scatter` + extra `fill='tozeroy'` trace | ✅ `stack('zero')` handles both sides | ⚠️ separate `varea` call for charge (two renderers) |
        | Step-shaped area (values held across the timestep) | ✅ `line_shape='hv'` on each trace; handles **irregular** timesteps by construction | ✅ `mark_area(interpolate='step-after')`; handles **irregular** timesteps by construction | ⚠️ no built-in step-area — use `vbar_stack` + the `step` glyph. Irregular timesteps need a per-row `width` column (`time.diff()` → ms) and a per-row centre (`time + width/2`) instead of a hardcoded hourly width |
        | Secondary y-axis | ✅ `yaxis='y2'` + `overlaying='y'` | ✅ `resolve_scale(y='independent')` | ✅ `extra_y_ranges` + `LinearAxis(..., 'right')` |
        | Unified cross-series hover | ✅ `hovermode='x unified'` | ⚠️ needs wide-form pivot + `selection_point(nearest=True)` + invisible selectors + a rule layer with consolidated tooltip | ⚠️ works with `CrosshairTool` + `HoverTool(renderers=[anchor], mode='vline')` — a few moving parts |
        | Legend click to toggle | ✅ native | ⚠️ `selection_point` + `transform_filter` on every layer | ✅ `click_policy='mute'` |
        | Restack on toggle | ✅ native | ✅ via `transform_filter` (rows drop out, Vega recomputes the stack before rendering) | ❌ `varea_stack` takes a fixed list of stackers computed at render time; toggling means changing the list or recomputing `cumsum` from the visible subset — a `CustomJS` callback in static export, a Python callback with a Bokeh server (not available in WASM) |
        | Shared legend across area + lines | ✅ automatic | ⚠️ explicit color scale with `domain` / `range` on every layer | ✅ automatic |
        | **Interactive latency** | ⚠️ noticeable lag on legend click — stack recomputes and animates | ✅ snappy — the filter just drops rows before the mark renders | ✅ snappy — mute is an alpha toggle, no re-layout |
        | **Layout pitfalls** | ⚠️ legend can overlap the secondary y-axis labels at small widths — have to manually push the legend or shrink the right margin | ✅ clean spacing by default; axis + legend coexist | ⚠️ toolbar visible by default; legend is in-plot until you `add_layout(legend[0], "right")` |
        | **Verbosity** (plotting cell, LOC) | ~45 | ~55 | ~70 |
        | **Customization ceiling** (how far this can be pushed) | ✅ high — full `go.Figure` API; Python-side callbacks via `FigureWidget`. *Still lots untouched here: annotations, range-sliders, crossfilter.* | ✅ high — can drop to raw Vega-Lite / Vega for anything the Python API can't express. *Vega-Lite supports brushing, animations, multi-view dashboards.* | ✅ highest — `CustomJS` gives arbitrary browser-side JS, plus the widget / server model for Python-side logic. *Restack-on-toggle would be one `CustomJS` away; full dashboards are native.* |
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
    week = df_full[
        (df_full["scenario"] == "baseline")
        & (df_full["period"] == 2030)
        & (df_full["time"] >= pd.Timestamp("2030-07-14"))
        & (df_full["time"] <= pd.Timestamp("2030-07-20 23:00"))
    ].reset_index(drop=True)

    week_ts = week.drop_duplicates(subset="time")[
        ["time", "demand", "storage_soc"]
    ].reset_index(drop=True)

    week_stacked = week.assign(
        power=lambda d: d["generation"].where(d["flow"] != "batt_charge", -d["generation"])
    )
    week
    return week, week_stacked, week_ts


@app.cell
def _():
    mo.md(
        """
        ## Dispatch over the week

        Stacked area of generation flows. Battery **charge** is flipped negative
        so it sits below zero. Demand is overlaid as a dotted line. Battery
        **state of charge** (SoC) is plotted on a secondary y-axis.
        """
    )
    return


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(week, week_ts):
    _t0 = time.perf_counter()
    _colors = {
        "solar": "#F4B400",
        "wind": "#1A73E8",
        "gas": "#616161",
        "batt_discharge": "#34A853",
        "batt_charge": "#EA4335",
    }

    fig_dispatch_plotly = go.Figure()

    for _flow in ["solar", "wind", "gas", "batt_discharge"]:
        _sub = week[week["flow"] == _flow]
        fig_dispatch_plotly.add_trace(
            go.Scatter(
                x=_sub["time"],
                y=_sub["generation"],
                name=_flow,
                stackgroup="supply",
                mode="none",
                line_shape="hv",
                fillcolor=_colors[_flow],
            )
        )

    _ch = week[week["flow"] == "batt_charge"]
    fig_dispatch_plotly.add_trace(
        go.Scatter(
            x=_ch["time"],
            y=-_ch["generation"],
            name="batt_charge",
            fill="tozeroy",
            mode="none",
            line_shape="hv",
            fillcolor=_colors["batt_charge"],
        )
    )
    fig_dispatch_plotly.add_trace(
        go.Scatter(
            x=week_ts["time"],
            y=week_ts["demand"],
            mode="lines",
            name="demand",
            line={"color": "black", "width": 2, "dash": "dot", "shape": "hv"},
        )
    )
    fig_dispatch_plotly.add_trace(
        go.Scatter(
            x=week_ts["time"],
            y=week_ts["storage_soc"],
            mode="lines",
            name="SoC",
            line={"color": "purple", "width": 2, "shape": "hv"},
            yaxis="y2",
        )
    )
    fig_dispatch_plotly.update_layout(
        yaxis={"title": "Power (MW)"},
        yaxis2={"title": "SoC (MWh)", "overlaying": "y", "side": "right"},
        hovermode="x unified",
    )
    _elapsed_plotly = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_plotly:.1f} ms**_"), fig_dispatch_plotly]
    )
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(week, week_stacked, week_ts):
    _t0 = time.perf_counter()
    _domain = ["solar", "wind", "gas", "batt_discharge", "batt_charge", "demand", "SoC"]
    _range = ["#F4B400", "#1A73E8", "#616161", "#34A853", "#EA4335", "#000000", "purple"]
    _color = alt.Color(
        "flow:N", scale=alt.Scale(domain=_domain, range=_range), legend=alt.Legend(title=None)
    )

    _legend_sel = alt.selection_point(
        fields=["flow"],
        bind="legend",
        toggle="true",
        value=[{"flow": f} for f in _domain],
    )

    _area = (
        alt.Chart(week_stacked)
        .mark_area(interpolate="step-after")
        .encode(
            x="time:T",
            y=alt.Y("power:Q").stack("zero").title("Power (MW)"),
            color=_color,
        )
        .transform_filter(_legend_sel)
        .add_params(_legend_sel)
    )
    _demand = (
        alt.Chart(week_ts.assign(flow="demand"))
        .mark_line(strokeDash=[4, 2], strokeWidth=2, interpolate="step-after")
        .encode(x="time:T", y="demand:Q", color=_color)
        .transform_filter(_legend_sel)
    )
    _soc = (
        alt.Chart(week_ts.assign(flow="SoC"))
        .mark_line(strokeWidth=2, interpolate="step-after")
        .encode(x="time:T", y=alt.Y("storage_soc:Q").title("SoC (MWh)"), color=_color)
        .transform_filter(_legend_sel)
    )

    # Unified hover: wide-form data + nearest-time selection + rule with all fields
    _wide_alt = week.pivot_table(index="time", columns="flow", values="generation").reset_index()
    _wide_alt["demand"] = week_ts["demand"].to_numpy()
    _wide_alt["storage_soc"] = week_ts["storage_soc"].to_numpy()

    _nearest = alt.selection_point(
        nearest=True, on="pointerover", fields=["time"], empty=False
    )
    _selectors = (
        alt.Chart(_wide_alt)
        .mark_rule(opacity=0)
        .encode(
            x="time:T",
            tooltip=[
                alt.Tooltip("time:T", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("solar:Q", format=".1f"),
                alt.Tooltip("wind:Q", format=".1f"),
                alt.Tooltip("gas:Q", format=".1f"),
                alt.Tooltip("batt_discharge:Q", format=".1f"),
                alt.Tooltip("batt_charge:Q", format=".1f"),
                alt.Tooltip("demand:Q", format=".1f"),
                alt.Tooltip("storage_soc:Q", format=".1f"),
            ],
        )
        .add_params(_nearest)
    )
    _rule = (
        alt.Chart(_wide_alt)
        .mark_rule(color="#888")
        .encode(
            x="time:T",
            opacity=alt.condition(_nearest, alt.value(0.5), alt.value(0)),
        )
    )

    chart_dispatch_altair = (
        alt.layer(_area + _demand, _soc, _selectors, _rule)
        .resolve_scale(y="independent")
        .properties(width=720, height=380)
        .interactive()
    )
    _elapsed_altair = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_altair:.1f} ms**_"), chart_dispatch_altair]
    )
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(week_stacked, week_ts):
    _t0 = time.perf_counter()
    _wide = week_stacked.pivot_table(index="time", columns="flow", values="power").reset_index()
    _wide["demand"] = week_ts["demand"].to_numpy()
    _wide["soc"] = week_ts["storage_soc"].to_numpy()
    # Per-row bar width from the actual time step — works for irregular spacing too.
    _wide["delta_ms"] = _wide["time"].diff().shift(-1).dt.total_seconds() * 1000
    _wide["delta_ms"] = _wide["delta_ms"].fillna(_wide["delta_ms"].median())
    _wide["time_center"] = _wide["time"] + pd.to_timedelta(_wide["delta_ms"] / 2, unit="ms")
    _source = ColumnDataSource(_wide)

    p_dispatch_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=380,
        y_axis_label="Power (MW)",
        tools="pan,wheel_zoom,box_zoom,reset",
    )
    p_dispatch_bokeh.add_tools(CrosshairTool(dimensions="height"))
    _positive_flows = ["solar", "wind", "gas", "batt_discharge"]
    _positive_colors = ["#F4B400", "#1A73E8", "#616161", "#34A853"]
    p_dispatch_bokeh.vbar_stack(
        stackers=_positive_flows,
        x="time_center",
        width="delta_ms",
        source=_source,
        color=_positive_colors,
        legend_label=_positive_flows,
    )
    p_dispatch_bokeh.vbar(
        x="time_center",
        top=0,
        bottom="batt_charge",
        width="delta_ms",
        source=_source,
        color="#EA4335",
        legend_label="batt_charge",
    )
    _demand_renderer = p_dispatch_bokeh.step(
        x="time",
        y="demand",
        source=_source,
        color="black",
        line_width=2,
        line_dash="dotted",
        mode="after",
        legend_label="demand",
    )
    p_dispatch_bokeh.add_tools(
        HoverTool(
            renderers=[_demand_renderer],
            mode="vline",
            tooltips=[
                ("time", "@time{%F %H:%M}"),
                ("solar", "@solar{0.1} MW"),
                ("wind", "@wind{0.1} MW"),
                ("gas", "@gas{0.1} MW"),
                ("batt_discharge", "@batt_discharge{0.1} MW"),
                ("batt_charge", "@batt_charge{0.1} MW"),
                ("demand", "@demand{0.1} MW"),
                ("SoC", "@soc{0.1} MWh"),
            ],
            formatters={"@time": "datetime"},
        )
    )

    _soc_min = week_ts["storage_soc"].min()
    _soc_max = week_ts["storage_soc"].max()
    p_dispatch_bokeh.extra_y_ranges = {
        "soc_axis": Range1d(start=_soc_min - 5, end=_soc_max + 5)
    }
    p_dispatch_bokeh.add_layout(
        LinearAxis(y_range_name="soc_axis", axis_label="SoC (MWh)"), "right"
    )
    p_dispatch_bokeh.step(
        x="time",
        y="soc",
        source=_source,
        color="purple",
        line_width=2,
        mode="after",
        y_range_name="soc_axis",
        legend_label="SoC",
    )

    p_dispatch_bokeh.legend.click_policy = "mute"
    p_dispatch_bokeh.add_layout(p_dispatch_bokeh.legend[0], "right")
    _elapsed_bokeh = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_bokeh:.1f} ms**_"), p_dispatch_bokeh]
    )
    return


if __name__ == "__main__":
    app.run()
