"""Fabric notebook entry point for the Silver-to-Gold star-schema load."""

import os

from pyspark.sql import SparkSession

from enterprise_sales_data_hub.gold_model import build_gold_model


def process_silver_to_gold(
    silver_table_path: str | None = None,
) -> None:
    """Read the Silver Delta table and overwrite the three Gold tables."""
    silver_table_path = silver_table_path or os.environ.get(
        "SILVER_TRANSACTIONS_PATH"
    )
    if not silver_table_path:
        raise ValueError(
            "Provide the Silver table ABFS path using "
            "silver_table_path or SILVER_TRANSACTIONS_PATH."
        )

    spark = SparkSession.builder.getOrCreate()
    silver_df = spark.read.format("delta").load(silver_table_path)
    dim_customer, dim_date, fact_sales = build_gold_model(silver_df)

    for table_name, dataframe in (
        ("dim_customer", dim_customer),
        ("dim_date", dim_date),
        ("fact_sales", fact_sales),
    ):
        (
            dataframe.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(table_name)
        )


if __name__ == "__main__":
    process_silver_to_gold()
