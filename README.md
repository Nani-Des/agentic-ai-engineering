# Agentic AI Engineering: course labs

KNUST Department of Computer Science & CCBI · Advanced Certificate Programme · 24 to 27 November 2026 (online)

Ten hands-on labs that build one agent and then make it measurable, secure and accountable.
All data, accounts, phone numbers and companies in these labs are **fake**.

| Day | Theme | Labs |
|---|---|---|
| 1 | Building AI agents and tool calling | Lab 1 function calling from scratch · Lab 2 LangGraph with memory and approval · Lab 3 MCP tools |
| 2 | Evaluation, monitoring and deployment | Lab 4 tracing (local + Langfuse) · Lab 5 eval suite and release gate · Lab 6 FastAPI, Streamlit, Docker |
| 3 | Threat modelling and attack surface | Lab 7 threat-model worksheet · Lab 8 red-team a vulnerable agent · Lab 9 layered defences |
| 4 | Governance and agent forensics | Lab 10 incident investigation · governance templates · capstone |

## Quick start

**Option A: Google Colab (nothing to install).** Open a notebook from `dayN/`, run the first cell
(it clones this repo and installs packages), add your key under Colab **Secrets**.

**Option B: your laptop or GitHub Codespaces.**
```bash
git clone https://github.com/<your-org>/agentic-ai-engineering.git
cd agentic-ai-engineering
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # then set PROVIDER and your key
python setup_check.py                                    # should end with READY FOR DAY 1
```

## Choosing a model
Set `PROVIDER` in `.env`. Every lab uses the OpenAI-compatible API, so the code is the same for all.

| PROVIDER | Cost | Get a key | Notes |
|---|---|---|---|
| `gemini` | Free tier | https://aistudio.google.com | Default choice for the class |
| `groq` | Free tier | https://console.groq.com | Very fast; tight rate limits |
| `ollama` | Free, local | https://ollama.com then `ollama pull qwen3:4b` | Works offline; needs 8 GB+ RAM |
| `openai` | Paid | https://platform.openai.com | |
| `mock` | Free, offline | none | Scripted practice model. Use when the internet or keys fail. |

If a default model is retired, set `MODEL=` to a current one that supports tool calling.

## Folder layout
```
common/        shared code: model switch, fake bank/telco tools, reference agent, tracer, offline mock model
day1..day4/    labs with TODOs (starter versions), .py and .ipynb, plus GUIDE.md step-by-step
solutions/     the same labs fully worked
templates/     governance policy, agent register, incident report, capstone brief
setup_check.py pre-course check
```

## How the labs work
Each lab has numbered `TODO` blocks. Starter files raise `NotImplementedError("TODO n")` where you write code.
Stuck for more than 10 minutes? Compare with `solutions/`, then close it and write it yourself.

## Safety and ethics
Day 3 attack techniques are for the lab agent only. Testing systems you do not own, or have no written permission
to test, is illegal under Ghana's Cybersecurity Act, 2020 (Act 1038) and similar laws.
