# Simple_Chatbot.py
import os
import base64
import streamlit as st
from dotenv import load_dotenv
from helpers.llm_helper import chat, stream_parser
from config import Config  # noqa: F401

load_dotenv()

st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CSS: tight padding, sticky input, responsive header, circular/bordered image ---
st.markdown("""
<style>
  .block-container { padding-top: 0.75rem !important; padding-bottom: 1.25rem !important; }

  /* prevent iOS zoom on focus */
  textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }

  /* keep generic images from overflowing */
  [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }

  /* sticky chat input on small screens */
  @media (max-width: 640px) {
    [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
  }

  /* header title sizing */
  .cg-title h1 {
    margin-bottom: 0.25rem !important;
    line-height: 1.1 !important;
    font-size: clamp(1.35rem, 4vw + 0.25rem, 2.15rem) !important;
  }
  .cg-subtle {
    margin-top: 0rem !important;
    color: #6b7280;
    font-size: clamp(0.9rem, 2.6vw, 1rem) !important;
  }

  /* HEADER photo: circle crop + border (works even if border-radius is ignored elsewhere) */
  .cg-header-avatar img {
    width: 64px !important;
    height: 64px !important;
    object-fit: cover !important;
    /* try multiple ways to force a circle; if any fail, border still shows elegantly */
    border-radius: 50% !important;
    -webkit-clip-path: circle(50% at 50% 50%);
    clip-path: circle(50% at 50% 50%);
    border: 2px solid #e5e7eb;      /* subtle border */
    display: block !important;
  }

  /* stack header on phones + smaller avatar */
  @media (max-width: 640px) {
    .cg-header-wrap .stColumn { width: 100% !important; display: block !important; }
    .cg-header-avatar img { width: 52px !important; height: 52px !important; }
  }
</style>
""", unsafe_allow_html=True)

# --- Utils ---
def find_avatar_path() -> str | None:
    for fname in ("coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"):
        if os.path.exists(fname):
            return fname
    return None

def img_to_base64(path: str) -> tuple[str, str]:
    """Return (data_uri, mime) for local image."""
    ext = os.path.splitext(path)[1].lower()
    mime = "imag
