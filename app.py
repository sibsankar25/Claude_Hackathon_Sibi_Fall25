import streamlit as st
import os
from summarizer import extract_text, summarize_with_claude

st.title("Doc TL;DR Work Assistant")
st.write(
    "Paste text or upload a PDF, DOCX, or TXT file to generate a concise summary. "
    "Optionally, extract concrete action items for work-related documents."
)

# 1. Pasted text input
st.markdown("### 1. Paste text (optional)")
pasted_text = st.text_area(
    "Paste text here (if filled, this will be used instead of the file):",
    height=200,
    placeholder="Paste any report, meeting notes, spec, or other document text here..."
)

# 2. File upload
st.markdown("### 2. Or upload a file")
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])

# 3. Summary style
st.markdown("### 3. Choose summary style")
mode = st.radio(
    "Summary style",
    [
        "Ultra short (1–2 sentences)",
        "Short (5 bullet points)",
        "Detailed (2–3 paragraphs)",
    ],
)

# 4. Action items option
action_items = st.checkbox(
    "Also extract action items / next steps (recommended for work docs)",
    value=True
)

# 5. Run summarization
if st.button("Summarize"):
    # Decide where to get text from
    if pasted_text.strip():
        text = pasted_text.strip()
        source = "pasted text"
    elif uploaded_file is not None:
        name = uploaded_file.name
        ext = os.path.splitext(name)[1].lower().lstrip(".")

        try:
            text = extract_text(uploaded_file, ext)
            source = f"uploaded file ({ext})"
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            st.stop()
    else:
        st.error("Please paste some text or upload a file.")
        st.stop()

    # Truncate very long input to avoid token issues
    MAX_CHARS = 15000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        st.warning("Input was long – truncated for this demo.")

    # Show basic stats (optional but nice for demo)
    word_count = len(text.split())
    st.info(f"Approx. input length: {word_count} words.")

    # Call Claude
    try:
        with st.spinner(f"Summarizing {source} with Claude..."):
            summary = summarize_with_claude(text, mode_label=mode, action_items=action_items)

        st.subheader("Summary & Actions")
        st.markdown(summary)
    except Exception as e:
        st.error(f"Something went wrong while calling Claude: {e}")
