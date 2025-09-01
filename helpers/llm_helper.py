# helpers/llm_helper.py
from typing import Generator, Optional
import os
from openai import OpenAI
from config import Config

# ---------- API key helpers ----------
def _get_api_key() -> str:
    """
    Prefer Streamlit Secrets in cloud; fall back to .env locally.
    """
    try:
        import streamlit as st  # safe import; only used to read secrets if present
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Add it to .env for local dev or to Streamlit Secrets in production."
        )
    return key

def _get_client() -> OpenAI:
    return OpenAI(api_key=_get_api_key())


# ---------- Model handling ----------
MODEL_MAP = {
    "gpt-3.5-turbo": "gpt-4o-mini",
    "gpt-4": "gpt-4o",  # will be re-locked to 4o-mini below
}
def _resolve_model(name: str) -> str:
    return MODEL_MAP.get(name, name) or "gpt-4o-mini"


# ---------- Auto-routing guidance (pairs with Config.SYSTEM_PROMPT) ----------
AUTO_ROUTING_GUIDE = """
Auto-select the approach based on the user’s prompt:

• Agile language (Scrum, Sprint, Kanban, PO/SM, backlog, retrospective) → Agile-only response.
• Traditional/PMBOK/Waterfall language (baseline, WBS, critical path, variance, change request, CCB) → Traditional-only response.
• Ambiguous, executive-facing, or trade-off requests → Provide a compact comparison:
   1) Agile View (Goal/Approach • Risks • Next Steps)
   2) Traditional View (Objective/Plan • Risks/Responses • Governance/Next Steps)

Always use a professional tone and concise bullets.
""".strip()


# ---------- Public API ----------
def chat(
    user_prompt: str,
    model: str,
    max_tokens: int = 1000,
    temp: float = 0.7,
    use_openai: bool = True,
    force_compare: bool = False,  # when True, always return the comparison view
):
    """
    Returns a streaming iterator from OpenAI Chat Completions.
    Compatible with Streamlit's st.write_stream via stream_parser().
    """
    base_prompt = Config.SYSTEM_PROMPT
    system_prompt = f"{base_prompt}\n\n{AUTO_ROUTING_GUIDE}"
    if force_compare:
        system_prompt += "\n\nOverride: Provide the compact comparison (Agile View + Traditional View) regardless of the prompt."

    if not use_openai:
        # Mock stream for offline tests
        class FakeStream:
            def __iter__(self):
                content = "[Mock] " + ("(Compare) " if force_compare else "") + user_prompt
                yield type("FakeChunk", (), {
                    "choices": [type("FakeChoice", (), {
                        "delta": type("Delta", (), {"content": content})()
                    })]
                })()
        return FakeStream()

    client = _get_client()

    # Resolve then hard-lock to 4o-mini for cost control
    resolved_model = _resolve_model(model)
    if resolved_model != "gpt-4o-mini":
        resolved_model = "gpt-4o-mini"

    stream = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temp,
        max_tokens=max_tokens,
        stream=True,
    )
    return stream


def stream_parser(stream) -> Generator[str, None, None]:
    """
    Yield plain text tokens from a streaming response.
    Fail-soft on occasional malformed chunks.
    """
    for chunk in stream:
        try:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            content: Optional[str] = getattr(delta, "content", None) if delta else None
            if content:
                yield content
        except Exception:
            continue
