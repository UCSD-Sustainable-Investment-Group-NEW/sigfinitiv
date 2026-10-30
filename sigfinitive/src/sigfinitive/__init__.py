"""Sigfinitive: UCSD Sustainable Investment Group's ESG and financial data SDK.

    import sigfinitive as sf

    sf.ping()
    sf.get_values(["co2_equivalent_emissions_total"], peer_group="Retail", year=2023)
    sf.sql("SELECT * FROM companies")

Write functions live in `sigfinitive.ingest` and need a write-capable login.
"""

from sigfinitive.db import close, connect, ping, query_df, sql
from sigfinitive.queries import (
    coverage,
    get_company,
    get_values,
    lagged_changes,
    list_companies,
    list_peer_groups,
    screen,
    zscores,
)

__version__ = "0.1.0"

__all__ = [
    "close",
    "connect",
    "coverage",
    "get_company",
    "get_values",
    "lagged_changes",
    "list_companies",
    "list_peer_groups",
    "ping",
    "query_df",
    "screen",
    "sql",
    "zscores",
]