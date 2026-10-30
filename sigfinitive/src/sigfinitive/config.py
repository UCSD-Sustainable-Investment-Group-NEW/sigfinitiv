"""Shared settings and constants.

Nothing in this file is secret. Passwords only ever come from the environment.
"""

# ── Database location ─────────────────────────────────────────────────────
# Fill in once from the Neon console (Connection details → host), then commit.
# The host is not a secret; the password is.
DEFAULT_HOST = ""  # e.g. "ep-example-123456.us-east-2.aws.neon.tech"
DEFAULT_DB_NAME = "neondb"
CONNECT_TIMEOUT = 10  # seconds; covers Neon waking from idle

# ── Environment variable names ────────────────────────────────────────────
ENV_DATABASE_URL = "SIGFINITIVE_DATABASE_URL"
ENV_DB_USER = "SIGFINITIVE_DB_USER"
ENV_DB_PASSWORD = "SIGFINITIVE_DB_PASSWORD"
ENV_DB_HOST = "SIGFINITIVE_DB_HOST"
ENV_DB_NAME = "SIGFINITIVE_DB_NAME"

# ── Data contract ─────────────────────────────────────────────────────────
# Columns of a long-format values frame, as stored in metric_values.
VALUE_COLUMNS = ["ticker", "year", "metric", "value", "category"]
CATEGORIES = ("esg", "financial")
