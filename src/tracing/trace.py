from dataclasses import dataclass
from threading import local

_thread_local = local()


@dataclass
class TraceData:
    tag: str
    trace: str


class Trace:
    def __init__(self, name: str):
        self.name = name
        self.trace_data = []

    def add_trace_data(self, tag, trace):
        self.trace_data.append(TraceData(tag, trace))


def create_trace(name: str):
    return Trace(name)


def bind_trace(trace: Trace):
    _thread_local.trace = trace


def get_trace() -> Trace:
    return getattr(_thread_local, "trace", None)
