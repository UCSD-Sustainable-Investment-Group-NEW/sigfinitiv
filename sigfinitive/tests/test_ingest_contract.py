import pandas as pd
import pytest

from sigfinitive.errors import ContractError
from sigfinitive.ingest import load_values, normalize_metric_name


@pytest.mark.parametrize(
    "label, key",
    [
        ("CO2 Equivalent Emissions Total", "co2_equivalent_emissions_total"),
        ("Revenue from Goods & Services", "revenue_from_goods_services"),
        ("Net Margin - %", "net_margin_pct"),
        ("  Energy Use Total ", "energy_use_total"),
        ("Total Energy Use / Million in Revenue $", "total_energy_use_million_in_revenue"),
        ("already_normalized", "already_normalized"),
    ],
)
def test_normalize_metric_name(label, key):
    assert normalize_metric_name(label) == key


ROWS = [
    {"Ticker": "cost.o", "Year": 2023, "Metric": "Net Margin - %", "Value": 2.6, "Category": "Financial"},
    {"Ticker": "COST.O", "Year": 2023, "Metric": "CO2 Equivalent Emissions Total", "Value": 2900000, "Category": "ESG"},
    {"Ticker": "COST.O", "Year": 2022, "Metric": "Energy Use Total", "Value": "--", "Category": "esg"},
]
EXPECTED_COLUMNS = ["ticker", "year", "metric", "value", "category"]


def test_load_from_dataframe_cleans_values():
    out = load_values(pd.DataFrame(ROWS))
    assert list(out.columns) == EXPECTED_COLUMNS
    assert len(out) == 2  # the "--" row is dropped
    assert set(out["metric"]) == {"net_margin_pct", "co2_equivalent_emissions_total"}
    assert set(out["ticker"]) == {"COST.O"}
    assert set(out["category"]) == {"esg", "financial"}


def test_load_from_csv(tmp_path):
    path = tmp_path / "values.csv"
    pd.DataFrame(ROWS).to_csv(path, index=False)
    assert len(load_values(path)) == 2


def test_load_from_excel(tmp_path):
    path = tmp_path / "values.xlsx"
    pd.DataFrame(ROWS).to_excel(path, index=False, sheet_name="data")
    assert len(load_values(path, sheet="data")) == 2


def test_rejects_unsupported_file(tmp_path):
    path = tmp_path / "values.txt"
    path.write_text("x")
    with pytest.raises(ContractError, match="Unsupported"):
        load_values(path)


def test_rejects_missing_column():
    with pytest.raises(ContractError, match="Missing columns"):
        load_values(pd.DataFrame(ROWS).drop(columns=["Category"]))


def test_rejects_unknown_category():
    df = pd.DataFrame(ROWS)
    df.loc[0, "Category"] = "other"
    with pytest.raises(ContractError, match="Unknown categories"):
        load_values(df)


def test_rejects_duplicates_after_normalizing():
    df = pd.DataFrame([ROWS[0], {**ROWS[0], "Metric": "net margin %"}])
    with pytest.raises(ContractError, match="repeat"):
        load_values(df)