# ADF Naming and Parameter Standards

## Naming Standards

- Linked services: `ls_<system>_<project>`
- Datasets: `ds_<system>_<entity>`
- Pipelines: `pl_<action>_<entity>`
- Triggers: `tr_<frequency>_<pipeline>`
- Lookup activities: `lookup_<purpose>`
- Copy activities: `copy_<source>_to_<target>`
- Databricks activities: `run_<layer>_<entity>`
- Variables: `v_<name>`
- Parameters: `p_<name>`

## Existing Examples

- `ls_postgresql_ridestream`
- `ls_adls_ridestream`
- `ls_keyvault_ridestream`
- `ls_databricks_ridestream`
- `ds_postgresql_passengers`
- `ds_adls_passengers`
- `pl_full_load_passengers`
- `pl_incremental_passengers`

## Pipeline Parameter Strategy

The following parameters will be passed dynamically:

- `p_environment`
- `p_entity_name`
- `p_load_type`
- `p_load_date`
- `p_batch_id`
- `p_source_path`
- `p_target_path`
- `p_previous_watermark`
- `p_current_watermark`
- `p_checkpoint_path`
- `p_notebook_path`

Environment value:

- `dev`

Load-type values:

- `FULL`
- `INCREMENTAL`
- `BACKFILL`
- `RECOVERY`

Parameters will allow one generic pipeline to process multiple entities without creating separate pipelines for every table.
