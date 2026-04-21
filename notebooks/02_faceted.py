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
    from bokeh.layouts import gridplot
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    from plotly.subplots import make_subplots


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 02 — Scenarios compared via faceting

        Chapter 01 showed one week of one scenario. Real energy-system analysis
        usually asks *"how does the dispatch look across scenarios"* — five
        decarbonisation strategies, three demand assumptions, etc. The natural
        visual is **small multiples**: the same stacked-area plot repeated
        once per scenario.

        This chapter takes the **same week** as chapter 01 (2030-07-14 to
        2030-07-20) but spans all five scenarios. ≈ 4k rows total — well
        under every lib's default cap, so no escape hatches needed. Data
        volume is deliberately modest here — full-year scaling and the
        performance cliff are the subject of the next chapter. SoC is
        dropped (secondary axes add noise when multiplied across 5 facets)
        but demand stays as an overlay so each facet shows whether supply
        meets load.

        ## What the plot should do

        - Five stacked-area plots — one per scenario — laid out as small
          multiples
        - Each facet shows one week of generation (solar, wind, gas,
          batt_discharge above zero; batt_charge below)
        - **Demand** as a dotted-black line overlay in each facet
        - Step-shaped areas (dispatch is held constant each hour)
        - A shared colour scheme and legend across facets
        - Shared x-axis (time) so you can compare at the same date across
          scenarios

        ## Where the libraries differ

        ✅ = does what we want out of the box.
        ⚠️ = works, but needed a specific non-default pattern.
        ❌ = doesn't support / not implemented.

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Faceting API | ⚠️ `make_subplots(cols=5)` + loop building traces per subplot; `px.area` doesn't handle signed stacking so we're already in `go` territory | ✅ `.facet(column='scenario:N')` — one line | ⚠️ manual: build N separate figures in a Python loop, combine with `gridplot`; no native faceting |
        | Shared x-axis across facets | ⚠️ `shared_xaxes='all'` on `make_subplots` — `shared_xaxes=True` actually means "share within columns" and silently does nothing for a single-row layout | ✅ automatic; Altair shares scales across facets by default | ⚠️ explicit: `p.x_range = first_figure.x_range` on every subsequent figure |
        | Shared legend | ⚠️ one legend entry per subplot by default; filter with `showlegend=flow not seen before` | ✅ automatic | ⚠️ each figure has its own legend; you typically hide all but one or use a separate Legend model |
        | Per-facet titles | ✅ `subplot_titles=[...]` | ✅ facet label automatic from field value | ⚠️ set `title=` on each figure in the loop |

        *(Data-volume ceilings — Plotly's JSON payload size, Altair's 20 k-row
        cap, marimo's output cap — are a real concern and get their own
        treatment in the next chapter at full-year resolution.)*
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
    # Same week as chapter 01, but across all five scenarios. Hourly × 5
    # scenarios × 5 flows ≈ 4k rows — comfortably under every default cap.
    # Full-year scaling + escape hatches are the subject of the next chapter.
    week = df_full[
        (df_full["period"] == 2030)
        & (df_full["time"] >= pd.Timestamp("2030-07-14"))
        & (df_full["time"] <= pd.Timestamp("2030-07-20 23:00"))
    ].reset_index(drop=True)
    week_stacked = week.assign(
        power=lambda d: d["generation"].where(d["flow"] != "batt_charge", -d["generation"])
    )
    week_ts = (
        week.drop_duplicates(subset=["scenario", "time"])[["scenario", "time", "demand"]]
        .reset_index(drop=True)
    )
    scenarios = sorted(week["scenario"].unique().tolist())
    colors_map = {
        "solar": "#F4B400",
        "wind": "#1A73E8",
        "gas": "#616161",
        "batt_discharge": "#34A853",
        "batt_charge": "#EA4335",
    }
    week
    return colors_map, scenarios, week, week_stacked, week_ts


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(colors_map, scenarios, week, week_ts):
    _t0 = time.perf_counter()

    fig_faceted_plotly = make_subplots(
        rows=1,
        cols=len(scenarios),
        shared_xaxes="all",
        shared_yaxes="all",
        subplot_titles=scenarios,
        horizontal_spacing=0.02,
    )

    _seen = set()
    for _col_idx, _scen in enumerate(scenarios, start=1):
        _sub = week[week["scenario"] == _scen]
        for _flow in ["solar", "wind", "gas", "batt_discharge"]:
            _data = _sub[_sub["flow"] == _flow]
            fig_faceted_plotly.add_trace(
                go.Scatter(
                    x=_data["time"],
                    y=_data["generation"],
                    name=_flow,
                    stackgroup=f"pos_{_col_idx}",
                    mode="none",
                    line_shape="hv",
                    fillcolor=colors_map[_flow],
                    showlegend=_flow not in _seen,
                    legendgroup=_flow,
                ),
                row=1,
                col=_col_idx,
            )
            _seen.add(_flow)
        _ch = _sub[_sub["flow"] == "batt_charge"]
        fig_faceted_plotly.add_trace(
            go.Scatter(
                x=_ch["time"],
                y=-_ch["generation"],
                name="batt_charge",
                fill="tozeroy",
                mode="none",
                line_shape="hv",
                fillcolor=colors_map["batt_charge"],
                showlegend="batt_charge" not in _seen,
                legendgroup="batt_charge",
            ),
            row=1,
            col=_col_idx,
        )
        _seen.add("batt_charge")
        _d = week_ts[week_ts["scenario"] == _scen]

        fig_faceted_plotly.add_trace(
            go.Scatter(
                x=_d["time"],
                y=_d["demand"],
                name="demand",
                mode="lines",
                line={"color": "black", "width": 1.5, "dash": "dot", "shape": "hv"},
                showlegend="demand" not in _seen,
                legendgroup="demand",
            ),
            row=1,
            col=_col_idx,
        )
        _seen.add("demand")

    fig_faceted_plotly.update_layout(
        height=380,
        width=1200,
        hovermode="x unified",
    )
    fig_faceted_plotly.update_yaxes(title_text="Power (MW)", row=1, col=1)

    _elapsed_plotly = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_plotly:.1f} ms**_"), fig_faceted_plotly]
    )
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(week_stacked, week_ts):
    _t0 = time.perf_counter()

    _domain = ["solar", "wind", "gas", "batt_discharge", "batt_charge", "demand"]
    _range = ["#F4B400", "#1A73E8", "#616161", "#34A853", "#EA4335", "#000000"]
    _color = alt.Color(
        "flow:N",
        scale=alt.Scale(domain=_domain, range=_range),
        legend=alt.Legend(title=None),
    )

    # Facet needs one top-level data source, so fold demand into week_stacked
    # as another flow value; the area and line marks filter on flow.
    _demand_as_flow = week_ts.assign(flow="demand", power=week_ts["demand"])[
        ["scenario", "time", "flow", "power"]
    ]
    week_long = pd.concat(
        [week_stacked[["scenario", "time", "flow", "power"]], _demand_as_flow],
        ignore_index=True,
    )

    _area = (
        alt.Chart(week_long)
        .transform_filter(alt.datum.flow != "demand")
        .mark_area(interpolate="step-after")
        .encode(
            x=alt.X("time:T").title(None),
            y=alt.Y("power:Q").stack("zero").title("Power (MW)"),
            color=_color,
        )
    )
    _demand_line = (
        alt.Chart(week_long)
        .transform_filter(alt.datum.flow == "demand")
        .mark_line(strokeDash=[4, 2], strokeWidth=1.5, interpolate="step-after")
        .encode(x="time:T", y="power:Q", color=_color)
    )
    chart_faceted_altair = (
        (_area + _demand_line)
        .properties(width=220, height=260)
        .facet(column=alt.Column("scenario:N").title(None))
    )

    _elapsed_altair = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_altair:.1f} ms**_"), chart_faceted_altair]
    )
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(colors_map, scenarios, week_stacked, week_ts):
    _t0 = time.perf_counter()

    _figures = []
    _positive_flows = ["solar", "wind", "gas", "batt_discharge"]
    _positive_colors = [colors_map[f] for f in _positive_flows]

    for _i, _scen in enumerate(scenarios):
        _sub = week_stacked[week_stacked["scenario"] == _scen]
        _wide = _sub.pivot_table(index="time", columns="flow", values="power").reset_index()
        _wide["delta_ms"] = _wide["time"].diff().shift(-1).dt.total_seconds() * 1000
        _wide["delta_ms"] = _wide["delta_ms"].fillna(_wide["delta_ms"].median())
        _wide["time_center"] = _wide["time"] + pd.to_timedelta(_wide["delta_ms"] / 2, unit="ms")
        _wide["demand"] = week_ts[week_ts["scenario"] == _scen]["demand"].to_numpy()
        _source = ColumnDataSource(_wide)

        _is_last = _i == len(scenarios) - 1

        def _lbl(_value):  # noqa: B023
            return {"legend_label": _value} if _is_last else {}

        _fig = figure(
            x_axis_type="datetime",
            width=240,
            height=260,
            title=_scen,
            y_axis_label="Power (MW)" if _i == 0 else None,
            tools="pan,wheel_zoom,box_zoom,reset",
        )
        _fig.vbar_stack(
            stackers=_positive_flows,
            x="time_center",
            width="delta_ms",
            source=_source,
            color=_positive_colors,
            **_lbl(_positive_flows),
        )
        _fig.vbar(
            x="time_center",
            top=0,
            bottom="batt_charge",
            width="delta_ms",
            source=_source,
            color=colors_map["batt_charge"],
            **_lbl("batt_charge"),
        )
        _fig.step(
            x="time",
            y="demand",
            source=_source,
            color="black",
            line_width=1.5,
            line_dash="dotted",
            mode="after",
            **_lbl("demand"),
        )
        if _i > 0:
            _fig.x_range = _figures[0].x_range
        if _is_last:
            _fig.legend.click_policy = "mute"
            _fig.add_layout(_fig.legend[0], "right")
        _figures.append(_fig)

    p_faceted_bokeh = gridplot([_figures], toolbar_location="above")

    _elapsed_bokeh = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed_bokeh:.1f} ms**_"), p_faceted_bokeh]
    )
    return


if __name__ == "__main__":
    app.run()
