# Prometheus SRCDS Exporter

This is an exporter for the Prometheus monitoring system.
It exports data from SRCDS Gameservers (e.g. CSGO, TF2, L4D2, ...) via rcon.
It uses the `status` and `stats` commands for this.

## How to install:

1. `git clone https://github.com/991jo/srcds_exporter.git`
2. `cd srcds_exporter`
3. `python3 -m venv .`
4. `source bin/activate`
4. `pip install -r requirements.txt`
5. `python3 main.py`

## How to query via Prometheus:

You can use the following example config.
Please adjust the IP:port in the last row to the IP:port your exporter uses.
```
  - job_name: srcds

    scrape_interval: 5s

    metrics_path: /metrics

    static_configs:
          - targets: ["<ip>:<port>:<rconpassword>"]

    relabel_configs:
        - source_labels: [__address__]
          regex: "(.+:.+):.+"
          replacement: "$1"
          target_label: __param_target
        - source_labels: [__address__]
          regex: ".+:.+:(.+)"
          replacement: "$1"
          target_label: __param_password
        - source_labels: [__param_target]
          target_label: instance
        - target_label: __address__
          replacement: 127.0.0.1:9200  # The real ip/port of the srcds_exporter
```

Basically you have to build this URL:
`http://<exporter-address>:9200/metrics?target=<host>:<port>&password=<yourrconpassword>`
You can use this URL for debugging purposes ;)

## TODO

- [x] make example config for Prometheus
- [ ] investigate aiorcon not timing out properly
- [ ] make ip and port configurable
- [ ] add a systemd unit file
