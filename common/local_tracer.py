"""
A tiny tracer that writes every model call and tool call to a JSONL file.

It shows what observability platforms (Langfuse, LangSmith, Phoenix) capture, and it works offline.
Each line is one event: run_id, parent_run_id, type, name, inputs/outputs, tokens, timings.
"""
import json
import time
import uuid
from datetime import datetime, timezone

from langchain_core.callbacks import BaseCallbackHandler


class LocalTracer(BaseCallbackHandler):
    def __init__(self, path: str = "traces.jsonl", trace_id: str = None, user_id: str = None):
        self.path = path
        self.trace_id = trace_id or uuid.uuid4().hex[:12]
        self.user_id = user_id
        self._start = {}

    def _write(self, event: dict):
        event.update({"ts": datetime.now(timezone.utc).isoformat(), "trace_id": self.trace_id, "user_id": self.user_id})
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")

    # --- model calls ---
    def on_chat_model_start(self, serialized, messages, *, run_id, parent_run_id=None, **kw):
        self._start[run_id] = time.perf_counter()
        last = messages[0][-1] if messages and messages[0] else None
        self._write({"type": "llm_start", "run_id": str(run_id), "parent_run_id": str(parent_run_id),
                     "n_messages": len(messages[0]) if messages else 0,
                     "last_message": getattr(last, "content", "")[:500]})

    def on_llm_end(self, response, *, run_id, **kw):
        gen = response.generations[0][0]
        msg = getattr(gen, "message", None)
        usage = getattr(msg, "usage_metadata", None) or {}
        self._write({"type": "llm_end", "run_id": str(run_id),
                     "latency_ms": round((time.perf_counter() - self._start.pop(run_id, time.perf_counter())) * 1000),
                     "tool_calls": getattr(msg, "tool_calls", []), "output": (gen.text or "")[:500],
                     "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0)})

    def on_llm_error(self, error, *, run_id, **kw):
        self._write({"type": "llm_error", "run_id": str(run_id), "error": repr(error)})

    # --- tool calls ---
    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, **kw):
        self._start[run_id] = time.perf_counter()
        self._write({"type": "tool_start", "run_id": str(run_id), "parent_run_id": str(parent_run_id),
                     "tool": (serialized or {}).get("name"), "input": input_str[:500]})

    def on_tool_end(self, output, *, run_id, **kw):
        self._write({"type": "tool_end", "run_id": str(run_id),
                     "latency_ms": round((time.perf_counter() - self._start.pop(run_id, time.perf_counter())) * 1000),
                     "output": str(getattr(output, "content", output))[:500]})

    def on_tool_error(self, error, *, run_id, **kw):
        self._write({"type": "tool_error", "run_id": str(run_id), "error": repr(error)})
