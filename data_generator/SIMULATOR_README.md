# RideStream Event Simulator

Dry-run example:

```bash
python ridestream_event_simulator.py --total-events 100 --events-per-second 5 --duplicate-pct 5 --late-pct 5 --malformed-pct 2 --seed 42
```

Publishing is enabled later with `--publish` after Event Hubs is created and credentials are retrieved securely at runtime. Never commit connection strings.
