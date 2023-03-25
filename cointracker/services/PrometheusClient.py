import logging

import prometheus_client
from prometheus_async.aio import time as aio_time
from prometheus_client import start_wsgi_server, Counter, Histogram

from cointracker.utils.utils import get_config


class PrometheusClient:
    def __init__(self):
        self.logger = logging.getLogger('main')
        self.config = get_config().prometheus
        self.port = self.config.port
        self.setup()

    @staticmethod
    def setup():
        # Disabling Default Collector metrics (process, gc, and platform)
        prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
        prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
        prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    def run_server(self):
        self.logger.info(f"Starting Prometheus server on port {self.port}")
        start_wsgi_server(self.port)

    @staticmethod
    def get_request_counter():
        c = Counter("requests", '', ['bot_uuid', 'label'])
        return c

    @staticmethod
    def get_latency_summary(bot_uuid, label):
        h = Histogram("request_time_seconds", "", ['bot_uuid', 'path_name'])
        h = h.labels(bot_uuid, label)
        return h

    @staticmethod
    def get_metrics_obj(metric_type, label=None, bot_uuid=None):
        if metric_type == "latency":
            return aio_time(PrometheusClient.get_latency_summary(bot_uuid, label))
        elif metric_type == "counter":
            return PrometheusClient.get_request_counter()
