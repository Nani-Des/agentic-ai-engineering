# %% [markdown]
# # Lab 1: Function calling from scratch
# **Day 1, 10:30 to 12:00.** Goal: build the agent loop yourself with no framework, so you know what
# LangGraph, CrewAI and the SDKs are doing for you.
#
# You will:
# 1. Describe tools to the model with JSON Schema.
# 2. Send a question and read back the model's **tool call**.
# 3. Run the tool in Python and return the result.
# 4. Loop until the model gives a final answer (with a step limit, so it cannot loop forever).
#
# **Setup.** In Colab, run the first cell. Locally, copy `.env.example` to `.env` and set `PROVIDER`.
# With no key or no internet, `PROVIDER=mock` runs an offline practice model.

# %%
# Colab only: uncomment and run once
# !git clone https://github.com/<your-org>/agentic-ai-engineering.git
# %cd agentic-ai-engineering/day1
# !pip install -q -r ../requirements.txt

import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) if "__file__" in globals() else os.path.abspath("../..")
sys.path.insert(0, ROOT)

from common.llm import get_client, model_name, provider
from common.tools import get_momo_balance, list_data_bundles, convert_currency, calculator

client = get_client()
print("Provider:", provider(), "| model:", model_name())

# %% [markdown]
# ## Step 1: Describe the tools
# The model never sees your Python. It only sees a **name**, a **description** and a **JSON Schema** of the
# arguments. Good descriptions are the single biggest lever on tool-choice accuracy.

# %%
TOOLS = [
    {"type": "function", "function": {
        "name": "get_momo_balance",
        "description": "Get the mobile-money wallet balance in GHS for a 10-digit Ghana phone number.",
        "parameters": {"type": "object",
                       "properties": {"phone": {"type": "string", "description": "10 digits, e.g. 0241234567"}},
                       "required": ["phone"]}}},
    {"type": "function", "function": {
        "name": "list_data_bundles",
        "description": "List data bundles and their prices in GHS for one network.",
        "parameters": {"type": "object",
                       "properties": {"network": {"type": "string", "enum": ["MTN", "Telecel", "AT"]}},
                       "required": ["network"]}}},
    # TODO 1: add a tool definition for convert_currency(amount, from_currency, to_currency).
    #         Use "number" for amount and an enum of GHS, USD, EUR, GBP, NGN, XOF for the currencies.
    {"type": "function", "function": {
        "name": "convert_currency",
        "description": "Convert an amount of money between currencies (demo rates).",
        "parameters": {"type": "object",
                       "properties": {
                           "amount": {"type": "number"},
                           "from_currency": {"type": "string", "enum": ["GHS", "USD", "EUR", "GBP", "NGN", "XOF"]},
                           "to_currency": {"type": "string", "enum": ["GHS", "USD", "EUR", "GBP", "NGN", "XOF"]}},
                       "required": ["amount", "from_currency", "to_currency"]}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression. Use it for any maths instead of guessing.",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string", "description": "e.g. (1200*0.15)+30"}},
                       "required": ["expression"]}}},
]

# The "registry": tool name -> Python function
REGISTRY = {"get_momo_balance": get_momo_balance, "list_data_bundles": list_data_bundles,
            "convert_currency": convert_currency, "calculator": calculator}

# %% [markdown]
# ## Step 2: One call, look at the raw tool call
# The model does not run anything. It returns *which* tool it wants and the *arguments* as a JSON string.

# %%
SYSTEM = ("You are a helpful assistant for a Ghanaian bank and telco. Use the tools for any balance, "
          "bundle, currency or maths question. Never invent numbers.")

resp = client.chat.completions.create(
    model=model_name(),
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": "What's the balance on 0241234567?"}],
    tools=TOOLS,
)
msg = resp.choices[0].message
print("finish_reason:", resp.choices[0].finish_reason)
for tc in msg.tool_calls or []:
    print("tool:", tc.function.name, "| arguments:", tc.function.arguments)

# %% [markdown]
# ## Step 3: Run a tool call safely
# Never `eval` model output. Parse the JSON, look the name up in the registry, and turn any error into a
# result the model can read, so one bad call does not crash the agent.

# %%
def run_tool(name: str, arguments: str) -> dict:
    # TODO 2: look up the function in REGISTRY, parse `arguments` with json.loads, call it with **kwargs
    #         and return the result. Return {"error": "..."} for an unknown tool or bad JSON/arguments.
    fn = REGISTRY.get(name)
    if fn is None:
        return {"error": f"Unknown tool {name}"}
    try:
        return fn(**json.loads(arguments or "{}"))
    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Bad arguments for {name}: {e}"}


print(run_tool("get_momo_balance", '{"phone": "0241234567"}'))
print(run_tool("does_not_exist", "{}"))

# %% [markdown]
# ## Step 4: The agent loop
# model -> tool calls? -> run them -> append results -> model again ... until a plain answer or the step limit.

# %%
def run_agent(question: str, max_steps: int = 5, verbose: bool = True) -> str:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for step in range(max_steps):
        resp = client.chat.completions.create(model=model_name(), messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        # Keep the assistant's tool-call message in the history; the API needs it before the results.
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function",
             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls]})
        # TODO 3: for every tool call, run it with run_tool and append a message
        #         {"role": "tool", "tool_call_id": ..., "content": json.dumps(result)}.
        #         If verbose, print the step, tool name, arguments and result.
        for tc in msg.tool_calls:
            result = run_tool(tc.function.name, tc.function.arguments)
            if verbose:
                print(f"[step {step + 1}] {tc.function.name}({tc.function.arguments}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return "Stopped: step limit reached without a final answer."


# %%
for q in ["What's the balance on 0209876543?",
          "Show me the MTN data bundles.",
          "Convert 250 USD to GHS.",
          "What is (1250.75 - 312.10) * 0.02?"]:
    print("\nQ:", q)
    print("A:", run_agent(q))

# %% [markdown]
# ## Challenges (pick one)
# 1. Ask "Convert my balance on 0241234567 to USD". Does the model chain two tools? What breaks with `max_steps=1`?
# 2. Break a tool description on purpose (e.g. make `calculator` say "returns the weather"). Watch tool choice degrade.
# 3. Add `search_knowledge_base` from `common/tools.py` as a fifth tool and ask about opening hours.
# 4. Print `resp.usage` in the loop and add up tokens per question. Which question cost most, and why?
