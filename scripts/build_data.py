#!/usr/bin/env python
"""Regenerate the committed dispatch parquet from the generator in data/loaders.py.

Run this when you change the generator (capacities, scenarios, timesteps, etc.):

    uv run python scripts/build_data.py

The generated file is committed to the repo so notebooks can load it without
running the generator at display time.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.loaders import make_dispatch_dataframe  # noqa: E402

OUT_PATH = ROOT / "notebooks" / "public" / "dispatch.parquet"


def main() -> None:
    df = make_dispatch_dataframe()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, compression="snappy")
    print(f"wrote {OUT_PATH.relative_to(Path.cwd())}  ({OUT_PATH.stat().st_size / 1e6:.2f} MB, {len(df):,} rows)")


if __name__ == "__main__":
    main()
