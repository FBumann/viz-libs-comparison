#!/usr/bin/env bash
# Two-stage build:
#   1. Export every marimo notebook to a WASM-powered standalone HTML under
#      docs/assets/notebooks/.
#   2. Build the mkdocs-material site, embedding the notebooks via iframe.
# Final output lives in ./_site.
set -euo pipefail

cd "$(dirname "$0")/.."

NOTEBOOK_OUT="docs/assets/notebooks"

# --- stage 1: marimo WASM exports -------------------------------------------
rm -rf "$NOTEBOOK_OUT"
mkdir -p "$NOTEBOOK_OUT"

for nb in notebooks/*.py; do
    name=$(basename "$nb" .py)
    out="$NOTEBOOK_OUT/${name}.html"
    echo "--> exporting $nb -> $out"
    uv run marimo export html-wasm "$nb" -o "$out" --mode run -f
done

# marimo bundles a CLAUDE.md into each export that mkdocs would otherwise
# turn into a published page. Drop it.
rm -f "$NOTEBOOK_OUT/CLAUDE.md"

# --- stage 2: mkdocs site build ---------------------------------------------
echo ""
echo "--> building mkdocs site -> _site"
uv run mkdocs build --strict

echo ""
echo "Done. Preview with:"
echo "  uv run python -m http.server --directory _site 8765"
