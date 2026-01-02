from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from os import environ


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
        return

    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
