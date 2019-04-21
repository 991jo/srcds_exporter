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

## Multi-Server vs. Single Server Mode

Initially this software was build as an exporter which can query many servers.
This conflicts a bit with the Prometheus Exporter mentality that you should
run one exporter per instance of your application.
Also you would have to know the RCON password which would get passed around
in HTTP requests.
Therefore SRCDS Exporter now supports the single server mode.
In this mode you have to specify the ip, port and password as a start
parameter. But your HTTP requests dont need those parameters anymore.
Also the exporter does not answer requests which have those fields set.

## How to query via Prometheus:

### Multi-Server-Mode

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

### Single-Server-Mode

For the single server mode you have to specify the parameters on the commandline.

    python3 main.py --server_address <server address> --server_port <port> --password <rcon password>

Your Prometheus config could look like this:

```
  - job_name: srcds

    scrape_interval: 5s

    metrics_path: /metrics

    static_configs:
          - targets: ["<ip>:<port>"]
```

## Known issues

Some servers do not respond to RCON while changing maps.
This results in timeouts and connection errors for the exporter.
This means that you won't get data while the server changes the map.
This is okay because many of the metrics are irrelevant during map change anyway
(e.g. the server FPS rate).

## Getting Help

For a list of the commandline arguments start the exporter with the `--help`
flag.
If you have other problems, feel free to open an issue.

## TODO

- [x] make example config for Prometheus
- [ ] investigate aiorcon not timing out properly
- [x] make ip and port configurable
- [ ] add a systemd unit file

## Docker Support

The Dockerfile was added by [https://github.com/xvzf]. Thanks for that.
I am not using docker, I can not give you support on that.

## More information

I wrote a blog post about this exporter. You can find it [here](http://swagspace.org/posts/srcds-exporter.html)
