"""Guards the public API: if a name disappears, the API and front end break."""

import pytest

import sigfinitive as sf
from sigfinitive import ingest

PUBLIC = [
    "close", "connect", "coverage", "get_company", "get_values",
    "lagged_changes", "list_companies", "list_peer_groups", "ping",
    "query_df", "screen", "sql", "zscores",
]

INGEST = [
    "normalize_metric_name", "load_values", "load_workspace_export",
    "upsert_company", "upsert_values", "replace_company",
    "save_peer_group", "delete_peer_group",
]


@pytest.mark.parametrize("name", PUBLIC)
def test_public_function_exists(name):
    assert callable(getattr(sf, name))


@pytest.mark.parametrize("name", INGEST)
def test_ingest_function_exists(name):
    assert callable(getattr(ingest, name))