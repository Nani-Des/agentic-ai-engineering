# Day 4 step-by-step: AI governance and agent forensics

**Outcome:** you can place an agent in an autonomy tier, write its register entry and policy controls,
investigate an incident from logs, and present your capstone.

## Morning worksheet (10:00 to 11:00) · `templates/`
1. Open `agent_register_template.csv`. Add a row for your capstone agent. Every column must be filled.
2. Choose its autonomy tier using section 4 of `agent_governance_policy_template.md`, and list the minimum controls.
3. Decide your kill switch: what exactly is switched off, by whom, and how fast?

## Lab 10: Incident investigation (13:00 to 14:00) · `lab10_forensics`
1. Read the scenario at the top. Assign roles: lead, evidence handler, timeline, writer.
2. Step 0: record the SHA-256 of every evidence file in your report (chain of custody).
3. **TODO 1:** verify the audit log's hash chain. Which line fails, and what does that mean?
4. **TODO 2:** reconcile the agent's log with the bank ledger. Which transfer was altered, and how?
5. **TODO 3:** rebuild the incident session timeline.
6. **TODO 4:** inspect the suspicious email: sender domain, SPF, DKIM, body.
7. Step 6: read the change log. What changed the night before, by whom, with what ticket?
8. Write the incident report from `templates/incident_report_template.md`. 15 minutes, then 2 teams present.

## Capstone (14:00) · `templates/capstone_brief.md`
8 minutes per team, rubric in the brief. Have the demo recorded as a backup.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `incident_pack` missing | The first cell builds it automatically; or run `python generate_incident.py` in `day4/` |
| Verify says OK | You regenerated the pack after editing; rerun `generate_incident.py` to restore the staged tamper |
