#!/usr/bin/env bash
# Export every marimo notebook in ./notebooks to a WASM-powered standalone
# HTML page under ./_site. Used both locally (preview) and by CI (Pages deploy).
set -euo pipefail

cd "$(dirname "$0")/.."

rm -rf _site
mkdir -p _site

for nb in notebooks/*.py; do
    name=$(basename "$nb" .py)
    if [ "$name" = "00_index" ]; then
        out="_site/index.html"
    else
        out="_site/${name}.html"
    fi
    echo "--> exporting $nb -> $out"
    uv run marimo export html-wasm "$nb" -o "$out" --mode run -f
done

echo ""
echo "Done. Preview with:"
echo "  uv run python -m http.server --directory _site 8765"
