"""Tests for the shared Bronze-to-Silver cleansing logic."""

from enterprise_sales_data_hub.cleansing import cleanse_transactions


def test_cleanses_fields_and_drops_rows_without_transaction_id(spark):
    data = [
        ("1", "  USER@Domain.Com ", " us ", "2024-01-31", "12.50", 2),
        ("2", "TEST@domain.com", "gb", "2024-02-01", "8", 1),
        (None, "ignored@example.com", "ca", "2024-02-02", "4", 1),
    ]
    schema = [
        "transaction_id",
        "customer_email",
        "country_code",
        "transaction_date",
        "amount",
        "quantity",
    ]

    result = cleanse_transactions(spark.createDataFrame(data, schema))
    rows = {
        row["transaction_id"]: row
        for row in result.orderBy("transaction_id").collect()
    }

    assert set(rows) == {"1", "2"}
    assert rows["1"]["customer_email"] == "user@domain.com"
    assert rows["1"]["country_code"] == "US"
    assert str(rows["1"]["transaction_date"]) == "2024-01-31"
    assert rows["1"]["amount_usd"] == 12.5
    assert rows["1"]["updated_at"] is not None


def test_keeps_one_row_per_transaction_id(spark):
    data = [
        ("duplicate", "first@example.com", "us", "2024-01-01", "1", 1),
        ("duplicate", "second@example.com", "gb", "2024-01-02", "2", 2),
    ]
    schema = [
        "transaction_id",
        "customer_email",
        "country_code",
        "transaction_date",
        "amount",
        "quantity",
    ]

    result = cleanse_transactions(spark.createDataFrame(data, schema))

    assert result.count() == 1
