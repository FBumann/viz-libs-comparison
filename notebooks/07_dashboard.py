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
    from bokeh.layouts import column as bk_column
    from bokeh.models import ColumnDataSource, CustomJS, Select
    from bokeh.plotting import figure


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 07 — Dashboard composition

        A mini-dashboard: a **scenario dropdown** drives two plots at once —
        a dispatch stacked-area on top and a per-flow capacity bar chart
        below. It's the smallest useful "app" pattern and exercises how each
        library ties a widget to several views.

        - **Altair** uses `alt.binding_select` → `selection_point` →
          `transform_filter`. One selection, referenced by both charts; the
          widget is embedded in the Vega-Lite spec.
        - **Plotly** has `updatemenus` baked into figures, but they're
          awkward for multi-plot coordination. The marimo-idiomatic path is
          `mo.ui.dropdown` — its `.value` is a reactive handle; cells that
          depend on it re-run on change, rebuilding both figures in Python.
        - **Bokeh** uses a `Select` widget plus `CustomJS` callbacks that
          filter a shared `ColumnDataSource` and push changes to both plots.

        ## What the plot should do

        - Scenario dropdown with 5 options
        - Dispatch stacked-area for the selected scenario (one week)
        - Total generation by flow (bar chart) for the same scenario
        - Both plots update instantly when the dropdown changes

        ## Where the libraries differ

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Native widget-in-chart | ⚠️ `updatemenus` exist but tie to trace visibility, not data filters — awkward for multi-plot coordination | ✅ `alt.binding_select` + `selection_point` + `transform_filter` — fully declarative | ✅ `Select` widget from `bokeh.models` — a real widget sitting next to the plots |
        | Cross-widget cross-plot coordination | via marimo (`mo.ui.dropdown` → Python re-runs cells) | via one shared Vega selection referenced by both charts | via one `CustomJS` callback attached to the widget that updates both sources |
        | Update latency | Python round-trip — mild lag | sub-frame (Vega signal) | sub-frame (CustomJS runs in browser) |
        | Requires a Python kernel for the widget | yes (via marimo, but runs in Pyodide in WASM — still Python) | no — pure browser | no — pure browser |
        | Code volume | ~20 lines (widget + two figures rebuild) | ~15 lines (one selection, two charts with filter) | ~40 lines (Select + two sources + CustomJS body) |
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
        (df_full["period"] == 2030)
        & (df_full["time"] >= pd.Timestamp("2030-07-14"))
        & (df_full["time"] <= pd.Timestamp("2030-07-20 23:00"))
    ].reset_index(drop=True)
    week_stacked = week.assign(
        power=lambda d: d["generation"].where(d["flow"] != "batt_charge", -d["generation"])
    )
    # Per (scenario, flow) totals over the week — for the capacity/energy bar
    totals = (
        week.groupby(["scenario", "flow"])["generation"]
        .sum()
        .reset_index()
        .rename(columns={"generation": "total_mwh"})
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
    return colors_map, scenarios, totals, week, week_stacked


@app.cell
def _():
    mo.md("### Altair — `binding_select`")
    return


@app.cell
def _(colors_map, scenarios, totals, week_stacked):
    _t0 = time.perf_counter()

    _domain = ["solar", "wind", "gas", "batt_discharge", "batt_charge"]
    _range = [colors_map[f] for f in _domain]
    _color = alt.Color(
        "flow:N", scale=alt.Scale(domain=_domain, range=_range), legend=alt.Legend(title=None)
    )

    _sel = alt.selection_point(
        name="scenario_sel",
        fields=["scenario"],
        bind=alt.binding_select(options=scenarios, name="Scenario: "),
        value=[{"scenario": "baseline"}],
    )

    _dispatch = (
        alt.Chart(week_stacked)
        .mark_area(interpolate="step-after")
        .encode(
            x=alt.X("time:T").title(None),
            y=alt.Y("power:Q").stack("zero").title("Power (MW)"),
            color=_color,
        )
        .transform_filter(_sel)
        .add_params(_sel)
        .properties(width=720, height=280)
    )
    _bars = (
        alt.Chart(totals)
        .mark_bar()
        .encode(
            x=alt.X("flow:N", sort=_domain).title(None),
            y=alt.Y("total_mwh:Q").title("Total MWh"),
            color=_color,
        )
        .transform_filter(_sel)
        .properties(width=720, height=180)
    )
    chart_dash_altair = _dispatch & _bars

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_dash_altair])
    return


@app.cell
def _():
    mo.md("### Plotly — via `mo.ui.dropdown` (marimo reactivity)")
    return


@app.cell
def _(scenarios):
    scenario_plotly = mo.ui.dropdown(
        options=scenarios, value="baseline", label="Scenario"
    )
    scenario_plotly
    return (scenario_plotly,)


@app.cell
def _(colors_map, scenario_plotly, totals, week):
    _t0 = time.perf_counter()
    _scen = scenario_plotly.value
    _sub = week[week["scenario"] == _scen]
    _tot = totals[totals["scenario"] == _scen]

    fig_disp_plotly = go.Figure()
    for _flow in ["solar", "wind", "gas", "batt_discharge"]:
        _f = _sub[_sub["flow"] == _flow]
        fig_disp_plotly.add_trace(
            go.Scatter(
                x=_f["time"],
                y=_f["generation"],
                name=_flow,
                stackgroup="supply",
                mode="none",
                line_shape="hv",
                fillcolor=colors_map[_flow],
            )
        )
    _ch = _sub[_sub["flow"] == "batt_charge"]
    fig_disp_plotly.add_trace(
        go.Scatter(
            x=_ch["time"],
            y=-_ch["generation"],
            name="batt_charge",
            fill="tozeroy",
            mode="none",
            line_shape="hv",
            fillcolor=colors_map["batt_charge"],
        )
    )
    fig_disp_plotly.update_layout(yaxis_title="Power (MW)", height=280, hovermode="x unified")

    fig_bar_plotly = go.Figure(
        data=go.Bar(
            x=_tot["flow"],
            y=_tot["total_mwh"],
            marker_color=[colors_map[f] for f in _tot["flow"]],
        )
    )
    fig_bar_plotly.update_layout(yaxis_title="Total MWh", height=200)

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack(
        [mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), fig_disp_plotly, fig_bar_plotly]
    )
    return


