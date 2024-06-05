from dataclasses import dataclass
from threading import local
import os
from typing import Optional, Tuple
from tracing.render import render_trace

_thread_local = local()


@dataclass
class TraceData:
    tag: str
    trace: str
    tokens: Optional[Tuple[int, int]] = None


class Trace:

    def __init__(self, name: str):
        from datetime import datetime

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.name = f"{current_time}_{name}"
        self.trace_data = []

    def add_trace_data(
        self, tag: str, trace: str, tokens: Optional[Tuple[int, int]] = None
    ) -> None:
        """
        Add trace data with the given tag, trace, and optional tokens to the trace.
        Args:
                tag: The tag associated with the trace data.
                trace: The HTML trace to be written.
                tokens: An optional tuple indicating the start and end tokens.
        Returns:
                None
        """
        if self.name == "":
            return
        self.trace_data.append(TraceData(tag, trace, tokens))
        html_trace = render_trace(self)
        os.makedirs("traces", exist_ok=True)
        with open(f"traces/{self.name}.html", "w", encoding="utf-8") as f:
            f.write(html_trace)


def create_trace(name: str):
    return Trace(name)


def bind_trace(trace: Trace):
    _thread_local.trace = trace


def get_trace() -> Trace:
    return getattr(_thread_local, "trace", Trace(""))


class TraceNotFound(Exception):
    pass


def trace(tag, trace_string, tokens: Optional[Tuple[int, int]] = None):
    current_trace = get_trace()
    if current_trace is None:
        raise TraceNotFound("No active trace found")
    current_trace.add_trace_data(tag, trace_string, tokens)
