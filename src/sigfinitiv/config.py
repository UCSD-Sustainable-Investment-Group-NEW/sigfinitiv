"""Shared settings and constants.

Nothing in this file is secret. Passwords only ever come from the environment.
"""

# ── Database location ─────────────────────────────────────────────────────
# Fill in once from the Neon console (Connection details → host), then commit.
# The host is not a secret; the password is.
DEFAULT_HOST = "ep-shy-sunset-arv1ebmj.c-4.us-west-2.aws.neon.tech"
DEFAULT_DB_NAME = "neondb"
CONNECT_TIMEOUT = 10  # seconds; covers Neon waking from idle

# ── Environment variable names ────────────────────────────────────────────
ENV_DATABASE_URL = "SIGFINITIV_DATABASE_URL"
ENV_DB_USER = "SIGFINITIV_DB_USER"
ENV_DB_PASSWORD = "SIGFINITIV_DB_PASSWORD"
ENV_DB_HOST = "SIGFINITIV_DB_HOST"
ENV_DB_NAME = "SIGFINITIV_DB_NAME"

# ── Data contract ─────────────────────────────────────────────────────────
# Columns of a long-format values frame, as stored in metric_values.
VALUE_COLUMNS = ["ticker", "year", "metric", "value", "category"]
CATEGORIES = ("esg", "financial")
