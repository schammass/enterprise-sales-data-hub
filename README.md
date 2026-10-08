# Enterprise Sales Data Hub

Starter project for a Microsoft Fabric medallion pipeline that transforms raw
sales transactions into a dimensional model for Power BI.

## Repository layout

```text
.
├── .azure-pipelines/
│   └── fabric-ci-cd.yml
├── docker/
│   └── Dockerfile
├── data/
│   └── raw/
│       └── sales/
│           └── raw_transactions.json
├── enterprise_sales_data_hub/
│   └── cleansing.py
├── notebooks/
│   └── 01_bronze_to_silver.py
├── sql/
│   └── 01_gold_star_schema.sql
├── tests/
│   ├── conftest.py
│   └── test_cleansing.py
├── .gitignore
├── README.md
└── requirements.txt
```

## 1. Local setup and Git

Initialize the repository if it has not already been initialized, then create
and activate a Python 3.10 virtual environment:

```bash
git init
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The Azure Pipeline in `.azure-pipelines/fabric-ci-cd.yml` runs Flake8 and the
PySpark unit tests on pushes to `main`. In Azure DevOps, create a pipeline that
points to this YAML file.

## 2. Bronze ingestion in Fabric

Create three Lakehouses in the Fabric workspace:

- `sales_bronze_lh` for raw files.
- `sales_silver_lh` for cleansed Delta tables.
- `sales_gold_lh` for Gold data if the Gold model is stored in a Lakehouse.

In `sales_bronze_lh`, create a OneLake Shortcut under
`Files/raw/sales/` to the source directory in ADLS Gen2 or Amazon S3. Configure
the connection and credentials in Fabric; do not put credentials in this
repository.

For this training PoC, `data/raw/sales/raw_transactions.json` is a small
synthetic sample that you can upload directly to `Files/raw/sales/` in the
Bronze Lakehouse instead of configuring an external shortcut.

## 3. Bronze to Silver

Import `notebooks/01_bronze_to_silver.py` into a Fabric notebook. Attach the
Bronze and Silver Lakehouses, set `BRONZE_TRANSACTIONS_PATH` to the JSON file
path, and set `SILVER_TRANSACTIONS_TABLE` to the fully qualified Silver table
name if the defaults do not match the workspace. For example, an absolute
OneLake ABFS path can be supplied for the Bronze JSON file.

The reusable transformation is in
`enterprise_sales_data_hub/cleansing.py`; it can be validated locally with
pytest before publishing or running the notebook.

## 4. Silver to Gold star schema

The script in `sql/01_gold_star_schema.sql` uses Fabric Warehouse CTAS syntax
and expects a Fabric Warehouse named `sales_gold_wh`, with the Silver Lakehouse
`sales_silver_lh` in the same workspace. Run it in that Warehouse's SQL
editor. It recreates the customer and date dimensions and sales fact table on
each run.

The Lakehouse SQL Analytics Endpoint is read-only for data-definition and
write operations; do not run this CTAS script against that endpoint. If Gold
must be stored in `sales_gold_lh`, implement the table writes through Spark
instead.

## 5. Local tests and Power BI

Run the local checks with:

```bash
flake8 enterprise_sales_data_hub notebooks tests
pytest tests/
```

For a local container test environment, build and run:

```bash
docker build -f docker/Dockerfile -t enterprise-sales-data-hub .
docker run --rm enterprise-sales-data-hub
```

In Fabric, create a semantic model over the Gold tables and use Direct Lake
where supported by the workspace and model configuration. The Azure Pipeline
currently validates Python and tests only; publishing Fabric items and binding
deployment-pipeline stages require workspace-specific identities, connections,
and deployment configuration and are not automated by this starter pipeline.
