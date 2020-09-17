from prometheus_client import start_http_server, Counter
import time

# app_stats_covid_stats_total{ctr="sample",instance="app:8000",job="app"}
sample_counter = Counter(
    namespace="app",
    subsystem="stats",
    name="covid_stats",
    documentation="doc",
    labelnames=("ctr",),
)


if __name__ == '__main__':
    start_http_server(8000)
    while True:
        pass

