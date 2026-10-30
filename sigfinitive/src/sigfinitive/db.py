"""Database connection.

Credentials come from environment variables (or a .env file in your working
directory), never from function arguments, so they never end up saved in a
notebook.

Analysts set:
    SIGFINITIVE_DB_USER, SIGFINITIVE_DB_PASSWORD

Services such as the API, or anyone pointing at a dev branch, set instead:
    SIGFINITIVE_DATABASE_URL
"""

from __future__ import annotations

import os
from typing import Any, Sequence

import pandas as pd
import psycopg
from dotenv import find_dotenv, load_dotenv

from sigfinitive import config
from sigfinitive.errors import ConfigError

_connection: psycopg.Connection | None = None
_env_loaded = False


def _load_env() -> None:
    """Load a .env file from the current directory (or a parent) once."""
    global _env_loaded
    if not _env_loaded:
        # usecwd=True: search from where the user runs their code,
        # not from where the package is installed.
        load_dotenv(find_dotenv(usecwd=True))
        _env_loaded = True


def connect() -> psycopg.Connection:
    """Open a new connection to the database.

    Uses SIGFINITIVE_DATABASE_URL if set; otherwise builds the connection from
    SIGFINITIVE_DB_USER and SIGFINITIVE_DB_PASSWORD plus the host in config.py.
    Connections are in autocommit mode; writes use explicit transactions.
    """
    _load_env()

    url = os.getenv(config.ENV_DATABASE_URL)
    if url:
        return psycopg.connect(url, connect_timeout=config.CONNECT_TIMEOUT, autocommit=True)

    user = os.getenv(config.ENV_DB_USER)
    password = os.getenv(config.ENV_DB_PASSWORD)
    if not user or not password:
        raise ConfigError(
            f"No database credentials found. Set {config.ENV_DB_USER} and "
            f"{config.ENV_DB_PASSWORD} in a .env file in your working directory "
            "(see .env.example)."
        )

    host = os.getenv(config.ENV_DB_HOST) or config.DEFAULT_HOST
    if not host:
        raise ConfigError(
            "Database host is not configured. Set DEFAULT_HOST in "
            f"sigfinitive/config.py or {config.ENV_DB_HOST} in your .env file."
        )

    return psycopg.connect(
        host=host,
        dbname=os.getenv(config.ENV_DB_NAME) or config.DEFAULT_DB_NAME,
        user=user,
        password=password,
        sslmode="require",
        connect_timeout=config.CONNECT_TIMEOUT,
        autocommit=True,
    )


def get_connection() -> psycopg.Connection:
    """Return a shared connection, opening (or reopening) it when needed."""
    global _connection
    if _connection is None or _connection.closed or _connection.broken:
        _connection = connect()
    return _connection


def close() -> None:
    """Close the shared connection, if one is open."""
    global _connection
    if _connection is not None and not _connection.closed:
        _connection.close()
    _connection = None


def query_df(sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> pd.DataFrame:
    """Run a read query and return the result as a DataFrame.

    Every read function in queries.py should go through this. Always pass
    values through `params` (%s or %(name)s placeholders), never by building
    the SQL string yourself.

    Neon closes idle connections when it scales to zero, so a dropped
    connection is reopened and the query retried once.
    """
    for attempt in range(2):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description is None:
                    return pd.DataFrame()
                columns = [col.name for col in cur.description]
                return pd.DataFrame(cur.fetchall(), columns=columns)
        except psycopg.OperationalError:
            close()
            if attempt == 1:
                raise
    raise AssertionError("unreachable")


def sql(query: str, params: Sequence[Any] | dict[str, Any] | None = None) -> pd.DataFrame:
    """Run your own SQL and get a DataFrame back.

        sf.sql("SELECT * FROM companies WHERE industry = %s", ["Diversified Retail"])

    Pass values as parameters (%s or %(name)s) rather than pasting them into
    the string. With a read-only login, only SELECT queries are allowed.
    """
    return query_df(query, params)


def ping() -> bool:
    """Check that the database is reachable with your credentials."""
    result = query_df("SELECT 1 AS ok")
    return int(result.iloc[0, 0]) == 1