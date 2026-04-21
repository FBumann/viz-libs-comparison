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

    # Scale-up escape hatch 1: lift marimo's 8 MB output cap by mutating the
    # live runtime config. `pyproject.toml` and `os.environ` both fail to
    # reach the Pyodide context at export time — direct mutation is the only
    # path that works in WASM.
    from marimo._runtime.context import ContextNotInitializedError, get_context

    try:
        get_context().marimo_config["runtime"]["output_max_bytes"] = 100_000_000
    except ContextNotInitializedError:
        pass

    import io
    import time

    import altair as alt
    import marimo as mo
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.io as pio
    from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool, LinearAxis, Range1d
    from bokeh.plotting import figure

    # Scale-up escape hatch 2: load plotly.js from CDN instead of inlining
    # it (~3 MB saved per figure).
    pio.renderers.default = "notebook_connected"

    # Scale-up escape hatch 3: Altair's default transformer refuses >20k
    # rows (`MaxRowsError`). The Altair-recommended fix is VegaFusion, which
    # ships a Rust native extension unavailable in Pyodide. Fall back to
    # embedding the full dataset in the Vega-Lite spec.
    alt.data_transformers.enable("default", max_rows=None)


@app.cell
def _():
    mo.md(
        """
        &larr; [Home](../../index.html)

        # 03 — Performance at full-year scale

        Chapter 01 rendered one week of dispatch. This chapter renders the
        **same plot** at the full 8,760-hour annual resolution — one scenario,
        one period, every hour of the year. The point isn't to learn something
        new about the data; it's to see **how each library copes with 52× more
        points** and what it cost to get there.

        ## Escape hatches applied (see the setup cell)

        - **marimo** — output cap raised from 8 MB to 100 MB at runtime via
          `get_context().marimo_config[...]`. Without this, plot cells emit
          `Your output is too large`.
        - **Plotly** — `pio.renderers.default = "notebook_connected"` loads
          plotly.js from CDN, trimming ~3 MB per figure.
        - **Altair** — `data_transformers.enable("default", max_rows=None)`
          removes the hard-coded 20,000-row limit. The Altair-recommended
          transformer (VegaFusion) can't be used in Pyodide because it ships
          a Rust native extension.
        - **Bokeh** — nothing special; canvas rendering handles raw arrays.

        ## What's being measured

        The `Python build` number above each plot is the time spent
        constructing the figure/spec in Python. The bigger costs —
        JSON-to-DOM parsing, first render, zoom/pan latency — happen in the
        browser after this notebook finishes executing. Watch for them as
        you interact.

        | Dimension | Plotly | Altair | Bokeh |
        |---|---|---|---|
        | Python build time for 8,760 × 5 flows | expected modest (a few dozen ms; main work is trace construction) | expected moderate (Altair's Python API builds a spec dict; volume shows in serialization) | expected modest (ColumnDataSource is just a numpy wrapper) |
        | First render in browser | heavy — 60k+ point JSON spec to parse, then SVG/canvas paint | heaviest — Vega-Lite re-serializes then processes, then Vega renders | lightest — canvas draws raw arrays directly |
        | Zoom / pan latency | noticeable on big stacks (recompute) | similar to Plotly, sometimes slower on transforms | smoothest |
        | Hover responsiveness | fine (sparse hit-testing) | degrades at this scale (per-row hover work) | fine (manually configured vline hover) |
        | Exported HTML size contribution | ~8-10 MB (data + plotly.js CDN stub) | ~10-15 MB (data embedded in Vega spec + deps) | ~2-5 MB (binary-ish ColumnDataSource serialization) |
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
    year = df_full[
        (df_full["scenario"] == "baseline") & (df_full["period"] == 2030)
    ].reset_index(drop=True)

    year_ts = year.drop_duplicates(subset="time")[
        ["time", "demand", "storage_soc"]
    ].reset_index(drop=True)

    year_stacked = year.assign(
        power=lambda d: d["generation"].where(d["flow"] != "batt_charge", -d["generation"])
    )
    year
    return year, year_stacked, year_ts


@app.cell
def _():
    mo.md("### Plotly")
    return


@app.cell
def _(year, year_ts):
    _t0 = time.perf_counter()

    _colors = {
        "solar": "#F4B400",
        "wind": "#1A73E8",
        "gas": "#616161",
        "batt_discharge": "#34A853",
        "batt_charge": "#EA4335",
    }

    fig_perf_plotly = go.Figure()
    for _flow in ["solar", "wind", "gas", "batt_discharge"]:
        _sub = year[year["flow"] == _flow]
        fig_perf_plotly.add_trace(
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
    _ch = year[year["flow"] == "batt_charge"]
    fig_perf_plotly.add_trace(
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
    fig_perf_plotly.add_trace(
        go.Scatter(
            x=year_ts["time"],
            y=year_ts["demand"],
            mode="lines",
            name="demand",
            line={"color": "black", "width": 1, "dash": "dot", "shape": "hv"},
        )
    )
    fig_perf_plotly.add_trace(
        go.Scatter(
            x=year_ts["time"],
            y=year_ts["storage_soc"],
            mode="lines",
            name="SoC",
            line={"color": "purple", "width": 1, "shape": "hv"},
            yaxis="y2",
        )
    )
    fig_perf_plotly.update_layout(
        yaxis={"title": "Power (MW)"},
        yaxis2={"title": "SoC (MWh)", "overlaying": "y", "side": "right"},
        hovermode="x unified",
    )

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), fig_perf_plotly])
    return


@app.cell
def _():
    mo.md("### Altair")
    return


@app.cell
def _(year_stacked, year_ts):
    _t0 = time.perf_counter()

    _domain = ["solar", "wind", "gas", "batt_discharge", "batt_charge", "demand", "SoC"]
    _range = ["#F4B400", "#1A73E8", "#616161", "#34A853", "#EA4335", "#000000", "purple"]
    _color = alt.Color(
        "flow:N", scale=alt.Scale(domain=_domain, range=_range), legend=alt.Legend(title=None)
    )

    _area = (
        alt.Chart(year_stacked)
        .mark_area(interpolate="step-after")
        .encode(
            x="time:T",
            y=alt.Y("power:Q").stack("zero").title("Power (MW)"),
            color=_color,
        )
    )
    _demand = (
        alt.Chart(year_ts.assign(flow="demand"))
        .mark_line(strokeDash=[4, 2], strokeWidth=1, interpolate="step-after")
        .encode(x="time:T", y="demand:Q", color=_color)
    )
    _soc = (
        alt.Chart(year_ts.assign(flow="SoC"))
        .mark_line(strokeWidth=1, interpolate="step-after")
        .encode(
            x="time:T",
            y=alt.Y("storage_soc:Q").title("SoC (MWh)"),
            color=_color,
        )
    )
    chart_perf_altair = (
        alt.layer(_area + _demand, _soc)
        .resolve_scale(y="independent")
        .properties(width=720, height=380)
        .interactive()
    )

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), chart_perf_altair])
    return


@app.cell
def _():
    mo.md("### Bokeh")
    return


@app.cell
def _(year_stacked, year_ts):
    _t0 = time.perf_counter()

    _wide = year_stacked.pivot_table(index="time", columns="flow", values="power").reset_index()
    _wide["demand"] = year_ts["demand"].to_numpy()
    _wide["soc"] = year_ts["storage_soc"].to_numpy()
    _wide["delta_ms"] = _wide["time"].diff().shift(-1).dt.total_seconds() * 1000
    _wide["delta_ms"] = _wide["delta_ms"].fillna(_wide["delta_ms"].median())
    _wide["time_center"] = _wide["time"] + pd.to_timedelta(_wide["delta_ms"] / 2, unit="ms")
    _source = ColumnDataSource(_wide)

    p_perf_bokeh = figure(
        x_axis_type="datetime",
        width=720,
        height=380,
        y_axis_label="Power (MW)",
        tools="pan,wheel_zoom,box_zoom,reset",
    )
    p_perf_bokeh.add_tools(CrosshairTool(dimensions="height"))

    _positive_flows = ["solar", "wind", "gas", "batt_discharge"]
    _positive_colors = ["#F4B400", "#1A73E8", "#616161", "#34A853"]
    p_perf_bokeh.vbar_stack(
        stackers=_positive_flows,
        x="time_center",
        width="delta_ms",
        source=_source,
        color=_positive_colors,
        legend_label=_positive_flows,
    )
    p_perf_bokeh.vbar(
        x="time_center",
        top=0,
        bottom="batt_charge",
        width="delta_ms",
        source=_source,
        color="#EA4335",
        legend_label="batt_charge",
    )
    _demand_r = p_perf_bokeh.step(
        x="time",
        y="demand",
        source=_source,
        color="black",
        line_width=1,
        line_dash="dotted",
        mode="after",
        legend_label="demand",
    )
    p_perf_bokeh.add_tools(
        HoverTool(
            renderers=[_demand_r],
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

    _soc_min = year_ts["storage_soc"].min()
    _soc_max = year_ts["storage_soc"].max()
    p_perf_bokeh.extra_y_ranges = {
        "soc_axis": Range1d(start=_soc_min - 5, end=_soc_max + 5)
    }
    p_perf_bokeh.add_layout(
        LinearAxis(y_range_name="soc_axis", axis_label="SoC (MWh)"), "right"
    )
    p_perf_bokeh.step(
        x="time",
        y="soc",
        source=_source,
        color="purple",
        line_width=1,
        mode="after",
        y_range_name="soc_axis",
        legend_label="SoC",
    )

    p_perf_bokeh.legend.click_policy = "mute"
    p_perf_bokeh.add_layout(p_perf_bokeh.legend[0], "right")

    _elapsed = (time.perf_counter() - _t0) * 1000
    mo.vstack([mo.md(f"_Python build: **{_elapsed:.1f} ms**_"), p_perf_bokeh])
    return


if __name__ == "__main__":
    app.run()
