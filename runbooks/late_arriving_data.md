# Late-Arriving Data Handling

## Late-Arriving Fact Behaviour

A fact is considered late when its business event date is earlier than its arrival or ingestion date.

Late Ride and Payment facts are still processed when their `updated_at` value is newer than the committed watermark. Delta MERGE inserts unseen facts and updates existing facts only when the incoming record is newer.

After processing a late fact, only the affected Gold date, partition, or aggregate key is recalculated instead of rebuilding every Gold record.

## Late-Arriving Dimension Behaviour

When a required Driver, Passenger, Vehicle, or Location dimension is unavailable, the related fact temporarily uses the Unknown surrogate key.

After the missing dimension arrives, the affected fact can be updated with the correct surrogate key.

For SCD Type 2 dimensions, the correct historical dimension version is selected by matching the fact event timestamp against the dimension's `effective_from` and `effective_to` validity range.
