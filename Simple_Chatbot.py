# Simple_Chatbot.py
import os, io, base64
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from helpers.llm_helper import chat, stream_parser
from config import Config  # noqa: F401

load_dotenv()

st.set_page_config(
    page_title="Ask Coach Greg?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---- Tuning: vertical crop focus for the header photo (percent from top) ----
FOCUS_Y = 15  # try 15–25; lower = show more top

# --- CSS: tight padding, sticky input, tidy header ---
st.markdown("""
<style>
  .block-container { padding-top: 0.75rem !important; padding-bottom: 1.25rem !important; }
  textarea, input, .stTextInput, .stChatInputContainer textarea { font-size: 16px !important; }
  [data-testid="stImage"] img { max-width: 100% !important; height: auto !important; }
  @media (max-width: 640px) {
    [data-testid="stChatInput"] { position: sticky; bottom: 0; z-index: 5; }
  }
  .cg-title h1 {
    margin-bottom: 0.25rem !important;
    line-height: 1.1 !important;
    font-size: clamp(1.35rem, 4vw + 0.25rem, 2.15rem) !important;
  }
  .cg-subtle { margin-top: 0rem !important; color: #6b7280; font-size: clamp(0.9rem, 2.6vw, 1rem) !important; }

  /* Header avatar border (image itself is already circular via alpha mask) */
  .cg-header-avatar img {
    width: 72px; height: 72px; border-radius: 50%;
    border: 2px solid #e5e7eb; display: block;
  }
  @media (max-width: 640px) {
    .cg-header-wrap .stColumn { width: 100% !important; display: block !important; }
    .cg-header-avatar img { width: 56px; height: 56px; }
  }

  /* Make assistant avatar in chat circular too */
  [data-testid="stChatMessageAvatar"] img {
    border-radius: 50% !important;
    object-fit: cover !important;
  }
</style>
""", unsafe_allow_html=True)

# --- Utils ---
def find_avatar_path() -> str | None:
    for fname in ("coach_greg.png", "coach_greg.jpg", "coach_greg.jpeg"):
        if os.path.exists(fname):
            return fname
    return None

def crop_square_with_focus(img: Image.Image, focus_y_pct: float) -> Image.Image:
    """
    Return a square crop. For portrait images, slide the square vertically based on focus_y_pct (0-100).
    For landscape, center horizontally.
    """
    w, h = img.size
    if w == h:
        return img.copy()

    if h > w:  # portrait → slide vertically
        max_off = h - w
        y_off = int(round(max(0, min(100, focus_y_pct)) / 100.0 * max_off))
        return img.crop((0, y_off, w, y_off + w))
    else:      # landscape → center horizontally
        x_off = (w - h) // 2
        return img.crop((x_off, 0, x_off + h, h))

def circle_mask(size: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((0, 0, size, size), fill=255)
    return m

def make_header_circle_data_uri(path: str, size: int = 72, focus_y_pct: float = 18) -> str:
    """Load image, crop to square with vertical focus, resize, apply circular mask (alpha),
    and return a PNG data URI suitable for <img src=...>."""
    img = Image.open(path).convert("RGBA")
    sq = crop_square_with_focus(img, focus_y_pct)
    sq = sq.resize((size, size), Image.LANCZOS)

    # Apply circular mask (transparent corners)
    mask = circle_mask(size)
    sq.putalpha(mask)

    buf = io.BytesIO()
    sq.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

avatar_path = find_avatar_path()
bot_avatar = avatar_path if avatar_path else "🤖"

# --- Header: pre-cropped circular PNG (server-side) + title/subtitle ---
st.markdown('<div class="cg-header-wrap">', unsafe_allow_html=True)
hcol_img, hcol_text = st.columns([0.16, 0.84])

with hcol_img:
    if avatar_path:
        data_uri = make_header_circle_data_uri(avatar_path, size=72, focus_y_pct=FOCUS_Y)
        st.markdown(f'<div class="cg-header-avatar"><img alt="Coach Greg" src="{data_uri}"/></div>', unsafe_allow_html=True)
    else:
        st.markdown("🤖")

with hcol_text:
    st.markdown('<div class="cg-title">', unsafe_allow_html=True)
    st.title("Ask Coach Greg?")
    st.markdown('<div class="cg-subtle"><strong>Model:</strong> gpt-4o-mini</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Keep history performant on mobile
MAX_HISTORY = 50
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

# --- Render history (assistant uses your headshot path as avatar) ---
for message in st.session_state.messages:
    avatar = bot_avatar if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- Chat input & LLM call ---
temperature = 0.7
max_token_length = 1000
placeholder = "Ask about Agile or Traditional PM (e.g., ‘Sprint Review agenda’ or ‘baseline variance handling’)"

if user_prompt := st.chat_input(placeholder):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant", avatar=bot_avatar):
        with st.spinner("Thinking…"):
            try:
                llm_response = chat(
                    user_prompt,
                    model="gpt-4o-mini",
                    max_tokens=max_token_length,
                    temp=temperature,
                    use_openai=True,
                )
                stream_output = st.write_stream(stream_parser(llm_response))
            except Exception as e:
                stream_output = f"⚠️ Error generating response: {e}"
                st.error(stream_output)

    st.session_state.messages.append({"role": "assistant", "content": stream_output})

# --- Actions row (AFTER messages so it shows on first turn) ---
if st.session_state.messages:
    transcript = "\n\n".join(
        f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages
    )
    col_dl, col_reset = st.columns(2)
    with col_dl:
        st.download_button(
            "Download Transcript",
            transcript,
            file_name="chat_transcript.txt",
            use_container_width=True,
        )
    with col_reset:
        if st.button("Reset Chat", use_container_width=True):
            st.session_state.clear()
            st.rerun()
