# RideStream Event Hubs Configuration

## Resource Configuration

- Namespace: ridestream-eventhubs-dev
- Event Hub: ride-events
- Region: Central India
- Pricing tier: Standard
- Throughput units: 1
- Partition count: 2
- Partition key: ride_id
- Retention period: 1 day
- Databricks consumer group: databricks-bronze-cg

## Security Configuration

- Simulator policy: simulator-send
- Simulator permission: Send only
- Databricks policy: databricks-listen
- Databricks permission: Listen only
- Connection strings must not be stored in GitHub or notebooks.
- Connection strings must be retrieved securely at runtime.

## Cleanup and Shutdown Checklist

- Stop the Python event simulator after testing.
- Stop Databricks Structured Streaming queries safely.
- Stop Databricks compute after testing.
- Keep Event Hubs only while real-time development is active.
- Remove unnecessary temporary authorization policies.
- Capture required evidence before deleting Event Hubs.
- Delete the Event Hubs namespace after the final portfolio demonstration if it is no longer required.
