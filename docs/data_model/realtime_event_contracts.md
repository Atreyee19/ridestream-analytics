# RideStream Real-Time Event Contracts

## Purpose

This document defines the structure, validation rules and processing behaviour of RideStream events published to Azure Event Hubs.

---

## Common Event Fields

Every real-time event must contain:

- `event_id`: Globally unique identifier for the event.
- `event_type`: Name of the business event.
- `event_version`: Version of the event schema.
- `event_timestamp`: UTC time when the business event happened.
- `producer_timestamp`: UTC time when the simulator published the event.
- `ride_id`: Ride business key used as the Event Hubs partition key.

### Common Optional Fields

- `source_system`: Name of the event-producing system.
- `correlation_id`: Identifier used to connect related events.
- `trace_id`: Identifier used for pipeline troubleshooting.
- `metadata`: Optional technical information about the event.

---

# Event Contracts

## 1. `ride_requested`

Generated when a passenger requests a ride.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `passenger_id`
- `pickup_location_id`
- `dropoff_location_id`
- `estimated_fare`
- `currency`

### Optional Fields

- `promotion_code`
- `special_instructions`

---

## 2. `driver_assigned`

Generated when a driver accepts or is assigned to a ride.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `driver_id`
- `vehicle_id`

### Optional Fields

- `estimated_arrival_minutes`
- `driver_distance_km`

---

## 3. `ride_started`

Generated when the passenger pickup is completed and the ride starts.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `passenger_id`
- `driver_id`
- `vehicle_id`
- `pickup_location_id`
- `pickup_at`

### Optional Fields

- `start_latitude`
- `start_longitude`

---

## 4. `ride_completed`

Generated when the passenger reaches the destination.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `passenger_id`
- `driver_id`
- `vehicle_id`
- `pickup_location_id`
- `dropoff_location_id`
- `pickup_at`
- `dropoff_at`
- `distance_km`
- `duration_minutes`
- `base_fare`
- `surge_amount`
- `discount_amount`
- `tax_amount`
- `total_fare`
- `currency`

### Optional Fields

- `toll_amount`
- `waiting_charge`
- `driver_incentive_amount`

---

## 5. `ride_cancelled`

Generated when a requested or accepted ride is cancelled.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `cancelled_at`
- `cancellation_reason`
- `cancelled_by`

### Optional Fields

- `passenger_id`
- `driver_id`
- `vehicle_id`
- `cancellation_fee`

### Accepted `cancelled_by` Values

- `PASSENGER`
- `DRIVER`
- `SYSTEM`

---

## 6. `payment_updated`

Generated when a payment is attempted, completed, failed or refunded.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `payment_id`
- `transaction_reference`
- `payment_method`
- `payment_status`
- `payment_amount`
- `currency`
- `payment_timestamp`

### Optional Fields

- `failure_reason`
- `refund_amount`
- `refund_timestamp`

### Accepted Payment Status Values

- `PENDING`
- `SUCCESS`
- `FAILED`
- `REFUNDED`

---

## 7. `driver_location_updated`

Generated when the latest driver location is received.

### Required Fields

- `event_id`
- `event_type`
- `event_version`
- `event_timestamp`
- `producer_timestamp`
- `ride_id`
- `driver_id`
- `latitude`
- `longitude`
- `location_timestamp`

### Optional Fields

- `speed_kmph`
- `heading`
- `accuracy_meters`

---

# Event Versioning

- Initial event schema version is `1`.
- New optional fields can be added without changing existing fields.
- Required fields must not be removed from an existing version.
- Existing field data types must not be changed within the same version.
- Breaking changes require a new `event_version`.
- Consumers must safely ignore unknown optional fields.

---

# Event Hubs Partitioning

- `ride_id` is the Event Hubs partition-routing key.
- Events belonging to the same ride should normally be sent to the same partition.
- Partition-level ordering will help process ride lifecycle events in sequence.
- Global ordering across all Event Hubs partitions is not assumed.

---

# Event Lateness Rules

Use the following allowed-lateness rules:

- Ride lifecycle events: `15 minutes`
- Payment events: `30 minutes`
- Driver-location events: `5 minutes`
- Master-data updates: processed using `updated_at` without an event-time lateness limit.

Events arriving within the allowed-lateness threshold will be processed normally.

Events arriving beyond the allowed-lateness threshold will be written to the late-event observation or quarantine table for investigation.

---

# Duplicate Event Behaviour

- `event_id` is the primary deduplication key.
- Events with the same `event_id` must not create duplicate Silver records.
- Duplicate events will be counted in the audit results.
- Duplicate events may be stored in an observation table for testing.
- Event replay must not create duplicate Gold facts.

---

# Out-of-Order Event Behaviour

Ride events may arrive in a different order from the actual business sequence.

Expected sequence:

```text
ride_requested
    ↓
driver_assigned
    ↓
ride_started
    ↓
ride_completed or ride_cancelled
