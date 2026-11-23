# Day 1 step-by-step: Building AI agents and tool calling

**Outcome:** by 16:00 you have a working agent that calls tools, remembers a conversation, asks a human
before sending money, and loads tools from an MCP server.

## Before 09:00
1. Run `python setup_check.py` (or the first cell in Colab). It must end with `READY FOR DAY 1`.
2. If it fails on the key or the internet, set `PROVIDER=mock` so you can still follow every lab, and ask the help desk.

## Lab 1: Function calling from scratch (10:30 to 12:00) · `lab1_function_calling`
1. Run the setup cell. Check it prints your provider and model.
2. **Step 1:** read the three tool definitions. Do **TODO 1**: write the JSON Schema for `convert_currency`.
3. **Step 2:** run the single call. You should see `tool: get_momo_balance | arguments: {"phone": "0241234567"}`.
   The model did not run anything; it only asked.
4. **Step 3:** do **TODO 2** (`run_tool`). Expected: a balance dict, then `{'error': 'Unknown tool does_not_exist'}`.
5. **Step 4:** do **TODO 3** (append tool results). Run the four questions. Each should print one `[step 1]` line
   and an answer containing the right figure (balance 312.1, MTN bundles, 3800 GHS, 18.773).
6. Pick one challenge. Be ready to share what you saw.

## Lab 2: LangGraph agent with memory and approval (13:45 to 15:00) · `lab2_langgraph_agent`
1. Run Step 1. Notice `@tool` turns docstrings into the schemas you wrote by hand.
2. **TODO 1** in `send_money`: call `interrupt({...})` and only pay when the answer is `yes`.
3. **TODO 2:** build the graph (two nodes, three edges, `InMemorySaver`). The printed Mermaid shows the loop.
4. Step 3: two questions on thread `demo-1`, then the memory check (should report 8 messages).
5. Step 4: ask for a transfer. The output shows `Paused for approval`. **TODO 3:** resume with `Command(resume="yes")`,
   then run again with `"no"` on a new thread and confirm nothing is added to `TRANSFERS`.

## Lab 3: Tools over MCP (15:00 to 15:45) · `lab3_mcp_client` + `telco_mcp_server.py`
1. Open `telco_mcp_server.py` and read it: three tools and one resource, about 40 lines.
2. **TODO 1:** list the tools from the server. Expect three names with descriptions.
3. Run Step 2: the same agent, but tools came from MCP. Answers should match Lab 2.
4. **TODO 2:** read the `faq://all` resource.
5. Challenge 1: add an `airtime_topup` tool to the server, rerun, and see it appear with no agent changes.

## Low-code track (non-coders, same times)
Build the Lab 2 agent in **n8n** (n8n.io cloud trial or `npx n8n`):
1. New workflow > add **Chat Trigger** > add **AI Agent** node.
2. Chat Model: **Google Gemini Chat Model** (paste your AI Studio key) or **Groq Chat Model**.
3. Memory: **Simple Memory** (window 10).
4. Tools: add a **Code Tool** named `get_momo_balance` that returns a fixed JSON for 0241234567, and an
   **HTTP Request Tool** to a public API (e.g. an exchange-rate API) for currency.
5. In the agent's system message paste the Lab 2 `SYSTEM` text. Open the chat and test the four Lab 1 questions.
6. Approval: put a **Send and Wait for Response** (email or Slack) step before any "send money" action and discuss
   why the approval must sit outside the model.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Add it to `.env` or Colab Secrets and rerun the first cell |
| `429` / rate limit | Wait 60 s; switch `PROVIDER=groq` or `mock`; don't loop many questions at once |
| Model answers without calling a tool | Make the tool description more specific; try a stronger `MODEL` |
| `NotImplementedError: TODO 2` | That's your next exercise: fill in that block |
| Lab 3 hangs | The server path is wrong; run from the repo's `day1/` folder; check `python telco_mcp_server.py` starts |
| Colab "event loop is already running" | Make sure `nest_asyncio` is installed (it is in requirements) |
