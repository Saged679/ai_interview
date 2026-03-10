"""
app.py — Streamlit UI for the Afaf Interview Agent
Run with: streamlit run app.py
"""

import os
import json
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AGENT_ID = os.getenv("AGENT_ID", "")
INTERVIEW_PORT = 8502


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Afaf — AI Interview Agent",
    page_icon="🎙️",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header { text-align: center; padding: 1rem 0 0.5rem 0; }
    .main-header h1 { font-size: 2.4rem; margin-bottom: 0.2rem; }
    .main-header p  { font-size: 1.1rem; color: #888; }
    .start-link {
        display: block;
        text-align: center;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #10a37f, #0d8c6d);
        color: white !important;
        font-size: 1.3rem;
        font-weight: 700;
        border-radius: 10px;
        text-decoration: none;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(16, 163, 127, 0.3);
        transition: all 0.2s ease;
    }
    .start-link:hover {
        background: linear-gradient(135deg, #0d8c6d, #0a7a5e);
        box-shadow: 0 6px 20px rgba(16, 163, 127, 0.4);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🎙️ Afaf — AI Interview Agent</h1>
        <p>Enter a job description, then start your voice interview with Afaf</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Sidebar — Knowledge Base viewer ─────────────────────────────────────────
with st.sidebar:
    st.header("📄 Interviewee Knowledge Base")
    st.caption("This is the data Afaf uses during the interview.")

    kb_tab1, kb_tab2 = st.tabs(["CV Data", "GitHub Projects"])

    with kb_tab1:
        cv_path = os.path.join("knowledge_base", "cv_data.txt")
        if os.path.exists(cv_path):
            with open(cv_path, "r", encoding="utf-8") as f:
                st.text(f.read())
        else:
            st.warning("cv_data.txt not found.")

    with kb_tab2:
        gh_path = os.path.join("knowledge_base", "github_projects.txt")
        if os.path.exists(gh_path):
            with open(gh_path, "r", encoding="utf-8") as f:
                st.text(f.read())
        else:
            st.warning("github_projects.txt not found.")

    st.divider()
    st.subheader("⚙️ Configuration")
    st.text_input("Agent ID", value=AGENT_ID, disabled=True)
    st.text_input(
        "API Key",
        value=API_KEY[:8] + "..." if API_KEY else "",
        disabled=True,
    )

# ── Validation ───────────────────────────────────────────────────────────────
if not AGENT_ID:
    st.error(
        "**AGENT_ID** is not set. Run `python create_agent.py` first "
        "to create the agent and populate your `.env` file."
    )
    st.stop()

if not API_KEY:
    st.error("**ELEVENLABS_API_KEY** is not set in your `.env` file.")
    st.stop()


# ── Interview HTML generator ────────────────────────────────────────────────
def generate_interview_html(agent_id: str, job_description: str) -> str:
    """Generate a standalone HTML page with the ElevenLabs conversational widget.
    This runs outside Streamlit's iframe so audio input/output works properly."""
    dv = json.dumps({"job_description": job_description})
    # Escape for safe use inside a single-quoted HTML attribute
    dv_attr = dv.replace("&", "&amp;").replace("'", "&#39;")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview with Afaf</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .header {{
            text-align: center;
            padding: 2rem 1rem 1rem;
        }}
        .header h1 {{
            font-size: 2.2rem;
            color: #fff;
            margin-bottom: 0.5rem;
        }}
        .header p {{
            color: #aaa;
            font-size: 1.1rem;
            max-width: 500px;
            margin: 0 auto;
        }}
        .status {{
            background: rgba(16, 163, 127, 0.15);
            border: 1px solid rgba(16, 163, 127, 0.4);
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            margin: 1.5rem 0;
            color: #52c97a;
            font-size: 1rem;
            text-align: center;
        }}
        .widget-area {{
            flex: 1;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            width: 100%;
            padding: 1rem 2rem 3rem;
        }}
        .footer {{
            text-align: center;
            padding: 1rem;
            color: #555;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎙️ Interview with Afaf</h1>
        <p>Your AI interviewer is ready to begin</p>
    </div>
    <div class="status" id="status">
        ⏳ Loading interview widget...
    </div>
    <div class="widget-area">
        <elevenlabs-convai
            agent-id="{agent_id}"
            dynamic-variables='{dv_attr}'
        ></elevenlabs-convai>
    </div>
    <div class="footer">
        Powered by ElevenLabs Conversational AI
    </div>

    <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
    <script>
        // Wait for widget to load, then auto-click the call button
        let clickAttempts = 0;
        function tryAutoStart() {{
            clickAttempts++;
            const widget = document.querySelector('elevenlabs-convai');
            if (!widget) {{
                if (clickAttempts < 40) setTimeout(tryAutoStart, 500);
                return;
            }}
            document.getElementById('status').innerHTML =
                '✅ Widget loaded! Attempting to start call...';

            // Try to click the call button inside shadow DOM
            try {{
                if (widget.shadowRoot) {{
                    const buttons = widget.shadowRoot.querySelectorAll('button');
                    for (const btn of buttons) {{
                        btn.click();
                        document.getElementById('status').innerHTML =
                            '🎙️ Interview in progress — speak naturally with Afaf';
                        document.getElementById('status').style.borderColor = 'rgba(90, 159, 212, 0.4)';
                        document.getElementById('status').style.background = 'rgba(30, 42, 58, 0.5)';
                        document.getElementById('status').style.color = '#5a9fd4';
                        return;
                    }}
                }}
            }} catch(e) {{}}

            if (clickAttempts < 20) {{
                setTimeout(tryAutoStart, 1000);
            }} else {{
                document.getElementById('status').innerHTML =
                    '✅ Widget loaded! Click the <strong>phone button</strong> below to start.';
            }}
        }}
        setTimeout(tryAutoStart, 2000);
    </script>
</body>
</html>"""


# ── HTTP Server for interview page ──────────────────────────────────────────
class QuietHTTPHandler(SimpleHTTPRequestHandler):
    """Serve files from the static/ directory without logging."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="static", **kwargs)

    def log_message(self, format, *args):
        pass


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def _start_interview_server(port: int):
    os.makedirs("static", exist_ok=True)
    try:
        server = ReusableHTTPServer(("0.0.0.0", port), QuietHTTPHandler)
        server.serve_forever()
    except OSError:
        pass  # port already bound from a previous run


# Start the file server once per session
if "server_started" not in st.session_state:
    thread = threading.Thread(
        target=_start_interview_server, args=(INTERVIEW_PORT,), daemon=True
    )
    thread.start()
    time.sleep(0.3)
    st.session_state["server_started"] = True


# ── Job Description input ────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    job_description = st.text_area(
        "📋 Job Description",
        height=200,
        placeholder=(
            "Paste the job description here...\n\n"
            "Example: We are looking for a Full-Stack Software Engineer "
            "with experience in React, Node.js, and cloud services (AWS). "
            "The ideal candidate should have strong problem-solving skills..."
        ),
    )

with col2:
    st.markdown("#### 💡 How it works")
    st.markdown(
        """
        1. **Paste** a job description on the left
        2. Click **🚀 Start Interview**
        3. A new browser tab opens with the voice interview
        4. The call starts automatically (or click the phone button)
        5. Afaf asks progressively harder questions based on:
           - The job description you provided
           - The interviewee's CV & GitHub projects
        """
    )

st.divider()

# ── Start Interview ─────────────────────────────────────────────────────────
if job_description.strip():
    # Pre-generate the interview page so it's ready when the user clicks
    html_content = generate_interview_html(AGENT_ID, job_description.strip())
    os.makedirs("static", exist_ok=True)
    with open(os.path.join("static", "interview.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    url = f"http://localhost:{INTERVIEW_PORT}/interview.html"

    st.markdown(
        f'<a class="start-link" href="{url}" target="_blank">'
        f"🚀 Start Interview (opens in new tab)"
        f"</a>",
        unsafe_allow_html=True,
    )

    with st.expander("📝 Preview Job Description"):
        st.write(job_description.strip())
else:
    st.info("👆 Enter a job description above, then click **Start Interview** to begin.")
