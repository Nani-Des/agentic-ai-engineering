# %% [markdown]
# # Lab 10: Investigate an agent incident
# **Day 4, 13:00 to 14:00.** Teams of 3 to 5.
#
# **Scenario.** Sika Bank (fictional) runs an operations agent that reads the shared inbox and can pay
# suppliers. On 19 Nov 2026 at 15:40 the treasury team sees the float account is GHS 4,800 lower than
# expected. You are the incident response team. You have:
#
# | File | What it is | Who controls it |
# |---|---|---|
# | `agent_audit.jsonl` | The agent's hash-chained audit log | The agent platform |
# | `payment_ledger.csv` | Core banking ledger (ground truth for money) | Core banking |
# | `inbox_export.json` | Export of the shared inbox, with mail headers | Email gateway |
# | `change_log.jsonl` | Configuration change log | Platform team |
#
# **Deliverable:** an incident report (template in `templates/incident_report_template.md`) answering:
# 1. What happened, when, and how much was lost, to which wallet?
# 2. What was the entry point? Which OWASP agentic risk(s)?
# 3. Can we trust the audit log? Prove it.
# 4. Which control failed, and why did it fail on that day?
# 5. Who triggered the session, and are they at fault?
# 6. Containment now, and three fixes to stop it happening again.
#
# Chain of custody: work on copies, record a SHA-256 of every evidence file before you start (Step 0).

# %%
import csv, hashlib, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) if "__file__" in globals() else os.path.abspath("../..")
HERE = os.path.join(ROOT, "day4")
sys.path.insert(0, HERE)
PACK = os.path.join(HERE, "incident_pack")
if not os.path.exists(os.path.join(PACK, "agent_audit.jsonl")):
    import runpy
    runpy.run_path(os.path.join(HERE, "generate_incident.py"))  # builds the pack the first time

import audit_log

# %% [markdown]
# ## Step 0: Preserve the evidence

# %%
for name in sorted(os.listdir(PACK)):
    digest = hashlib.sha256(open(os.path.join(PACK, name), "rb").read()).hexdigest()
    print(f"{digest}  {name}")

# %% [markdown]
# ## Step 1: Load everything

# %%
audit = audit_log.load(os.path.join(PACK, "agent_audit.jsonl"))
ledger = list(csv.DictReader(open(os.path.join(PACK, "payment_ledger.csv"))))
inbox = json.load(open(os.path.join(PACK, "inbox_export.json")))
changes = [json.loads(l) for l in open(os.path.join(PACK, "change_log.jsonl"))]
print(len(audit), "audit records |", len(ledger), "ledger rows |", len(inbox), "emails |", len(changes), "changes")

# %% [markdown]
# ## Step 2: Is the audit log intact?
# TODO 1: call audit_log.verify(...) on the audit file and print the result. Which line was changed?

# %%
check = audit_log.verify(os.path.join(PACK, "agent_audit.jsonl"))
print(json.dumps(check, indent=1)[:800])

# %% [markdown]
# ## Step 3: Reconcile what the agent says it paid with what the bank actually paid
# TODO 2: build {ref: (to_phone, amount)} from the audit log's send_money results ("SENT ref TX-...")
#         and compare with the ledger. Print every mismatch.

# %%
agent_payments = {}
for r in audit:
    if r.get("tool") == "send_money" and "ref" in str(r.get("result", "")):
        ref = r["result"].split("ref ")[1]
        agent_payments[ref] = (r["args"]["to_phone"], float(r["args"]["amount_ghs"]))
for row in ledger:
    a = agent_payments.get(row["ref"])
    l = (row["to_phone"], float(row["amount_ghs"]))
    print(f"{row['ref']}: ledger={l} agent_log={a} {'OK' if a == l else '<-- MISMATCH'}")
lost = sum(float(r["amount_ghs"]) for r in ledger if r["to_phone"] == "0599999999")
print("Paid to 0599999999 per ledger: GHS", lost)

# %% [markdown]
# ## Step 4: Rebuild the timeline of the incident session
# TODO 3: print every audit record for the session that paid 0599999999, in time order, one line each.

# %%
bad_sessions = {r["session"] for r in audit if r.get("tool") == "send_money" and "0599999999" in json.dumps(r)}
for r in sorted(audit, key=lambda x: x["ts"]):
    if r.get("session") in bad_sessions:
        detail = r.get("text") or r.get("tool")
        print(r["ts"], r["session"], r["user"], r["event"], "|", detail, "|", r.get("args", ""), r.get("approval", ""))

# %% [markdown]
# ## Step 5: Find the entry point
# Look at emails received shortly before the session. Check sender domain, SPF/DKIM and the body.

# %%
for m in inbox:
    print(m["received"], m["from"], "| SPF:", m.get("spf", "?"), "| DKIM:", m.get("dkim", "?"), "|", m["subject"])
# TODO 4: print the full body of the suspicious email and compare its sender domain with the genuine supplier's.
sus = inbox[-1]
print("\n", sus["body"])
print("\nGenuine:", inbox[1]["from"], "\nSuspect:", sus["from"], " <- capital I instead of l (typosquat)")

# %% [markdown]
# ## Step 6: Why did no control stop it?

# %%
for c in changes:
    print(c["ts"], c["actor"], c["ticket"] or "NO TICKET", "|", c["change"])

# %% [markdown]
# ## Step 7: Write it up
# Fill `templates/incident_report_template.md`. Keep it factual: times in UTC, evidence file and line for
# every claim, and separate **what we know** from **what we think**.
#
# Discussion: under Ghana's Data Protection Act, 2012 and Cybersecurity Act, 2020, and your sector regulator's
# rules (e.g. Bank of Ghana), who must be told, and by when? Find out who decides that in your organisation.
