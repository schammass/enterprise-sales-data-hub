"""Fabric notebook entry point for the Bronze-to-Silver transaction load."""

import os

from pyspark.sql import SparkSession

from enterprise_sales_data_hub.cleansing import cleanse_transactions


def process_bronze_to_silver(
    bronze_path: str | None = None,
    silver_table: str | None = None,
) -> None:
    """Read raw JSON transactions, cleanse them, and overwrite Silver."""
    bronze_path = bronze_path or os.environ.get(
        "BRONZE_TRANSACTIONS_PATH",
        "Files/raw/sales/raw_transactions.json",
    )
    silver_table = silver_table or os.environ.get(
        "SILVER_TRANSACTIONS_TABLE",
        "sales_silver_lh.dim_transactions_cleansed",
    )

    spark = SparkSession.builder.getOrCreate()
    raw_df = spark.read.option("multiline", "true").json(bronze_path)
    cleansed_df = cleanse_transactions(raw_df)
    (
        cleansed_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(silver_table)
    )


if __name__ == "__main__":
    process_bronze_to_silver()
