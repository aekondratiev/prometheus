# prometheus telegram alert service with proxy
prometheus telegram alert service with proxy support + some other staff

# install
```
pip install -r requirements.txt
```

Change on prometheus_py_bot.py
* TOKEN
* chat_id
* proxies

# alertmanager configuration example
```
	receivers:
	- name: 'telegram'
	  webhook_configs:
	  - url: http://127.0.0.1:9119/alert
	    send_resolved: true
```      

# systemd service 

* /etc/systemd/system/prometheus-pybot.service   
```
[Unit]
Description=Tornado

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/prometheus_py_bot.py

WorkingDirectory=/tmp

User=root
Group=root

Restart=always

[Install]
WantedBy=multi-user.target
```
# Way to get the chat ID (ID permanent for all bots)
* Add bot on channel
* Send any message on this channel
* Access access the link https://api.telegram.org/botXXX:YYYY/getUpdates (xxx:yyyy botID)

# prometheus some configs

* /etc/prometheus/prometheus.yml 
```
# my global config
global:
  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets:
       - 127.0.0.1:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  - "rules/node.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'
    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    static_configs:
    - targets: ['prometheus.fqdn:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['host1.fqdn:9100', 'host2.fqdn:9100']
```

* /etc/prometheus/rules/node.yml 
```
groups:
  - name: alerting_rules
    rules:
      - alert: PreditciveHostDiskSpace
        expr: (predict_linear(node_filesystem_free_bytes{device!~"tmpfs", fstype="ext4", instance!="backup.lxc.local:9100"}[4h], 24 * 3600) / (1024 * 1024 * 1024)) < 40
        for: 10m
        labels:
          severity: warning
        annotations:
          description: 'Disk space is likely to will fill on volume
            {{ $labels.mountpoint }} within the next 24 hours for hostname: {{ $labels.instance }}, GB free: {{ $value | printf "%.1f" }}'
          summary: 'Disk will be full soon, GB free: {{ $value | printf "%.1f" }}'

      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          description: 'Host {{ $labels.instance }} has been down for more than 5 minutes.'
          summary: 'Host {{ $labels.instance }} is down'

      - alert: CpuUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="node",mode="idle"}[10m])) * 100) > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          description: 'CPU on {{ $labels.instance }} load more than 30%, is {{ $value | printf "%.1f" }}'
          summary: 'CPU on {{ $labels.instance }} load more than 30%, is {{ $value | printf "%.1f" }}'

      - alert: RamUsage
        expr: 100 * (1 - ((avg_over_time(node_memory_MemFree_bytes[24h]) + avg_over_time(node_memory_Cached_bytes[24h]) + avg_over_time(node_memory_Buffers_bytes[24h])) / avg_over_time(node_memory_MemTotal_bytes[24h]))) > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          description: 'Memory used on {{ $labels.instance }} more than 90%, is {{ $value | printf "%.1f" }}'
          summary: 'Memory used on {{ $labels.instance }} > is {{ $value | printf "%.1f" }} > 90%'
```

* /etc/prometheus/alertmanager.yml 
```
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 4h
  receiver: 'telegram-webhook'
receivers:
- name: 'telegram-webhook'
  webhook_configs:
  - url: http://127.0.0.1:9119/alert
    send_resolved: true
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```
