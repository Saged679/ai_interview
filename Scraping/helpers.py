import re


def clean_page_text(text: str) -> str:
    """Clean and organize text extracted from a single PDF page."""
    text = re.sub(r"\(cid:\d+\)", "", text)          # remove icon/cid codes
    text = re.sub(r"[ \t]+", " ", text)               # normalize horizontal spaces only
    text = re.sub(r"\n{3,}", "\n\n", text)            # collapse excess blank lines
    text = re.sub(r" *\n *", "\n", text)              # trim spaces around newlines
    return text.strip()
