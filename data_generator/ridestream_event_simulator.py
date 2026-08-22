"""RideStream synthetic Event Hubs simulator.

Runs in dry-run mode by default. Later, --publish sends events to Azure Event Hubs
using a connection string supplied securely through the EVENT_HUB_CONNECTION_STRING
environment variable and EVENT_HUB_NAME.
"""

import argparse
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

EVENT_TYPES = [
    "ride_requested",
    "driver_assigned",
    "ride_started",
    "ride_completed",
    "ride_cancelled",
    "payment_updated",
    "driver_location_updated",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def common_event(event_type: str, ride_id: int, event_time: datetime) -> Dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": 1,
        "event_timestamp": iso_utc(event_time),
        "producer_timestamp": iso_utc(utc_now()),
        "ride_id": ride_id,
        "source_system": "ridestream_simulator",
    }


def build_event(event_type: str, ride_id: int, event_time: datetime, rng: random.Random) -> Dict[str, Any]:
    event = common_event(event_type, ride_id, event_time)
    passenger_id = ((ride_id - 1) % 10_000) + 1
    driver_id = ((ride_id - 1) % 2_000) + 1
    vehicle_id = driver_id
    pickup_id = ((ride_id - 1) % 500) + 1
    dropoff_id = (pickup_id % 500) + 1

    if event_type == "ride_requested":
        event.update({"passenger_id": passenger_id, "pickup_location_id": pickup_id,
                      "dropoff_location_id": dropoff_id,
                      "estimated_fare": round(rng.uniform(100, 700), 2), "currency": "INR"})
    elif event_type == "driver_assigned":
        event.update({"driver_id": driver_id, "vehicle_id": vehicle_id,
                      "estimated_arrival_minutes": rng.randint(2, 12)})
    elif event_type == "ride_started":
        event.update({"passenger_id": passenger_id, "driver_id": driver_id,
                      "vehicle_id": vehicle_id, "pickup_location_id": pickup_id,
                      "pickup_at": iso_utc(event_time)})
    elif event_type == "ride_completed":
        distance = round(rng.uniform(2, 35), 2)
        base = round(60 + distance * 14, 2)
        surge = round(base * 0.20, 2) if ride_id % 5 == 0 else 0.0
        discount = 25.0 if ride_id % 7 == 0 else 0.0
        tax = round(base * 0.05, 2)
        total = round(max(base + surge + tax - discount, 0), 2)
        event.update({"passenger_id": passenger_id, "driver_id": driver_id,
                      "vehicle_id": vehicle_id, "pickup_location_id": pickup_id,
                      "dropoff_location_id": dropoff_id,
                      "pickup_at": iso_utc(event_time - timedelta(minutes=25)),
                      "dropoff_at": iso_utc(event_time), "distance_km": distance,
                      "duration_minutes": 25, "base_fare": base,
                      "surge_amount": surge, "discount_amount": discount,
                      "tax_amount": tax, "total_fare": total, "currency": "INR"})
    elif event_type == "ride_cancelled":
        event.update({"cancelled_at": iso_utc(event_time),
                      "cancellation_reason": "Synthetic cancellation",
                      "cancelled_by": rng.choice(["PASSENGER", "DRIVER", "SYSTEM"]),
                      "passenger_id": passenger_id, "driver_id": driver_id})
    elif event_type == "payment_updated":
        event.update({"payment_id": ride_id, "transaction_reference": f"TXN-{ride_id:010d}",
                      "payment_method": rng.choice(["CASH", "UPI", "CREDIT_CARD", "DEBIT_CARD", "WALLET"]),
                      "payment_status": rng.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"]),
                      "payment_amount": round(rng.uniform(100, 700), 2), "currency": "INR",
                      "payment_timestamp": iso_utc(event_time)})
    elif event_type == "driver_location_updated":
        event.update({"driver_id": driver_id, "latitude": round(rng.uniform(22.45, 22.65), 7),
                      "longitude": round(rng.uniform(88.25, 88.50), 7),
                      "location_timestamp": iso_utc(event_time),
                      "speed_kmph": round(rng.uniform(0, 60), 1)})
    return event


def make_malformed(rng: random.Random) -> str:
    return rng.choice([
        '{"event_id": "broken", "event_type": ',
        json.dumps({"event_id": str(uuid.uuid4()), "event_type": "ride_requested"}),
        "not-json-at-all",
    ])


def generate_messages(total: int, duplicate_pct: float, late_pct: float,
                      malformed_pct: float, seed: int) -> List[str]:
    rng = random.Random(seed)
    messages: List[str] = []
    valid_messages: List[str] = []
    start_ride_id = 300_001

    for index in range(total):
        if rng.random() < malformed_pct / 100:
            messages.append(make_malformed(rng))
            continue

        event_type = EVENT_TYPES[index % len(EVENT_TYPES)]
        event_time = utc_now()
        if rng.random() < late_pct / 100:
            event_time -= timedelta(minutes=rng.randint(20, 120))
        event = build_event(event_type, start_ride_id + index // len(EVENT_TYPES), event_time, rng)
        payload = json.dumps(event, separators=(",", ":"))
        messages.append(payload)
        valid_messages.append(payload)

        if valid_messages and rng.random() < duplicate_pct / 100:
            messages.append(rng.choice(valid_messages))
    return messages


def publish_messages(messages: List[str]) -> None:
    connection_string = os.getenv("EVENT_HUB_CONNECTION_STRING")
    event_hub_name = os.getenv("EVENT_HUB_NAME", "ride-events")
    if not connection_string:
        raise RuntimeError("EVENT_HUB_CONNECTION_STRING is not set securely at runtime.")
    from azure.eventhub import EventData, EventHubProducerClient

    producer = EventHubProducerClient.from_connection_string(
        conn_str=connection_string, eventhub_name=event_hub_name
    )
    try:
        for payload in messages:
            batch = producer.create_batch(partition_key=_partition_key(payload))
            batch.add(EventData(payload))
            producer.send_batch(batch)
    finally:
        producer.close()


def _partition_key(payload: str) -> str:
    try:
        return str(json.loads(payload).get("ride_id", "invalid"))
    except json.JSONDecodeError:
        return "malformed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events-per-second", type=float, default=5.0)
    parser.add_argument("--total-events", type=int, default=100)
    parser.add_argument("--duplicate-pct", type=float, default=5.0)
    parser.add_argument("--late-pct", type=float, default=5.0)
    parser.add_argument("--malformed-pct", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--output", default="simulator_output.jsonl")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    messages = generate_messages(args.total_events, args.duplicate_pct,
                                 args.late_pct, args.malformed_pct, args.seed)

    with open(args.output, "w", encoding="utf-8") as handle:
        for message in messages:
            handle.write(message + "\n")

    logging.info(json.dumps({
        "status": "generated", "requested_event_count": args.total_events,
        "actual_message_count": len(messages), "output": args.output,
        "publish_enabled": args.publish, "seed": args.seed,
    }))

    if args.publish:
        delay = 1.0 / max(args.events_per_second, 0.1)
        for message in messages:
            publish_messages([message])
            time.sleep(delay)
        logging.info(json.dumps({"status": "published", "count": len(messages)}))


if __name__ == "__main__":
    main()
