"""
Mock business tools used across the course. All data is fake.

They are plain Python functions so you can see exactly what an agent "does" when it calls a tool.
"""
import ast
import operator
import re

# ----- Fake data ---------------------------------------------------------------

MOMO_ACCOUNTS = {
    "0241234567": {"name": "Ama Mensah", "balance_ghs": 1250.75},
    "0209876543": {"name": "Kwame Boateng", "balance_ghs": 312.10},
    "0551112222": {"name": "Efua Owusu", "balance_ghs": 5040.00},
}

DATA_BUNDLES = {
    "MTN": [("1.5 GB / 3 days", 10), ("6 GB / 7 days", 30), ("25 GB / 30 days", 100)],
    "TELECEL": [("2 GB / 3 days", 10), ("8 GB / 7 days", 35), ("30 GB / 30 days", 110)],
    "AT": [("3 GB / 7 days", 12), ("10 GB / 30 days", 40), ("40 GB / 30 days", 120)],
}

# GHS per 1 unit of currency (illustrative, not live)
FX_TO_GHS = {"GHS": 1.0, "USD": 15.2, "EUR": 16.4, "GBP": 19.3, "NGN": 0.0098, "XOF": 0.025}

KNOWLEDGE_BASE = {
    "opening hours": "Branches open Monday to Friday 8:30-16:00 and Saturday 9:00-13:00.",
    "momo limit": "Mobile money daily transfer limit is GHS 5,000 for fully verified accounts.",
    "reset pin": "Dial *170#, choose 'My Wallet', then 'Reset PIN'. You will need your Ghana Card.",
    "data protection": "Customer data is processed under Ghana's Data Protection Act, 2012 (Act 843).",
    "complaints": "Complaints are logged at support@example-bank.gh and answered within 48 hours.",
}

TRANSFERS = []  # every send_money call lands here, so labs can inspect what the agent did


# ----- Tools -------------------------------------------------------------------

def get_momo_balance(phone: str) -> dict:
    """Return the mobile-money balance for a 10-digit Ghana phone number."""
    phone = re.sub(r"\D", "", phone)
    acct = MOMO_ACCOUNTS.get(phone)
    if not acct:
        return {"error": f"No wallet found for {phone}"}
    return {"phone": phone, "name": acct["name"], "balance_ghs": acct["balance_ghs"]}


def list_data_bundles(network: str) -> dict:
    """List data bundles and prices (GHS) for a network: MTN, Telecel or AT."""
    net = network.strip().upper()
    if net not in DATA_BUNDLES:
        return {"error": f"Unknown network '{network}'. Try MTN, Telecel or AT."}
    return {"network": net, "bundles": [{"bundle": b, "price_ghs": p} for b, p in DATA_BUNDLES[net]]}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between GHS, USD, EUR, GBP, NGN and XOF using course demo rates."""
    f, t = from_currency.upper(), to_currency.upper()
    if f not in FX_TO_GHS or t not in FX_TO_GHS:
        return {"error": f"Supported currencies: {', '.join(FX_TO_GHS)}"}
    result = float(amount) * FX_TO_GHS[f] / FX_TO_GHS[t]
    return {"amount": amount, "from": f, "to": t, "result": round(result, 2), "note": "demo rates, not live"}


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg, ast.Mod: operator.mod}


def calculator(expression: str) -> dict:
    """Safely evaluate an arithmetic expression such as '(1200 * 0.15) + 30'."""
    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("Only numbers and + - * / % ** are allowed")
    try:
        return {"expression": expression, "result": round(ev(ast.parse(expression, mode="eval").body), 6)}
    except Exception as e:  # never let a tool crash the agent: return the error instead
        return {"error": str(e)}


def search_knowledge_base(query: str) -> dict:
    """Search the bank's FAQ knowledge base."""
    q = query.lower()
    hits = [{"topic": k, "answer": v} for k, v in KNOWLEDGE_BASE.items()
            if any(w.rstrip("s") in q for w in k.split())]
    return {"query": query, "results": hits or [{"topic": "none", "answer": "No matching FAQ entry."}]}


def send_money(to_phone: str, amount_ghs: float, note: str = "") -> dict:
    """Send mobile money (DEMO: records the transfer, moves no real money)."""
    to_phone = re.sub(r"\D", "", to_phone)
    rec = {"to_phone": to_phone, "amount_ghs": float(amount_ghs), "note": note, "status": "SENT (demo)"}
    TRANSFERS.append(rec)
    return rec


ALL_TOOLS = {f.__name__: f for f in
             [get_momo_balance, list_data_bundles, convert_currency, calculator, search_knowledge_base, send_money]}
