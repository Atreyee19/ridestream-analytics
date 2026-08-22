# RideStream Azure Resource Configuration

## Naming Convention

Pattern:

`ridestream-<resource-type>-dev`

Existing resource names are retained to avoid unnecessary cost and re-creation.

## Resource Tags

- project: RideStream Analytics
- environment: dev
- owner: portfolio
- purpose: real-time-data-engineering

## Resource Group

- Resource group: Streaming_ride_project

## Existing Resources

- PostgreSQL: ridestream-postgres-2002
- ADLS Gen2: streamingridestorage
- Azure Data Factory: ridestream-azuredf
- Azure Databricks: streamingRideDataboricks
- Databricks Access Connector: ridestream-access-connector
- Databricks SQL Warehouse: ridestream_dbt_warehouse
- Unity Catalog: ridestream_catalog

## Environment Strategy

Only the `dev` environment is implemented in this portfolio project.

## Environment Parameterization

Environment-specific resource names, paths and settings will be passed through:

- ADF pipeline parameters
- Databricks notebook widgets
- Databricks job parameters
- Configuration files
- Airflow variables

## Region

All new compatible Azure resources will use the same region as the existing Databricks, ADLS and ADF resources.

Verified project region: `<enter-region-after-checking>`
``
