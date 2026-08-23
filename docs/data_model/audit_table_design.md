# RideStream Audit Table Design

## 1. Pipeline Run Audit

Table name: `pipeline_run_audit`

Purpose: Track every ADF and Databricks pipeline execution.

Columns:

- run_id
- batch_id
- pipeline_name
- entity_name
- load_type
- start_timestamp
- end_timestamp
- status
- rows_read
- rows_written
- rows_rejected
- previous_watermark
- current_watermark
- error_message
- created_at

## 2. File Processing Audit

Table name: `file_processing_audit`

Purpose: Track every source file processed by the pipeline.

Columns:

- file_audit_id
- run_id
- batch_id
- entity_name
- source_file
- source_path
- file_checksum
- file_size
- expected_row_count
- actual_row_count
- processing_status
- processed_timestamp
- error_message

## 3. Data Quality Audit

Table name: `data_quality_results`

Purpose: Store data-quality rule results for Bronze, Silver and Gold.

Columns:

- quality_result_id
- run_id
- batch_id
- entity_name
- processing_stage
- rule_id
- rule_name
- severity
- rows_checked
- failed_row_count
- status
- sample_failed_keys
- executed_at
