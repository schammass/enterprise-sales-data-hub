"""Tests for the Silver-to-Gold dimensional transformations."""

from enterprise_sales_data_hub.gold_model import build_gold_model


def test_builds_customer_date_and_sales_tables(spark):
    data = [
        (
            "T001",
            "ana@example.com",
            "Ana Silva",
            "BR",
            "2026-10-01",
            125.5,
            2,
            "2026-10-08 19:20:00",
        ),
        (
            "T002",
            "joao@example.com",
            "João Souza",
            "US",
            "2026-10-02",
            80.0,
            1,
            "2026-10-08 19:21:00",
        ),
    ]
    schema = [
        "transaction_id",
        "customer_email",
        "customer_name",
        "country_code",
        "transaction_date",
        "amount_usd",
        "quantity",
        "updated_at",
    ]
    silver_df = spark.createDataFrame(data, schema)
    silver_df = silver_df.withColumn(
        "transaction_date",
        silver_df["transaction_date"].cast("date"),
    ).withColumn("updated_at", silver_df["updated_at"].cast("timestamp"))

    dim_customer, dim_date, fact_sales = build_gold_model(silver_df)

    customers = {
        row["customer_email"]: row["customer_key"]
        for row in dim_customer.collect()
    }
    dates = {row["date_key"] for row in dim_date.collect()}
    sales = {row["transaction_id"]: row for row in fact_sales.collect()}

    assert len(customers) == 2
    assert len(set(customers.values())) == 2
    assert dates == {20261001, 20261002}
    assert set(sales) == {"T001", "T002"}
    assert sales["T001"]["customer_key"] == customers["ana@example.com"]
    assert sales["T001"]["date_key"] == 20261001
    assert sum(row["amount_usd"] for row in sales.values()) == 205.5


def test_deduplicates_customer_dimension_by_normalized_email(spark):
    data = [
        (
            "T001",
            " ANA@example.com ",
            "Ana",
            "BR",
            "2026-10-01",
            10.0,
            1,
            "2026-10-08 19:20:00",
        ),
        (
            "T002",
            "ana@example.com",
            "Ana Updated",
            "BR",
            "2026-10-02",
            20.0,
            1,
            "2026-10-08 19:21:00",
        ),
    ]
    schema = [
        "transaction_id",
        "customer_email",
        "customer_name",
        "country_code",
        "transaction_date",
        "amount_usd",
        "quantity",
        "updated_at",
    ]
    silver_df = spark.createDataFrame(data, schema)
    silver_df = silver_df.withColumn(
        "transaction_date",
        silver_df["transaction_date"].cast("date"),
    ).withColumn("updated_at", silver_df["updated_at"].cast("timestamp"))

    dim_customer, _, _ = build_gold_model(silver_df)
    customers = dim_customer.collect()

    assert len(customers) == 1
    assert customers[0]["customer_email"] == "ana@example.com"
    assert customers[0]["customer_name"] == "Ana Updated"
