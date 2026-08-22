# ADLS Folder and File Standards

## Transactional Entity Folder Pattern

Use date-partitioned folders for rides, payments and ratings:

ridestream/landing/<entity>/year=<yyyy>/month=<mm>/day=<dd>/batch_id=<batch_id>/

Example:

ridestream/landing/rides/year=2026/month=08/day=22/batch_id=batch_001/

## Master Entity Folder Pattern

Use full-load and incremental folders for passengers, drivers, vehicles and locations:

ridestream/landing/<entity>/full/

ridestream/landing/<entity>/incremental/year=<yyyy>/month=<mm>/day=<dd>/batch_id=<batch_id>/

## File Naming Standard

<entity>_<load_type>_<yyyyMMdd_HHmmss>_<batch_id>.<format>

Examples:

rides_incremental_20260822_120000_batch_001.parquet

drivers_full_20260822_090000_batch_full.parquet

## Archive Folder Standard

Processed source files will be moved to:

ridestream/archive/<entity>/year=<yyyy>/month=<mm>/day=<dd>/<original_file_name>

Files must be archived only after successful downstream processing.

## Quarantine Folder Standard

Invalid files and records will be stored under:

ridestream/rejected/<entity>/year=<yyyy>/month=<mm>/day=<dd>/batch_id=<batch_id>/

Each quarantined record must include:

- batch_id
- source_file
- rejection_reason_code
- rejection_reason_text
- quarantine_timestamp
- original_payload where practical


## Storage Cleanup Runbook

- Never delete production checkpoint folders.
- Delete only disposable test checkpoints after testing.
- Keep Landing files until Bronze processing succeeds.
- Move successfully processed Landing files to Archive when archive logic is implemented.
- Keep quarantined files until errors are corrected and reprocessed.
- Delete temporary test files after validation.
- Retain Bronze, Silver, Gold and Audit data required for evidence.
- Stop all streaming jobs before deleting related checkpoints or Delta data.
- Review the exact storage path before every delete operation.
- Do not delete the ridestream container while the project is active.
