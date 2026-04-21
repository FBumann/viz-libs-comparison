# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.2",
#     "pandas==2.3.3",
#     "palmerpenguins==0.1.4",
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
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        &larr; [Home](../../index.html)

        # Smoke test

        Same scatter in Plotly, Altair, and Bokeh. If this page loads in a browser
        **with no Python kernel** and all three plots respond to hover/zoom,
        the WASM export pipeline works and we can build the full comparison on top.
        """
    )
    return


@app.cell
def _():
    from palmerpenguins import load_penguins
    df = load_penguins().dropna().reset_index(drop=True)
    df.head()
    return (df,)


@app.cell
def _(mo):
    mo.md("## Plotly")
    return


@app.cell
def _(df):
    import plotly.express as px

    fig_plotly = px.scatter(
        df,
        x="bill_length_mm",
        y="bill_depth_mm",
        color="species",
        hover_data=["island", "body_mass_g"],
        title="Penguins — Plotly",
    )
    fig_plotly
    return (fig_plotly,)


@app.cell
def _(mo):
    mo.md("## Altair")
    return


@app.cell
def _(df):
    import altair as alt

    chart_altair = (
        alt.Chart(df)
        .mark_point(size=60)
        .encode(
            x=alt.X("bill_length_mm:Q", scale=alt.Scale(zero=False)),
            y=alt.Y("bill_depth_mm:Q", scale=alt.Scale(zero=False)),
            color="species:N",
            tooltip=["species", "island", "body_mass_g"],
        )
        .properties(title="Penguins — Altair", width=600, height=400)
        .interactive()
    )
    chart_altair
    return (chart_altair,)


@app.cell
def _(mo):
    mo.md("## Bokeh")
    return


@app.cell
def _(df):
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    from bokeh.transform import factor_cmap

    species = sorted(df["species"].unique().tolist())
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    source = ColumnDataSource(df)

    p = figure(
        width=600,
        height=400,
        x_axis_label="bill_length_mm",
        y_axis_label="bill_depth_mm",
        title="Penguins — Bokeh",
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        tooltips=[("species", "@species"), ("island", "@island"), ("body_mass_g", "@body_mass_g")],
    )
    p.scatter(
        x="bill_length_mm",
        y="bill_depth_mm",
        source=source,
        size=8,
        color=factor_cmap("species", palette=palette, factors=species),
        legend_field="species",
    )
    p
    return (p,)


if __name__ == "__main__":
    app.run()
