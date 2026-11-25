# %% [markdown]
# # Lab 6: Ship it as an API
# **Day 2, 15:00 to 15:45.** Goal: wrap the agent in a FastAPI service with basic production guards,
# test it, then run it in Docker or on a free host.
#
# The service lives in `deploy/app.py`. This notebook tests it **in-process** (no server needed),
# then the GUIDE shows the terminal and hosting steps.

# %%
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.path.abspath("..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "day2", "deploy"))
os.environ.setdefault("APP_API_KEYS", "dev-key")
os.environ.setdefault("RATE_LIMIT_PER_MIN", "5")

from fastapi.testclient import TestClient
import app as service

client = TestClient(service.app)
H = {"X-API-Key": "dev-key"}

# %% [markdown]
# ## Step 1: Health and a normal request

# %%
print(client.get("/health").json())
r = client.post("/chat", headers=H, json={"message": "Show me MTN bundles", "session_id": "t1"})
print(r.status_code, r.json())

# %% [markdown]
# ## Step 2: Test the guards
# TODO 1: write requests that prove each guard works and print the status codes:
#   (a) no API key -> 401, (b) a 5,000-character message -> 422, (c) more than 5 calls in a minute -> 429.

# %%
raise NotImplementedError("TODO 1: write this part")

# %% [markdown]
# ## Step 3: Run it for real (terminal / Codespace)
# ```bash
# cd day2/deploy
# uvicorn app:app --reload --port 8000          # API at http://localhost:8000/docs
# streamlit run ui_streamlit.py                 # chat UI in a second terminal
# ```
# ## Step 4: Container and hosting
# ```bash
# docker build -f day2/deploy/Dockerfile -t bank-agent .      # from the repo root
# docker run -p 8000:8000 --env-file .env bank-agent
# ```
# Free hosting options: Render (Web Service from the Dockerfile), Hugging Face Spaces (Docker space),
# Google Cloud Run. Set PROVIDER, the model key and APP_API_KEYS as **secrets** in the host, never in code.
#
# ## Production checklist (discuss)
# - Secrets in a vault or host secrets, rotated; separate keys per client.
# - Persistent checkpointer (Postgres/SQLite) instead of memory, or sessions vanish on restart.
# - Tracing on (Lab 4) and evals in CI (Lab 5) before every deploy.
# - Cost cap per key per day; alert on spikes.
# - Timeouts and a fallback model when the provider is down.
