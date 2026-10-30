"""Read functions: the analyst-facing API.

Each function's signature and docstring is the contract the API and front end
build against. To implement one: write the SQL, run it with `query_df`, return
exactly the documented columns, and add a test. Don't change a signature
without telling the team.

Tables (see sql/001_init.sql):
    metric_values      (ticker, year, metric, value, category)
    companies          (ticker, name, industry, country)
    peer_group_members (group_name, ticker)

Metric names are normalized keys, e.g. "co2_equivalent_emissions_total"
(see ingest.normalize_metric_name).
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from sigfinitive.db import query_df  # noqa: F401  (used by implementations)


def _todo(name: str) -> NotImplementedError:
    return NotImplementedError(f"sigfinitive.{name} is not implemented yet")


# ── Lookups ───────────────────────────────────────────────────────────────

def list_companies(industry: str | None = None) -> pd.DataFrame:
    """Companies in the database.

    Args:
        industry: Only companies in this TRBC industry group.

    Returns:
        Columns: ticker, name, industry, country. One row per company.
    """
    raise _todo("list_companies")


def list_peer_groups() -> dict[str, list[str]]:
    """Saved peer groups.

    Returns:
        {group_name: [ticker, ...]}
    """
    raise _todo("list_peer_groups")


def coverage(peer_group: str | None = None) -> pd.DataFrame:
    """How many companies report each metric.

    Args:
        peer_group: Only count companies in this peer group.

    Returns:
        Columns: metric, category, companies (int), first_year, last_year.
        Sorted by companies, ascending, so gaps show first.
    """
    raise _todo("coverage")


# ── Values ────────────────────────────────────────────────────────────────

def get_company(
    ticker: str,
    metrics: Sequence[str] | None = None,
    years: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """All values for one company.

    Args:
        ticker: e.g. "COST.O".
        metrics: Only these metric keys. Default: all.
        years: Inclusive (start, end). Default: all years.

    Returns:
        Columns: ticker, year, metric, value, category.
    """
    raise _todo("get_company")


def get_values(
    metrics: Sequence[str],
    *,
    tickers: Sequence[str] | None = None,
    peer_group: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    year: int | None = None,
    years: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Values for several metrics across companies. Filters combine with AND.

    Pass `year` for a single year (cross-sectional) or `years` for a range,
    not both.

    Returns:
        Columns: ticker, year, metric, value, category.
    """
    raise _todo("get_values")


def screen(
    metric: str,
    *,
    year: int,
    min_value: float | None = None,
    max_value: float | None = None,
    peer_group: str | None = None,
) -> list[str]:
    """Tickers whose value for `metric` in `year` falls within the bounds.

    Returns:
        Sorted list of tickers.
    """
    raise _todo("screen")


# ── Analysis queries ──────────────────────────────────────────────────────

def zscores(
    metric: str,
    *,
    peer_group: str,
    years: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Each company's value as a Z-score against its peer group, per year.

    z = (value - peer-group mean for that year) / peer-group std dev for that year

    Returns:
        Columns: ticker, year, value, z_score. z_score is NaN when the
        group's std dev is 0 or fewer than 2 companies report that year.
    """
    raise _todo("zscores")


def lagged_changes(
    esg: str,
    financial: str,
    *,
    lag: int = 1,
    peer_group: str | None = None,
    tickers: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Pairs an ESG metric's year-over-year % change in year T with a
    financial metric's year-over-year % change in year T + lag.

    Returns:
        Columns: ticker, esg_year, esg_change, financial_change.
        Changes are fractions (0.05 = +5%). Rows where either change can't
        be computed are dropped.
    """
    raise _todo("lagged_changes")
