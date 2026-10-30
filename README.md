# Sigfinitiv

The UCSD Sustainable Investment Group’s Python package for ESG and financial
company data. It connects straight to our Neon Postgres database; no server
is needed.

## Install

```bash
pip install git+https://github.com/UCSD-Sustainable-Investment-Group-NEW/sigfinitiv
```

## Set up your login

Create a `.env` file in the folder you run your code from (copy `.env.example`):

```
SIGFINITIV_DB_USER=your_username
SIGFINITIV_DB_PASSWORD=your_password
```

Ask the project lead for your login. Never paste your password into a
notebook or commit `.env`.

## Analysts: reading data

```python
import sigfinitiv as sf

sf.ping()  # True if you're connected

# Ready-made queries
df = sf.get_values(
    ["co2_equivalent_emissions_total", "revenue_from_goods_services"],
    peer_group="US Retailers",
    year=2023,
)
sf.zscores("co2_equivalent_emissions_total", peer_group="US Retailers")
sf.lagged_changes("co2_equivalent_emissions_total", "revenue_from_goods_services", lag=2)

# Your own SQL
sf.sql(
    "SELECT ticker, value FROM metric_values WHERE metric = %s AND year = %s",
    ["net_margin_pct", 2023],
)

# Save any result
df.to_csv("retail_2023.csv", index=False)
df.to_excel("retail_2023.xlsx", index=False)
```

Every function returns a pandas DataFrame. Metric names are lowercase keys:
`"Net Margin - %"` is stored as `net_margin_pct`. `sf.coverage()` lists every
metric and how many companies report it. Analyst logins are read-only, so
`sf.sql` can only run SELECT queries.

## Data maintainers: loading data

Needs a login with write access.

```python
from sigfinitiv import ingest

ingest.upsert_company("COST.O", "Costco Wholesale Corp", "Diversified Retail", "United States")
ingest.upsert_values("costco_values.csv")             # add or update rows
ingest.replace_company("COST.O", "costco_values.xlsx") # full re-upload
```

Files can be CSV or Excel (`.xlsx`), or a DataFrame, with these columns:

| ticker | year | metric | value | category |
|---|---|---|---|---|
| COST.O | 2023 | Net Margin - % | 2.6 | financial |
| COST.O | 2023 | CO2 Equivalent Emissions Total | 2900000 | esg |

Column names can be in any case and extra columns are ignored. Metric labels
are converted to keys automatically, and blank or `--` values are skipped.
Raw Refinitiv Workspace exports have a different layout; convert them first
with `ingest.load_workspace_export(path)`.

## Data model

| Table | Columns | Key |
|---|---|---|
| `metric_values` | ticker, year, metric, value, category | (ticker, year, metric); extra index on (metric, year) |
| `companies` | ticker, name, industry, country | ticker |
| `peer_group_members` | group_name, ticker | (group_name, ticker) |

One row per company, year and metric. Missing data is a missing row. The full
schema and database roles are in `sql/001_init.sql`.

## For contributors

```
src/sigfinitiv/
├── config.py    # database host, env variable names, data contract constants
├── db.py        # connect(), ping(), sql(): done
├── queries.py   # read functions: stubs to implement
└── ingest.py    # write functions: stubs; load_values() and normalize_metric_name() done
```

**Status:** the connection, `ping()`, `sql()`, `load_values()` and
`normalize_metric_name()` work. Every other function raises
`NotImplementedError`.

**Implementing a stub:**
1. Keep the signature and the returned columns exactly as documented. They
   are the contract the API and front end rely on. Discuss changes first.
2. Read functions: write the SQL and run it with `query_df(sql, params)`.
   Always pass values as parameters (`%s` or `%(name)s`), never with f-strings.
3. Write functions: start from `load_values(source)` (already in place), and
   wrap multi-row writes in `with get_connection().transaction():`.
4. Add a test in `tests/`.

**Local development:**
```bash
git clone https://github.com/UCSD-Sustainable-Investment-Group-NEW/sigfinitiv
cd sigfinitiv
python -m venv .venv
.venv\Scripts\activate          # Windows; macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
Database tests are skipped unless credentials are set. Point
`SIGFINITIV_DATABASE_URL` at the Neon **dev** branch while developing, never
production.