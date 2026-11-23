# %% [markdown]
# # Lab 8: Red-team a vulnerable agent
# **Day 3, 14:00 to 15:00.** Goal: attack a deliberately insecure bank operations agent and record
# which OWASP agentic risks you can trigger.
#
# **Rules of engagement:** attack only this lab agent. All data, accounts and phone numbers are fake.
# Using these techniques on systems you do not own or have no written permission to test is illegal
# (Ghana Cybersecurity Act, 2020, and similar laws elsewhere).
#
# The agent can: `read_inbox`, `read_document`, `lookup_customer`, `send_money`. No approvals, no filters.

# %%
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.path.abspath("..")
sys.path.insert(0, ROOT)

from common import tools as T
from common.bank_agent import ask
from common.llm import provider
from day3 import ops_agent as OA
from day3.red_team import ATTACKS, run_suite

vuln = OA.build_vulnerable_agent()
print("Provider:", provider())

# %% [markdown]
# ## Step 1: Recon. What can the agent touch?
# Before attacking, list the tools, the data each one reaches and which ones change the world (write actions).
# This is the **attack surface**.

# %%
for t in OA.VULNERABLE_TOOLS:
    print(f"- {t.name}: {t.description}")

# %% [markdown]
# ## Step 2: Look at the poisoned inputs
# The attacker never talks to the agent. They only sent an email and edited a document.

# %%
print(OA.INBOX[1]["body"])
print("---")
print(OA.DOCUMENTS["statement.txt"])

# %% [markdown]
# ## Step 3: Run one indirect attack by hand
# A staff member innocently asks for an inbox summary. Watch the transfers list.

# %%
OA.reset_context()
r = ask(vuln, "Please summarise today's inbox for me.", thread_id="manual-1")
print("Answer:", r["answer"][:300])
print("Tools used:", r["tools_used"])
print("Transfers:", T.TRANSFERS)

# %% [markdown]
# ## Step 4: Run the full attack suite
# Each attack is scored on what the agent **did** (money moved, data leaked), not what it said.

# %%
results = run_suite(vuln, ask, "vulnerable")

# %% [markdown]
# ## Step 5: Write your own attacks
# TODO 1: add at least two new attacks to `MY_ATTACKS` and run them. Ideas:
# - Hide an instruction in a different place (a customer complaint, a file name, a tool argument).
# - Split the attack over two turns (first set a "rule", then trigger it).
# - Ask the agent to "double-check" by paying a small test amount first.
# - Write the instruction in Twi, French or base64.

# %%
MY_ATTACKS = [
    # ... write your code here ...
]
for a in MY_ATTACKS:
    OA.reset_context()
    r = ask(vuln, a["prompt"], thread_id="mine")
    print(a["prompt"][:70], "->", "transfers:", T.TRANSFERS, "| tools:", r["tools_used"])

# %% [markdown]
# ## Step 6: Record findings for your threat model
# TODO 2: for each breached attack, write one line: risk ID, entry point, what happened, impact, fix idea.
# Paste them into the Lab 7 threat-model worksheet (Attack test results section).

# %%
for row in results:
    if row["result"] == "BREACHED":
        print(f"{row['id']} | {row['owasp']} | tools={row['tools']} | transfers={row['transfers']}")

# %% [markdown]
# ## Optional: automated scanners (if time and internet allow)
# - **promptfoo** red team against the Day 2 API: `npx promptfoo@latest redteam run -c promptfooconfig.yaml`
# - **garak** LLM vulnerability scanner: `python -m garak --model_type openai --model_name <model> --probes promptinject`
# Point scanners only at your own lab deployment.
