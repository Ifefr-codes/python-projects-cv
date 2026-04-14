"""
AI Document Q&A Tool (PDF Chatbot)
------------------------------------
Upload a PDF and ask questions about it using the Anthropic Claude API.
Usage: streamlit run pdf_qa_app.py
Requires: ANTHROPIC_API_KEY in a .env file or set as environment variable.
"""

import os
import streamlit as st
from PyPDF2 import PdfReader
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PDF Q&A Tool",
    page_icon="📄",
    layout="centered",
)

st.title("📄 AI PDF Q&A Tool")
st.caption("Upload a PDF document and ask questions about its content.")

# ── API CLIENT ────────────────────────────────────────────────────────────────

@st.cache_resource
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY not found. Add it to a .env file.")
        st.stop()
    return Anthropic(api_key=api_key)


# ── PDF TEXT EXTRACTION ───────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


# ── TRUNCATE CONTEXT (Claude's context window has limits) ─────────────────────

def truncate_text(text, max_chars=80000):
    if len(text) > max_chars:
        st.warning(f"⚠️ Document is large. Using first {max_chars:,} characters.")
        return text[:max_chars]
    return text


# ── MAIN APP ──────────────────────────────────────────────────────────────────

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
        pdf_text = truncate_text(pdf_text)

    if not pdf_text:
        st.error("Could not extract text from this PDF. It may be a scanned image.")
        st.stop()

    st.success(f"✅ PDF loaded: **{uploaded_file.name}** ({len(pdf_text):,} characters extracted)")

    # Show document preview
    with st.expander("📋 Preview extracted text"):
        st.text(pdf_text[:2000] + ("..." if len(pdf_text) > 2000 else ""))

    st.divider()

    # Chat interface
    st.subheader("💬 Ask a question about the document")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if user_question := st.chat_input("Ask anything about the PDF..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Build the prompt
        system_prompt = f"""You are a helpful document assistant. 
Answer questions based ONLY on the document content provided below.
If the answer is not in the document, say so clearly.

--- DOCUMENT CONTENT ---
{pdf_text}
--- END DOCUMENT ---"""

        # Build conversation history for API
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Call Claude API with streaming
        client = get_client()
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=api_messages,
            ) as stream:
                for text_chunk in stream.text_stream:
                    full_response += text_chunk
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        # Save assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear chat history"):
            st.session_state.messages = []
            st.rerun()

else:
    st.info("👆 Upload a PDF to get started.")
    st.markdown("""
**How it works:**
1. Upload any PDF document
2. The app extracts the text content
3. Ask questions in plain English
4. Claude answers based on the document

**Good for:** Research papers, manuals, reports, contracts, lecture notes
""")
