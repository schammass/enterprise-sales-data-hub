"""Reusable cleansing transformations for Fabric notebooks and local tests."""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    lower,
    to_date,
    trim,
    upper,
)


def cleanse_transactions(raw_df: DataFrame) -> DataFrame:
    """Normalize transaction fields and discard rows without an identifier."""
    return (
        raw_df
        .filter(col("transaction_id").isNotNull())
        .withColumn("customer_email", lower(trim(col("customer_email"))))
        .withColumn("country_code", upper(trim(col("country_code"))))
        .withColumn(
            "transaction_date",
            to_date(col("transaction_date"), "yyyy-MM-dd"),
        )
        .withColumn("amount_usd", col("amount").cast("double"))
        .withColumn("updated_at", current_timestamp())
        .dropDuplicates(["transaction_id"])
    )
