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


@app.cell
def _():
    import warnings

    warnings.filterwarnings("ignore", message=".*narwhals.*")

    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
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
        """
    )
    return


@app.cell
async def _(mo):
    import io

    import pandas as pd

    _path = str(mo.notebook_location() / "public" / "dispatch.parquet")
    if _path.startswith(("http://", "https://")):
        from pyodide.http import pyfetch

        _resp = await pyfetch(_path)
        df_full = pd.read_parquet(io.BytesIO(await _resp.bytes()))
    else:
        df_full = pd.read_parquet(_path)
    df_full
    return (df_full, pd)


@app.cell
def _(df_full, pd):
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
def _(mo):
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
def _(mo):
    mo.md("### Plotly")
    return


@app.cell
def _(week, week_ts):
    import plotly.graph_objects as go

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
            fillcolor=_colors["batt_charge"],
        )
    )
    fig_dispatch_plotly.add_trace(
        go.Scatter(
            x=week_ts["time"],
            y=week_ts["demand"],
            mode="lines",
            name="demand",
            line={"color": "black", "width": 2, "dash": "dot"},
        )
    )
    fig_dispatch_plotly.add_trace(
        go.Scatter(
            x=week_ts["time"],
            y=week_ts["storage_soc"],
            mode="lines",
            name="SoC",
            line={"color": "purple", "width": 2},
            yaxis="y2",
        )
    )
    fig_dispatch_plotly.update_layout(
        yaxis={"title": "Power (MW)"},
        yaxis2={"title": "SoC (MWh)", "overlaying": "y", "side": "right"},
        hovermode="x unified",
    )
    fig_dispatch_plotly
    return


@app.cell
def _(mo):
    mo.md("### Altair")
    return


@app.cell
def _(week_stacked, week_ts):
    import altair as alt

    _domain = ["solar", "wind", "gas", "batt_discharge", "batt_charge", "demand", "SoC"]
    _range = ["#F4B400", "#1A73E8", "#616161", "#34A853", "#EA4335", "#000000", "purple"]
    _color = alt.Color(
        "flow:N", scale=alt.Scale(domain=_domain, range=_range), legend=alt.Legend(title=None)
    )

    _all_flows = ["solar", "wind", "gas", "batt_discharge", "batt_charge"]
    _legend_sel = alt.selection_point(
        fields=["flow"],
        bind="legend",
        toggle="true",
        value=[{"flow": f} for f in _all_flows],
    )

    _area = (
        alt.Chart(week_stacked)
        .mark_area()
        .encode(
            x="time:T",
            y=alt.Y("power:Q").stack("zero").title("Power (MW)"),
            color=_color,
            tooltip=[
                alt.Tooltip("time:T", format="%Y-%m-%d %H:%M"),
                "flow:N",
                alt.Tooltip("power:Q", format=".1f"),
            ],
        )
        .transform_filter(_legend_sel)
        .add_params(_legend_sel)
    )
    _demand = (
        alt.Chart(week_ts.assign(flow="demand"))
        .mark_line(strokeDash=[4, 2], strokeWidth=2)
        .encode(
            x="time:T",
            y="demand:Q",
            color=_color,
            tooltip=[alt.Tooltip("time:T"), alt.Tooltip("demand:Q", format=".1f")],
        )
    )
    _soc = (
        alt.Chart(week_ts.assign(flow="SoC"))
        .mark_line(strokeWidth=2)
        .encode(
            x="time:T",
            y=alt.Y("storage_soc:Q").title("SoC (MWh)"),
            color=_color,
            tooltip=[alt.Tooltip("time:T"), alt.Tooltip("storage_soc:Q", format=".1f")],
        )
    )
    chart_dispatch_altair = (
        alt.layer(_area + _demand, _soc)
        .resolve_scale(y="independent")
        .properties(width=720, height=380)
        .interactive()
    )
    chart_dispatch_altair
    return


@app.cell
def _(mo):
    mo.md("### Bokeh")
    return


@app.cell
def _(week_stacked, week_ts):
    from bokeh.models import ColumnDataSource, HoverTool, LinearAxis, Range1d
    from bokeh.plotting import figure

    _wide = week_stacked.pivot_table(index="time", columns="flow", values="power").reset_index()
    _wide["demand"] = week_ts["demand"].to_numpy()
    _wide["soc"] = week_ts["storage_soc"].to_numpy()
    _source = ColumnDataSource(_wide)

    p_dispatch_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=380,
        y_axis_label="Power (MW)",
        tools="pan,wheel_zoom,box_zoom,reset",
    )
    p_dispatch_bokeh.add_tools(
        HoverTool(
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
    _positive_flows = ["solar", "wind", "gas", "batt_discharge"]
    _positive_colors = ["#F4B400", "#1A73E8", "#616161", "#34A853"]
    p_dispatch_bokeh.varea_stack(
        stackers=_positive_flows,
        x="time",
        source=_source,
        color=_positive_colors,
        legend_label=_positive_flows,
    )
    p_dispatch_bokeh.varea(
        x="time",
        y1=0,
        y2="batt_charge",
        source=_source,
        color="#EA4335",
        legend_label="batt_charge",
    )
    p_dispatch_bokeh.line(
        x="time",
        y="demand",
        source=_source,
        color="black",
        line_width=2,
        line_dash="dotted",
        legend_label="demand",
    )

    _soc_min = week_ts["storage_soc"].min()
    _soc_max = week_ts["storage_soc"].max()
    p_dispatch_bokeh.extra_y_ranges = {
        "soc_axis": Range1d(start=_soc_min - 5, end=_soc_max + 5)
    }
    p_dispatch_bokeh.add_layout(
        LinearAxis(y_range_name="soc_axis", axis_label="SoC (MWh)"), "right"
    )
    p_dispatch_bokeh.line(
        x="time",
        y="soc",
        source=_source,
        color="purple",
        line_width=2,
        y_range_name="soc_axis",
        legend_label="SoC",
    )

    p_dispatch_bokeh.legend.click_policy = "mute"
    p_dispatch_bokeh
    return


if __name__ == "__main__":
    app.run()
