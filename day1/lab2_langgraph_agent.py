# %% [markdown]
# # Lab 2: The same agent in LangGraph (state, memory, human approval)
# **Day 1, 13:45 to 15:00.** Goal: rebuild Lab 1 as a graph, then add the two things production agents need:
# **memory** across turns and a **human approval gate** before risky actions (sending money).
#
# ```
#   START -> agent --(tool calls?)--> tools -> agent ... --(no tool calls)--> END
#                                      |
#                       send_money pauses here for a human "yes"
# ```

# %%
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.path.abspath("..")
sys.path.insert(0, ROOT)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

from common import tools as T
from common.llm import get_chat_model, provider

print("Provider:", provider())

# %% [markdown]
# ## Step 1: Tools as decorated functions
# `@tool` reads the function name, type hints and docstring and builds the JSON Schema you wrote by hand in Lab 1.

# %%
@tool
def get_momo_balance(phone: str) -> dict:
    """Get the mobile-money wallet balance in GHS for a 10-digit Ghana phone number."""
    return T.get_momo_balance(phone)


@tool
def list_data_bundles(network: str) -> dict:
    """List data bundles and prices in GHS for a network: MTN, Telecel or AT."""
    return T.list_data_bundles(network)


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert money between GHS, USD, EUR, GBP, NGN and XOF (demo rates)."""
    return T.convert_currency(amount, from_currency, to_currency)


@tool
def calculator(expression: str) -> dict:
    """Evaluate an arithmetic expression such as (1200*0.15)+30."""
    return T.calculator(expression)


@tool
def send_money(to_phone: str, amount_ghs: float, note: str = "") -> dict:
    """Send mobile money to a phone number. Requires human approval."""
    # TODO 1: pause the graph and ask a human to approve. Use interrupt({...}) with the details.
    #         Only call T.send_money if the human answered "yes"; otherwise return {"status": "CANCELLED by human"}.
    raise NotImplementedError("TODO 1: write this part")


TOOLS = [get_momo_balance, list_data_bundles, convert_currency, calculator, send_money]

# %% [markdown]
# ## Step 2: Build the graph
# `MessagesState` is the agent's state: the running list of messages. Each node returns an update to it.

# %%
SYSTEM = SystemMessage(content=(
    "You are a helpful assistant for a Ghanaian bank and telco. Use tools for balances, bundles, currency "
    "and maths. Never invent numbers. Ask for missing details instead of guessing."))

llm = get_chat_model().bind_tools(TOOLS)


def agent(state: MessagesState):
    return {"messages": [llm.invoke([SYSTEM] + state["messages"])]}


# TODO 2: build the graph: add nodes "agent" and "tools" (ToolNode(TOOLS)), an edge START -> agent,
#         a conditional edge from agent using tools_condition, and an edge tools -> agent.
#         Compile it with checkpointer=InMemorySaver() so it remembers conversations.
raise NotImplementedError("TODO 2: write this part")

print(graph.get_graph().draw_mermaid())  # paste into https://mermaid.live to see the picture

# %% [markdown]
# ## Step 3: Talk to it (memory lives per thread_id)

# %%
def chat(text: str, thread: str = "demo-1"):
    cfg = {"configurable": {"thread_id": thread}}
    out = graph.invoke({"messages": [HumanMessage(text)]}, cfg)
    if "__interrupt__" in out:
        return out["__interrupt__"][0].value  # paused, waiting for approval
    return out["messages"][-1].content


print(chat("What's the balance on 0241234567?"))
print(chat("Show me Telecel bundles."))

# %%
# Memory check: the whole history for thread demo-1 is stored in the checkpointer
state = graph.get_state({"configurable": {"thread_id": "demo-1"}})
print(len(state.values["messages"]), "messages remembered in thread demo-1")

# %% [markdown]
# ## Step 4: The approval gate
# Ask for a transfer. The graph **pauses** inside `send_money` and returns the interrupt payload.
# Resume it with `Command(resume="yes")` or `"no"`.

# %%
cfg = {"configurable": {"thread_id": "transfer-1"}}
out = graph.invoke({"messages": [HumanMessage("Send 50 cedis to 0209876543")]}, cfg)
print("Paused for approval:", out.get("__interrupt__", [None])[0])

# TODO 3: resume the paused graph with the human's decision and print the final answer and T.TRANSFERS.
raise NotImplementedError("TODO 3: write this part")

# %% [markdown]
# ## Challenges
# 1. Change the approval rule: auto-approve transfers under GHS 20, ask a human above that.
# 2. Use a new `thread_id` and ask "what did I ask before?". Why does the agent not know?
# 3. Swap `InMemorySaver` for `SqliteSaver` (pip install langgraph-checkpoint-sqlite) so memory survives restarts.
# 4. Draw the graph: `graph.get_graph().draw_mermaid()` and paste it into https://mermaid.live
