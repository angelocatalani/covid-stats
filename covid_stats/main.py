from prometheus_client import start_http_server, Counter
import random
import time

c  = Counter(
    namespace="app",
    subsystem="stats",
    name="covid_stats",
    documentation="doc",
    labelnames=("ctr",),
)

def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        c.labels(ctr="sample").inc()
        time.sleep(1)