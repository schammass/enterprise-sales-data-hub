"""Shared pytest fixtures."""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Provide one local Spark session for the test suite."""
    session = (
        SparkSession.builder
        .appName("testing-enterprise-sales-data-hub")
        .master("local[1]")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
