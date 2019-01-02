# Prometheus SRCDS Exporter

This is an exporter for the Prometheus monitoring system.
It exports data from SRCDS Gameservers (e.g. CSGO, TF2, L4D2, ...) via rcon.
It uses the status and stats commands for this.

## How to install:

1. clone this repository
2. cd srcds_exporter
3. python3 -m venv .
4. source bin/activate
4. pip install -r requirements.txt
5. python3 main.py

## How to query via Prometheus:

you have to use the URL http://<exporter-address>:9200/metrics?target=<host>:<port>&password=<yourrconpassword>

## TODO

- [ ] make example config for Prometheus
- [ ] investigate aiorcon not timing out properly
