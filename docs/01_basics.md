# 01 — Basics

Scatter, line, bar, histogram. The bread-and-butter plots every library must get
right — and the place where API ergonomics differ most, before customization
requirements kick in.

Each plot below uses each library's **idiomatic high-level API**: `plotly.express`
for Plotly, the fluent `alt.Chart().mark_*().encode()` syntax for Altair, and
`bokeh.plotting.figure` for Bokeh. This is what you'd actually reach for in a
real notebook, not what's maximally concise or maximally powerful.

!!! info "How to read the embed below"
    The iframe is the full notebook. Code for each library is shown next to its
    rendered plot — use that to compare the API surface directly. Scroll inside
    the iframe to move through scatter → line → bar → histogram.

<div class="marimo-embed-wrapper">
<iframe class="marimo-embed" src="./assets/notebooks/01_basics.html" height="7000"></iframe>
<div class="marimo-embed-actions">
<a href="./assets/notebooks/01_basics.html" target="_blank">Open standalone &rarr;</a>
</div>
</div>

## Evaluation

### Lines of code

Counting the **plotting code only** — data loading and aggregation shared across
all three, so they're excluded. Counted including the final `fig`/`chart`/`p`
line that renders.

| Plot       | Plotly (px) | Altair  | Bokeh   |
|------------|:-----------:|:-------:|:-------:|
| Scatter    | **3**       | 10      | 15      |
| Line       | **1**       | 9       | 10      |
| Bar (grouped) | **2**    | **6**   | 16      |
| Histogram  | **6**       | 7       | 18      |

Plotly Express is consistently the shortest — it's what `px` is designed for.
Altair is close on most plots and beats Plotly on the grouped bar because its
`mean(...)` aggregation in the encoding means you don't pre-aggregate in pandas.
Bokeh trails on every row because its imperative model asks you to construct the
figure, the source, the tools, the tooltips, and the colour mapping yourself.

### Default interactivity (no extra config)

For each lib, what interactivity works *without* any extra code beyond what's
shown above?

| Feature                 | Plotly | Altair | Bokeh |
|-------------------------|:------:|:------:|:-----:|
| Hover tooltips          | ✅     | ✅     | ✅ *(via `tools=...,hover`)* |
| Pan + zoom              | ✅     | ✅ *(via `.interactive()`)* | ✅ |
| Legend click to hide    | ✅     | ❌     | ✅ *(via `click_policy='hide'`)* |
| Double-click to reset   | ✅     | ✅     | ❌ *(explicit reset tool)* |

Plotly is the "batteries-included" option — every common interaction works the
moment the plot renders. Altair needs a trailing `.interactive()` for zoom.
Bokeh needs its tools declared up front, which is a one-time habit cost that
disappears after the first plot.

### Ergonomics notes

**Plotly.** `px` maps almost one-to-one onto "plot this column by that column,
colored by this one." The moment you want something it doesn't express (e.g., a
bar chart of an aggregated mean), you drop to pandas or switch to
`plotly.graph_objects`, which is a significantly more verbose API.

**Altair.** Consistent grammar. Once you know `alt.Chart().mark_x().encode(...)`,
every plot is that shape — only the mark and the encodings change. Aggregation
in the encoding (`mean(body_mass_g)`) is genuinely nicer than pre-aggregating.
The main friction point is the type suffixes (`:Q`, `:N`, `:O`, `:T`) which are
invisible trip-wires for beginners.

**Bokeh.** The imperative "build your figure, add glyphs, configure tools" model
is powerful but verbose for simple cases. A grouped bar chart needs a pivot and
a `dodge` transform; an overlaid histogram needs a manual `np.histogram` +
`quad`. The payoff is that every knob is accessible — Bokeh never makes a
high-level choice you can't undo.

## Verdict

For the basics, **Plotly Express** is the obvious default: it produces the
shortest, most-interactive-by-default code for every plot in this chapter. If
you know the shape of your chart and just want it rendered, reach for `px`
first.

**Altair** is the right choice when your workflow leans on *layered aggregations*
(the `mean()` / `count()` encodings) or you want a single consistent API across
many plot types. It costs a few more lines per plot but buys you a more
principled, composable mental model that pays off later in faceting and
multi-layer work.

**Bokeh** is the wrong first choice for basics — you're paying the full cost of
its imperative model without yet benefiting from its customization ceiling.
Hold judgement until later chapters (interactive, dashboards) where Bokeh's
model starts earning its keep.
