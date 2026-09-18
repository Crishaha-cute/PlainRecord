"""
PlainRecord — MVP Streamlit app

Lets a patient/caregiver paste in or upload a clinical note/record and get
a plain-language explanation of what it says, powered by Gemini.

Run locally:
    streamlit run app.py

Requires a Gemini API key in a local .env file as GEMINI_API_KEY.
"""

import os
import datetime as dt

import streamlit as st
from dotenv import load_dotenv
from google import genai

from src.record_reader import extract_text
from src.translator import translate_to_plain_language
from src.feedback_store import save_feedback

st.set_page_config(page_title="PlainRecord", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600&display=swap');

    :root {
        --ink: #202a29;
        --muted: #66716f;
        --teal: #2f7d73;
        --teal-dark: #245f58;
        --mint: #e8f2f0;
        --paper: #ffffff;
        --line: #d9e1df;
        --background: #f3f5f4;
        --accent-soft: #9bc8c1;
    }

    .stApp {
        background: var(--background);
        color: var(--ink);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1120px;
        margin: 2rem auto 3rem;
        padding: 0 2.35rem 2.8rem;
        position: relative;
        border: 1px solid var(--line);
        border-radius: 22px;
        background: var(--paper);
        box-shadow: 0 18px 55px rgba(32, 42, 41, 0.08);
    }
    .window-chrome {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        min-height: 3.2rem;
        margin: 0 -2.35rem 2.2rem;
        padding: 0 1.35rem;
        border-bottom: 1px solid var(--line);
        background: #fafbfb;
        border-radius: 22px 22px 0 0;
        color: var(--muted);
        font: 600 0.75rem 'DM Sans', sans-serif;
    }
    .window-dots { display: flex; gap: 0.38rem; }
    .window-dot { width: 0.62rem; height: 0.62rem; border-radius: 50%; background: #bdc6c4; }
    .window-dot:first-child, .window-dot:nth-child(2), .window-dot:last-child { background: #bdc6c4; }
    .window-title { margin-left: auto; margin-right: auto; transform: translateX(-2.15rem); }
    [data-testid="stCheckbox"] {
        position: absolute;
        top: 0.82rem;
        left: auto;
        right: 1.35rem;
        z-index: 5;
    }
    [data-testid="stElementContainer"]:has(> [data-testid="stCheckbox"]) {
        position: static;
        width: 0;
        height: 0;
        overflow: visible;
    }
    [data-testid="stCheckbox"] label p {
        color: var(--muted);
        font-size: 1.1rem;
        line-height: 1;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--paper);
        box-shadow: 0 12px 35px rgba(32, 42, 41, 0.05);
    }

    h1, h2, h3, p, label, [data-testid="stCaptionContainer"] { font-family: 'DM Sans', sans-serif; }
    h1 { font-family: 'Fraunces', Georgia, serif !important; color: var(--ink); letter-spacing: 0; }
    h2, h3 { color: var(--ink); letter-spacing: 0; }
    .brand-mark {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        color: var(--teal-dark);
        font: 700 1.05rem 'DM Sans', sans-serif;
        letter-spacing: 0.01em;
    }
    .brand-icon {
        display: inline-grid;
        place-items: center;
        width: 2rem;
        height: 2rem;
        border-radius: 10px;
        background: var(--teal);
        color: white;
        font-size: 1.15rem;
    }
    .hero-copy { max-width: 650px; margin: 0.4rem 0 1.7rem; }
    .hero-copy p { color: var(--muted); font-size: 1.05rem; line-height: 1.6; }
    .eyebrow {
        color: var(--teal);
        font: 700 0.72rem 'DM Sans', sans-serif;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }
    .step-row { display: flex; gap: 0.75rem; margin: 0.4rem 0 1.2rem; }
    .step {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        color: var(--muted);
        font: 600 0.78rem 'DM Sans', sans-serif;
    }
    .step.active { color: var(--teal-dark); }
    .step-number {
        display: inline-grid;
        place-items: center;
        width: 1.55rem;
        height: 1.55rem;
        border: 1px solid var(--accent-soft);
        border-radius: 50%;
        font-size: 0.72rem;
    }
    .step.active .step-number { background: var(--teal); border-color: var(--teal); color: white; }
    .step-divider { width: 2rem; border-top: 1px solid var(--line); margin-top: 0.78rem; }
    .tip-box {
        padding: 1rem 1.1rem;
        border-left: 3px solid var(--accent-soft);
        border-radius: 0 10px 10px 0;
        background: var(--mint);
        color: var(--ink);
        font: 0.88rem/1.5 'DM Sans', sans-serif;
    }
    .tip-box strong { display: block; margin-bottom: 0.25rem; }
    .result-label { color: var(--teal); font: 700 0.75rem 'DM Sans', sans-serif; letter-spacing: 0.11em; text-transform: uppercase; }
    .result-title { margin: 0.15rem 0 0.9rem; font: 600 2rem 'Fraunces', Georgia, serif; color: var(--ink); }
    .privacy-note { color: var(--muted); font-size: 0.78rem; line-height: 1.5; }
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        min-height: 2.7rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
    }
    .stButton > button[kind="primary"] { background: var(--teal); border-color: var(--teal); }
    .stButton > button[kind="primary"]:hover { background: var(--teal-dark); border-color: var(--teal-dark); }
    .stTextArea textarea, .stTextInput input { border-radius: 10px; border-color: var(--line); }
    body:has(.theme-dark-marker) {
            --ink: #f1eee7;
            --muted: #b3aea5;
            --teal: #c58f66;
            --teal-dark: #e0b18e;
            --mint: #27221e;
            --paper: #17191a;
            --line: #383a39;
            --background: #0b0d0e;
            --accent-soft: #715644;
    }
    body:has(.theme-dark-marker) .stApp {
            background: var(--background);
    }
    body:has(.theme-dark-marker) [data-testid="stMainBlockContainer"] {
            border-color: var(--line);
            background: var(--paper);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    }
    body:has(.theme-dark-marker) .window-chrome {
            border-bottom-color: var(--line);
            background: #1c1e1f;
    }
    body:has(.theme-dark-marker) .window-dot,
    body:has(.theme-dark-marker) .window-dot:first-child,
    body:has(.theme-dark-marker) .window-dot:nth-child(2),
    body:has(.theme-dark-marker) .window-dot:last-child { background: #5a5b59; }
    body:has(.theme-dark-marker) [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            background: #1b1d1e;
            box-shadow: 0 16px 45px rgba(0, 0, 0, 0.2);
    }
    body:has(.theme-dark-marker) .stMarkdown,
    body:has(.theme-dark-marker) .stMarkdown p,
    body:has(.theme-dark-marker) label,
    body:has(.theme-dark-marker) [data-testid="stCaptionContainer"],
    body:has(.theme-dark-marker) [data-testid="stFileUploaderDropzone"] {
            color: var(--ink);
    }
    body:has(.theme-dark-marker) .hero-copy p,
    body:has(.theme-dark-marker) .privacy-note { color: var(--muted); }
    body:has(.theme-dark-marker) .tip-box { border-left-color: var(--teal); background: var(--mint); color: var(--ink); }
    body:has(.theme-dark-marker) .step-number { border-color: var(--accent-soft); }
    body:has(.theme-dark-marker) .step-divider { border-top-color: var(--line); }
    body:has(.theme-dark-marker) .stTextArea textarea,
    body:has(.theme-dark-marker) .stTextInput input {
            background: #101213;
            color: var(--ink);
            border-color: var(--line);
    }
    body:has(.theme-dark-marker) .stTextArea textarea::placeholder,
    body:has(.theme-dark-marker) .stTextInput input::placeholder { color: #8e8980; }
    body:has(.theme-dark-marker) [data-testid="stFileUploaderDropzone"] { background: #101213; border-color: var(--line); }
    body:has(.theme-dark-marker) .stButton > button:not([kind="primary"]),
    body:has(.theme-dark-marker) .stDownloadButton > button {
            background: #222526;
            color: var(--ink);
            border-color: #4b4d4b;
    }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { margin: 0.6rem auto 1.5rem; padding: 0 1rem 1.8rem; border-radius: 16px; }
        .window-chrome { margin: 0 -1rem 1.5rem; border-radius: 16px 16px 0 0; }
        .window-title { transform: none; }
        [data-testid="stCheckbox"] { top: 0.72rem; left: auto; right: 0.8rem; }
        .step-row { gap: 0.4rem; }
        .step-divider { width: 0.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

dark_mode = st.toggle(
    "☾",
    value=False,
    key="dark_mode",
    help="Toggle dark mode",
)

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY", "")

if dark_mode:
    st.markdown('<span class="theme-dark-marker"></span>', unsafe_allow_html=True)

st.markdown(
    '<div class="window-chrome"><div class="window-dots"><span class="window-dot"></span><span class="window-dot"></span><span class="window-dot"></span></div><div class="window-title">PlainRecord workspace</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="brand-mark"><span class="brand-icon">+</span> PlainRecord</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-copy"><div class="eyebrow">A clearer way to read your care</div>'
    '<h1>Your record, in plain English.</h1>'
    '<p>Turn clinical notes, lab results, and scanned documents into a calm, readable explanation you can understand and discuss with your care team.</p></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="step-row">'
    '<div class="step active"><span class="step-number">1</span> Share record</div>'
    '<div class="step-divider"></div>'
    '<div class="step"><span class="step-number">2</span> Read explanation</div>'
    '<div class="step-divider"></div>'
    '<div class="step"><span class="step-number">3</span> Ask better questions</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ---------- Input ----------
with st.container(border=True):
    st.markdown('<div class="result-label">Step 1</div><h2>Share your record</h2>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Choose an input method",
        ["Paste text", "Upload a file"],
        horizontal=True,
        label_visibility="collapsed",
    )

    record_text = ""
    record_image = None
    record_image_mime_type = None

    if input_mode == "Paste text":
        input_col, tip_col = st.columns([1.7, 1], gap="large")
        with input_col:
            record_text = st.text_area(
                "Clinical note, lab result, or summary",
                height=210,
                placeholder="Paste the text from your record here...",
                help="Remove names, addresses, or other details you do not need explained.",
            )
        with tip_col:
            st.markdown(
                '<div class="tip-box"><strong>What works well</strong>Paste a visit note, lab result, discharge summary, or medication list. PlainRecord will keep the explanation focused on what is actually in the record.</div>',
                unsafe_allow_html=True,
            )
    else:
        uploaded_file = st.file_uploader(
            "Upload a record",
            type=["pdf", "txt", "jpg", "jpeg", "png", "webp", "gif"],
            help="Accepted formats: PDF, TXT, JPG, JPEG, PNG, WEBP, and GIF.",
        )
        if uploaded_file is not None:
            if uploaded_file.type.startswith("image/"):
                record_image = uploaded_file.getvalue()
                record_image_mime_type = uploaded_file.type
                st.image(record_image, caption=f"Ready to explain: {uploaded_file.name}", use_container_width=True)
            else:
                record_text = extract_text(uploaded_file)
                with st.expander(f"Preview extracted text from {uploaded_file.name}"):
                    st.write(record_text)

    translate_clicked = st.button("Explain my record", type="primary", use_container_width=True)
    st.markdown(
        '<div class="privacy-note">For your privacy, remove personal details you do not need explained. This tool provides an explanation, not a diagnosis or medical advice.</div>',
        unsafe_allow_html=True,
    )


# ---------- Output ----------
if translate_clicked:
    if not api_key:
        st.error("Please set GEMINI_API_KEY in your .env file first.")
    elif not record_text.strip() and record_image is None:
        st.warning("Please paste or upload a record first.")
    else:
        with st.spinner("Reading your record..."):
            client = genai.Client(api_key=api_key)
            try:
                explanation = translate_to_plain_language(
                    client,
                    record_text,
                    image_bytes=record_image,
                    image_mime_type=record_image_mime_type,
                )
                st.session_state["last_explanation"] = explanation
                st.session_state["last_record"] = record_text
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if "last_explanation" in st.session_state:
    st.write("")
    with st.container(border=True):
        st.markdown('<div class="result-label">Step 2</div><div class="result-title">Your record, explained</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["last_explanation"])

        action_col, note_col = st.columns([1, 2], gap="large")
        with action_col:
            st.download_button(
                "Download explanation",
                data=st.session_state["last_explanation"],
                file_name="plain_language_explanation.txt",
                use_container_width=True,
            )
        with note_col:
            st.markdown('<div class="privacy-note">Bring this explanation to your next appointment and use it as a starting point for questions.</div>', unsafe_allow_html=True)

    with st.expander("How clear was this explanation?", expanded=False):
        thumbs = st.radio("Your feedback", ["👍 Helpful", "👎 Not helpful"], horizontal=True, label_visibility="collapsed")
        comment = st.text_input("Anything confusing, or feedback for us? (optional)")

        if st.button("Send feedback"):
            save_feedback(
                timestamp=dt.datetime.utcnow().isoformat(),
                rating=thumbs,
                comment=comment,
            )
            st.success("Thanks. Your feedback helps us improve PlainRecord.")
