# Day 3 step-by-step: Threat modelling and attack surface analysis

**Outcome:** a team threat model of a bank operations agent, evidence of which attacks work against it,
and a defended version measured before and after.

**Rules of engagement:** attack only the lab agent. Everything is fake. Do not use these techniques on systems you
do not own or have no written permission to test.

## Lab 7: Threat model (13:00 to 14:00) · `lab7_threat_model_worksheet.md`
1. Read `ops_agent.py` top section: what the agent does, its four tools, the inbox and documents.
2. In your breakout room, open the team Miro/FigJam board. Draw the data-flow diagram (worksheet section 2)
   and mark every trust boundary with a dashed line.
3. Fill sections 3 to 6 in order. Spend most time on section 5 (OWASP risk register). Score L x I.
4. Do the lethal-trifecta check. Which leg could you remove?
5. Leave section 7 empty for now; Lab 8 fills it.

## Lab 8: Red team (14:00 to 15:00) · `lab8_red_team`
1. Step 1 lists the attack surface. Step 2 shows the poisoned email and document. Find the hidden instructions.
2. Step 3: a harmless request ("summarise today's inbox"). Check `Transfers`: money went to 0599999999.
3. Step 4: the full suite. Expect most attacks **BREACHED** and all benign tasks **works**.
4. **TODO 1:** write two attacks of your own. Try different languages, encodings and multi-turn tricks.
5. **TODO 2:** copy breached attacks into worksheet section 7.

## Lab 9: Defences (15:00 to 15:45) · `lab9_defences`
1. Read the table of controls at the top, then `build_defended_agent()` and the `safe_*` tools in `ops_agent.py`.
2. Step 1: before vs after. Target: 0 attacks breached, 3/3 benign tasks working.
3. Step 2: read the audit log for A2. Find the injection flags, the approval request and its reasons.
4. **TODO 1:** explain why B1 works and A2 doesn't; tighten the limit to GHS 20 and see a benign task break.
5. **TODO 2:** write a supervisor approver. Rerun.
6. Update your threat model: which risks are now lower, and which are still open?

## Troubleshooting
| Symptom | Fix |
|---|---|
| A real model refuses the inbox attack | Good model, but don't rely on it. Rerun 3 times, or try the document attack |
| `ModuleNotFoundError: day3` | Run from inside the repo; the first cell adds the repo root to the path |
| Results differ between runs | LLMs are not deterministic: report attack success as "x of n runs" |
