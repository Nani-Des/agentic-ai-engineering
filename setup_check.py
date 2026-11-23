"""
Pre-course check: run `python setup_check.py` (or the first cell of any notebook) and post a screenshot
in the course chat. It checks Python, packages, your model key, and makes one real tool call.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ok = True
print(f"Python {sys.version.split()[0]}", "OK" if sys.version_info >= (3, 10) else "-> need 3.10 or newer")
for pkg in ["openai", "langgraph", "langchain_openai", "langfuse", "mcp", "fastapi", "dotenv"]:
    try:
        importlib.import_module(pkg)
        print(f"  {pkg:<18} OK")
    except ImportError:
        ok = False
        print(f"  {pkg:<18} MISSING -> pip install -r requirements.txt")

from common.llm import get_chat_model, model_name, provider  # noqa: E402
from common.bank_agent import ask, build_graph  # noqa: E402

print(f"\nPROVIDER={provider()}  MODEL={model_name()}")
if provider() == "mock":
    print("  You are in offline mock mode. Set PROVIDER and your API key in .env for the real labs.")
try:
    r = ask(build_graph(), "What's the balance on 0241234567?")
    print("  Agent answer:", r["answer"][:120])
    print("  Tools used:", r["tools_used"], "| latency", r["latency_ms"], "ms")
    if "get_momo_balance" not in r["tools_used"]:
        print("  WARNING: the model did not call the tool. Try another MODEL that supports tool calling.")
except Exception as e:
    ok = False
    print("  Agent call FAILED:", repr(e)[:300])

print("\nREADY FOR DAY 1" if ok else "\nFix the items above, or ask in the help-desk channel.")
