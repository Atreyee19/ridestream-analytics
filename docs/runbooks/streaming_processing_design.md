# RideStream Streaming Processing Design

## Event Hubs Offsets and Streaming Checkpoints

Azure Event Hubs exposes Kafka-compatible partition offsets for every event.

The Structured Streaming checkpoint stores the offsets that were successfully processed and committed. When the stream restarts using the same checkpoint, processing continues from the committed offsets without reprocessing earlier events.

A new or deleted checkpoint may cause retained Event Hubs events to be replayed. Therefore, production checkpoints must never be manually deleted. Checkpoint-loss experiments must use a separate disposable path.

## Watermark and State Management

RideStream uses a 10-minute watermark on `event_timestamp`.

The watermark limits how long Spark retains state for operations such as event deduplication. Events arriving within the allowed 10-minute lateness window can be processed normally.

Events arriving beyond the threshold are recorded in a separate late-events observation or quarantine table. A late older event must not overwrite a newer ride state.

## Schema Evolution

Streaming JSON is parsed using an explicit schema.

A new optional field does not break processing. Known fields continue to be parsed, while the complete original JSON remains available in `raw_event_payload`.

Approved schema changes are recorded with the entity, schema version, changed column, source file, affected row count, status, and timestamp.

## Malformed Data and Quarantine

Malformed JSON and records failing critical validation rules do not enter the valid Silver path.

Quarantined records preserve:

- Entity name
- Batch ID
- Source file
- Reason code
- Reason description
- Quarantine timestamp
- Original raw payload

A corrected file is submitted as a new controlled batch. Valid corrected records can then be reprocessed without modifying or deleting the original quarantine evidence.

## Deduplication and Checkpointing

Deduplication and checkpointing solve different problems.

Checkpointing tracks which source files or Event Hubs offsets have already been processed.

Deduplication removes repeated business records or events from the incoming data. Ride events are deduplicated using `event_id`. Repeated ride-state events can also be checked using `ride_id`, `event_type`, and `event_timestamp`.

Batch Ride records are deduplicated using `ride_id`, ordered by the latest `updated_at` and `bronze_ingestion_timestamp`.

## Late-Arriving Facts

A fact is late when its business event date is earlier than its arrival or ingestion date.

Late Ride and Payment facts are still processed when their `updated_at` value is newer than the existing target record. Delta MERGE inserts unseen facts and updates existing facts only when the incoming record is newer.

Only affected Gold dates, partitions, or aggregate keys are recalculated after a late fact is processed.

## Late-Arriving Dimensions

When a required Driver, Passenger, Vehicle, or Location dimension is unavailable, the related fact temporarily uses the Unknown surrogate key.

After the missing dimension arrives, the affected fact can be updated with the correct surrogate key.

For SCD Type 2 dimensions, the correct historical version is selected by matching the fact event timestamp between the dimension’s `effective_from` and `effective_to` values.

## End-to-End Idempotency Chain

### File-Discovery Level

ADF checks source paths and file-processing metadata before processing. A previously completed source file must not create another logical load unless controlled reprocessing is explicitly enabled.

### Bronze Checkpoint Level

Auto Loader checkpoints track discovered files, while Structured Streaming checkpoints track committed Event Hubs offsets. Restarting with the same checkpoint processes only new files or events.

### Silver MERGE Level

Silver tables use stable business keys such as `ride_id` and `payment_id`. Incoming records are deduplicated before Delta MERGE. Existing records are updated only when the incoming `updated_at` value is newer or the approved record hash has changed.

### Gold MERGE Level

Gold facts and aggregates use stable fact keys or aggregate keys. Reprocessing the same Silver records must update the existing Gold rows instead of inserting duplicate rows.

### Audit Level

The logical audit uniqueness concept is:

`batch_id + entity_name + processing_stage`

A completed combination must not create another successful audit result during an identical rerun. Controlled retries and reprocessing must retain traceable run information.

### Complete Idempotency Chain

1. ADF prevents unintended duplicate file discovery.
2. Auto Loader checkpoints prevent already committed files from being loaded again.
3. Event Hubs checkpoints prevent committed offsets from being reprocessed.
4. Silver deduplication removes repeated business records and events.
5. Silver Delta MERGE prevents duplicate target rows.
6. Gold Delta MERGE prevents duplicate facts and aggregates.
7. Audit uniqueness prevents duplicate completion records.
8. Identical reruns must leave Silver and Gold row counts unchanged.
9. A failed run must not commit an incorrect watermark.

## Near-Real-Time Gold Processing

### Target Analytics Latency

The RideStream portfolio demonstration targets an end-to-end analytics latency of five minutes or less from Event Hubs publication to Gold analytical output.

Actual latency depends on Databricks compute startup time, micro-batch frequency, Event Hubs availability, Delta MERGE duration, and reporting refresh mode.

### Gold Update Method

Gold Ride Fact records will be updated using short controlled micro-batches with `foreachBatch` and Delta MERGE.

Each micro-batch processes only newly accepted Silver ride-state events. A Ride Fact row is inserted for a new ride and updated as the ride progresses through requested, assigned, started, completed, or cancelled states.

The process prevents older out-of-order events from replacing a newer Ride Fact state.

### ADF and Structured Streaming Responsibilities

Azure Data Factory remains the batch and control-plane orchestrator.

ADF is responsible for:

- Master-data ingestion
- Scheduled dimension refreshes
- Backfills
- Data-quality checks
- Recovery workflows
- Stream-health monitoring
- Databricks notebook and job orchestration

PySpark Structured Streaming is responsible for:

- Reading live events from Event Hubs
- Checkpoint-based offset tracking
- Watermarking
- Stateful deduplication
- Micro-batch processing
- Silver current-state updates
- Near-real-time Gold updates

ADF does not process every streaming event. Databricks Structured Streaming continuously or periodically processes live events, while ADF manages scheduled and operational workflows.
