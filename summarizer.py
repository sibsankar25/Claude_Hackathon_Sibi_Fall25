from pypdf import PdfReader
import docx
from anthropic import Anthropic
import os

# Initialize Claude client using the API key from environment variable
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_text(file, extension: str) -> str:
    """Extract text from txt, pdf, or docx file."""

    # TXT files
    if extension == "txt":
        return file.read().decode("utf-8", errors="ignore")

    # PDF files
    elif extension == "pdf":
        reader = PdfReader(file)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages)

    # DOCX files
    elif extension == "docx":
        document = docx.Document(file)
        return "\n".join(para.text for para in document.paragraphs)

    # Unsupported file type
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def summarize_with_claude(text: str, mode_label: str, action_items: bool = False) -> str:
    """
    Send extracted text to Claude and return the summary.

    If action_items=True, also ask Claude to extract concrete next steps.
    """

    # Map UI label to internal mode
    if "Ultra short" in mode_label:
        mode = "ultra_short"
    elif "Short (" in mode_label:
        mode = "short"
    else:
        mode = "detailed"

    extra_instructions = ""
    if action_items:
        extra_instructions = """
After the summary, add a section titled 'Action Items' with a bullet list of concrete, actionable next steps inferred from the document.
Each bullet should be phrased as a clear action. If there are no obvious actions, add a single line 'No explicit action items found.'
"""

    prompt = f"""
You are a professional document assistant used in a work setting.

User selected summary mode: {mode}.
- ultra_short: 1–2 sentence TL;DR
- short: 5 concise bullet points
- detailed: 2–3 paragraphs

First, produce the summary in the requested style under a heading 'Summary'.

{extra_instructions}

Document:
{text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",  # from your console
        max_tokens=900,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # Anthropic returns a list of content blocks; grab first text block
    return response.content[0].text
