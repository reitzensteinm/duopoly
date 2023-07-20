from dataclasses import dataclass
from threading import local
import os
from tracing.render import render_trace

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

        # Save the trace to disk using the render function
        html_trace = render_trace(self)

        # Create the traces directory if it doesn't exist
        os.makedirs("traces", exist_ok=True)

        # Save the trace to an HTML file
        with open(f"traces/{self.name}.html", "w") as f:
            f.write(html_trace)


def create_trace(name: str):
    return Trace(name)


def bind_trace(trace: Trace):
    _thread_local.trace = trace


def get_trace() -> Trace:
    return getattr(_thread_local, "trace", Trace("New Trace"))


class TraceNotFound(Exception):
    pass


def trace(tag, trace_string):
    current_trace = get_trace()
    if current_trace is None:
        raise TraceNotFound("No active trace found")
    current_trace.add_trace_data(tag, trace_string)
