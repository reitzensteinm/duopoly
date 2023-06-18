from dataclasses import dataclass
from threading import local

_thread_local = local()


@dataclass
class TraceData:
    type: str
    trace: str


@dataclass
class Trace:
    trace_data_list: list[TraceData]


def create_trace():
    return Trace(trace_data_list=[])


def bind_trace(trace: Trace):
    _thread_local.trace = trace


def get_trace() -> Trace:
    return getattr(_thread_local, "trace", None)
