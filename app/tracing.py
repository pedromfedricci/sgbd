import socket
from os import environ
from urllib.parse import urlparse

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = structlog.get_logger("sgbd.tracing.exporter")


def _is_endpoint_reachable(endpoint: str, timeout: float = 1.0) -> bool:
    try:
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


def configure_tracing() -> None:
    resource = Resource.create(
        {
            "service.name": "sgbd.api",
            "service.version": environ.get("APP_VERSION", "0.0.0"),
        }
    )

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    endpoint = environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.warn("otlp endpoint was not provided")
        return

    if not _is_endpoint_reachable(endpoint):
        logger.warn("tracing disabled: endpoint unreachable", endpoint=endpoint)
        return

    try:
        exporter = OTLPSpanExporter(
            endpoint=f"{endpoint}/v1/traces",
            timeout=1.0,
        )

        processor = BatchSpanProcessor(
            exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
            export_timeout_millis=1000,
        )

        provider.add_span_processor(processor)
        logger.info("tracing enabled", endpoint=endpoint)
    except Exception:
        logger.exception("tracing disabled: exporter unavailable")
