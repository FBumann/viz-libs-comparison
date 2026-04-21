"""Shared dataset loaders used across all comparison notebooks.

Public API is a long-form `pandas.DataFrame`; the internal build uses xarray
for convenience but is not exposed.
"""

from functools import lru_cache

import numpy as np
import pandas as pd
import xarray as xr


@lru_cache(maxsize=1)
def make_dispatch_dataframe(n_hours: int = 8760, seed: int = 42) -> pd.DataFrame:
    """Synthetic energy-system dispatch as a long-form DataFrame.

    Columns
    -------
    scenario : str
    period : int
    flow : str   ('solar' | 'wind' | 'gas' | 'batt_charge' | 'batt_discharge')
    time : datetime64[ns]
    generation : float   MW (always non-negative)
    demand : float       MW (same across flows for a given scenario/period/time)
    storage_soc : float  MWh (same across flows)
    capacity : float     MW (installed capacity; same across time for a given flow)

    Shape mirrors a flixopt `flow_system.solution` after `.to_dataframe().reset_index()`.
    """
    ds = _make_dispatch_dataset(n_hours, seed)
    return ds.to_dataframe().reset_index()


@lru_cache(maxsize=1)
def _make_dispatch_dataset(n_hours: int = 8760, seed: int = 42) -> xr.Dataset:
    """Internal xarray build. Not part of the public API — use the DataFrame."""
    rng = np.random.default_rng(seed)

    times = pd.date_range("2030-01-01", periods=n_hours, freq="1h")
    flows = ["solar", "wind", "gas", "batt_charge", "batt_discharge"]
    scenarios = [
        "baseline",
        "high_renewables",
        "costly_gas",
        "electrification",
        "coupled_heat",
    ]
    periods = [2030, 2040]

    n_flow = len(flows)
    n_scen = len(scenarios)
    n_period = len(periods)

    hour = times.hour.to_numpy()
    doy = times.dayofyear.to_numpy()
    dow = times.dayofweek.to_numpy()

    solar_shape = np.clip(np.sin((hour - 6) * np.pi / 12), 0, None)
    solar_season = 0.55 + 0.45 * np.sin((doy - 80) * 2 * np.pi / 365)
    solar_profile = solar_shape * solar_season

    wind_trend = 0.35 + 0.20 * np.sin(doy * 2 * np.pi / 365)
    wind_profile = np.clip(wind_trend + rng.normal(0, 0.18, n_hours), 0.02, 1.0)

    demand_daily = 12 * np.sin((hour - 8) * 2 * np.pi / 24)
    demand_weekday = 8 * (dow < 5)
    demand_season = 18 + 18 * np.cos((doy - 15) * 2 * np.pi / 365)
    demand_base = 55.0 + demand_daily + demand_weekday + demand_season

    cap_base = {"solar": 80, "wind": 50, "gas": 90, "batt_charge": 25, "batt_discharge": 25}
    scenario_cap_scale = {
        "baseline":        {"solar": 1.0, "wind": 1.0, "gas": 1.0, "batt_charge": 1.0, "batt_discharge": 1.0},
        "high_renewables": {"solar": 1.9, "wind": 1.7, "gas": 0.6, "batt_charge": 2.2, "batt_discharge": 2.2},
        "costly_gas":      {"solar": 1.3, "wind": 1.2, "gas": 0.8, "batt_charge": 1.4, "batt_discharge": 1.4},
        "electrification": {"solar": 1.4, "wind": 1.3, "gas": 1.1, "batt_charge": 1.6, "batt_discharge": 1.6},
        "coupled_heat":    {"solar": 1.1, "wind": 1.2, "gas": 1.3, "batt_charge": 1.1, "batt_discharge": 1.1},
    }
    scenario_demand_scale = {
        "baseline": 1.0, "high_renewables": 1.0, "costly_gas": 1.0,
        "electrification": 1.35, "coupled_heat": 1.20,
    }
    period_growth = {2030: 1.0, 2040: 1.4}

    generation = np.zeros((n_scen, n_period, n_flow, n_hours))
    demand = np.zeros((n_scen, n_period, n_hours))
    storage_soc = np.zeros((n_scen, n_period, n_hours))
    capacity = np.zeros((n_scen, n_period, n_flow))

    for si, scen in enumerate(scenarios):
        for pi, per in enumerate(periods):
            for fi, fl in enumerate(flows):
                capacity[si, pi, fi] = cap_base[fl] * scenario_cap_scale[scen][fl] * period_growth[per]

            cap_solar = capacity[si, pi, 0]
            cap_wind = capacity[si, pi, 1]
            cap_gas = capacity[si, pi, 2]
            cap_batt = capacity[si, pi, 3]
            batt_energy = cap_batt * 4.0

            d = demand_base * scenario_demand_scale[scen] * period_growth[per]
            solar = cap_solar * solar_profile
            wind = cap_wind * wind_profile
            residual = d - solar - wind

            soc = np.zeros(n_hours)
            batt_dis = np.zeros(n_hours)
            batt_ch = np.zeros(n_hours)
            soc[0] = 0.5 * batt_energy
            for t in range(n_hours):
                if t > 0:
                    soc[t] = soc[t - 1]
                if residual[t] > 0:
                    dis = min(residual[t], cap_batt, soc[t])
                    batt_dis[t] = dis
                    soc[t] -= dis
                    residual[t] -= dis
                elif residual[t] < 0:
                    ch = min(-residual[t], cap_batt, batt_energy - soc[t])
                    batt_ch[t] = ch
                    soc[t] += ch
                    residual[t] += ch

            gas = np.clip(residual, 0, cap_gas)

            generation[si, pi, 0, :] = solar
            generation[si, pi, 1, :] = wind
            generation[si, pi, 2, :] = gas
            generation[si, pi, 3, :] = batt_ch
            generation[si, pi, 4, :] = batt_dis
            demand[si, pi, :] = d
            storage_soc[si, pi, :] = soc

    return xr.Dataset(
        data_vars={
            "generation": (("scenario", "period", "flow", "time"), generation),
            "demand": (("scenario", "period", "time"), demand),
            "storage_soc": (("scenario", "period", "time"), storage_soc),
            "capacity": (("scenario", "period", "flow"), capacity),
        },
        coords={
            "time": times,
            "flow": flows,
            "scenario": scenarios,
            "period": periods,
        },
    )
