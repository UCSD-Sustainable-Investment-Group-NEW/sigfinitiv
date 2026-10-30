-- Sigfinitive schema. Run once as the database owner, on the dev branch first.
-- Safe to re-run: every statement checks whether its object already exists.

-- ── Tables ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS companies (
    ticker   TEXT PRIMARY KEY,          -- e.g. 'COST.O'
    name     TEXT,
    industry TEXT,                      -- TRBC Industry Group
    country  TEXT
);

CREATE TABLE IF NOT EXISTS metric_values (
    ticker   TEXT             NOT NULL REFERENCES companies (ticker) ON DELETE CASCADE,
    year     INTEGER          NOT NULL,
    metric   TEXT             NOT NULL  -- normalized key, e.g. 'net_margin_pct'
             CHECK (metric ~ '^[a-z0-9]+(_[a-z0-9]+)*$'),
    value    DOUBLE PRECISION NOT NULL  -- missing data = no row, never NULL or NaN
             CHECK (value <> 'NaN'),
    category TEXT             NOT NULL CHECK (category IN ('esg', 'financial')),
    PRIMARY KEY (ticker, year, metric)  -- serves "everything for one company"
);

-- Serves "one metric across many companies", e.g. CO2 for a peer group in 2023.
CREATE INDEX IF NOT EXISTS metric_values_metric_year_idx
    ON metric_values (metric, year);

CREATE TABLE IF NOT EXISTS peer_group_members (
    group_name TEXT NOT NULL,
    ticker     TEXT NOT NULL REFERENCES companies (ticker) ON DELETE CASCADE,
    PRIMARY KEY (group_name, ticker)
);

-- ── Roles ─────────────────────────────────────────────────────────────────
-- Group roles hold the permissions; individual logins join a group.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_readonly') THEN
        CREATE ROLE analyst_readonly NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'api_readwrite') THEN
        CREATE ROLE api_readwrite NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO analyst_readonly, api_readwrite;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO api_readwrite;

-- Tables created later by the owner get the same grants automatically.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_readwrite;

-- ── Logins (run separately, one per person or service) ───────────────────
-- Use a long random password and share it privately, never in Git or chat.
--
--   CREATE ROLE quant_jane LOGIN PASSWORD '<password>' IN ROLE analyst_readonly;
--   CREATE ROLE api_service LOGIN PASSWORD '<password>' IN ROLE api_readwrite;
--
-- Removing someone:
--   DROP ROLE quant_jane;