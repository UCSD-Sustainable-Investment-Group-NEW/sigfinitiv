"""Write functions: for loading data, not for everyday analysis.

These need a database login with write access. With a read-only analyst
login they fail with a permission error, which is intended.

Every write function accepts its data as a CSV file, an Excel file or a
pandas DataFrame, and runs it through `load_values` first.

Every write that touches more than one row must run in one transaction:

    with get_connection().transaction():
        ...
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Sequence, Union

import pandas as pd

from sigfinitive import config
from sigfinitive.db import get_connection  # noqa: F401  (used by implementations)
from sigfinitive.errors import ContractError

ValuesSource = Union[str, os.PathLike, pd.DataFrame]

CSV_SUFFIXES = (".csv",)
EXCEL_SUFFIXES = (".xlsx", ".xlsm")


def _todo(name: str) -> NotImplementedError:
    return NotImplementedError(f"sigfinitive.ingest.{name} is not implemented yet")


# ── Input handling (implemented: defines the shared format) ───────────────

def normalize_metric_name(label: str) -> str:
    """Turn a display label into the stored metric key.

    Lowercase, % becomes "pct", every other run of non-alphanumeric
    characters becomes one underscore.

        "CO2 Equivalent Emissions Total" -> "co2_equivalent_emissions_total"
        "Revenue from Goods & Services"  -> "revenue_from_goods_services"
        "Net Margin - %"                 -> "net_margin_pct"
    """
    key = label.strip().lower().replace("%", " pct ")
    key = re.sub(r"[^a-z0-9]+", "_", key)
    return key.strip("_")


def _read_source(source: ValuesSource, sheet: str | int = 0) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"No file at {path}")

    suffix = path.suffix.lower()
    if suffix in CSV_SUFFIXES:
        return pd.read_csv(path)
    if suffix in EXCEL_SUFFIXES:
        return pd.read_excel(path, sheet_name=sheet)
    raise ContractError(
        f"Unsupported file type {suffix!r}. Use a CSV ({', '.join(CSV_SUFFIXES)}) "
        f"or Excel ({', '.join(EXCEL_SUFFIXES)}) file, or a DataFrame."
    )


def load_values(source: ValuesSource, sheet: str | int = 0) -> pd.DataFrame:
    """Read long-format values from a CSV file, Excel file or DataFrame, and
    clean them so they're ready to write.

    The input needs these columns, in any order and any capitalization:
        ticker, year, metric, value, category
    Extra columns are ignored.

    Cleaning:
      - metric names are converted to keys with normalize_metric_name,
        so raw labels like "Net Margin - %" are fine
      - tickers are uppercased, categories lowercased
      - rows with no usable value (blank, "--", text) are dropped, since
        missing data is stored as a missing row
      - year becomes int and value becomes float

    Args:
        source: Path to a .csv or .xlsx file, or a DataFrame.
        sheet: For Excel files, the sheet name or index. Default: first sheet.

    Raises:
        ContractError: missing columns, an unknown category, or the same
        (ticker, year, metric) appearing twice.
    """
    df = _read_source(source, sheet)
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in config.VALUE_COLUMNS if c not in df.columns]
    if missing:
        raise ContractError(f"Missing columns: {missing}. Expected {config.VALUE_COLUMNS}.")

    out = df[config.VALUE_COLUMNS].copy()

    # Postgres would store NaN as a real value, so unusable values must go.
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out = out.dropna(subset=config.VALUE_COLUMNS)

    out["ticker"] = out["ticker"].astype(str).str.strip().str.upper()
    out["metric"] = out["metric"].astype(str).map(normalize_metric_name)
    out["category"] = out["category"].astype(str).str.strip().str.lower()
    out["year"] = out["year"].astype(int)
    out["value"] = out["value"].astype(float)

    bad_categories = set(out["category"]) - set(config.CATEGORIES)
    if bad_categories:
        raise ContractError(f"Unknown categories {sorted(bad_categories)}; use {config.CATEGORIES}.")

    dupes = out[out.duplicated(subset=["ticker", "year", "metric"], keep=False)]
    if not dupes.empty:
        first = dupes.iloc[0]
        raise ContractError(
            f"{len(dupes)} rows repeat the same ticker, year and metric, e.g. "
            f"{first['ticker']} {first['year']} {first['metric']}. Each must appear once."
        )

    return out.reset_index(drop=True)


# ── Writes (stubs) ────────────────────────────────────────────────────────

def upsert_company(ticker: str, name: str, industry: str | None, country: str | None) -> None:
    """Insert a company, or update its name, industry and country if it exists."""
    raise _todo("upsert_company")


def upsert_values(source: ValuesSource, sheet: str | int = 0) -> int:
    """Insert values, updating any existing (ticker, year, metric) rows.

    Never deletes. Every ticker must already exist (see upsert_company).

    Args:
        source: Path to a .csv or .xlsx file, or a DataFrame (see load_values).
        sheet: For Excel files, the sheet name or index.

    Returns:
        Number of rows written.
    """
    values = load_values(source, sheet)  # noqa: F841
    raise _todo("upsert_values")


def replace_company(ticker: str, source: ValuesSource, sheet: str | int = 0) -> int:
    """Replace all of one company's values in a single transaction.

    Deletes the company's existing rows, then inserts the new ones. If
    anything fails, nothing changes. Use for a full re-upload. Every row in
    `source` must belong to `ticker`.

    Returns:
        Number of rows written.
    """
    values = load_values(source, sheet)  # noqa: F841
    raise _todo("replace_company")


def load_workspace_export(path: str | os.PathLike) -> pd.DataFrame:
    """Convert a Refinitiv Workspace export (ESG_Table_for_*.xlsx or
    CF-Export-*.xlsx) into a long-format values frame.

    Those files put metrics in rows and years in columns, so they need
    parsing first. Port the existing upload parser here.

    Returns:
        Columns: ticker, year, metric, value, category, ready for
        upsert_values or replace_company.
    """
    raise _todo("load_workspace_export")


def save_peer_group(name: str, tickers: Sequence[str]) -> None:
    """Create a peer group, or replace its members if it exists."""
    raise _todo("save_peer_group")


def delete_peer_group(name: str) -> None:
    """Delete a peer group. Company data is untouched."""
    raise _todo("delete_peer_group")