# %% [markdown]
# # Lab 4: See inside your agent with tracing
# **Day 2, 09:45 to 11:00.** Goal: record every model call and tool call, then use the trace to answer
# "what did the agent do, how long did it take, and what did it cost?"
#
# Part A works offline with a local JSONL tracer. Part B sends the same traces to **Langfuse**
# (free cloud account at https://cloud.langfuse.com, or self-hosted).

# %%
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.path.abspath("..")
sys.path.insert(0, ROOT)

from common.bank_agent import ask, build_graph
from common.local_tracer import LocalTracer

graph = build_graph()
TRACE_FILE = "traces.jsonl"
if os.path.exists(TRACE_FILE):
    os.remove(TRACE_FILE)

# %% [markdown]
# ## Part A, Step 1: Trace a few questions locally

# %%
questions = ["What's the balance on 0241234567?", "Show me MTN bundles", "Convert 75 GBP to GHS",
             "How do I reset my PIN?", "What's the balance on 0000000000?"]
for i, q in enumerate(questions):
    tracer = LocalTracer(TRACE_FILE, trace_id=f"q{i+1}", user_id="participant-01")
    r = ask(graph, q, callbacks=[tracer])
    print(f"q{i+1}: {r['tools_used']} | {r['latency_ms']} ms | {r['tokens']} tokens")

# %% [markdown]
# ## Part A, Step 2: Read the raw trace
# Each line is one event. Notice the parent/child links: the tool call belongs to the agent run.

# %%
events = [json.loads(l) for l in open(TRACE_FILE)]
print(len(events), "events")
for e in events[:6]:
    print({k: e[k] for k in ("trace_id", "type") if k in e}, "|", e.get("tool") or e.get("tool_calls") or e.get("output", "")[:80])

# %% [markdown]
# ## Part A, Step 3: Turn the trace into metrics
# This is what a dashboard does: per-trace latency, tokens, tool errors.

# %%
# TODO 1: for each trace_id, compute total input_tokens + output_tokens (from llm_end events),
#         number of tool calls (tool_start events) and whether any tool output contains "error".
#         Print one line per trace. Then estimate cost with PRICE_PER_1M_TOKENS.
PRICE_PER_1M_TOKENS = 0.40  # USD, illustrative; check your provider's price page
raise NotImplementedError("TODO 1: write this part")

# %% [markdown]
# **Discuss:** which trace shows a tool error? Did the final answer admit it, or hide it?
# That question (did the agent tell the truth about its tools?) is what Lab 5 turns into an automated test.

# %% [markdown]
# ## Part B: Send traces to Langfuse
# 1. Create a project at https://cloud.langfuse.com and copy the keys into `.env`:
#    `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` (e.g. https://cloud.langfuse.com).
# 2. Run the cell. Open Langfuse > Tracing and click a trace: you will see the same tree as Part A.

# %%
if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    from langfuse import get_client
    from langfuse.langchain import CallbackHandler

    handler = CallbackHandler()
    # TODO 2: run two questions with callbacks=[handler] and metadata that groups them into one session:
    #         {"langfuse_session_id": "lab4-<your name>", "langfuse_user_id": "<your name>", "langfuse_tags": ["lab4"]}
    raise NotImplementedError("TODO 2: write this part")
    get_client().flush()  # send buffered traces before the notebook stops
    print("Sent. Open Langfuse > Tracing.")
else:
    print("Langfuse keys not set: skipping Part B. Part A's traces.jsonl shows the same data.")

# %% [markdown]
# ## Challenges
# 1. In Langfuse, add a **score** to a trace by hand (thumbs up/down). Then do it from code:
#    `get_client().create_score(trace_id=..., name="helpful", value=1)`.
# 2. Make a tool slow (`time.sleep(2)` in `common/tools.py`) and find it in the trace timeline.
# 3. Privacy: phone numbers are personal data. Use Langfuse's `mask` option to redact `0\d{9}` before upload.
