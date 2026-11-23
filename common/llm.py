"""
One place to choose the model for every lab.

Set PROVIDER in your .env (or Colab secrets) to one of:
    gemini  - free key from https://aistudio.google.com   (GEMINI_API_KEY)
    groq    - free key from https://console.groq.com      (GROQ_API_KEY)
    ollama  - local model, no key (install https://ollama.com, then `ollama pull qwen3:4b`)
    openai  - paid key                                     (OPENAI_API_KEY)
    mock    - offline demo mode, no key, no internet (scripted "model" for practice and backup)

All real providers are called through the OpenAI-compatible API, so the same code works everywhere.
Override the model name with MODEL=... if the default is retired.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROVIDERS = {
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", "gemini-2.5-flash"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "llama-3.3-70b-versatile"),
    "ollama": ("http://localhost:11434/v1", None, "qwen3:4b"),
    "openai": (None, "OPENAI_API_KEY", "gpt-4.1-mini"),
}


def provider() -> str:
    return os.getenv("PROVIDER", "mock").lower()


def model_name() -> str:
    p = provider()
    if p == "mock":
        return "mock-model"
    return os.getenv("MODEL", PROVIDERS[p][2])


def _settings():
    p = provider()
    if p not in PROVIDERS:
        raise ValueError(f"Unknown PROVIDER '{p}'. Use one of: {', '.join(PROVIDERS)} or mock")
    base_url, key_env, _ = PROVIDERS[p]
    api_key = os.getenv(key_env) if key_env else "ollama"
    if not api_key:
        raise RuntimeError(f"{key_env} is not set. Add it to your .env file or Colab secrets.")
    return base_url, api_key


def get_client():
    """Raw OpenAI-style client (used in Lab 1)."""
    if provider() == "mock":
        from common.mock_llm import MockOpenAI
        return MockOpenAI()
    from openai import OpenAI
    base_url, api_key = _settings()
    return OpenAI(base_url=base_url, api_key=api_key)


def get_chat_model(temperature: float = 0):
    """LangChain chat model (used from Lab 2 onwards)."""
    if provider() == "mock":
        from common.mock_llm import MockChatModel
        return MockChatModel()
    from langchain_openai import ChatOpenAI
    base_url, api_key = _settings()
    return ChatOpenAI(model=model_name(), base_url=base_url, api_key=api_key, temperature=temperature)
