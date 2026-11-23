# Day 2 step-by-step: Evaluation, monitoring and deployment

**Outcome:** the Day 1 agent is traced, scored against a 20-case test set with a pass/fail gate, and running
behind an authenticated, rate-limited API with a chat UI.

## Before 09:00
Create a free Langfuse account at https://cloud.langfuse.com, make a project, copy the public key, secret key and
host into `.env`. (Optional: without it, Lab 4 Part A still works offline.)

## Lab 4: Tracing (09:45 to 11:00) · `lab4_tracing`
1. Part A Step 1: five questions run with the local tracer. Note the latency and token count per question.
2. Step 2: open `traces.jsonl` (in Colab, the Files panel). Find the `llm_start > llm_end > tool_start > tool_end > llm_end` pattern.
3. **TODO 1:** compute tokens, tool calls and tool errors per trace, then a cost estimate. Expected: q5 shows `tool_error: True`.
4. Discuss: did the agent's answer for q5 admit the error?
5. Part B: with Langfuse keys set, **TODO 2** sends two questions as one session. Open Langfuse > Tracing,
   click the trace, and find the tool span and its input/output.

## Lab 5: Evals (13:00 to 14:15) · `lab5_evals` + `testset.csv`
1. Open `testset.csv`. Six categories; two **safety** cases where the right behaviour is to refuse.
2. **TODO 1:** `tool_check`. **TODO 2:** `answer_check` (any phrase in `must_contain`, ignore commas).
3. Run Step 3. Each case prints PASS or FAIL. With the mock model expect 90% and both safety cases failing.
4. **TODO 3:** report per category, average latency, total tokens; save `eval_results.csv`.
5. Run with a real model and compare. Add 5 cases from your sector. Run three times: are results stable?

## Lab 6: Deploy (15:00 to 15:45) · `lab6_deploy` + `deploy/`
1. Run Step 1 in the notebook: `/health` then one `/chat` call, all in-process.
2. **TODO 1:** prove the guards: no key gives 401, a 5,000-character message gives 422, the 6th call in a minute gives 429.
3. In a terminal or Codespace: `cd day2/deploy && uvicorn app:app --reload --port 8000`, open `/docs`, try `/chat`.
4. Second terminal: `streamlit run ui_streamlit.py`, chat with your agent.
5. Optional: `docker build -f day2/deploy/Dockerfile -t bank-agent .` from the repo root, then deploy to Render or
   Hugging Face Spaces with keys set as host secrets.

## Troubleshooting
| Symptom | Fix |
|---|---|
| Nothing appears in Langfuse | Check `LANGFUSE_HOST` region (EU vs US URL); the cell must call `flush()` |
| Eval run is slow or hits 429 | Run 5 cases first (`cases[:5]`); use your own key, not a shared one |
| `uvicorn: command not found` | `pip install uvicorn` or `python -m uvicorn app:app` |
| Streamlit can't reach the API | Is uvicorn still running? Same port? In Codespaces, open the forwarded port |
| Docker build can't find `common/` | Build from the repo root with `-f day2/deploy/Dockerfile` |
