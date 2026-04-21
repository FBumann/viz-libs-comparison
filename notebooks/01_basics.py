# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas",
#     "numpy",
#     "palmerpenguins",
#     "vega-datasets",
#     "plotly",
#     "altair",
#     "bokeh",
# ]
# ///
import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # 01 — Basics

        Scatter, line, bar, histogram — the plots every library must get right.
        Each section renders the same plot in **Plotly**, **Altair**, and
        **Bokeh**, using each library's idiomatic high-level API.
        """
    )
    return


@app.cell
def _():
    from palmerpenguins import load_penguins
    from vega_datasets import data as vega_data

    penguins = load_penguins().dropna().reset_index(drop=True)
    gapminder = vega_data.gapminder()
    return gapminder, penguins


# ---------------------------------------------------------------------------
# Scatter — penguins bill length vs depth, colored by species
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md("## Scatter")
    return


@app.cell
def _(mo):
    mo.md("### Plotly")
    return


@app.cell
def _(penguins):
    import plotly.express as px

    fig_scatter_plotly = px.scatter(
        penguins,
        x="bill_length_mm",
        y="bill_depth_mm",
        color="species",
        hover_data=["island", "body_mass_g"],
    )
    fig_scatter_plotly
    return (px,)


@app.cell
def _(mo):
    mo.md("### Altair")
    return


@app.cell
def _(penguins):
    import altair as alt

    chart_scatter_altair = (
        alt.Chart(penguins)
        .mark_point()
        .encode(
            x=alt.X("bill_length_mm:Q").scale(zero=False),
            y=alt.Y("bill_depth_mm:Q").scale(zero=False),
            color="species:N",
            tooltip=["species", "island", "body_mass_g"],
        )
        .interactive()
    )
    chart_scatter_altair
    return (alt,)


@app.cell
def _(mo):
    mo.md("### Bokeh")
    return


@app.cell
def _(penguins):
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    from bokeh.transform import factor_cmap

    species_list = sorted(penguins["species"].unique().tolist())
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    source = ColumnDataSource(penguins)

    p_scatter = figure(
        width=600,
        height=400,
        x_axis_label="bill_length_mm",
        y_axis_label="bill_depth_mm",
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        tooltips=[("species", "@species"), ("island", "@island"), ("body_mass_g", "@body_mass_g")],
    )
    p_scatter.scatter(
        x="bill_length_mm",
        y="bill_depth_mm",
        source=source,
        size=8,
        color=factor_cmap("species", palette=palette, factors=species_list),
        legend_field="species",
    )
    p_scatter
    return (ColumnDataSource, factor_cmap, figure)


# ---------------------------------------------------------------------------
# Line — gapminder life expectancy over time for a handful of countries
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md("## Line")
    return


@app.cell
def _(gapminder):
    line_countries = ["Germany", "United States", "Japan", "India", "Brazil"]
    gm = gapminder[gapminder["country"].isin(line_countries)]
    return (gm,)


@app.cell
def _(mo):
    mo.md("### Plotly")
    return


@app.cell
def _(gm, px):
    fig_line_plotly = px.line(gm, x="year", y="life_expect", color="country")
    fig_line_plotly
    return


@app.cell
def _(mo):
    mo.md("### Altair")
    return


@app.cell
def _(alt, gm):
    chart_line_altair = (
        alt.Chart(gm)
        .mark_line()
        .encode(
            x="year:Q",
            y=alt.Y("life_expect:Q").scale(zero=False),
            color="country:N",
        )
        .interactive()
    )
    chart_line_altair
    return


@app.cell
def _(mo):
    mo.md("### Bokeh")
    return


@app.cell
def _(figure, gm, line_countries):
    from bokeh.palettes import Category10

    p_line = figure(
        width=600,
        height=400,
        x_axis_label="year",
        y_axis_label="life_expect",
        tools="pan,wheel_zoom,box_zoom,reset,hover",
    )
    for country, color in zip(line_countries, Category10[10]):
        sub = gm[gm["country"] == country]
        p_line.line(sub["year"], sub["life_expect"], color=color, legend_label=country, line_width=2)
    p_line.legend.click_policy = "hide"
    p_line
    return


# ---------------------------------------------------------------------------
# Bar — mean body mass per species × sex (grouped)
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md("## Bar")
    return


@app.cell
def _(mo):
    mo.md("### Plotly")
    return


@app.cell
def _(penguins, px):
    # px.bar has no built-in aggregation, so pre-aggregate with pandas
    bar_agg_plotly = penguins.groupby(["species", "sex"])["body_mass_g"].mean().reset_index()
    fig_bar_plotly = px.bar(
        bar_agg_plotly, x="species", y="body_mass_g", color="sex", barmode="group"
    )
    fig_bar_plotly
    return


@app.cell
def _(mo):
    mo.md("### Altair")
    return


@app.cell
def _(alt, penguins):
    chart_bar_altair = (
        alt.Chart(penguins)
        .mark_bar()
        .encode(
            x="species:N",
            y="mean(body_mass_g):Q",
            xOffset="sex:N",
            color="sex:N",
        )
    )
    chart_bar_altair
    return


@app.cell
def _(mo):
    mo.md("### Bokeh")
    return


@app.cell
def _(ColumnDataSource, figure, penguins):
    from bokeh.transform import dodge

    bar_agg_bokeh = penguins.groupby(["species", "sex"])["body_mass_g"].mean().reset_index()
    species_bar = sorted(bar_agg_bokeh["species"].unique().tolist())
    sexes = sorted(bar_agg_bokeh["sex"].unique().tolist())
    wide = bar_agg_bokeh.pivot(index="species", columns="sex", values="body_mass_g").reset_index()
    bar_source = ColumnDataSource(wide)

    p_bar = figure(
        x_range=species_bar,
        width=600,
        height=400,
        y_axis_label="mean body_mass_g",
        tools="pan,wheel_zoom,reset,hover",
    )
    bar_width = 0.35
    bar_colors = ["#1f77b4", "#ff7f0e"]
    for i, sex in enumerate(sexes):
        offset = (i - 0.5) * bar_width
        p_bar.vbar(
            x=dodge("species", offset, range=p_bar.x_range),
            top=sex,
            source=bar_source,
            width=bar_width,
            color=bar_colors[i],
            legend_label=sex,
        )
    p_bar.legend.click_policy = "hide"
    p_bar
    return


# ---------------------------------------------------------------------------
# Histogram — flipper length, overlaid by species
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md("## Histogram")
    return


@app.cell
def _(mo):
    mo.md("### Plotly")
    return


@app.cell
def _(penguins, px):
    fig_hist_plotly = px.histogram(
        penguins,
        x="flipper_length_mm",
        color="species",
        marginal="rug",
        opacity=0.7,
    )
    fig_hist_plotly
    return


@app.cell
def _(mo):
    mo.md("### Altair")
    return


@app.cell
def _(alt, penguins):
    chart_hist_altair = (
        alt.Chart(penguins)
        .mark_bar(opacity=0.6)
        .encode(
            x=alt.X("flipper_length_mm:Q").bin(maxbins=30),
            y=alt.Y("count()").stack(None),
            color="species:N",
        )
    )
    chart_hist_altair
    return


@app.cell
def _(mo):
    mo.md("### Bokeh")
    return


@app.cell
def _(figure, penguins):
    import numpy as np

    p_hist = figure(
        width=600,
        height=400,
        x_axis_label="flipper_length_mm",
        y_axis_label="count",
        tools="pan,wheel_zoom,reset,hover",
    )
    edges = np.linspace(
        penguins["flipper_length_mm"].min(), penguins["flipper_length_mm"].max(), 31
    )
    colors_hist = {"Adelie": "#1f77b4", "Chinstrap": "#ff7f0e", "Gentoo": "#2ca02c"}
    for sp, color in colors_hist.items():
        vals = penguins.loc[penguins["species"] == sp, "flipper_length_mm"]
        hist, _ = np.histogram(vals, bins=edges)
        p_hist.quad(
            top=hist,
            bottom=0,
            left=edges[:-1],
            right=edges[1:],
            fill_color=color,
            line_color="white",
            alpha=0.6,
            legend_label=sp,
        )
    p_hist.legend.click_policy = "hide"
    p_hist
    return


if __name__ == "__main__":
    app.run()
