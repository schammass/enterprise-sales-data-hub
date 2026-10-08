-- Run in the sales_gold_wh Fabric Warehouse, not a Lakehouse SQL Analytics Endpoint.
-- The Silver Lakehouse must be in the same workspace for three-part references.

DROP TABLE IF EXISTS dbo.fact_sales;
DROP TABLE IF EXISTS dbo.dim_date;
DROP TABLE IF EXISTS dbo.dim_customer;

CREATE TABLE dbo.dim_customer
AS
WITH ranked_customers AS (
    SELECT
        LOWER(LTRIM(RTRIM(customer_email))) AS normalized_email,
        customer_name,
        country_code,
        ROW_NUMBER() OVER (
            PARTITION BY LOWER(LTRIM(RTRIM(customer_email)))
            ORDER BY updated_at DESC
        ) AS row_num
    FROM [sales_silver_lh].[dbo].[dim_transactions_cleansed]
    WHERE customer_email IS NOT NULL
)
SELECT
    HASHBYTES('SHA2_256', normalized_email) AS customer_key,
    customer_name,
    normalized_email AS customer_email,
    country_code
FROM ranked_customers
WHERE row_num = 1;

CREATE TABLE dbo.dim_date
AS
SELECT DISTINCT
    CAST(CONVERT(char(8), transaction_date, 112) AS int) AS date_key,
    transaction_date AS full_date,
    YEAR(transaction_date) AS [year],
    MONTH(transaction_date) AS [month],
    DAY(transaction_date) AS [day],
    DATEPART(quarter, transaction_date) AS [quarter]
FROM [sales_silver_lh].[dbo].[dim_transactions_cleansed]
WHERE transaction_date IS NOT NULL;

CREATE TABLE dbo.fact_sales
AS
SELECT
    t.transaction_id,
    HASHBYTES(
        'SHA2_256',
        LOWER(LTRIM(RTRIM(t.customer_email)))
    ) AS customer_key,
    CAST(CONVERT(char(8), t.transaction_date, 112) AS int) AS date_key,
    t.amount_usd,
    t.quantity,
    t.updated_at
FROM [sales_silver_lh].[dbo].[dim_transactions_cleansed] AS t;
