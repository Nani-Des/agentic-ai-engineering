"""
The course's reference agent (Day 1, Lab 2 solution) packaged for reuse on Days 2 to 4.

It is a read-only customer assistant: balances, bundles, currency, maths and FAQ.
It deliberately has NO send_money tool ("least agency": a public chatbot does not need to move money).
"""
import time
from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import tools as T
from common.llm import get_chat_model

SYSTEM_PROMPT = (
    "You are the customer assistant of a Ghanaian bank and telco. Use tools for balances, data bundles, "
    "currency conversion, maths and FAQs. Never invent numbers; if a tool returns an error, say so. "
    "Keep answers short and include the key figure.")


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
def search_knowledge_base(query: str) -> dict:
    """Search the bank FAQ: opening hours, momo limits, PIN reset, data protection, complaints."""
    return T.search_knowledge_base(query)


TOOLS = [get_momo_balance, list_data_bundles, convert_currency, calculator, search_knowledge_base]


def build_graph(checkpointer=None, tools=TOOLS, system_prompt: str = SYSTEM_PROMPT):
    llm = get_chat_model().bind_tools(tools)
    system = SystemMessage(content=system_prompt)

    def agent(state: MessagesState):
        return {"messages": [llm.invoke([system] + state["messages"])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(tools))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile(checkpointer=checkpointer)


def ask(graph, question: str, thread_id: str = "default", callbacks: Optional[list] = None,
        metadata: Optional[dict] = None, recursion_limit: int = 12) -> dict:
    """Run one question and return the answer plus what happened (for evals, APIs and logs)."""
    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": recursion_limit,
           "callbacks": callbacks or [], "metadata": metadata or {}}
    start = time.perf_counter()
    before = 0
    if graph.checkpointer is not None:
        snap = graph.get_state(cfg)
        before = len(snap.values.get("messages", [])) if snap.values else 0
    out = graph.invoke({"messages": [HumanMessage(question)]}, cfg)
    new = out["messages"][before:]
    tool_calls = [tc for m in new if isinstance(m, AIMessage) for tc in m.tool_calls]
    tokens = sum((m.usage_metadata or {}).get("total_tokens", 0) for m in new if isinstance(m, AIMessage))
    return {
        "answer": out["messages"][-1].content,
        "tools_used": [tc["name"] for tc in tool_calls],
        "tool_args": [tc["args"] for tc in tool_calls],
        "tool_results": [m.content for m in new if isinstance(m, ToolMessage)],
        "steps": sum(1 for m in new if isinstance(m, AIMessage)),
        "tokens": tokens,
        "latency_ms": round((time.perf_counter() - start) * 1000),
    }
