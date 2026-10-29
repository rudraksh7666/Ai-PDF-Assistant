"""AI PDF Assistant: ask questions about, summarize, or translate any PDF with Gemini."""

import io
import os

import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

DEFAULT_MODEL = "gemini-3.5-flash"
MAX_CHARS = 60_000  # keep prompts a sensible size for very long PDFs

LANGUAGES = [
    "Hindi", "Punjabi", "Spanish", "French", "German",
    "Japanese", "Arabic", "Portuguese", "English",
]

st.set_page_config(page_title="AI PDF Assistant", page_icon="📄")


# ----------------------------------------------------------------- helpers
def get_secret(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets, then environment variables."""
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:  # no secrets.toml present
        pass
    return os.environ.get(name, default)


@st.cache_data(show_spinner=False)
def extract_text(data: bytes) -> tuple[str, int, bool]:
    """Return (text, page_count, was_truncated) for a PDF given as bytes."""
    reader = PdfReader(io.BytesIO(data))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(pages).strip()
    return text[:MAX_CHARS], len(reader.pages), len(text) > MAX_CHARS


def friendly_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "404" in msg or "no longer available" in msg or "not found" in msg:
        return (
            "That model isn't available. Change the model name in the sidebar "
            "(see the Gemini API docs for current model names)."
        )
    if "api key" in msg or "401" in msg or "403" in msg or "permission" in msg:
        return "The API key was rejected. Check that it is correct and active."
    if "429" in msg or "quota" in msg or "rate" in msg:
        return "Rate limit or quota reached. Wait a minute and try again."
    return f"Something went wrong: {exc}"


def ask_gemini(api_key: str, model: str, prompt: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )
    return response.text or "(The model returned an empty response.)"


def run_task(name: str, prompt: str, api_key: str, model: str) -> None:
    """Call Gemini and keep the result in session state so it survives reruns."""
    if not api_key:
        st.warning("Add your Gemini API key in the sidebar first.")
        return
    with st.spinner("Reading the document..."):
        try:
            st.session_state[name] = ask_gemini(api_key, model, prompt)
        except Exception as exc:
            st.error(friendly_error(exc))


def show_result(name: str, filename: str) -> None:
    result = st.session_state.get(name)
    if result:
        st.success("Done")
        st.markdown(result)
        st.download_button("Download as .md", result, file_name=filename)


# --------------------------------------------------------------------- UI
st.title("📄 AI PDF Assistant")
st.caption("Upload a PDF, then ask questions, summarize it, or translate it.")

with st.sidebar:
    st.header("Settings")
    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input(
            "Gemini API key", type="password",
            help="Get a free key at https://aistudio.google.com/apikey",
        )
    model = st.text_input("Model", value=get_secret("GEMINI_MODEL", DEFAULT_MODEL))

uploaded = st.file_uploader("Upload PDF", type="pdf")

if not uploaded:
    st.info("Upload a PDF to get started.")
    st.stop()

try:
    text, page_count, truncated = extract_text(uploaded.getvalue())
except Exception:
    st.error("I couldn't read that file. Is it a valid, unencrypted PDF?")
    st.stop()

if not text:
    st.warning(
        "No selectable text found. This is probably a scanned PDF, which this "
        "app can't read (it would need OCR)."
    )
    st.stop()

st.caption(f"{page_count} page(s) · {len(text):,} characters read")
if truncated:
    st.warning(f"Long document: only the first {MAX_CHARS:,} characters are used.")

tab_ask, tab_sum, tab_tr = st.tabs(["Ask a question", "Summarize", "Translate"])

with tab_ask:
    question = st.text_input("Ask a question about this PDF")
    if st.button("Answer"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            prompt = f"""Read the document below and answer the question.
Answer only using this document. If the answer is not in the document, say so.

Document:
{text}

Question:
{question}
"""
            run_task("answer", prompt, api_key, model)
    show_result("answer", "answer.md")

with tab_sum:
    style = st.radio("Summary style", ["Short (5 bullets)", "Detailed"], horizontal=True)
    if st.button("Summarize PDF"):
        detail = "5 concise bullet points" if style.startswith("Short") else (
            "a detailed summary with headings for each major section"
        )
        prompt = f"Summarize the document below as {detail}.\n\nDocument:\n{text}"
        run_task("summary", prompt, api_key, model)
    show_result("summary", "summary.md")

with tab_tr:
    language = st.selectbox("Translate into", LANGUAGES)
    if st.button("Translate PDF"):
        prompt = (
            f"Translate the document below into {language}. Keep the structure "
            f"(headings, lists) and do not add commentary.\n\nDocument:\n{text}"
        )
        run_task("translation", prompt, api_key, model)
    show_result("translation", f"translation_{language.lower()}.md")
