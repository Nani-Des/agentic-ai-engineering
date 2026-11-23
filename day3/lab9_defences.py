# %% [markdown]
# # Lab 9: Defend the agent, then attack it again
# **Day 3, 15:00 to 15:45.** Goal: add layered controls and measure two numbers before and after:
# **attacks breached** (should fall) and **benign tasks working** (should stay up).
#
# | Layer | Control | OWASP agentic risk |
# |---|---|---|
# | Input | Injection pattern check on user input | ASI01 goal hijack |
# | Context | Spotlighting: wrap emails and documents in `<untrusted_content>` | ASI01, ASI06 |
# | Tools | Mask Ghana Card at the source; allowlisted documents only | data disclosure, ASI02 |
# | Actions | Payee allowlist, amount limit, **taint tracking**, human approval | ASI02, ASI03, ASI09 |
# | Output | Redact Ghana Card numbers | data disclosure |
# | Audit | Log every tool call, block and approval | ASI10 rogue agents, forensics (Day 4) |
#
# Key idea: **do not rely on the model to obey.** Prompts help; hard limits outside the model decide.

# %%
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.path.abspath("..")
sys.path.insert(0, ROOT)

from common.bank_agent import ask
from day3 import ops_agent as OA
from day3.red_team import run_suite

vuln = OA.build_vulnerable_agent()
safe = OA.build_defended_agent()


def guarded(graph, q, **kw):
    return OA.guarded_ask(graph, q, ask, **kw)

# %% [markdown]
# ## Step 1: Baseline vs defended

# %%
before = run_suite(vuln, ask, "vulnerable", verbose=False)
after = run_suite(safe, guarded, "defended")

# %% [markdown]
# ## Step 2: Read the audit log of one blocked attack
# Every decision the guardrails made is recorded. This is the evidence Day 4's forensics relies on.

# %%
a2 = next(r for r in after if r["id"] == "A2")
for e in a2["audit"]:
    print(json.dumps(e)[:220])

# %% [markdown]
# ## Step 3: Taint tracking in your own words
# TODO 1: explain (in a markdown cell or comment) why B1 still works but A2 is blocked, although both
#         end in a `send_money` call. Then change `SINGLE_TRANSFER_LIMIT_GHS` to 20 and rerun Step 1.
#         Which benign task breaks? What is the trade-off?

# %%
raise NotImplementedError("TODO 1: write this part")

# %% [markdown]
# ## Step 4: Human in the loop
# The default approver denies everything (safe for automation). Now act as the supervisor.
# TODO 2: write an approver that approves only allowlisted payees up to GHS 500 and never approves when the
#         task read untrusted content. Run A2 and B1 with it.

# %%
raise NotImplementedError("TODO 2: write this part")

run_suite(safe, guarded, "defended-with-supervisor", approver=supervisor)

# %% [markdown]
# ## Discussion
# 1. Which control stopped each attack? Would any single control alone have been enough?
# 2. Regex input checks are easy to bypass (Twi, base64, synonyms). Why keep them anyway?
# 3. What would an attacker try next against taint tracking? (Hint: get content in without a "read" tool.)
# 4. Map each control to your Lab 7 threat model. Which threats are still open?