@app.cell
def _():
    mo.md("### Bokeh — `Select` widget + `CustomJS`")
    return


@app.cell
def _(colors_map, scenarios, totals, week):
    _t0 = time.perf_counter()

    _flows_pos = ["solar", "wind", "gas", "batt_discharge"]
    _initial = "baseline"

    # Long-form data indexed by scenario for fast JS filtering
    _week_records = {
        _s: week[week["scenario"] == _s].to_dict(orient="list") for _s in scenarios
    }
    _tot_records = {
        _s: totals[totals["scenario"] == _s].to_dict(orient="list") for _s in scenarios
    }

    # Wide-form sources used by the plots, initialised to baseline
    _initial_wide = (
        week[week["scenario"] == _initial]
        .assign(power=lambda d: d["generation"].where(d["flow"] != "batt_charge", -d["generation"]))
        .pivot_table(index="time", columns="flow", values="power")
        .reset_index()
    )
    _initial_wide["delta_ms"] = (
        _initial_wide["time"].diff().shift(-1).dt.total_seconds() * 1000
    )
    _initial_wide["delta_ms"] = _initial_wide["delta_ms"].fillna(
        _initial_wide["delta_ms"].median()
    )
    _initial_wide["time_center"] = _initial_wide["time"] + pd.to_timedelta(
        _initial_wide["delta_ms"] / 2, unit="ms"
    )
    _dispatch_source = ColumnDataSource(_initial_wide)

    _bar_source = ColumnDataSource(totals[totals["scenario"] == _initial])

    p_disp_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=260,
        y_axis_label="Power (MW)",
        tools="pan,wheel_zoom,reset",
    )
    p_disp_bokeh.vbar_stack(
        stackers=_flows_pos,
        x="time_center",
        width="delta_ms",
        source=_dispatch_source,
        color=[colors_map[f] for f in _flows_pos],
        legend_label=_flows_pos,
    )
    p_disp_bokeh.vbar(
        x="time_center",
        top=0,
        bottom="batt_charge",
        width="delta_ms",
        source=_dispatch_source,
        color=colors_map["batt_charge"],
        legend_label="batt_charge",
    )
    p_disp_bokeh.legend.click_policy = "mute"
    p_disp_bokeh.add_layout(p_disp_bokeh.legend[0], "right")

    _flow_order = list(totals["flow"].unique())
    p_bar_bokeh = figure(
        x_range=_flow_order,
        width=720,
        height=200,
        y_axis_label="Total MWh",
        tools="",
    )
    p_bar_bokeh.vbar(
        x="flow", top="total_mwh", width=0.7, source=_bar_source,
        color=[colors_map[f] for f in _flow_order],
    )

    _select = Select(title="Scenario", value=_initial, options=scenarios, width=200)
    _callback = CustomJS(
        args={
            "disp_src": _dispatch_source,
            "bar_src": _bar_source,
            "week_records": _week_records,
            "tot_records": _tot_records,
        },
        code="""
        const scen = cb_obj.value;
        const week = week_records[scen];
        const tot = tot_records[scen];

        // Rebuild wide-form power dict: time, solar, wind, gas, batt_discharge, batt_charge
        const flows = ["solar","wind","gas","batt_discharge","batt_charge"];
        const times_seen = [];
        const wide = {};
        for (const f of flows) wide[f] = [];
        for (let i = 0; i < week.time.length; i++) {
            const t = week.time[i];
            const f = week.flow[i];
            const g = week.generation[i];
            if (times_seen.indexOf(t) === -1) times_seen.push(t);
            // place in row for t
        }
        // Build a row per timestamp
        const rows = {};
        for (const t of times_seen) {
            rows[t] = {};
            for (const f of flows) rows[t][f] = 0;
        }
        for (let i = 0; i < week.time.length; i++) {
            const t = week.time[i];
            const f = week.flow[i];
            const g = week.generation[i];
            rows[t][f] = f === "batt_charge" ? -g : g;
        }
        const sorted_times = Object.keys(rows).map(Number).sort((a,b)=>a-b);
        const time_center = [];
        const delta_ms = [];
        for (let i = 0; i < sorted_times.length; i++) {
            const t = sorted_times[i];
            const next = i+1 < sorted_times.length ? sorted_times[i+1] : t + 3600000;
            const d = next - t;
            delta_ms.push(d);
            time_center.push(t + d/2);
        }
        const out = {"time": sorted_times, "time_center": time_center, "delta_ms": delta_ms};
        for (const f of flows) out[f] = sorted_times.map(t => rows[t][f]);
        disp_src.data = out;
        disp_src.change.emit();

        bar_src.data = {"scenario": tot.scenario, "flow": tot.flow, "total_mwh": tot.total_mwh};
        bar_src.change.emit();
        """,
    )
    _select.js_on_change("value", _callback)

    chart_dash_bokeh = bk_column(_select, p_disp_bokeh, p_bar_bokeh)

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_dash_bokeh])
    return


if __name__ == "__main__":
    app.run()
