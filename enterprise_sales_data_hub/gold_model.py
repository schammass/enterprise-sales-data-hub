"""Gold star-schema transformations shared by notebooks and local tests."""

from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import (
    col,
    date_format,
    dayofmonth,
    lower,
    month,
    quarter,
    row_number,
    sha2,
    trim,
    year,
)


def build_gold_model(
    silver_df: DataFrame,
) -> tuple[DataFrame, DataFrame, DataFrame]:
    """Build customer and date dimensions plus the sales fact table."""
    customer_window = Window.partitionBy("_normalized_email").orderBy(
        col("updated_at").desc_nulls_last(),
        col("customer_name").asc_nulls_last(),
    )

    dim_customer = (
        silver_df
        .filter(col("customer_email").isNotNull())
        .withColumn(
            "_normalized_email",
            lower(trim(col("customer_email"))),
        )
        .withColumn("_row_number", row_number().over(customer_window))
        .filter(col("_row_number") == 1)
        .select(
            sha2(col("_normalized_email"), 256).alias("customer_key"),
            "customer_name",
            col("_normalized_email").alias("customer_email"),
            "country_code",
        )
    )

    dim_date = (
        silver_df
        .filter(col("transaction_date").isNotNull())
        .select("transaction_date")
        .distinct()
        .select(
            date_format("transaction_date", "yyyyMMdd")
            .cast("int")
            .alias("date_key"),
            col("transaction_date").alias("full_date"),
            year("transaction_date").alias("year"),
            month("transaction_date").alias("month"),
            dayofmonth("transaction_date").alias("day"),
            quarter("transaction_date").alias("quarter"),
        )
    )

    fact_sales = silver_df.select(
        "transaction_id",
        sha2(
            lower(trim(col("customer_email"))),
            256,
        ).alias("customer_key"),
        date_format("transaction_date", "yyyyMMdd")
        .cast("int")
        .alias("date_key"),
        "amount_usd",
        "quantity",
        "updated_at",
    )

    return dim_customer, dim_date, fact_sales
