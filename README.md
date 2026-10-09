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
├── fabric_workspace/
│   └── <Fabric-managed item folders>
├── notebooks/
│   ├── 01_bronze_to_silver.py
│   └── 02_silver_to_gold.py
├── tests/
│   ├── conftest.py
│   ├── test_cleansing.py
│   └── test_gold_model.py
├── .gitignore
├── README.md
└── requirements.txt
```

`fabric_workspace/` is the target directory for native Fabric item definitions
created by Fabric Git integration. Fabric manages the item folders and their
metadata there. Do not move standalone Python or SQL source files into this
directory: they aren't converted into Fabric items by being placed there.

The `notebooks/` Python file is a source example for local development; it is
not the native notebook definition from the live workspace. The live notebook
and other supported workspace items become versioned under `fabric_workspace/`
when the workspace is connected and synced.

## 1. Local setup and Git

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The Azure Pipeline in `.azure-pipelines/fabric-ci-cd.yml` runs Flake8 and the
PySpark unit tests on pushes to `main` and `fabric-poc`. In Azure DevOps, create
a pipeline that points to this YAML file and connect it to the GitHub
repository.

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

The live Bronze-to-Silver notebook was created in the Fabric workspace. Attach
the Bronze and Silver Lakehouses to it, read the Bronze file with its ABFS path
when Bronze isn't the default Lakehouse, and save the output table while Silver
is the default Lakehouse. The native notebook definition is versioned under
`fabric_workspace/` through Fabric Git integration.

`notebooks/01_bronze_to_silver.py` documents a Python entry point for local
development. Its Fabric-specific paths and runtime imports need to be
configured for the workspace before using it there. The reusable cleansing
transformation is in `enterprise_sales_data_hub/cleansing.py` and is covered by
local pytest tests.

## 4. Silver to Gold star schema

The live Gold layer was built with Spark and saved as Delta tables in
`sales_gold_lh`: `dim_customer`, `dim_date`, and `fact_sales`. The reusable
transformations live in `enterprise_sales_data_hub/gold_model.py`; the
`notebooks/02_silver_to_gold.py` entry point reads the Silver Delta table and
writes these three tables to the notebook's default Lakehouse.

Before running the entry point in Fabric, pass the Silver table's copied ABFS
path to `process_silver_to_gold(silver_table_path=...)` and set
`sales_gold_lh` as the default Lakehouse. The write uses `overwrite`, so each
run replaces the existing Gold tables.

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

In Fabric, the PoC semantic model uses Direct Lake on OneLake over the Gold
tables. The Azure Pipeline validates Python and tests only; it does not deploy
Fabric items. Workspace synchronization is handled separately by Fabric Git
integration, while automated promotion between workspaces requires additional
deployment-pipeline configuration.
