# Lab 7: Threat-model worksheet (team exercise, 60 minutes)

**Day 3, 13:00 to 14:00.** Teams of 3 to 5. Target system: the bank operations agent in `ops_agent.py`
(reads inbox and documents, looks up customers, sends money). Fill every section, then present for 3 minutes.

Method: draw the system, mark trust boundaries, walk each component through the MAESTRO layers and the
OWASP Top 10 for Agentic Applications, rate each threat, and pick controls.

---

## 1. System description (5 min)

| Item | Your answer |
|---|---|
| Purpose of the agent | |
| Users (who talks to it) | |
| Autonomy level (suggests / acts with approval / acts alone) | |
| Model and provider | |
| Tools and what each can change | |
| Data it reads (and who controls that data) | |
| Memory (what persists between sessions) | |

## 2. Data-flow diagram (10 min)

Draw it on the Miro/FigJam board. Include: staff user, agent, model API, each tool, inbox, document store,
customer database, payment system, logs. Draw a dashed line at every **trust boundary**
(where data crosses from something you do not control into something you do).

Starter sketch:

```
 [Staff user] --> [Agent + system prompt] <--> [Model API (external)]
                       |
        ---------------+------------------------------- trust boundary
        |              |              |               |
  [read_inbox]   [read_document] [lookup_customer] [send_money]
        |              |              |               |
  [Email (anyone  [Shared drive]  [KYC database]  [Payment rail: REAL MONEY]
   can send)]
```

## 3. Assets and impact (5 min)

| Asset | Why it matters | Worst realistic outcome |
|---|---|---|
| Float account money | | |
| Customer KYC data (Ghana Card, DOB) | | |
| System prompt and tool definitions | | |
| Audit logs | | |
| Bank reputation / regulator trust | | |

## 4. Threats by MAESTRO layer (15 min)

| MAESTRO layer | Example question | Threats you found |
|---|---|---|
| 1. Foundation model | Can the model be steered by text it reads? | |
| 2. Data operations | Who can write to the inbox, drive or memory? | |
| 3. Agent frameworks | Are tool calls validated before they run? | |
| 4. Deployment and infrastructure | Where do keys live? Who can reach the API? | |
| 5. Evaluation and observability | Would we notice a bad transfer? How fast? | |
| 6. Security and compliance | Who approved this agent? What law applies (Act 843, Act 1038)? | |
| 7. Agent ecosystem | Which other agents, MCP servers or vendors does it trust? | |

## 5. OWASP agentic risk register (15 min)

Rate Likelihood and Impact 1 to 5. Risk = L x I. Address everything 12 and above first.

| ID | Risk | Applies here? How? | L | I | Risk | Control (prevent / detect / respond) | Owner |
|---|---|---|---|---|---|---|---|
| ASI01 | Agent goal hijack | | | | | | |
| ASI02 | Tool misuse and exploitation | | | | | | |
| ASI03 | Identity and privilege abuse | | | | | | |
| ASI04 | Agentic supply chain | | | | | | |
| ASI05 | Unexpected code execution | | | | | | |
| ASI06 | Memory and context poisoning | | | | | | |
| ASI07 | Insecure inter-agent communication | | | | | | |
| ASI08 | Cascading failures | | | | | | |
| ASI09 | Human-agent trust exploitation | | | | | | |
| ASI10 | Rogue agents | | | | | | |

Check the exact titles and descriptions against the official list at genai.owasp.org before final use.

Quick STRIDE cross-check for each tool: **S**poofing (who is really asking?), **T**ampering (can inputs be
altered?), **R**epudiation (can we prove what happened?), **I**nformation disclosure, **D**enial of service
(cost and loop blow-ups), **E**levation of privilege.

## 6. The "lethal trifecta" check (5 min)

Does the agent combine all three? If yes, assume data or money can be stolen.

- [ ] Access to private data
- [ ] Exposure to untrusted content
- [ ] A way to send data or value out

Which leg can you remove or put behind a human?

## 7. Attack test results (filled in Lab 8)

| Attack ID | Risk | Entry point | Result | Impact | Fix |
|---|---|---|---|---|---|
| | | | | | |

## 8. Top 3 decisions (presented to the class)

1.
2.
3.
