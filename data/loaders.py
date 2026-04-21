"""Shared dataset loaders used across all comparison notebooks."""

from functools import lru_cache

import pandas as pd


@lru_cache(maxsize=1)
def load_penguins() -> pd.DataFrame:
    from palmerpenguins import load_penguins as _load

    df = _load().dropna().reset_index(drop=True)
    return df


@lru_cache(maxsize=1)
def load_gapminder() -> pd.DataFrame:
    from vega_datasets import data

    return data.gapminder()
