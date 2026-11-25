# AI Agent Governance Policy (template)

**Organisation:** ____________  **Version:** 0.1  **Owner:** ____________  **Approved by:** ____________  **Review date:** ____________

Aligned with: NIST AI RMF (Govern, Map, Measure, Manage), ISO/IEC 42001 (AI management system),
OWASP Top 10 for Agentic Applications, Ghana Data Protection Act 2012 (Act 843), Cybersecurity Act 2020 (Act 1038),
and sector rules (e.g. Bank of Ghana, NCA). Replace or add the rules that apply to you.

## 1. Purpose and scope
This policy covers every AI agent that can take actions (call tools, change data, send messages or money) on behalf
of the organisation, whether built in-house, bought, or reached through a vendor or MCP server.

## 2. Principles
1. **Least agency.** An agent gets only the tools, data and autonomy its task needs, and nothing by default.
2. **Human accountability.** Every agent has a named business owner and technical owner.
3. **Traceability.** Every agent action is attributable to an agent identity and a requesting user, and is logged.
4. **Safe by default.** Untrusted content (email, web, documents, other agents) never authorises an action.
5. **Proportionate control.** Controls scale with the autonomy tier and impact (section 4).

## 3. Roles
| Role | Responsibilities |
|---|---|
| AI governance committee | Approves Tier 3-4 agents, owns this policy, reviews incidents |
| Business owner | Defines purpose, accepts residual risk, signs off go-live |
| Technical owner | Builds and operates the agent, keeps the register entry current |
| Security | Threat model, red-team test, monitoring rules, incident response |
| Data protection officer | DPIA, lawful basis, data minimisation, breach notification |
| Internal audit | Independent review of logs and controls |

## 4. Autonomy tiers
| Tier | Description | Minimum controls |
|---|---|---|
| 1 Assist | Drafts or suggests; a human performs every action | Register entry, basic evals, logging |
| 2 Act with approval | Acts after explicit human approval per action | + threat model, approval UI showing full action details |
| 3 Act within limits | Acts alone inside hard limits (amount, payee, scope) | + red-team test, runtime policy engine, alerting, kill switch |
| 4 Autonomous | Acts alone across systems or with other agents | + committee approval, continuous monitoring, quarterly audit |

## 5. Lifecycle requirements
| Stage | Requirement | Evidence |
|---|---|---|
| Propose | Use case, owner, tier, data categories | Register entry |
| Design | Threat model (MAESTRO + OWASP agentic), DPIA if personal data | Threat model, DPIA |
| Build | Tools scoped; secrets in vault; untrusted content marked; hard limits outside the model | Code review record |
| Test | Eval suite with pass threshold; red-team test of top risks | Eval report, red-team report |
| Approve | Sign-off per tier | Approval record |
| Operate | Tracing, tamper-evident audit log, alerts, cost limits | Dashboards, log retention |
| Change | Model, prompt, tool or limit changes go through change control with a ticket | Change log |
| Retire | Revoke credentials and tool access; archive logs | Decommission record |

## 6. Mandatory technical controls (Tier 2 and above)
- Unique agent identity and credentials; no shared or human credentials.
- Tool allowlist; write tools behind policy checks (limits, allowlists, approvals).
- Untrusted input tracking: once external content is read, high-impact actions need human approval.
- Personal data masked at the source; output redaction for identifiers (e.g. Ghana Card numbers).
- Tamper-evident logs retained for ____ months; logs include user, agent, tool, arguments, result, approval.
- Kill switch that disables tools within ____ minutes.
- Configuration changes to limits and allowlists require two-person approval and a ticket.

## 7. Monitoring and incidents
Alert on: actions above limits, new payees, spikes in tool calls or cost, injection flags, log-chain breaks.
Agent incidents follow the incident response plan; the DPO assesses notification duties to the
Data Protection Commission and affected persons; Security assesses reporting to the Cyber Security Authority.

## 8. Third-party agents, models and MCP servers
Vendor due diligence, pinned versions, review of tool descriptions, and contractual logging and incident terms.

## 9. Exceptions
Written, time-limited, approved by the governance committee, recorded in the register.

## 10. Review
This policy is reviewed every 12 months or after any significant incident.
