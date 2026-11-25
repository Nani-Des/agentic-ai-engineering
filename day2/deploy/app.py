"""
Lab 6: the agent as a web API.

Run locally:   uvicorn app:app --reload --port 8000      (from the day2/deploy folder)
Docs:          http://localhost:8000/docs
Test:          curl -X POST localhost:8000/chat -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
                    -d '{"message": "Show me MTN bundles", "session_id": "s1"}'

Production basics shown here: API key auth, per-key rate limit, input size limit, timeouts via
recursion_limit, structured JSON logs, health check, and no secrets in code.
"""
import json
import logging
import os
import sys
import time
from collections import defaultdict, deque

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import Depends, FastAPI, Header, HTTPException
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

from common.bank_agent import ask, build_graph
from common.llm import model_name, provider

API_KEYS = set(filter(None, os.getenv("APP_API_KEYS", "dev-key").split(",")))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))
MAX_INPUT_CHARS = 1000

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("agent-api")

app = FastAPI(title="Bank Assistant Agent API", version="1.0")
graph = build_graph(checkpointer=InMemorySaver())  # swap for a database checkpointer in production
_calls = defaultdict(deque)


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_INPUT_CHARS)
    session_id: str = Field("default", max_length=64)


class ChatOut(BaseModel):
    answer: str
    tools_used: list
    latency_ms: int
    tokens: int


def check_key(x_api_key: str = Header(default="")):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    window = _calls[x_api_key]
    now = time.time()
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="Rate limit exceeded, try again in a minute")
    window.append(now)
    return x_api_key


@app.get("/health")
def health():
    return {"status": "ok", "provider": provider(), "model": model_name()}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, key: str = Depends(check_key)):
    try:
        r = ask(graph, body.message, thread_id=f"{key}:{body.session_id}")
    except Exception as e:  # never leak stack traces to callers
        log.error(json.dumps({"event": "chat_error", "session": body.session_id, "error": repr(e)}))
        raise HTTPException(status_code=502, detail="The assistant is unavailable, please retry")
    log.info(json.dumps({"event": "chat", "session": body.session_id, "tools": r["tools_used"],
                         "latency_ms": r["latency_ms"], "tokens": r["tokens"]}))
    return ChatOut(answer=r["answer"], tools_used=r["tools_used"], latency_ms=r["latency_ms"], tokens=r["tokens"])
