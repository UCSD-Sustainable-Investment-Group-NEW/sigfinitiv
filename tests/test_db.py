import os

import pytest

import sigfinitiv as sf
from sigfinitiv import config, db
from sigfinitiv.errors import ConfigError

ENV_VARS = [
    config.ENV_DATABASE_URL,
    config.ENV_DB_USER,
    config.ENV_DB_PASSWORD,
    config.ENV_DB_HOST,
    config.ENV_DB_NAME,
]


@pytest.fixture
def no_credentials(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(db, "_env_loaded", True)  # don't read a real .env


def test_missing_credentials_gives_clear_error(no_credentials):
    with pytest.raises(ConfigError, match="SIGFINITIVE_DB_USER"):
        db.connect()


def test_missing_host_gives_clear_error(no_credentials, monkeypatch):
    monkeypatch.setenv(config.ENV_DB_USER, "someone")
    monkeypatch.setenv(config.ENV_DB_PASSWORD, "secret")
    monkeypatch.setattr(config, "DEFAULT_HOST", "")
    with pytest.raises(ConfigError, match="host"):
        db.connect()


@pytest.mark.skipif(
    not (os.getenv(config.ENV_DATABASE_URL) or os.getenv(config.ENV_DB_USER)),
    reason="no database credentials in the environment",
)
def test_ping_live():
    assert sf.ping() is True
    sf.close()
